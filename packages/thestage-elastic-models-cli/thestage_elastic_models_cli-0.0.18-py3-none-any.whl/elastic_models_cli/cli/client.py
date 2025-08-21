"""
Client command module for elastic-models-client CLI.
"""

from typing import Dict

from elastic_models_cli.cli.base import CommandModule, BaseCommandGroupModule
from elastic_models_cli.cli.registry import registry


class ClientModule(BaseCommandGroupModule):
    """Command module for client inference requests."""

    def __init__(self):
        self._sub_modules: Dict[str, CommandModule] = {}

    @property
    def sub_modules(self) -> Dict[str, CommandModule]:
        if not self._sub_modules:
            from ..client.diffusion.client import DiffusionClientModule
            from ..client.llm.client import LLMClientModule
            from ..client.vlm.client import VLMClientModule
            from ..client.stt.client import STTClientModule

            self._sub_modules = {
                "diffusion": DiffusionClientModule(),
                "llm": LLMClientModule(),
                "vlm": VLMClientModule(),
                "stt": STTClientModule(),
            }
        return self._sub_modules

    @property
    def module_name(self) -> str:
        return "client"

    @property
    def module_help(self) -> str:
        return "Run client-side inference requests"


# Register this module
registry.register(ClientModule)
