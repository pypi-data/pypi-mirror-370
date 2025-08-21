import ast
import io
import os
import time
from typing import Any, Dict, List

import numpy as np
import torch
from diffusers import DiffusionPipeline as HFDiffusionPipeline
from PIL import Image
from qlip_serve.common.model import BaseModel, SeqEnsembleModel
from qlip_serve.common.model_config import DynamicBatcher, ModelConfig
from qlip_serve.common.signature import ImageSignature, TensorSignature, TextSignature

from elastic_models.diffusers import DiffusionPipeline as EMDiffusionPipeline

# ----------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------
allowed_model_size = ("XL", "L", "M", "S", "eager")
model_size_env = "MODEL_SIZE"
model_size = os.getenv(model_size_env)
if not isinstance(model_size, str) or model_size not in allowed_model_size:
    raise ValueError(
        f"Invalid or missing {repr(model_size_env)} environment variable, must have one of these values "
        f"[{', '.join(map(repr, allowed_model_size))}], but got {repr(model_size)}."
    )

allowed_batch_size = list(range(1, 32 + 1))
max_batch_size_env = "BATCH_SIZE"
max_batch_size = os.getenv(max_batch_size_env)
try:
    max_batch_size = int(max_batch_size)
    if max_batch_size not in allowed_batch_size:
        raise ValueError()
except ValueError:
    raise ValueError(
        f"Invalid {repr(max_batch_size_env)} environment variable, must have one of these values "
        f"[{', '.join(map(repr, allowed_batch_size))}], but got {repr(max_batch_size)}"
    )

model_repo_env = "MODEL_REPO"
model_repo = os.environ.get(model_repo_env)
if not model_repo:
    raise ValueError(f"Environment variable {repr(model_repo_env)} must be set.")

# Generate model name dynamically based on repo and size
base_name = model_repo.split("/")[1].lower().replace(".", "-")
size_lower = model_size.lower()
model_name = f"{base_name}-{size_lower}-bs{max_batch_size}"

model_hf_commit_hash_env = "MODEL_HF_COMMIT_HASH"
commit_hash = os.environ.get(model_hf_commit_hash_env)

model_hf_load_env = "MODEL_HF_LOAD"
model_hf_load = os.environ.get(model_hf_load_env)
if model_hf_load is not None:
    model_hf_load = model_hf_load.lower() in ("true", "1", "t")
else:
    model_hf_load = True

# Project directory
PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/project")

# Hugging Face configuration
HF_TOKEN = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")
# TODO: parametrize through build_model params
HF_CACHE_DIR = os.path.join(PROJECT_DIR, ".cache", "huggingface")

# FLUX-only aspect ratio presets (fixed to fit [512, 1280] and be /32-aligned)
FLUX_ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1280, 736),  # ~16:9, within limits, /32 aligned
    "21:9": (1280, 544),  # exact /32, closest to 21:9
    "3:2": (1248, 832),
    "2:3": (832, 1248),
    "4:3": (1184, 896),
    "3:4": (896, 1184),
    "5:4": (1152, 928),
    "4:5": (928, 1152),
    "9:16": (736, 1280),  # ~9:16, within limits, /32 aligned
    "9:21": (544, 1280),  # exact /32, closest to 9:21
}


# Server-side validation constants - CRITICAL FOR SECURITY
MIN_INFERENCE_STEPS = 1
MAX_INFERENCE_STEPS = 1000
MIN_GUIDANCE_SCALE = 0.0
MAX_GUIDANCE_SCALE = 100.0
MIN_SEED = 0
MAX_SEED = 2**32 - 1  # uint32 max
MAX_PROMPT_LENGTH = 1000

# Default generation configuration
if model_repo == "black-forest-labs/FLUX.1-schnell":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 4,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
elif model_repo == "black-forest-labs/FLUX.1-dev":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 28,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
elif model_repo == "stabilityai/stable-diffusion-xl-base-1.0":
    MODEL_GENERATION_CONFIG = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 20,
        "guidance_scale": 6.5,
        "num_images_per_prompt": 1,
    }
