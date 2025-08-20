"""Locust file used by *elastic-models-client benchmark stt* command.

The implementation purposefully avoids the inference server's HTTP client that
Locust <HttpUser> offers because we already have a high-level helper (`send_prompt`)
that builds and sends the correct protobuf payload.  We therefore use a plain `User`
instead of `HttpUser` and manually fire the `request` event so that Locust's
statistics and reporters still work.
"""

from __future__ import annotations

import io
import json
import os
import random
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import numpy as np
from datasets import load_dataset
from locust import User, between, events, task
from pydub import AudioSegment
from scipy.stats import beta, uniform

from elastic_models_cli.client.stt.client import send_prompt

# -------------------------------------------------------------------------
# Environment configuration (populated by benchmark CLI)
# -------------------------------------------------------------------------

INFERENCE_URL: Optional[str] = os.environ.get("INFERENCE_URL")
ENDPOINT_PATH = urlparse(INFERENCE_URL).path if INFERENCE_URL else ""
METADATA_JSON: Optional[str] = os.environ.get("METADATA_JSON")
AUTHORIZATION: Optional[str] = os.environ.get("AUTHORIZATION")
JSONL_OUTPUT_PATH: Optional[str] = os.environ.get("JSONL_OUTPUT_PATH")

# STT-specific environment variables
HUGGINGFACE_ACCESS_TOKEN: Optional[str] = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")
DEBUG: bool = os.environ.get("DEBUG", "false").lower() in ["1", "true"]

# Optional wait time override so that the CLI can tune it.
MIN_WAIT: float = float(os.environ.get("LOCUST_MIN_WAIT", "1.0"))
MAX_WAIT: float = float(os.environ.get("LOCUST_MAX_WAIT", "2.0"))

# Legacy environment variables for backward compatibility
ENDPOINT_VERSION = os.environ.get("LOCUST_BENCHMARK__ENDPOINT_VERSION")
HOST = os.environ.get("LOCUST_BENCHMARK__HOST")
ENDPOINT_PATH_LEGACY = os.environ.get("LOCUST_BENCHMARK__ENDPOINT_PATH")
ENDPOINT_TYPE = os.environ.get("LOCUST_BENCHMARK__ENDPOINT_TYPE")
IS_SAGEMAKER = os.environ.get("LOCUST_BENCHMARK__IS_SAGEMAKER", "false").lower() in [
    "1",
    "true",
]
FOLDER_PATH = os.environ.get("LOCUST_BENCHMARK__FOLDER_PATH")

# Check if required environment variables are set
if INFERENCE_URL is None and HOST is None:
    raise RuntimeError(
        "Environment variable INFERENCE_URL or LOCUST_BENCHMARK__HOST must be set "
        "by the benchmark CLI."
    )

if METADATA_JSON is None:
    raise RuntimeError(
        "Environment variable METADATA_JSON must be set by the benchmark CLI."
    )

if HUGGINGFACE_ACCESS_TOKEN is None:
    raise RuntimeError("Environment variable HUGGINGFACE_ACCESS_TOKEN must be set.")

# Load metadata
with open(METADATA_JSON, "r", encoding="utf-8") as fh:
    METADATA: Dict[str, Any] = json.load(fh)

# Use legacy variables if new ones are not set
if INFERENCE_URL is None:
    inference_url = f"{HOST}/{ENDPOINT_PATH_LEGACY}"
    endpoint_path = urlparse(inference_url).path
else:
    inference_url = INFERENCE_URL
    endpoint_path = ENDPOINT_PATH

if JSONL_OUTPUT_PATH is None and FOLDER_PATH is not None:
    jsonl_output_path = f"{FOLDER_PATH}_output.jsonl"
else:
    jsonl_output_path = JSONL_OUTPUT_PATH


# -------------------------------------------------------------------------
# Audio processing utilities
# -------------------------------------------------------------------------


def generate_outlier(low, high, prob):
    """Generate an outlier value between low and high with a given probability."""
    if uniform.rvs(size=1) < prob:
        return uniform.rvs(loc=low, scale=high - low, size=1)[0]
    else:
        return 0


def fit_beta_distribution(x):
    """Fit a beta distribution to the input data x."""
    a1, b1, loc1, scale1 = beta.fit(x)
    return a1, b1, loc1, scale1


def generate_sample(beta_params, outlier_low, outlier_high, outlier_prob):
    """Generate a sample from a beta distribution with the given parameters, with occasional outliers."""
    a1, b1, loc1, scale1 = beta_params
    sample = beta.rvs(a1, b1, loc1, scale1, size=1)[0]
    outlier = generate_outlier(outlier_low, outlier_high, outlier_prob)
    result = int(max([sample, outlier]))
    return result


# TODO: add ability to use users histogram file
# with open("histogram.json", "r") as f:
#     histogram = json.load(f)
#
# histogram = dict(map(lambda x: (int(x[0]), x[1]), histogram.items()))
#
# # Move zero-length to the nearest
# histogram[1] += histogram[0]
# del histogram[0]
#
# x = []
# for n, c in histogram.items():
#     if n != 0:
#         x.extend([n] * c)
#
# beta_params = fit_beta_distribution(x)

# Example of realtime distribution
beta_params = (
    0.928644967525649,
    336.23244742481705,
    0.9999999999999999,
    1560.1215519714838,
)


