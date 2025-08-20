"""
Modular CLI framework for elastic-models-client.

This module provides a clean, class-based architecture for CLI commands
with proper separation of concerns and minimal dependencies.
"""

from .base import CLIManager
from .registry import CommandRegistry

# Import command modules to trigger registration

try:
    from elastic_models.cli import serve  # noqa: F401
except ModuleNotFoundError:
    # output some text here?
    pass

from . import benchmark, client  # noqa: F401

__all__ = ["CLIManager", "CommandRegistry"]
