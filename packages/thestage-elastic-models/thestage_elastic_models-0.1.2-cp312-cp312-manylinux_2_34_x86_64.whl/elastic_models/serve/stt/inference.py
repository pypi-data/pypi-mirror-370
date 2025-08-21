import io
import os
import time
from io import BytesIO
from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Tuple,
    Union,
    Generator,
    Iterator,
    Optional,
)

import numpy as np
import torch
import torchaudio
from qlip_serve.common.model import BaseModel, SeqEnsembleModel
from qlip_serve.common.model_config import ModelConfig
from qlip_serve.common.signature import FileSignature, TensorSignature, TextSignature
from scipy.io.wavfile import write
from transformers import (
    WhisperForConditionalGeneration as HFWhisperForConditionalGeneration,
)
from transformers import (
    WhisperProcessor,
)

from elastic_models.transformers import (
    WhisperForConditionalGeneration as EMWhisperForConditionalGeneration,
)

# ----------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------
allowed_model_size = ("XL", "L", "M", "S", "eager")
model_size_env = "MODEL_SIZE"
model_size = os.getenv(model_size_env)
if not isinstance(model_size, str) or model_size not in allowed_model_size:
    raise ValueError(
        f"Invalid or missing {repr(model_size_env)} environment variable, must have "
        f"one of these values [{', '.join(map(repr, allowed_model_size))}], "
        f"but got {repr(model_size)}."
    )

allowed_batch_size = list(range(1, 256 + 1))
max_batch_size_env = "BATCH_SIZE"
max_batch_size_str = os.getenv(max_batch_size_env)
try:
    if max_batch_size_str is None:
        raise ValueError("is not set")
    max_batch_size = int(max_batch_size_str)
    if max_batch_size not in allowed_batch_size:
        raise ValueError("not in allowed range")
except ValueError as e:
    raise ValueError(
        f"Invalid {repr(max_batch_size_env)} environment variable, must have one of "
        f"these values [{', '.join(map(repr, allowed_batch_size))}], but got "
        f"{repr(max_batch_size_str)}. Reason: {e}"
    )

allowed_pipeline_batch_size = list(range(1, 256 + 1))
pipeline_max_batch_size_env = "PIPELINE_MAX_BATCH_SIZE"
pipeline_max_batch_size_str = os.getenv(pipeline_max_batch_size_env)
try:
    if pipeline_max_batch_size_str is None:
        raise ValueError("is not set")
    pipeline_max_batch_size = int(pipeline_max_batch_size_str)
    if pipeline_max_batch_size not in allowed_pipeline_batch_size:
        raise ValueError("not in allowed range")
