# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""azure-resource-sweeper: detect and safely clean up stale and unused Azure resources."""

from azure.cli.core import AzCommandsLoader

from azext_resource_sweeper._help import helps  # noqa: F401

__version__ = "0.2.1"


class ResourceSweeperCommandsLoader(AzCommandsLoader):
    """Entry point that registers the ``az sweeper`` command group with the CLI."""

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        custom_type = CliCommandType(
            operations_tmpl="azext_resource_sweeper.custom#{}"
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_resource_sweeper.commands import load_command_table

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_resource_sweeper._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = ResourceSweeperCommandsLoader