else:
    raise ValueError(f"Model {repr(model_repo)} not supported yet.")


class Model(BaseModel):
    model_name = "model"
    inputs = [
        TextSignature(shape=(1,), dtype=np.object_, name="pos_prompt", external=True),
        TensorSignature(shape=(1,), dtype=np.uint32, name="seed", external=True),
        TextSignature(shape=(1,), dtype=np.object_, name="aspect_ratio", external=True),
        TensorSignature(
            shape=(1,), dtype=np.float32, name="guidance_scale", external=True
        ),
        TensorSignature(
            shape=(1,), dtype=np.uint32, name="num_inference_steps", external=True
        ),
    ]
    outputs = [
        ImageSignature(
            shape=(-1, -1, 3), dtype=np.uint8, name="image_pil", external=False
        ),
        TextSignature(
            shape=(1,), dtype=np.bytes_, name="metadata_internal", external=False
        ),
    ]
    device_type = "gpu"  # if torch.cuda.is_available() else "cpu"
    model_config = ModelConfig(
        max_batch_size=max_batch_size,
        batcher=DynamicBatcher(
            preferred_batch_size=[max_batch_size], preserve_ordering=False
        ),
    )

    def __init__(self):
        super().__init__()
        # Set device and precision
        self.device = "cuda" if self.device_type == "gpu" else "cpu"
        torch_dtype = torch.bfloat16 if self.device_type == "gpu" else torch.float32

        # Basic model initialization parameters
        init_params = {
            "torch_dtype": torch_dtype,
        }

        # Set generation configuration
        self.generation_config: dict[str, Any] = MODEL_GENERATION_CONFIG.copy()

        # Load model based on size
        if model_size == "eager":
            pipe_class = HFDiffusionPipeline
        else:
            init_params.update({"mode": model_size})
            pipe_class = EMDiffusionPipeline

        if model_hf_load:
            # Download from HF
            local_files_only = False
            cache_dir = HF_CACHE_DIR
        else:
            # Download from S3 (Should be consistent with S3 path)
            local_files_only = True
            # We need to copy all the files from S3 model directory
            # Because the snapshot directory symlinks to the files in the neighbors directories
            cache_dir = os.path.join(
                PROJECT_DIR,
                "artifacts/huggingface/hub/",
            )

        global_init_params = {
            "local_files_only": local_files_only,
            "cache_dir": cache_dir,
            "pretrained_model_name_or_path": model_repo,
        }

        if commit_hash:
            global_init_params["revision"] = commit_hash

        if model_hf_load:
            global_init_params["token"] = HF_TOKEN

        # Load model and tokenizer
        self.pipe = pipe_class.from_pretrained(
            **global_init_params,
            **init_params,
        ).to(self.device)

        self.pipe.set_progress_bar_config(leave=False)

        if model_size != "eager":
            print("Starting warmup...", flush=True)
            # Warmup run
            with torch.inference_mode():
                self.pipe(
                    prompt=["warmup"] * max_batch_size,
                    **self.generation_config,
                )
            print("Warmup completed.", flush=True)

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Any]:
        # SERVER-SIDE VALIDATION: Basic input sanity check
        if not inputs or "pos_prompt" not in inputs:
            raise ValueError("Invalid request: missing required 'pos_prompt' field")

        num_inputs = len(inputs["pos_prompt"])
        if num_inputs == 0:
            raise ValueError("Invalid request: empty prompt list")
        if num_inputs > max_batch_size:
            raise ValueError(
                f"Invalid request: batch size {num_inputs} exceeds maximum {max_batch_size}"
            )

        # Check if this is a FLUX model
        is_flux = "FLUX" in model_repo

        # Group inputs by generation parameters for batching
        batches = {}
        for i in range(num_inputs):
            # Extract parameters
            prompt = inputs["pos_prompt"][i][0].decode()

            # SERVER-SIDE VALIDATION: Validate and truncate prompt length
            if len(prompt) > MAX_PROMPT_LENGTH:
                print(
                    f"WARNING: Prompt length {len(prompt)} exceeds maximum "
                    f"{MAX_PROMPT_LENGTH}, truncating for security"
                )
                prompt = prompt[:MAX_PROMPT_LENGTH]

            seed = int(inputs["seed"][i][0])

            # SERVER-SIDE VALIDATION: Validate and clamp seed
            if seed < MIN_SEED:
                print(
                    f"WARNING: Seed {seed} below minimum {MIN_SEED}, clamping to minimum"
                )
                seed = MIN_SEED
            elif seed > MAX_SEED:
                print(
                    f"WARNING: Seed {seed} exceeds maximum {MAX_SEED}, clamping to maximum"
                )
                seed = MAX_SEED

            # Get optional parameters with defaults
            aspect_ratio = None
            if "aspect_ratio" in inputs and inputs["aspect_ratio"][i][0] != b"":
                aspect_ratio = inputs["aspect_ratio"][i][0].decode()

            guidance_scale = self.generation_config["guidance_scale"]
            if "guidance_scale" in inputs and inputs["guidance_scale"][i][0] != 0:
                guidance_scale = float(inputs["guidance_scale"][i][0])

                # SERVER-SIDE VALIDATION: Validate and clamp guidance_scale
                if guidance_scale < MIN_GUIDANCE_SCALE:
                    print(
                        f"WARNING: guidance_scale {guidance_scale} below minimum "
                        f"{MIN_GUIDANCE_SCALE}, clamping to minimum"
                    )
                    guidance_scale = MIN_GUIDANCE_SCALE
                elif guidance_scale > MAX_GUIDANCE_SCALE:
                    print(
                        f"WARNING: guidance_scale {guidance_scale} exceeds maximum "
                        f"{MAX_GUIDANCE_SCALE}, clamping to maximum"
                    )
                    guidance_scale = MAX_GUIDANCE_SCALE

            num_inference_steps = self.generation_config["num_inference_steps"]
            num_steps_input = inputs.get("num_inference_steps")
            if num_steps_input and num_steps_input[i][0] != 0:
                num_inference_steps = int(num_steps_input[i][0])
                # SERVER-SIDE VALIDATION: Validate and cap num_inference_steps
                if num_inference_steps < MIN_INFERENCE_STEPS:
                    print(
                        f"WARNING: num_inference_steps {num_inference_steps} below minimum "
                        f"{MIN_INFERENCE_STEPS}, clamping for security"
                    )
                    num_inference_steps = MIN_INFERENCE_STEPS
                elif num_inference_steps > MAX_INFERENCE_STEPS:
                    print(
                        f"WARNING: num_inference_steps {num_inference_steps} exceeds maximum "
                        f"{MAX_INFERENCE_STEPS}, clamping for security"
                    )
                    num_inference_steps = MAX_INFERENCE_STEPS

            # Handle aspect ratio for FLUX models
            width = self.generation_config["width"]
            height = self.generation_config["height"]
            actual_aspect_ratio = None  # Only set if actually applied
            if is_flux and aspect_ratio and aspect_ratio in FLUX_ASPECT_RATIOS:
                width, height = FLUX_ASPECT_RATIOS[aspect_ratio]
                actual_aspect_ratio = aspect_ratio  # Store only if applied

            # Create batch key (group by all parameters except prompt and seed)
            batch_key = (width, height, guidance_scale, num_inference_steps)

            if batch_key not in batches:
                batches[batch_key] = {
                    "prompts": [],
                    "seeds": [],
                    "indices": [],
                    "aspect_ratios": [],
                    "config": {
                        "width": width,
                        "height": height,
                        "guidance_scale": guidance_scale,
                        "num_inference_steps": num_inference_steps,
                        "num_images_per_prompt": self.generation_config[
                            "num_images_per_prompt"
                        ],
                    },
                }

            batches[batch_key]["prompts"].append(prompt)
            batches[batch_key]["seeds"].append(seed)
            batches[batch_key]["indices"].append(i)
            batches[batch_key]["aspect_ratios"].append(actual_aspect_ratio)

        # Process each batch
        all_results = [None] * num_inputs

        for batch_key, batch_data in batches.items():
            batch_prompts = batch_data["prompts"]
            batch_seeds = batch_data["seeds"]
            batch_indices = batch_data["indices"]
            batch_aspect_ratios = batch_data["aspect_ratios"]
            batch_config = batch_data["config"]

            # Create generators for this batch
            generators = []
            for seed in batch_seeds:
                generators.append(torch.Generator(device=self.device).manual_seed(seed))

            # Generate images for this batch
            start_time = time.time()
            with torch.inference_mode():
                images = self.pipe(
                    prompt=batch_prompts,
                    generator=generators,
                    output_type="pil",
                    **batch_config,
                ).images
            generation_time = (time.time() - start_time) / len(batch_prompts)

            # Store results in correct positions
            for j, idx in enumerate(batch_indices):
                all_results[idx] = {
                    "image_pil": images[j],
                    "metadata_internal": [
                        {
                            "generation_time": generation_time,
                            "batch_size": len(batch_prompts),
                            "seed": batch_seeds[j],
                            "aspect_ratio": batch_aspect_ratios[j],
                            "width": batch_config["width"],
                            "height": batch_config["height"],
                            "guidance_scale": batch_config["guidance_scale"],
                            "num_inference_steps": batch_config["num_inference_steps"],
                        }
                    ],
                }

        return all_results


