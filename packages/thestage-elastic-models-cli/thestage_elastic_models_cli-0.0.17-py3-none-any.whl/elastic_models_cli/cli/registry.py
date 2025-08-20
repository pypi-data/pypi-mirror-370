"""
Command registry for automatic module discovery.
"""

from typing import Dict, Type, List
from .base import CommandModule


class CommandRegistry:
    """Registry for command modules with auto-discovery capabilities."""

    def __init__(self):
        self._modules: Dict[str, Type[CommandModule]] = {}

    def register(self, module_class: Type[CommandModule]) -> None:
        """Register a command module class."""
        # Get module name from a temporary instance
        temp_instance = module_class()
        self._modules[temp_instance.module_name] = module_class

    def get_module_classes(self) -> Dict[str, Type[CommandModule]]:
        """Get all registered module classes."""
        return self._modules.copy()

    def create_modules(self) -> List[CommandModule]:
        """Create instances of all registered modules."""
        return [module_class() for module_class in self._modules.values()]


# Global registry instance
registry = CommandRegistry()
