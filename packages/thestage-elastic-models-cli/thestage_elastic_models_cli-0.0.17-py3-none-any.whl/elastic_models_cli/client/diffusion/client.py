import argparse
import ast
import hashlib
import io
import logging
import os
import random
import time
from typing import Any, Dict, List, Union

from PIL import Image

from qlip_serve.client import send_triton_request

from ...cli.base import BaseClientCommandModule
from ...cli.utils import (
    build_inference_url,
    extract_auth_header,
    resolve_and_load_metadata,
)

logger = logging.getLogger(__name__)


class DiffusionClientModule(BaseClientCommandModule):
    @property
    def module_name(self) -> str:
        return "diffusion"

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        super().register_command_args(parser, command_name)
        parser.add_argument("--pos-prompt", type=str, required=True)
        parser.add_argument("--seed", type=int, default=-1, required=False)
        parser.add_argument(
            "--aspect-ratio",
            type=str,
            default=None,
            required=False,
            help="Aspect ratio for FLUX models (e.g., '16:9', '1:1')",
        )
        parser.add_argument(
            "--guidance-scale",
            type=float,
            default=None,
            required=False,
            help="Guidance scale for generation",
        )
        parser.add_argument(
            "--num-inference-steps",
            type=int,
            default=None,
            required=False,
            help="Number of inference steps",
        )

    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        if command_name == "diffusion":
            return run_diffusion_client(args)
        else:
            raise ValueError(f"Unknown command: {command_name}")


def create_request_dict(args: Dict[str, Any]) -> Dict[str, List[Union[str, int]]]:
    TEST_PROMPTS = [
        (
            "biker with backpack on his back riding a motorcycle, Style by Ade "
            "Santora, Oilpunk, Cover photo, craig mullins style, on the cover of "
            "a magazine, Outdoor Magazine, inspired by Alex Petruk APe, image of "
            "a male biker, Cover of an award-winning magazine, the man has a "
            "backpack, photo for magazine, with a backpack, magazine cover"
        ),
        (
            "Simplified technical drawing, Leonardo da Vinci, Mechanical Dinosaur "
            "Skeleton, Minimalistic annotations, Hand-drawn illustrations, Basic "
            "design and engineering, Wonder and curiosity"
        ),
        (
            "overwhelmingly beautiful eagle framed with vector flowers, long shiny "
            "wavy flowing hair, polished, ultra detailed vector floral "
            "illustration mixed with hyper realism, muted pastel colors, vector "
            "floral details in background, muted colors, hyper detailed ultra "
            "intricate overwhelming realism in detailed complex scene with magical "
            "fantasy atmosphere, no signature, no watermark"
        ),
        (
            "futuristic lighthouse, flash light, hyper realistic, epic "
            "composition, cinematic, landscape vista photography, landscape "
            "veduta photo & tdraw, detailed landscape painting rendered in "
            "enscape, miyazaki, 4k detailed post processing, unreal engineered"
        ),
        (
            "underwater world, plants, flowers, shells, creatures, high detail, "
            "sharp focus, 4k"
        ),
        "pikachu eating spagetti, Antonio J. Manzanedo",
    ]

    if args["pos_prompt"]:
        pos_prompt = args["pos_prompt"]
    else:
        pos_prompt = random.choice(TEST_PROMPTS)

    request = {
        "pos_prompt": [pos_prompt],
        "seed": [args["seed"] if args["seed"] != -1 else random.randint(0, 1000)],
    }

    # Add optional parameters if provided
    if args.get("aspect_ratio"):
        request["aspect_ratio"] = [args["aspect_ratio"]]
    else:
        request["aspect_ratio"] = [""]

    if args.get("guidance_scale") is not None:
        request["guidance_scale"] = [args["guidance_scale"]]
    else:
        request["guidance_scale"] = [0.0]

    if args.get("num_inference_steps") is not None:
        request["num_inference_steps"] = [args["num_inference_steps"]]
    else:
        request["num_inference_steps"] = [0]

    return request


def send_prompt(
    pos_prompt: str,
    seed: int,
    url: str,
    authorization: str,
    metadata: Dict[str, Any],
    is_sagemaker: bool = False,
    aspect_ratio: str = "",
    guidance_scale: float = 0.0,
    num_inference_steps: int = 0,
) -> tuple[Image.Image, dict[str, Any]]:
    request_dict = {
        "pos_prompt": [pos_prompt],
        "seed": [seed],
        "aspect_ratio": [aspect_ratio],
        "guidance_scale": [guidance_scale],
        "num_inference_steps": [num_inference_steps],
    }

    formatted_auth = extract_auth_header(authorization)

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

    img_array = output_payloads["image"].postprocess(output_payloads["image"].data)
    img = Image.fromarray(img_array)
    output_metadata = ast.literal_eval(output_payloads["metadata"].data[0].decode())

    return (img, output_metadata)


