"""
Base classes for the modular CLI framework.
"""

import argparse
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Information about a CLI command."""

    name: str
    help: str


class CommandModule(ABC):
    """Base class for CLI command modules."""

    @property
    @abstractmethod
    def module_name(self) -> str:
        """Name of this command module."""
        pass

    @property
    @abstractmethod
    def module_help(self) -> str:
        """Help text for this command module."""
        pass

    @abstractmethod
    def get_commands(self) -> List[CommandInfo]:
        """Get list of commands provided by this module."""
        pass

    @abstractmethod
    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        """Register arguments for a specific command."""
        pass

    @abstractmethod
    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        """Execute a specific command."""
        pass

    def setup_subparser(
        self,
        subparsers,
    ) -> None:
        """Set up subparser for this module's commands."""
        commands = self.get_commands()

        if len(commands) == 1:
            # Single command - register directly
            command = commands[0]
            parser = subparsers.add_parser(command.name, help=command.help)
            self.register_command_args(parser, command.name)

            parser.set_defaults(
                func=lambda args: self.execute_command(command.name, args),
                command_name=command.name,
            )
        else:
            # Multiple commands - create subcommand structure
            module_parser = subparsers.add_parser(
                self.module_name, help=self.module_help
            )
            module_subparsers = module_parser.add_subparsers(
                title=f"{self.module_name.title()} Types",
                dest=f"{self.module_name}_type",
                help=f"Specify {self.module_name} type",
            )
            module_subparsers.required = True

            for command in commands:
                cmd_parser = module_subparsers.add_parser(
                    command.name, help=command.help
                )
                self.register_command_args(cmd_parser, command.name)

                cmd_parser.set_defaults(
                    func=lambda args, cmd_name=command.name: self.execute_command(
                        cmd_name, args
                    ),
                    command_name=command.name,
                )


class CLIManager:
    """Main CLI manager that coordinates all command modules."""

    def __init__(self, description: str = "Elastic Models CLI Tool"):
        self.description = description
        self.modules: Dict[str, CommandModule] = {}

    def register_module(self, module: CommandModule) -> None:
        """Register a command module."""
        self.modules[module.module_name] = module

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with all registered modules."""
        parser = argparse.ArgumentParser(
            description=self.description, prog="elastic-models-client"
        )

        subparsers = parser.add_subparsers(
            title="Commands", dest="command", help="Available commands"
        )
        subparsers.required = True

        # Register all modules
        for module in self.modules.values():
            module.setup_subparser(subparsers)

        return parser

    def run(self, argv: Optional[List[str]] = None) -> Any:
        """Run the CLI with the given arguments."""
        import sys

        parser = self.create_parser()
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)

        if hasattr(args, "func"):
            return args.func(args)
        else:
            parser.print_help()
            return 1


class BaseCommandGroupModule(CommandModule):
    """Base class for a group of command modules."""

    @property
    @abstractmethod
    def sub_modules(self) -> Dict[str, "CommandModule"]:
        """Return a dictionary of sub-modules."""
        pass

    def get_commands(self) -> List[CommandInfo]:
        """Get commands from all sub-modules."""
        commands = []
        for _, module in self.sub_modules.items():
            commands.extend(module.get_commands())
        return commands

    def _find_and_execute_on_module(
        self, command_name: str, operation_name: str, operation_func
    ) -> Any:
        """Find the appropriate sub-module and execute an operation on it.

        Args:
            command_name: The name of the command to find
            operation_name: Name of the operation (for error messages)
            operation_func: Function to execute on the found module

        Returns:
            The result of the operation_func, or None if no return value
        """
        errors = []
        for module_name, module in self.sub_modules.items():
            try:
                # Check if the command belongs to the current module
                if any(cmd.name == command_name for cmd in module.get_commands()):
                    return operation_func(module)
            except ValueError as e:
                # Store the error with module context
                errors.append(f"Error in module '{module_name}': {str(e)}")
                continue

        # If we get here, no module handled the command
        if errors:
            error_details = "\n".join(errors)
            raise ValueError(
                f"Command '{command_name}' {operation_name} failed:\n{error_details}"
            )
        else:
            raise ValueError(f"Unknown command: {command_name}")

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        """Register command arguments for the appropriate sub-module."""
        self._find_and_execute_on_module(
            command_name,
            "validation",
            lambda module: module.register_command_args(parser, command_name),
        )

    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        """Execute a command in the appropriate sub-module."""
        return self._find_and_execute_on_module(
            command_name,
            "execution",
            lambda module: module.execute_command(command_name, args),
        )


class BaseClientCommandModule(CommandModule):
    """Base command module for client inference requests."""

    @property
    @abstractmethod
    def module_name(self) -> str:
        pass

    @property
    def module_help(self) -> str:
        return f"Run {self.module_name} client"

    def get_commands(self) -> List[CommandInfo]:
        return [
            CommandInfo(
                name=self.module_name,
                help=self.module_help,
            )
        ]

    def register_command_args(
        self, parser: argparse.ArgumentParser, command_name: str
    ) -> None:
        """Register client command arguments."""
        if command_name == self.module_name:
            # Create mutually exclusive group for metadata sources
            metadata_group = parser.add_mutually_exclusive_group()

            metadata_group.add_argument(
                "--metadata-json", type=str, help="Path to local metadata.json file"
            )
            metadata_group.add_argument(
                "--metadata-url", type=str, help="URL to fetch metadata from"
            )
            metadata_group.add_argument(
                "--metadata-host",
                type=str,
                help="Metadata server hostname (defaults to --host, "
                "mutually exclusive with --metadata-url and --metadata-json)",
            )

            parser.add_argument(
                "--metadata-port",
                type=int,
                default=8003,
                help="Metadata server port (default: 8003, used with --metadata-host)",
            )

            parser.add_argument(
                "--host",
                type=str,
                default="localhost",
                help="Inference server hostname (default: localhost)",
            )
            parser.add_argument(
                "--port",
                type=int,
                default=8000,
                help="Inference server port (default: 8000)",
            )
            parser.add_argument(
                "--protocol",
                type=str,
                default="http",
                choices=["http", "https"],
                help="Protocol (default: http)",
            )
            parser.add_argument(
                "--inference-url",
                type=str,
                help="Full Inference server URL (overrides host/port/protocol)",
            )
            parser.add_argument(
                "--authorization",
                type=str,
                required=False,
                help="Basic Auth username:password or Bearer token.",
            )
            parser.add_argument(
                "--log-level",
                type=str,
                default="NONE",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"],
                help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL, "
                "NONE)",
            )
            parser.add_argument(
                "--timeout",
                type=int,
                default=10,
                help="Request timeout in seconds (default: 10)",
            )
        else:
            raise ValueError(f"Unknown client command: {command_name}")

    @abstractmethod
    def execute_command(self, command_name: str, args: argparse.Namespace) -> Any:
        """Execute client command."""
        pass
