"""
Utilities for elastic-models-client CLI client operations.
"""

import argparse
import ipaddress
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

# Setup logger
logger = logging.getLogger(__name__)

# Default cache file
DEFAULT_METADATA_PATH = "metadata.json"
DEFAULT_METADATA_PORT = 8003
DEFAULT_TRITON_PORT = 8000
DEFAULT_TIMEOUT = 10
HTTP_PROTOCOL = "http"


# Simple exceptions - no complex hierarchy needed
class MetadataError(Exception):
    """Base exception for metadata issues."""

    pass


class MetadataNotFoundError(MetadataError):
    """Metadata cannot be found from any source."""

    pass


@dataclass
class MetadataConfig:
    """Configuration for resolving model metadata."""

    metadata_url: Optional[str] = None
    metadata_file: Optional[str] = None
    metadata_host: Optional[str] = None
    metadata_port: int = DEFAULT_METADATA_PORT
    host: str = "localhost"
    protocol: str = HTTP_PROTOCOL
    cache_enabled: bool = True
    timeout: int = DEFAULT_TIMEOUT

    @classmethod
    def from_args(cls, args) -> "MetadataConfig":
        """Create a MetadataConfig instance from argparse.Namespace."""
        return cls(
            metadata_url=getattr(args, "metadata_url", None),
            metadata_file=getattr(args, "metadata_json", None),
            metadata_host=getattr(args, "metadata_host", None),
            metadata_port=getattr(args, "metadata_port", DEFAULT_METADATA_PORT),
            host=getattr(args, "host", "localhost"),
            protocol=getattr(args, "protocol", HTTP_PROTOCOL),
            timeout=getattr(args, "timeout", DEFAULT_TIMEOUT),
        )


class SimpleMetadataResolver:
    """Simple, practical metadata resolver without unnecessary complexity."""

    def __init__(self, config: MetadataConfig):
        self.config = config

    def resolve(self, force_download: bool = False) -> Dict[str, Any]:
        """
        Resolve metadata using simple priority order:
        1. Force download (if requested)
        2. Explicit file (--metadata-json)
        3. Explicit URL (--metadata-url)
        4. Cache then default URL
        """
        logger.debug("Starting metadata resolution")

        if force_download:
            return self._force_download()

        # Try explicit file first (takes precedence over URL)
        if self.config.metadata_file:
            logger.info(f"Using explicit file: {self.config.metadata_file}")
            return self._load_from_file(self.config.metadata_file)

        # Try explicit URL second
        if self.config.metadata_url:
            logger.info(f"Using explicit URL: {self.config.metadata_url}")
            return self._download_and_cache(self.config.metadata_url)

        # Try cache first, then default URL
        if self.config.cache_enabled:
            try:
                logger.debug(f"Trying cache: {DEFAULT_METADATA_PATH}")
                return self._load_from_file(DEFAULT_METADATA_PATH)
            except (MetadataNotFoundError, MetadataError):
                logger.debug("Cache miss or invalid, trying default URL")

        # Fall back to default URL
        default_url = self._build_default_url()
        logger.info(f"Using default URL: {default_url}")
        return self._download_and_cache(default_url)

    def _force_download(self) -> Dict[str, Any]:
        """Force download from default URL, ignoring cache and explicit URL."""
        default_url = self._build_default_url()
        logger.info(f"Force downloading from: {default_url}")
        return self._download_and_cache(default_url)

    def _build_default_url(self) -> str:
        """Build default metadata server URL."""
        host = self.config.metadata_host or self.config.host or "localhost"
        try:
            ipaddress.IPv6Address(host)
            host = f"[{host}]"
        except ValueError:
            pass  # Not a bare IPv6 address

        return (
            f"{self.config.protocol}://{host}:{self.config.metadata_port}/api/metadata"
        )

    def _download_and_cache(self, url: str) -> Dict[str, Any]:
        """Download metadata from URL and optionally cache it."""
        try:
            logger.debug(f"Downloading metadata from: {url}")
            response = requests.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            metadata = response.json()

            # Cache if enabled
            if self.config.cache_enabled:
                try:
                    with open(DEFAULT_METADATA_PATH, "w") as f:
                        json.dump(metadata, f, indent=2)
                    logger.debug(f"Cached metadata to: {DEFAULT_METADATA_PATH}")
                except IOError as e:
                    logger.warning(f"Could not cache metadata: {e}")

            return metadata

        except requests.exceptions.RequestException as e:
            raise MetadataNotFoundError(f"Failed to download metadata from {url}: {e}")
        except json.JSONDecodeError as e:
            raise MetadataError(f"Invalid JSON from {url}: {e}")

    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load metadata from local file."""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise MetadataNotFoundError(f"Metadata file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise MetadataError(f"Invalid JSON in {file_path}: {e}")


def resolve_and_load_metadata(
    args: argparse.Namespace, force_download: bool = False
) -> Dict[str, Any]:
    """
    Main entry point for metadata resolution - matches existing interface.

    Args:
        args: Parsed command line arguments
        force_download: If True, bypass cache and download fresh metadata

    Returns:
        Metadata dictionary

    Raises:
        MetadataError: If metadata cannot be resolved
    """
    config = MetadataConfig.from_args(args)
    resolver = SimpleMetadataResolver(config)

    try:
        return resolver.resolve(force_download=force_download)
    except MetadataError:
        # Re-raise metadata errors as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise MetadataError(f"Unexpected error resolving metadata: {e}")


def extract_auth_header(auth_arg: Optional[str]) -> Optional[str]:
    """Extracts authorization token from string or file path."""
    if not auth_arg:
        return None
    if auth_arg.lower().startswith("path:"):
        token_path = auth_arg.split(":", 1)[1]
        with open(token_path, "r", encoding="utf-8") as f:
            return f"Bearer {f.read().strip()}"
    return f"Bearer {auth_arg}"


def build_inference_url(args: argparse.Namespace, metadata: Dict[str, Any]) -> str:
    """Construct the full inference URL based on protocol, host, port, and metadata."""
    if hasattr(args, "inference_url") and args.inference_url:
        base_url = args.inference_url.rstrip("/")
        model_name = metadata.get("model", {}).get("name", "unknown")
        return f"{base_url}/v2/models/{model_name}/infer"

    model_name = metadata.get("model", {}).get("name", "unknown")
    if args.protocol in ["http", "https"]:
        return f"{args.protocol}://{args.host}:{args.port}/v2/models/{model_name}/infer"

    # For gRPC, which doesn't use a standard URL for the requests library
    return f"{args.host}:{args.port}"


def build_inference_ready_url(
    args: argparse.Namespace, metadata: Dict[str, Any]
) -> str:
    """Construct the model readiness check URL."""
    if hasattr(args, "inference_url") and args.inference_url:
        base_url = args.inference_url.rstrip("/")
        model_name = metadata.get("model", {}).get("name", "unknown")
        return f"{base_url}/v2/models/{model_name}/ready"

    model_name = metadata.get("model", {}).get("name", "unknown")
    if args.protocol in ["http", "https"]:
        return f"{args.protocol}://{args.host}:{args.port}/v2/models/{model_name}/ready"

    # For gRPC, readiness check is often done differently or not at all.
    # Returning a URL that can be used for a simple health check if applicable.
    return f"{args.protocol}://{args.host}:{args.port}/v2/health/ready"
