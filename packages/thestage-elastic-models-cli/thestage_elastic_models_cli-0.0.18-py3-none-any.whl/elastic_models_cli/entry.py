"""
New modular CLI entry point for elastic-models-client.

This replaces the old cli.py with a clean, modular architecture that
segregates commands into separate modules with minimal dependencies.
"""

from typing import List, Optional

from .cli import CLIManager

# Import the cli module to trigger auto-registration of commands.
# The __init__.py in the 'cli' package imports all command modules.
# Each command module then calls `registry.register()` on itself.


def main(argv: Optional[List[str]] = None):
    """
    Main entry point for the elastic-models-client CLI

    Args:
        argv: Command line arguments
    """
    # Create CLI manager
    cli_manager = CLIManager(description="Elastic Models CLI Tool")

    # Auto-discover and register all command modules
    from .cli.registry import registry

    for module in registry.create_modules():
        cli_manager.register_module(module)

    # Run the CLI
    return cli_manager.run(argv)


if __name__ == "__main__":
    main()