class CommonVoiceSampler:
    """Dataset sampler for Common Voice data."""

    def __init__(self):
        self.datasets = {}
        self.selected_languages = ["de", "en", "es", "it", "ru", "pl"]
        self._lock = threading.Lock()  # Add thread safety

    def get_sample(self):
        """Get a sample from the Common Voice dataset."""
        with self._lock:  # Protect access to datasets
            lang_id = random.choice(self.selected_languages)
            if lang_id not in self.datasets:
                self.datasets[lang_id] = iter(
                    load_dataset(
                        "mozilla-foundation/common_voice_16_1",
                        lang_id,
                        split="validation",
                        streaming=True,
                        token=HUGGINGFACE_ACCESS_TOKEN,
                        trust_remote_code=True,
                    )
                )

            return next(self.datasets[lang_id])


# Global sampler instance
sampler = CommonVoiceSampler()


# -------------------------------------------------------------------------
# Locust user
# -------------------------------------------------------------------------


class STTUser(User):
    wait_time = between(MIN_WAIT, MAX_WAIT)

    @task
    def infer(self) -> None:  # noqa: D401
        """Send a single audio sample to the inference server STT endpoint."""
        global sampler

        start_time = time.perf_counter()
        try:
            # Get audio sample from dataset
            sample_data = sampler.get_sample()
            rate = sample_data["audio"]["sampling_rate"]
            data = sample_data["audio"]["array"]
            lang_id = sample_data["locale"]
            original_sentence = sample_data["sentence"]

            # Convert the audio data to 16-bit sample width
            data_16bit = (data * 32767).astype(np.int16)

            # Create an AudioSegment from the 16-bit audio data
            audio_segment = AudioSegment(
                data_16bit.tobytes(),
                frame_rate=rate,
                sample_width=2,  # 16-bit
                channels=1,
            )

            # Set the desired sampling rate
            target_sampling_rate = 16000

            # Resample the audio to the desired sampling rate
            resampled_audio = audio_segment.set_frame_rate(target_sampling_rate)

            # TODO: CHANGE TO FALSE IF YOU NEED SPEEDBENCHMARK, RETURN TRUE FOR QUALBENCH
            # TODO: ADD ARGUMENT FOR THIS
            ORIGINAL_LENGTH = True
            if not ORIGINAL_LENGTH:
                # Find the probability of an outlier
                outlier_low = beta.ppf(0.999, *beta_params)  # (~ 27s)
                outlier_high = beta.ppf(0.9999999999, *beta_params)  # (~ 92s)
                # Create a dummy x for outlier probability calculation
                x = (
                    np.random.beta(*beta_params[:2], size=1000) * beta_params[3]
                    + beta_params[2]
                )
                outlier_prob = sum(np.array(x) > outlier_low) / len(x)  # (~ 0.1)

                cut_duration = generate_sample(
                    beta_params,
                    outlier_low=outlier_low,
                    outlier_high=outlier_high,
                    outlier_prob=outlier_prob,
                )

                # Calculate the target duration in milliseconds
                target_duration_ms = cut_duration * 1000

                # Adjust the duration of the audio segment
                if len(resampled_audio) < target_duration_ms:
                    # Repeat the audio segment to reach the target duration
                    adjusted_audio = resampled_audio * (
                        target_duration_ms // len(resampled_audio) + 1
                    )
                    adjusted_audio = adjusted_audio[:target_duration_ms]
                else:
                    # Trim the audio segment to the target duration
                    adjusted_audio = resampled_audio[:target_duration_ms]
            else:
                cut_duration = (
                    len(sample_data["audio"]["array"])
                    / sample_data["audio"]["sampling_rate"]
                )
                adjusted_audio = resampled_audio

            # Convert the adjusted audio segment to WAV format
            bytes_wav = io.BytesIO()
            adjusted_audio.export(bytes_wav, format="wav")
            bytes_wav.seek(0)
            wav_data = bytes_wav.read()

            # Send the request using the client
            transcription, response_metadata = send_prompt(
                sample=wav_data,
                lang_id=lang_id,
                url=inference_url,
                authorization=AUTHORIZATION,
                metadata=METADATA,
                is_sagemaker=IS_SAGEMAKER,
            )

            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_length = len(transcription.encode("utf-8"))

            events.request.fire(
                request_type="inference",
                name=endpoint_path,
                response_time=response_time_ms,
                response_length=response_length,
                exception=None,
            )

            # Log debug information and save to JSONL if enabled
            if DEBUG or jsonl_output_path:
                real_duration = (
                    len(sample_data["audio"]["array"])
                    / sample_data["audio"]["sampling_rate"]
                )

                if DEBUG:
                    print(f"Select {cut_duration}s from {real_duration}s")
                    print(f"Original:  {original_sentence}", flush=True)
                    print(f"Predicted: {transcription}", flush=True)

                if jsonl_output_path:
                    utc_datetime = datetime.utcnow().isoformat() + "Z"
                    entry = {
                        "utc_datetime": utc_datetime,
                        "real_duration": real_duration,
                        "cut_duration": cut_duration,
                        "original_sentence": original_sentence,
                        "lang_id": lang_id,
                        "predicted_sentence": transcription,
                        "url": inference_url,
                        **response_metadata,
                    }
                    with open(jsonl_output_path, "a") as jsonl_file:
                        jsonl_file.write(json.dumps(entry) + "\n")

        except StopIteration:
            # Reset sampler if dataset is exhausted
            sampler = CommonVoiceSampler()
            # Retry the task
            self.infer()

        except Exception as exc:  # noqa: BLE001
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            events.request.fire(
                request_type="inference",
                name=endpoint_path,
                response_time=response_time_ms,
                response_length=0,
                exception=exc,
            )
            raise
