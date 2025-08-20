"""
Benchmark command module for elastic-models-client CLI.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List

import requests

from .base import BaseClientCommandModule
from .registry import registry
from .utils import (
    build_inference_ready_url,
    build_inference_url,
    extract_auth_header,
    resolve_and_load_metadata,
)


class BenchmarkModule(BaseClientCommandModule):
    """Command module for running benchmarks."""

    @property
    def module_name(self) -> str:
        return "benchmark"

    @property
    def module_help(self) -> str:
        return "Run benchmarks using Locust"

    def _find_benchmark_types(self) -> List[str]:
        """Scan for subdirectories with a locustfile.py to determine benchmark types."""
        serve_dir = Path(__file__).parent.parent / "client"
        benchmark_types = []
        for entry in serve_dir.iterdir():
            if entry.is_dir() and (entry / "locustfile.py").exists():
                benchmark_types.append(entry.name)
        return benchmark_types

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        """Register benchmark-specific arguments."""
        super().register_command_args(parser, command_name)

        benchmark_types = self._find_benchmark_types()
        if not benchmark_types:
            # Handle case where no benchmarks are found
            parser.description = "No benchmark types found."
            return
        parser.add_argument(
            "benchmark_type",
            choices=benchmark_types,
            help="Type of benchmark to run (e.g. 'llm').",
        )
        # Concurrency / number of requests
        parser.add_argument(
            "--concurrency",
            "-c",
            type=str,
            default="1",
            help=(
                "Concurrent Locust users. Can be a single integer or a "
                "comma-separated list of integers (e.g., '1,2,4'). (default: 1)"
            ),
        )
        parser.add_argument(
            "--num-requests",
            "-n",
            type=int,
            default=1,
            help="Total number of requests (default: 1)",
        )

        # Output
        parser.add_argument(
            "--output-prefix",
            type=str,
            default="report",
            help="Prefix for Locust CSV / HTML reports (default: 'report')",
        )

        parser.add_argument(
            "--output-dir",
            type=str,
            help=(
                "Directory to save benchmark reports. If not specified, files are saved"
                " in the current directory."
            ),
        )

        # # Benchmark-specific prompt
        # parser.add_argument(
        #     "--prompt",
        #     type=str,
        #     help="Prompt to benchmark with. If omitted a default prompt is used.",
        # )

        # Locust wait time parameters
        parser.add_argument(
            "--min-wait",
            type=float,
            default=0.5,
            help="Minimum wait time between tasks for a user in seconds.",
        )
        parser.add_argument(
            "--max-wait",
            type=float,
            default=2.0,
            help="Maximum wait time between tasks for a user in seconds.",
        )
        parser.add_argument(
            "--log-jsonl",
            action="store_true",
            help="Enable logging of each request/response to a JSONL file.",
        )

    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        """Execute benchmark command."""
        # benchmark_type is in args from register_command_args
        original_concurrency_str = args.concurrency
        try:
            concurrencies = [
                int(c.strip()) for c in original_concurrency_str.split(",")
            ]
        except ValueError as e:
            raise ValueError(
                "Invalid format for --concurrency. Please use a single integer or a "
                "comma-separated list of integers."
            ) from e

        for i, concurrency_val in enumerate(concurrencies):
            args.concurrency = concurrency_val
            if len(concurrencies) > 1:
                print(
                    f"--- Running benchmark {i + 1}/{len(concurrencies)} "
                    f"with concurrency={concurrency_val} ---"
                )
            self._run_locust_benchmark(args)
            if len(concurrencies) > 1 and i < len(concurrencies) - 1:
                print("\n")

    def _run_locust_benchmark(self, args: argparse.Namespace) -> None:
        """Constructs and executes the Locust benchmark command."""
        import subprocess
        import sys
        import tempfile

        args_dict = vars(args)
        benchmark_type = args.benchmark_type

        # --- Load metadata ---
        # Only force download if no explicit metadata file is provided
        force_download = not bool(args_dict.get("metadata_json"))
        metadata = resolve_and_load_metadata(args, force_download=force_download)
        model_name = metadata["model"]["name"]

        if args_dict.get("metadata_json"):
            metadata_json_path = args_dict["metadata_json"]
        else:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix="_metadata.json", mode="w", encoding="utf-8"
            ) as tmp:
                json.dump(metadata, tmp)
                metadata_json_path = tmp.name

        # --- Construct server URLs ---
        ready_url = build_inference_ready_url(args, metadata)
        infer_url = build_inference_url(args, metadata)

        # --- Validate server readiness ---
        try:
            # TODO: temporal fix for using server timeout only
            # timeout = args_dict.get("timeout", 5)
            headers = {}
            authorization = args_dict.get("authorization")
            if authorization:
                headers["Authorization"] = extract_auth_header(authorization)

            # TODO: temporal disabling ready url due to Nginx Rules for Salad
            # resp = requests.get(ready_url, timeout=timeout, headers=headers)
            # resp.raise_for_status()

        except requests.exceptions.RequestException as exc:
            model_name = metadata.get("model", {}).get("name", "unknown")
            raise RuntimeError(
                f"Inference model '{model_name}' not ready or metadata is wrong. "
                f"Could not reach {ready_url}: {exc}"
            ) from exc

        # --- Handle output paths and check for existing files ---
        output_prefix = (
            f"{args.output_prefix}_{str(args.concurrency)}_{str(args.num_requests)}"
        )
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path_prefix = output_dir / output_prefix
        else:
            output_path_prefix = Path(output_prefix)

        # Check for existing files
        potential_files = [
            f"{output_path_prefix}_stats.csv",
            f"{output_path_prefix}_stats_history.csv",
            f"{output_path_prefix}_failures.csv",
            f"{output_path_prefix}.html",
        ]
        existing_files = [f for f in potential_files if Path(f).exists()]

        if existing_files:
            print("Warning: The following files already exist and will be overwritten:")
            for f in existing_files:
                print(f" - {f}")

        # --- Save benchmark parameters ---
        params_path = f"{output_path_prefix}_params.json"
        with open(params_path, "w", encoding="utf-8") as f:
            params_to_save = vars(args).copy()
            # The 'func' key from argparse is not JSON serializable
            params_to_save.pop("func", None)
            params_to_save["model_name"] = model_name
            params_to_save["utc_datetime"] = datetime.utcnow().isoformat() + "Z"
            json.dump(params_to_save, f, indent=4, default=str)
        print(f"Benchmark parameters saved to {params_path}")

        # --- Prepare Locust environment ---
        env = os.environ.copy()
        env["INFERENCE_URL"] = infer_url
        env["METADATA_JSON"] = metadata_json_path
        # TODO: add ability to extend paramset with benchmark classes (existed client class?)
        # if args_dict.get("prompt"):
        #     env["PROMPT"] = args_dict["prompt"]
        # if args_dict.get("pos-prompt"):
        #     env["POS_PROMPT"] = args_dict["pos-prompt"]
        if authorization:
            env["AUTHORIZATION"] = authorization
        env["LOCUST_MIN_WAIT"] = str(args.min_wait)
        env["LOCUST_MAX_WAIT"] = str(args.max_wait)
        if args.log_jsonl:
            jsonl_output_path = f"{output_path_prefix}_output.jsonl"
            env["JSONL_OUTPUT_PATH"] = str(jsonl_output_path)

        # --- Build and run Locust command ---
        locustfile_path = self._get_locustfile_path(benchmark_type)
        locust_cmd = [
            sys.executable,
            "-m",
            "locust",
            "--headless",
            "--users",
            str(args.concurrency),
            "--iterations",
            str(args.num_requests),
            "--csv-full-history",
            "--csv",
            str(output_path_prefix),
            "--html",
            f"{output_path_prefix}.html",
            "--locustfile",
            locustfile_path,
        ]

        print("Running Locust with command:", " ".join(locust_cmd))
        # TODO: temporal fix to force locust continue the work
        subprocess.run(locust_cmd, env=env)

    def _get_locustfile_path(self, benchmark_type: str) -> str:
        """Return the absolute path to the packaged locustfile for a given type."""
        from pathlib import Path

        locust_path = (
            Path(__file__).parent.parent / "client" / benchmark_type / "locustfile.py"
        )
        if not locust_path.exists():
            raise FileNotFoundError(
                f"locustfile.py not found for benchmark type '{benchmark_type}' at "
                f"{locust_path}"
            )
        return str(locust_path)


# Register this module
registry.register(BenchmarkModule)
