import argparse
import ast
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple, Union

from qlip_serve.client import send_triton_request

from ...cli.base import BaseClientCommandModule
from ...cli.registry import registry
from ...cli.utils import (
    build_inference_url,
    extract_auth_header,
    resolve_and_load_metadata,
)

# Setup logger
logger = logging.getLogger(__name__)


class STTClientModule(BaseClientCommandModule):
    @property
    def module_name(self) -> str:
        return "stt"

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        super().register_command_args(parser, command_name)
        parser.add_argument(
            "--sample",
            type=str,
            required=True,
            help="Path to audio file or audio bytes for STT processing",
        )
        parser.add_argument(
            "--lang-id",
            dest="lang_id",
            type=str,
            required=True,
            help="Language ID for speech recognition",
        )

    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        if command_name == "stt":
            return run_stt_client(args)
        else:
            raise ValueError(f"Unknown command: {command_name}")


# Register this module
registry.register(STTClientModule)


def send_prompt(
    sample: Union[bytes, str],
    lang_id: str,
    url: str,
    authorization: Optional[str],
    metadata: Dict[str, Any],
    is_sagemaker: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """Send STT request to Triton server and return transcription and metadata."""

    request_dict = {
        "audio_bytes_tensor": sample,
        "lang_id": [lang_id],
    }

    formatted_auth = extract_auth_header(authorization) if authorization else None

    try:
        output_payloads = send_triton_request(
            request_dict=request_dict,
            metadata_dict=metadata,
            triton_url=url,
            is_sagemaker=is_sagemaker,
            authorization=formatted_auth,
        )
    except ValueError as e:
        raise e

    # Extract transcription
    transcription = output_payloads["transcription"].data[0].decode()

    # Parse metadata, handling string representation of dict with single quotes.
    # Standard JSON decoders (json.loads) require double quotes.
    # ast.literal_eval safely parses such strings.
    output_metadata = ast.literal_eval(output_payloads["metadata"].data[0].decode())

    return transcription, output_metadata


def run_stt_client(args: argparse.Namespace):
    """Runs the STT client logic with parsed arguments."""
    args_dict = vars(args)

    # Configure logging
    log_level_str = args_dict.get("log_level", "NONE").upper()
    if log_level_str == "NONE":
        logging.getLogger().addHandler(logging.NullHandler())
    else:
        numeric_level = getattr(logging, log_level_str, None)
        if not isinstance(numeric_level, int):
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            )
            logger.warning(f"Invalid log level '{log_level_str}'. Defaulting to INFO.")
        else:
            logging.basicConfig(
                level=numeric_level,
                format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            )

    metadata = resolve_and_load_metadata(args, force_download=False)

    sample = args_dict["sample"]
    lang_id = args_dict["lang_id"]

    try:
        inference_url = build_inference_url(args, metadata)
        start_time = time.time()
        transcription, output_metadata = send_prompt(
            sample=sample,
            lang_id=lang_id,
            url=inference_url,
            authorization=args_dict["authorization"],
            metadata=metadata,
        )
        response_time = time.time() - start_time

        # Print results
        print(
            json.dumps(
                {"transcription": transcription, "metadata": output_metadata}, indent=2
            )
        )

    except ValueError as e:
        # Check if it's the specific 404 error we want to retry
        error_str = str(e)
        if "404" in error_str and "unknown model" in error_str:
            logger.warning(
                f"Initial request failed with unknown model ({error_str}). "
                "Attempting metadata refresh and retry..."
            )
            try:
                # Force metadata refresh
                metadata = resolve_and_load_metadata(args, force_download=True)
                logger.info("Metadata refreshed successfully.")

                # Retry send_prompt
                logger.info("Retrying request with refreshed metadata...")
                start_time = time.time()
                inference_url = build_inference_url(args, metadata)
                transcription, output_metadata = send_prompt(
                    sample=sample,
                    lang_id=lang_id,
                    url=inference_url,
                    authorization=args_dict["authorization"],
                    metadata=metadata,
                )
                response_time = time.time() - start_time
                logger.info("Retry request successful.")

                # Print results
                print(
                    json.dumps(
                        {"transcription": transcription, "metadata": output_metadata},
                        indent=2,
                    )
                )

            except Exception as retry_e:
                logger.error(f"Retry attempt failed: {retry_e}")
                raise retry_e  # Raise the error from the retry attempt
        else:
            # If it's a different ValueError, re-raise it
            logger.error(f"Request failed with unhandled error: {e}")
            raise e

    # Print timing info to stderr if logging is enabled
    if logger.isEnabledFor(logging.INFO):
        logger.info("--- STT Client Timing Info ---")
        logger.info(f"Sample: {sample}")
        logger.info(f"Language ID: {lang_id}")
        generation_time = output_metadata.get("generation_time", "N/A")
        logger.info(f"Server Generation time: {generation_time:.2f}s")
        logger.info(f"Total client time: {response_time:.2f}s")
        logger.info("------------------------------")


if __name__ == "__main__":
    run_stt_client(argparse.ArgumentParser().parse_args())
