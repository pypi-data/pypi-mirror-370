"""Locust file used by *elastic-models-client benchmark llm* command.

The implementation purposefully avoids the inference server's HTTP client that Locust <HttpUser>
offers because we already have a high-level helper (`send_llm_prompt`) that builds
and sends the correct protobuf payload.  We therefore use a plain `User` instead
of `HttpUser` and manually fire the `request` event so that Locust's statistics
and reporters still work.
"""

from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from locust import User, between, events, task

from elastic_models_cli.client.llm.client import send_prompt

# -------------------------------------------------------------------------
# Environment configuration (populated by benchmark CLI)
# -------------------------------------------------------------------------


INFERENCE_URL: str = os.environ.get("INFERENCE_URL")
ENDPOINT_PATH = urlparse(INFERENCE_URL).path
METADATA_JSON: Optional[str] = os.environ.get("METADATA_JSON")
# TODO: add ability to parametrize prompt len/distribution
# TODO : add ability to use datasets
PROMPT: str = os.environ.get("PROMPT", "What is the meaning of life?")
AUTHORIZATION: Optional[str] = os.environ.get("AUTHORIZATION")
JSONL_OUTPUT_PATH: Optional[str] = os.environ.get("JSONL_OUTPUT_PATH")

# Optional wait time override so that the CLI can tune it.
MIN_WAIT: float = float(os.environ.get("LOCUST_MIN_WAIT", "0.5"))
MAX_WAIT: float = float(os.environ.get("LOCUST_MAX_WAIT", "2.0"))

if METADATA_JSON is None:
    raise RuntimeError(
        "Environment variable METADATA_JSON must be set by the benchmark CLI."
    )


with open(METADATA_JSON, "r", encoding="utf-8") as fh:
    METADATA: Dict[str, Any] = json.load(fh)


# -------------------------------------------------------------------------
# Locust user
# -------------------------------------------------------------------------


class LLMUser(User):
    wait_time = between(MIN_WAIT, MAX_WAIT)

    @task
    def infer(self) -> None:  # noqa: D401
        """Send a single prompt to the inference server LLM endpoint."""

        seed = random.randint(0, 10000)

        start_time = time.perf_counter()
        try:
            response_text, response_data = send_prompt(
                prompt=PROMPT,
                seed=seed,
                metadata=METADATA,
                url=INFERENCE_URL,
                authorization=AUTHORIZATION,
                # TODO: parametrize
                is_sagemaker=False,
            )

            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_length = len(response_text.encode("utf-8"))

            events.request.fire(
                request_type="inference",
                name=ENDPOINT_PATH,
                response_time=response_time_ms,
                response_length=response_length,
                exception=None,
            )

            if JSONL_OUTPUT_PATH:
                utc_datetime = datetime.utcnow().isoformat() + "Z"
                entry = {
                    "utc_datetime": utc_datetime,
                    "prompt": PROMPT,
                    "url": INFERENCE_URL,
                    **response_data,
                }
                with open(JSONL_OUTPUT_PATH, "a") as jsonl_file:
                    jsonl_file.write(json.dumps(entry) + "\n")

        except Exception as exc:  # noqa: BLE001
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            events.request.fire(
                request_type="inference",
                name=ENDPOINT_PATH,
                response_time=response_time_ms,
                response_length=0,
                exception=exc,
            )
            raise