def run_diffusion_client(args: argparse.Namespace):
    """Runs the diffusion client logic with parsed arguments."""
    args_dict = vars(args)

    # Configure logging - Example: Use basicConfig if not configured by root
    # This assumes no explicit --log-level arg for this client yet.
    # If root logger has no handlers, add basic config.
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

    metadata = resolve_and_load_metadata(args, force_download=False)

    request_dict = create_request_dict(args_dict)
    suffix_dir = metadata["model"]["name"]
    # print(f"Signature: {json.dumps(metadata, indent=2)}")

    output_base_dir = "output"
    output_dir = os.path.join(output_base_dir, suffix_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Extract prompt and seed with correct types
    pos_prompt: str = str(request_dict["pos_prompt"][0])
    seed: int = int(request_dict["seed"][0])
    aspect_ratio: str = (
        str(request_dict["aspect_ratio"][0]) if request_dict.get("aspect_ratio") else ""
    )
    guidance_scale: float = (
        float(request_dict["guidance_scale"][0])
        if request_dict.get("guidance_scale")
        else 0.0
    )
    num_inference_steps: int = (
        int(request_dict["num_inference_steps"][0])
        if request_dict.get("num_inference_steps")
        else 0
    )

    try:
        url = build_inference_url(args, metadata)
        start_time = time.time()
        img, output_metadata = send_prompt(
            pos_prompt=pos_prompt,
            seed=seed,
            url=url,
            authorization=args_dict["authorization"],
            metadata=metadata,
            aspect_ratio=aspect_ratio,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        )
        response_time = time.time() - start_time
        print(output_metadata)

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

                # Update suffix_dir and ensure directory exists
                # in case model name changed
                new_suffix_dir = metadata["model"]["name"]
                if new_suffix_dir != suffix_dir:
                    logger.info(
                        f"Model name changed from '{suffix_dir}' to '{new_suffix_dir}'. "
                        "Updating output path."
                    )
                    suffix_dir = new_suffix_dir
                    output_dir = os.path.join(output_base_dir, suffix_dir)
                    os.makedirs(output_dir, exist_ok=True)

                # Retry send_prompt
                logger.info("Retrying request with refreshed metadata...")
                start_time = time.time()
                url = build_inference_url(args, metadata)
                img, output_metadata = send_prompt(
                    pos_prompt=pos_prompt,
                    seed=seed,
                    url=url,
                    authorization=args_dict["authorization"],
                    metadata=metadata,
                    aspect_ratio=aspect_ratio,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                )
                response_time = time.time() - start_time
                print(output_metadata)
                logger.info("Retry request successful.")

            except Exception as retry_e:
                logger.error(f"Retry attempt failed: {retry_e}")
                raise retry_e  # Raise the error from the retry attempt
        else:
            # If it's a different ValueError, re-raise it
            logger.error(f"Request failed with unhandled error: {e}")
            raise e

    # Convert PIL Image to bytes for size calculation
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="webp")  # Save as webp
    response_length = len(img_byte_arr.getvalue())

    # Hash requires bytes, ensure prompt is encoded
    image_meta_hash = hashlib.sha256(pos_prompt.encode("utf-8")).hexdigest()

    image_path = os.path.join(output_dir, f"{int(time.time())}_{image_meta_hash}.webp")
    img.save(
        image_path,
        format="webp",
    )

    # Build generation details string
    gen_details = []
    if output_metadata.get("aspect_ratio"):
        gen_details.append(f"Aspect: {output_metadata['aspect_ratio']}")
    width = output_metadata.get("width", "N/A")
    height = output_metadata.get("height", "N/A")
    gen_details.append(f"{width}x{height}")
    gen_details.append(f"Steps: {output_metadata.get('num_inference_steps', 'N/A')}")
    gen_details.append(f"Guidance: {output_metadata.get('guidance_scale', 'N/A')}")
    print(
        f"Image generated. Prompt: {pos_prompt}, Size: {response_length} bytes, "
        f"Gen time: {output_metadata['generation_time']:.2f}s, "
        f"Total time: {response_time:.2f}s"
    )
    print(f"Generation details: {', '.join(gen_details)}")
    print(f"Image saved to: {image_path}")