class PostProcessor(BaseModel):
    model_name = "postprocessor"
    inputs = [
        ImageSignature(
            shape=(-1, -1, 3), dtype=np.uint8, name="image_pil", external=False
        ),
        TextSignature(
            shape=(1,), dtype=np.bytes_, name="metadata_internal", external=False
        ),
    ]
    outputs = [
        ImageSignature(shape=(1,), dtype=np.bytes_, name="image", external=True),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata", external=True),
    ]
    device_type = "cpu"
    model_config = ModelConfig(
        max_batch_size=max_batch_size,
        batcher=DynamicBatcher(
            preferred_batch_size=[max_batch_size], preserve_ordering=False
        ),
    )
    model_count = 4

    def serialize_image(self, image_array: np.ndarray, format="WEBP", **params):
        buffer = io.BytesIO()
        pil_image = Image.fromarray(image_array)

        # Save image to buffer
        pil_image.save(buffer, format=format, **params)
        image_bytes = buffer.getvalue()
        return image_bytes

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Dict[str, Any]]:
        num_inputs = len(inputs["image_pil"])

        # It will be more efficient for speed to convert images to uint8 or with lossy codec
        result = []
        for i in range(num_inputs):
            image_pil = inputs["image_pil"][i]
            start_time = time.time()
            image = self.serialize_image(image_pil, format="WEBP", quality=80)
            postprocessing_time = time.time() - start_time
            metadata = ast.literal_eval(inputs["metadata_internal"][i][0].decode())
            metadata["postprocessing_time"] = postprocessing_time
            result.append({"image": image, "metadata": metadata})

        return result


class EnsembleModel(SeqEnsembleModel):
    model_name = model_name
    models = [Model, PostProcessor]
    inputs = [
        TextSignature(shape=(1,), dtype=np.object_, name="pos_prompt", external=True),
        TensorSignature(shape=(1,), dtype=np.uint32, name="seed", external=True),
        TextSignature(shape=(1,), dtype=np.object_, name="aspect_ratio", external=True),
        TensorSignature(
            shape=(1,), dtype=np.float32, name="guidance_scale", external=True
        ),
        TensorSignature(
            shape=(1,), dtype=np.uint32, name="num_inference_steps", external=True
        ),
    ]
    outputs = [
        ImageSignature(shape=(1,), dtype=np.bytes_, name="image", external=True),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata", external=True),
    ]
    model_config = ModelConfig(max_batch_size=max_batch_size)
