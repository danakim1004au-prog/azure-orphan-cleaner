# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""azure-orphan-cleaner: detect and safely clean up orphaned Azure resources."""

from azure.cli.core import AzCommandsLoader

from azext_orphan_cleaner._help import helps  # noqa: F401

__version__ = "0.1.0"


class OrphanCleanerCommandsLoader(AzCommandsLoader):
    """Entry point that registers the ``az orphan`` command group with the CLI."""

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        custom_type = CliCommandType(
            operations_tmpl="azext_orphan_cleaner.custom#{}"
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_orphan_cleaner.commands import load_command_table

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_orphan_cleaner._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = OrphanCleanerCommandsLoader