except ValueError as e:
    raise ValueError(
        f"Invalid {repr(pipeline_max_batch_size_env)} environment variable, must have "
        f"one of these values [{', '.join(map(repr, allowed_pipeline_batch_size))}], "
        f"but got {repr(pipeline_max_batch_size_str)}. Reason: {e}"
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
model_hf_load_str = os.environ.get(model_hf_load_env)
model_hf_load: bool
if model_hf_load_str is not None:
    model_hf_load = model_hf_load_str.lower() in ("true", "1", "t")
else:
    model_hf_load = True

# Project directory
PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/project")

# Hugging Face configuration
HF_TOKEN = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")
HF_CACHE_DIR = os.path.join(PROJECT_DIR, ".cache", "huggingface")

# Default generation configuration
if model_repo == "openai/whisper-large-v3":
    MODEL_GENERATION_CONFIG = {
        "num_beams": 1,
        "cache_implementation": "flexi-static",
        "disable_compile": True,
    }
else:
    raise ValueError(f"Model {repr(model_repo)} not supported yet.")

WHISPER_SAMPLE_RATE = 16000


# Inspiration: https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/audio.py
def decode_audio(
    input_file: Union[str, BinaryIO],
    sampling_rate: int = WHISPER_SAMPLE_RATE,
    split_stereo: bool = False,
):
    """Decodes the audio.

    Args:
      input_file: Path to the input file or a file-like object.
      sampling_rate: Resample the audio to this sample rate.
      split_stereo: Return separate left and right channels.

    Returns:
      A float32 Torch Tensor.

      If `split_stereo` is enabled, the function returns a 2-tuple with the
      separated left and right channels.
    """

    # TODO: torchaudio._backend.utils.load has been deprecated. As TorchAudio
    # is no longer being actively developed, this function can no longer be
    # supported. See https://github.com/pytorch/audio/issues/3902 for more
    # details. It will be removed from 2.9 release.
    waveform, audio_sf = torchaudio.load(input_file)  # waveform: channels X T

    if audio_sf != sampling_rate:
        waveform = torchaudio.functional.resample(
            waveform, orig_freq=audio_sf, new_freq=sampling_rate
        )
    if split_stereo:
        return waveform[0], waveform[1]

    return waveform.mean(0)


def generate_noise_sample(
    duration: float, sample_rate: int
) -> Dict[str, Union[np.ndarray, int, BytesIO]]:
    """Generate a noise sample for testing/warmup purposes.

    Args:
        duration: Duration of the noise sample in seconds
        sample_rate: Sample rate for the audio

    Returns:
        Dictionary containing array, sampling_rate, and bytes buffer
    """
    num_samples = int(sample_rate * duration)
    # Generate proper audio array first
    audio_array = np.random.randn(num_samples)  # Gaussian noise
    audio_array = audio_array.astype(np.float32)

    # Normalize to [-1, 1] range
    audio_array /= np.max(np.abs(audio_array))

    # Convert to bytes buffer with WAV format
    buffer = BytesIO()
    write(buffer, sample_rate, audio_array)
    buffer.seek(0)

    return {"array": audio_array, "sampling_rate": sample_rate, "bytes": buffer}


def warmup_model(
    processor: WhisperProcessor,
    model: Union[HFWhisperForConditionalGeneration, EMWhisperForConditionalGeneration],
    warmup_pipeline_max_batch_size: int,
    full_warmup: bool = False,
) -> None:
    """Warmup the model with noise samples to prepare for inference.

    Args:
        processor: Whisper processor for audio preprocessing
        model: Whisper model to warmup
        warmup_pipeline_max_batch_size: Maximum batch size to test
        full_warmup: Whether to test all batch sizes or just the maximum
    """
    if full_warmup:
        min_batch_size = 0
    else:
        min_batch_size = warmup_pipeline_max_batch_size - 1

    # Calculate total steps for progress tracking
    total_steps = warmup_pipeline_max_batch_size - min_batch_size
    current_step = 0

    for batch_size in range(warmup_pipeline_max_batch_size, min_batch_size, -1):
        current_step += 1
        progress_percent = (current_step / total_steps) * 100

        # Display progress with carriage return to overwrite previous line
        progress_msg = (
            f"\rWarmup progress: {progress_percent:.1f}% - "
            f"Processing batch size {batch_size}..."
        )
        print(progress_msg, end="", flush=True)

        samples = [
            generate_noise_sample(duration=1.0, sample_rate=WHISPER_SAMPLE_RATE)
            for _ in range(batch_size)
        ]
        languages = ["en"] * batch_size

        # For Whisper processing - use the array directly
        inputs = processor(
            audio=[sample["array"] for sample in samples],
            sampling_rate=WHISPER_SAMPLE_RATE,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            torch_dtype=model.dtype,
        )

        input_features = inputs["input_features"].to(model.device).to(model.dtype)

        model.generate(input_features, language=languages, task="transcribe")

    # Clear the progress line and print completion message
    spaces = " " * 20
    completion_msg = "\rWarmup progress: 100.0% - Completed all batch sizes!" + spaces
    print(completion_msg, flush=True)


class TheStageASRPipeline:
    def __init__(
        self,
        model: Union[
            HFWhisperForConditionalGeneration, EMWhisperForConditionalGeneration
        ],
        processor: WhisperProcessor,
        device: str,
    ) -> None:
        """Initialize the ASR pipeline.

        Args:
            model: Whisper model for inference
            processor: Whisper processor for audio preprocessing
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.model = model
        self.processor = processor
        self.device = device

    def chunk_generator_all(
        self, inputs: List[np.ndarray], chunk_length_samples: int
    ) -> Generator[Tuple[int, int, np.ndarray], None, None]:
        """Generate chunks from all input audio samples.

        Args:
            inputs: List of audio arrays
            chunk_length_samples: Length of each chunk in samples

        Yields:
            Tuple of (sample_id, chunk_id, audio_chunk)
        """
        for sample_id, audio in enumerate(inputs):
            num_chunks = (len(audio) + chunk_length_samples - 1) // chunk_length_samples
            for chunk_id in range(num_chunks):
                start_idx = chunk_id * chunk_length_samples
                end_idx = min((chunk_id + 1) * chunk_length_samples, len(audio))
                audio_chunk = audio[start_idx:end_idx]
                audio_chunk = self.pad_audio_chunk(audio_chunk, chunk_length_samples)
                yield (sample_id, chunk_id, audio_chunk)

    def pad_audio_chunk(
        self, audio_chunk: np.ndarray, target_length: int
    ) -> np.ndarray:
        """Pad or truncate audio chunk to target length.

        Args:
            audio_chunk: Audio chunk to process
            target_length: Target length in samples

        Returns:
            Processed audio chunk of target length
        """
        current_length = len(audio_chunk)
        if current_length < target_length:
            padding = np.zeros(target_length - current_length, dtype=audio_chunk.dtype)
            audio_chunk = np.concatenate((audio_chunk, padding))
        elif current_length > target_length:
            audio_chunk = audio_chunk[:target_length]
        return audio_chunk

    def batch_iterator(
        self,
        generator: Generator[Tuple[int, int, np.ndarray], None, None],
        batch_size: int,
    ) -> Iterator[List[Tuple[int, int, np.ndarray]]]:
        """Create batches from a generator.

        Args:
            generator: Generator yielding individual items
            batch_size: Size of each batch

        Yields:
            Lists of items forming batches
        """
        from itertools import islice

        iterator = iter(generator)
        for first in iterator:
            batch = [first] + list(islice(iterator, batch_size - 1))
            yield batch

    def generate(
        self,
        inputs: List[np.ndarray],
        lang_ids: List[str],
        batch_size: int,
        chunk_length_s: float = 30.0,
        **generate_kwargs: Any,
    ) -> List[str]:
        """Generate transcriptions for input audio samples.

        Args:
            inputs: List of audio arrays to transcribe
            lang_ids: List of language IDs for each input
            batch_size: Batch size for processing
            chunk_length_s: Length of each chunk in seconds
            **generate_kwargs: Additional arguments for generation

        Returns:
            List of transcription strings
        """
        chunks: Dict[int, List[Tuple[int, str]]] = {
            sample_id: [] for sample_id in range(len(inputs))
        }
        full_transcriptions: List[str] = []

        chunk_length_samples = int(chunk_length_s * WHISPER_SAMPLE_RATE)

        all_chunks_generator = self.chunk_generator_all(inputs, chunk_length_samples)
        batch_iter = self.batch_iterator(all_chunks_generator, batch_size)

        for batch in batch_iter:
            sample_ids = [sample_id for sample_id, chunk_id, audio_chunk in batch]
            chunk_ids = [chunk_id for sample_id, chunk_id, audio_chunk in batch]
            audio_chunks = [audio_chunk for sample_id, chunk_id, audio_chunk in batch]
            batch_lang_ids = [lang_ids[sample_id] for sample_id in sample_ids]

            padded_inputs = self.processor.feature_extractor(
                audio_chunks,
                sampling_rate=WHISPER_SAMPLE_RATE,
                return_tensors="pt",
                padding=False,  # No need to pad here since audio chunks are already padded
            )

            input_features = padded_inputs.input_features.to(self.device)
            if hasattr(self.model, "dtype"):
                input_features = input_features.to(self.model.dtype)

            with torch.inference_mode():
                predicted_ids = self.model.generate(
                    input_features,
                    language=batch_lang_ids,
                    task="transcribe",
                    **generate_kwargs,
                )

            transcription_chunks = self.processor.tokenizer.batch_decode(
                predicted_ids, skip_special_tokens=True
            )

            for sample_id, chunk_id, transcription in zip(
                sample_ids, chunk_ids, transcription_chunks
            ):
                chunks[sample_id].append((chunk_id, transcription))

        for sample_id in range(len(inputs)):
            chunks[sample_id].sort(key=lambda x: x[0])

            full_transcription = " ".join(
                [transcription for chunk_id, transcription in chunks[sample_id]]
            )

            full_transcriptions.append(full_transcription)

        return full_transcriptions

    def __call__(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
        batch_size: int = 1,
        return_timestamps: bool = False,
        generate_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        """Call the pipeline for transcription.

        Args:
            inputs: Audio input(s) to transcribe
            batch_size: Batch size for processing
            return_timestamps: Whether to return timestamps (not implemented)
            generate_kwargs: Additional generation arguments
            **kwargs: Additional keyword arguments including lang_ids

        Returns:
            List of dictionaries containing transcription results
        """
        if generate_kwargs is None:
            generate_kwargs = {}

        if not isinstance(inputs, list):
            inputs = [inputs]

        # Extract lang_ids from kwargs or default to 'en'
        lang_ids = kwargs.get("lang_ids", ["en"] * len(inputs))

        transcriptions = self.generate(
            inputs=inputs, lang_ids=lang_ids, batch_size=batch_size, **generate_kwargs
        )

        return [{"text": text} for text in transcriptions]


class Preprocessor(BaseModel):
    inputs = [
        FileSignature((-1,), np.bytes_, "audio_bytes_tensor", allow_ragged_batch=False),
        TextSignature((-1,), np.bytes_, "lang_id", allow_ragged_batch=False),
    ]
    outputs = [
        TensorSignature((-1,), np.float32, "decoded_audio"),
        TextSignature((-1,), np.bytes_, "lang_id_processed"),
    ]
    model_name = "preprocessor"
    model_config = ModelConfig(max_batch_size=max_batch_size)
    device_type = "cpu"

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Dict[str, Any]]:
        """Process audio bytes and language IDs.

        Args:
            inputs: Dictionary containing audio_bytes_tensor and lang_id arrays

        Returns:
            List of dictionaries with decoded_audio and lang_id_processed
        """
        processed_audios = []

        for audio_bytes, input_lang_id in zip(
            inputs["audio_bytes_tensor"], inputs["lang_id"]
        ):
            lang_id = input_lang_id[0].decode("utf8")
            # Decode and process each audio sample
            decoded_audio = decode_audio(io.BytesIO(audio_bytes[0]))
            if lang_id == "":
                lang_id = "en"

            processed_audios.append(
                {
                    "decoded_audio": decoded_audio,
                    "lang_id_processed": [lang_id.encode()],
                }
            )

        return processed_audios


class Whisper(BaseModel):
    inputs = [
        TensorSignature((-1,), np.float32, "decoded_audio", allow_ragged_batch=True),
        TextSignature((-1,), np.bytes_, "lang_id_processed", allow_ragged_batch=False),
    ]
    outputs = [
        TextSignature((-1,), np.bytes_, "transcription"),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata"),
    ]
    model_name = "model"
    model_config = ModelConfig(max_batch_size=max_batch_size)
    # device_type = "gpu" if torch.cuda.is_available() else "cpu"
    # CHANGE HERE FOR LOCAL TEST PURPOSES (to "cpu")
    device_type = "gpu"  # hardcode to avoid possible ambiguity

    def __init__(self) -> None:
        """Initialize the Whisper model with proper configuration."""
        super().__init__()
        # Set device and precision
        self.device = "cuda" if self.device_type == "gpu" else "cpu"
        torch_dtype = torch.float16 if self.device_type == "gpu" else torch.float32

        # Basic model initialization parameters
        init_params: Dict[str, Any] = {
            "torch_dtype": torch_dtype,
        }

        # Set generation configuration
        self.generation_config: Dict[str, Any] = MODEL_GENERATION_CONFIG.copy()

        # Load model based on size
        if model_size == "eager":
            model_class = HFWhisperForConditionalGeneration
        else:
            model_class = EMWhisperForConditionalGeneration
            init_params.update({"mode": model_size})
            self.generation_config.update(
                {
                    "cache_implementation": "flexi-static",
                    "disable_compile": True,
                }
            )

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

        global_init_params: Dict[str, Any] = {
            "local_files_only": local_files_only,
            "cache_dir": cache_dir,
            "pretrained_model_name_or_path": model_repo,
        }

        if commit_hash:
            global_init_params["revision"] = commit_hash

        if model_hf_load:
            global_init_params["token"] = HF_TOKEN

        self.processor = WhisperProcessor.from_pretrained(**global_init_params)
        self.model = model_class.from_pretrained(
            **global_init_params,
            **init_params,
        )

        if self.device_type == "gpu":
            self.model = self.model.to(self.device).half()
        else:
            self.model = self.model.to(self.device)

        self.model.eval()

        self.pipeline = TheStageASRPipeline(self.model, self.processor, self.device)

        if model_size != "eager":
            print("Starting warmup...", flush=True)
            # Warmup run
            warmup_model(
                processor=self.processor,
                model=self.model,
                warmup_pipeline_max_batch_size=pipeline_max_batch_size,
                full_warmup=True,
            )
            print("Warmup completed.", flush=True)
            print(
                f"Cache implementation: "
                f"{self.model.generation_config.cache_implementation}",
                flush=True,
            )

    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Dict[str, Any]]:
        """Process decoded audio through the Whisper model.

        Args:
            inputs: Dictionary containing decoded_audio and lang_id_processed arrays

        Returns:
            List of dictionaries with transcription and metadata
        """
        input_batch_size = len(inputs["decoded_audio"])

        # Calculate total number of 30-second chunks that will be created
        chunk_length_samples = int(30.0 * WHISPER_SAMPLE_RATE)
        total_chunks = 0
        for audio in inputs["decoded_audio"]:
            num_chunks = (len(audio) + chunk_length_samples - 1) // chunk_length_samples
            total_chunks += num_chunks

        # No matter what to use: pipeline_batch_size/pipeline_max_batch_size
        # We compute it only for the metadata purposes
        pipeline_batch_size = min(total_chunks, pipeline_max_batch_size)

        start_time = time.time()
        output = self.pipeline.generate(
            inputs=inputs["decoded_audio"],
            lang_ids=[
                lang_id[0].decode("utf-8") for lang_id in inputs["lang_id_processed"]
            ],
            # Handle batch size to avoid possible GPU memory overflow and control response time
            batch_size=pipeline_batch_size,
            **self.generation_config,
        )
        generation_time = (time.time() - start_time) / input_batch_size

        outputs = [
            {
                "transcription": np.array([s.strip().encode("utf-8")], dtype="object"),
                "metadata": [
                    {
                        "generation_time": generation_time,
                        "batch_size": input_batch_size,
                        "pipeline_batch_size": pipeline_batch_size,
                        "batch_chunks": total_chunks,
                    }
                ],
            }
            for s in output
        ]
        return outputs


class BaseEnsembleModel(SeqEnsembleModel):
    models = [Preprocessor, Whisper]
    inputs = [
        FileSignature(
            (-1,),
            np.bytes_,
            "audio_bytes_tensor",
            allow_ragged_batch=False,
            external=True,
        ),
        TextSignature(
            (-1,), np.bytes_, "lang_id", allow_ragged_batch=False, external=True
        ),
    ]
    outputs = [
        TensorSignature((-1,), np.bytes_, "transcription", external=True),
        TextSignature(shape=(1,), dtype=np.bytes_, name="metadata", external=True),
    ]
    model_name = model_name
    model_config = ModelConfig(max_batch_size=max_batch_size)
