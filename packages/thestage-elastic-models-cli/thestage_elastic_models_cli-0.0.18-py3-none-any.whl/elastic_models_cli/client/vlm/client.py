import argparse
import ast
import json
import logging
import random
import time
from typing import Any, Dict, Optional

from qlip_serve.client import send_triton_request

from ...cli.base import BaseClientCommandModule
from ...cli.utils import (
    build_inference_url,
    extract_auth_header,
    resolve_and_load_metadata,
)

# Setup logger
logger = logging.getLogger(__name__)


class VLMClientModule(BaseClientCommandModule):
    @property
    def module_name(self) -> str:
        return "vlm"

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        super().register_command_args(parser, command_name)
        parser.add_argument(
            "--prompt",
            type=str,
            required=True,
            help="Input prompt for the VLM.",
        )
        parser.add_argument(
            "--image-url",
            type=str,
            required=False,
            help="Input image url for the VLM.",
            default=None,
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=-1,
            required=False,
            help="Seed for generation (if supported by model).",
        )

    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        if command_name == "vlm":
            # TODO: add 2nd inheritance for send_prompt +run_client adding here
            return run_vlm_client(args)
        else:
            raise ValueError(f"Unknown command: {command_name}")


# TODO: add support of receiving raw answer
# TODO: better failbacks?
def send_prompt(
    prompt: str,
    image: str,
    metadata: Dict[str, Any],
    url: str,
    seed: Optional[int] = None,
    authorization: Optional[str] = None,
    is_sagemaker: bool = False,
    # Add other LLM params as needed, e.g., max_tokens, temperature
) -> tuple[str, Optional[Dict[str, Any]]]:  # Return text and optional full dict
    # Adapt request_dict based on expected Triton input names for the LLM
    # This is a guess and needs to match the specific LLM model's config.pbtxt
    request_dict: Dict[str, Any] = {
        "prompt": [prompt],
        "image": [image],
        # Include other params if the model expects them
        # "max_tokens": [max_tokens],
        # "temperature": [temperature],
    }
    if seed is not None and seed != -1:
        request_dict["seed"] = [seed]

    formatted_auth = extract_auth_header(authorization) if authorization else None

    output_payloads = send_triton_request(
        request_dict=request_dict,
        metadata_dict=metadata,
        triton_url=url,
        is_sagemaker=is_sagemaker,
        authorization=formatted_auth,
    )

    expected_output_key = "output"
    if expected_output_key in output_payloads:
        response_text = "Error: Could not process LLM response."
        output_dict = None
        try:
            raw_bytes = output_payloads[expected_output_key].data[0]
            decoded_string = raw_bytes.decode("utf-8")

            # Now parse the decoded string
            try:
                # Parse the string representation of the dictionary
                parsed_data = ast.literal_eval(decoded_string)
                if isinstance(parsed_data, dict):
                    output_dict = parsed_data  # Store the full dict
                    # Extract the actual response text from the 'response' key if present
                    if "response" in output_dict:
                        response_text = output_dict["response"]
                    else:
                        logger.warning("Warning: Parsed dict lacks 'response' key.")
                        # Keep output_dict, use decoded string as fallback
                        response_text = decoded_string
                else:
                    logger.warning("Warning: Parsed output is not a dictionary.")
                    logger.warning(f"Parsed output type: {type(parsed_data)}")
                    response_text = decoded_string  # Fallback to decoded string
            except (SyntaxError, ValueError) as e_parse:
                logger.warning(
                    f"Warning: Could not parse decoded output string as dict: {e_parse}"
                )
                response_text = decoded_string  # Fallback to decoded string

        except (IndexError, AttributeError, UnicodeDecodeError) as e_decode:
            logger.error(f"Error accessing or decoding raw output data: {e_decode}")
            # response_text is already set to an error message
        except KeyError:
            logger.warning(
                f"Warning: Expected output key '{expected_output_key}' not found "
                f"in response."
            )
            logger.warning(f"Available outputs: {list(output_payloads.keys())}")
            # response_text is already set to an error message
    else:
        logger.warning(
            f"Warning: Expected output '{expected_output_key}' not found in response."
        )
        logger.warning(f"Available outputs: {list(output_payloads.keys())}")
        response_text = "Error: Could not parse LLM response."
        output_dict = None  # No dict if key not found

    # Potentially parse metadata if the LLM provides it similarly to diffusion
    # output_metadata = ast.literal_eval(output_payloads["metadata"].data[0].decode())

    return response_text, output_dict  # Return both


def run_vlm_client(args: argparse.Namespace):
    """Runs the LLM client logic with parsed arguments."""
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

    metadata = resolve_and_load_metadata(args)

    prompt = args_dict["prompt"]
    seed = (
        args_dict["seed"] if args_dict["seed"] != -1 else random.randint(0, 10000)
    )  # Random seed if not set

    image_url = args_dict["image_url"]
    if image_url is None:
        image = ""
    else:
        image = image_url

    inference_url = build_inference_url(args, metadata)
    try:
        start_time = time.time()
        response_text, output_dict = send_prompt(
            prompt=prompt,
            seed=seed,
            url=inference_url,
            authorization=args_dict["authorization"],
            metadata=metadata,
            image=image,
            # Pass other LLM params from args_dict if added
            # max_tokens=args_dict["max_tokens"],
            # temperature=args_dict["temperature"],
        )
        response_time = time.time() - start_time
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

                inference_url = build_inference_url(args, metadata)

                # Retry send_prompt
                logger.info("Retrying request with refreshed metadata...")
                start_time = time.time()
                response_text, output_dict = send_prompt(
                    prompt=prompt,
                    seed=seed,
                    url=inference_url,
                    authorization=args_dict["authorization"],
                    metadata=metadata,
                    image=image,
                    # Pass other LLM params from args_dict if added
                    # max_tokens=args_dict["max_tokens"],
                    # temperature=args_dict["temperature"],
                )
                response_time = time.time() - start_time
                logger.info("Retry request successful.")

            except Exception as retry_e:
                logger.error(f"Retry attempt failed: {retry_e}")
                raise retry_e  # Raise the error from the retry attempt
        else:
            # If it's a different ValueError, re-raise it
            logger.error(f"Request failed with unhandled error: {e}")
            raise e

    # Reverted to print for clean JSON output
    if output_dict and "response" in output_dict:
        # If we have a dictionary and it contains the 'response' key,
        # print the whole dictionary for easy parsing.
        print(json.dumps(output_dict))
    elif response_text:
        # Fallback if output_dict is not as expected but we have response_text
        try:
            # Attempt to format as a JSON string if it's simple text.
            print(json.dumps({"response": response_text}))
        except TypeError:  # If response_text is not serializable
            print(response_text)  # Print as is
    else:
        print(json.dumps({"error": "No response generated or error in processing."}))

    # Print other info to stderr or controlled by logger if needed for debugging
    if logger.isEnabledFor(logging.INFO):
        logger.info("--- Client Side Timing & Prompt Info ---")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Total client time: {response_time:.2f}s")
        logger.info("---------------------------------------")
