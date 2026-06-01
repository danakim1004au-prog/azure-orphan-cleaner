# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Command table: wires ``az sweeper <verb>`` to functions in ``custom.py``."""


def load_command_table(self, _):
    """Register the ``sweeper`` command group and its commands."""
    with self.command_group("sweeper") as g:
        g.custom_command("scan", "scan_resources")
        # Confirmation is handled inside clean_resources() so we can respect the
        # --dry-run / --yes combination ourselves.
        g.custom_command("clean", "clean_resources")

    return self.command_table
