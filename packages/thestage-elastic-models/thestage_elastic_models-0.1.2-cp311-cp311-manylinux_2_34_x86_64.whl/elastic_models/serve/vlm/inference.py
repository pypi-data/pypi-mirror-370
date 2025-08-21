import os
import time
from typing import Any

import numpy as np
import torch
from qlip_serve.common.model import BaseModel
from qlip_serve.common.model_config import DynamicBatcher, ModelConfig
from qlip_serve.common.signature import TextSignature
from transformers import AutoModelForImageTextToText as HFAutoModelForImageTextToText
from transformers import AutoProcessor

from elastic_models.transformers import (
    AutoModelForImageTextToText as EMAutoModelForImageTextToText,
)

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

allowed_batch_size = list(range(1, 16 + 1))
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
if model_size != "eager":
    model_name = f"{model_name}-paged"

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
HF_CACHE_DIR = os.path.join(PROJECT_DIR, ".cache", "huggingface")

# Default generation configuration
MODEL_GENERATION_CONFIG = {
    "max_new_tokens": 256,
    "min_new_tokens": 256,
    "temperature": 1.0,
    "top_p": 0.95,
    "do_sample": True,
}


class Model(BaseModel):
    model_name = model_name
    inputs = [
        TextSignature(shape=(1,), dtype=np.object_, name="prompt", external=True),
        TextSignature(shape=(1,), dtype=np.object_, name="image", external=True),
    ]
    outputs = [
        TextSignature(shape=(1,), dtype=np.bytes_, name="output", external=True),
    ]
    device_type = "gpu"
    model_config = ModelConfig(
        max_batch_size=max_batch_size,
        batcher=DynamicBatcher(
            preferred_batch_size=[max_batch_size],
            preserve_ordering=False,
            max_queue_delay_microseconds=500000,
        ),
    )

    def __init__(self):
        super().__init__()

        # Set device and precision
        self.device = "cuda" if self.device_type == "gpu" else "cpu"
        torch_dtype = torch.bfloat16 if self.device_type == "gpu" else torch.float32

        # Maximum allowed input tokens
        self.max_input_tokens = 4096

        # Basic model initialization parameters
        model_init_params = {
            "torch_dtype": torch_dtype,
            "attn_implementation": "sdpa",
        }

        # Set generation configuration
        self.generation_config: dict[str, Any] = MODEL_GENERATION_CONFIG.copy()

        # Load model based on size
        if model_size == "eager":
            model_class = HFAutoModelForImageTextToText
        else:
            model_init_params.update({"mode": model_size})
            model_class = EMAutoModelForImageTextToText
            self.generation_config["cache_implementation"] = "paged"

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
            "pretrained_model_name_or_path": model_repo,
            "local_files_only": local_files_only,
            "cache_dir": cache_dir,
        }

        if commit_hash:
            global_init_params["revision"] = commit_hash

        if model_hf_load:
            global_init_params["trust_remote_code"] = True
            global_init_params["token"] = HF_TOKEN

        # Load model and tokenizer
        self.model = model_class.from_pretrained(
            **global_init_params,
            **model_init_params,
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(
            **global_init_params,
            # add_eos_token=False,
            # padding_side="left",
            # pad_token="<|end_of_text|>",
        )
        self.tokenizer = self.processor.tokenizer

        if model_size != "eager":
            print("Starting warmup...", flush=True)
            # pick a token‐ID that definitely isn't the pad‐token
            non_pad_id = (
                self.tokenizer.bos_token_id
                if self.tokenizer.bos_token_id is not None
                else 0
            )

            # Create dummy input tensors
            dummy_input_ids = torch.full(
                (
                    max_batch_size,
                    self.max_input_tokens,
                ),  # max batch size x max sequence length
                non_pad_id,
                device=self.device,
            )
            attention_mask = torch.ones_like(dummy_input_ids)

            # Warmup run
            with torch.inference_mode():
                self.model.generate(
                    input_ids=dummy_input_ids,
                    attention_mask=attention_mask,
                    **self.generation_config,
                )

            print("Warmup completed.", flush=True)

    def forward(self, input_batch: dict[str, list[np.ndarray[Any, Any]]]) -> list[Any]:
        # Decode batch inputs from bytes to strings
        decoded_prompts = [
            prompt_bytes[0].decode() for prompt_bytes in input_batch["prompt"]
        ]
        decoded_images = [
            image_bytes[0].decode() for image_bytes in input_batch["image"]
        ]
        batch_size = len(decoded_prompts)

        chat_messages_batch = []
        for prompt, image in zip(decoded_prompts, decoded_images):
            content = [
                {"type": "text", "text": prompt},
            ]
            if image:
                content.append({"type": "image", "image": image})
            chat_messages_batch.append(
                [
                    # {
                    #     "role": "system",
                    #     "content": "You are a helpful AI assistant. "
                    #     "Be direct and concise in your responses.",
                    # },
                    {
                        "role": "user",
                        "content": content,
                    },
                ]
            )

        print(chat_messages_batch, flush=True)

        # Tokenize inputs using chat template formatting
        inputs = self.processor.apply_chat_template(
            chat_messages_batch,
            padding=True,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.device, dtype=torch.bfloat16)

        input_ids = inputs["input_ids"]
        # Validate token lengths against model limits
        for sample_idx, input_sequence in enumerate(input_ids):
            sequence_length = len(input_sequence)
            if sequence_length > self.max_input_tokens:
                raise ValueError(
                    f"Sample {sample_idx} exceeds token limit "
                    f"({sequence_length} > {self.max_input_tokens})"
                )

        # Generate responses with timing measurement
        generation_start = time.monotonic()
        with torch.inference_mode():
            generation_output = self.model.generate(
                **inputs,
                num_return_sequences=1,
                return_dict_in_generate=True,
                **self.generation_config,
            )
        avg_time_per_sample = (time.monotonic() - generation_start) / batch_size

        # Process model outputs and compile results
        input_sequence_lengths = [len(seq) for seq in input_ids]
        results = []

        for sample_idx in range(batch_size):
            input_token_count = input_sequence_lengths[sample_idx]
            full_sequence_length = generation_output.sequences[sample_idx].shape[0]

            # Extract only the newly generated tokens
            generated_tokens = generation_output.sequences[sample_idx][
                input_token_count:full_sequence_length
            ]
            generated_text = self.processor.decode(
                generated_tokens, skip_special_tokens=True
            )

            # Calculate performance metrics
            generated_token_count = full_sequence_length - input_token_count
            tokens_per_second = generated_token_count / avg_time_per_sample

            results.append(
                {
                    "output": [
                        {
                            "response": generated_text,
                            "generation_time": avg_time_per_sample,
                            "batch_size": batch_size,
                            "num_tokens": generated_token_count,
                            "input_tokens": input_token_count,
                            "tps": tokens_per_second,
                        }
                    ]
                }
            )

        return results
