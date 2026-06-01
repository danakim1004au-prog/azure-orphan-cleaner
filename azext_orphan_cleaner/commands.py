# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Command table: wires ``az orphan <verb>`` to functions in ``custom.py``."""


def load_command_table(self, _):
    """Register the ``orphan`` command group and its commands."""
    with self.command_group("orphan") as g:
        g.custom_command("scan", "scan_orphans")
        # Confirmation is handled inside clean_orphans() so we can respect the
        # --dry-run / --yes combination ourselves.
        g.custom_command("clean", "clean_orphans")

    return self.command_table
