import importlib
import logging
import os

from aiwb import __version__
from aiwb.core import Client

import click


class CLIGroup(click.Group):
    def __init__(self, *args, lazy_subcommands=None, **kwargs):
        super().__init__(*args, **kwargs)
        # lazy_subcommands is a map of the form:
        #
        #   {command-name} -> {module-name}.{command-object-name}
        #
        self.lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx):
        base = super().list_commands(ctx)
        lazy = sorted(self.lazy_subcommands.keys())
        return base + lazy

    def get_command(self, ctx, cmd_name):
        if cmd_name in self.lazy_subcommands:
            return self._lazy_load(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _lazy_load(self, cmd_name):
        # lazily loading a command, first get the module name and attribute name
        import_path = self.lazy_subcommands[cmd_name]
        modname, cmd_object_name = import_path.rsplit(".", 1)
        # do the import
        mod = importlib.import_module(modname)
        # get the Command object from that module
        cmd_object = getattr(mod, cmd_object_name)
        # check the result to make debugging easier
        if not isinstance(cmd_object, click.Command):
            raise TypeError(f"Lazy loading of {import_path} failed by returning a non-command object")
        return cmd_object

    def format_commands(self, ctx, formatter):
        command_list = []
        subcommand_list = []

        commands = self.list_commands(ctx)
        if not commands:
            return

        # Find the length of the longest command name
        max_len = max(len(cmd) for cmd in commands)
        total_width = max_len + 12

        for cmd_name in commands:
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None or cmd.hidden:
                continue
            help_text = cmd.get_short_help_str().strip()

            padded = cmd_name.ljust(total_width)
            if isinstance(cmd, click.Group):
                if not help_text:
                    subcommand_list.append((cmd_name, ""))
                else:
                    subcommand_list.append((f"{padded}:", f"{help_text}"))
            elif not help_text:
                command_list.append((cmd_name, ""))
            else:
                command_list.append((f"{padded}:", f"{help_text}"))

        if command_list:
            with formatter.section("Commands"):
                formatter.write_dl(command_list, col_spacing=1)

        if subcommand_list:
            with formatter.section("Subcommands"):
                formatter.write_dl(subcommand_list, col_spacing=1)


@click.group(
    cls=CLIGroup,
    lazy_subcommands={
        "login": "aiwb.cli.auth.login",
        "logout": "aiwb.cli.auth.logout",
        "organization": "aiwb.cli.organization.organization",
        "whoami": "aiwb.cli.auth.whoami",
        "workbench": "aiwb.cli.workbench.cli",
        "ide": "aiwb.cli.ide.cli",
        "storage": "aiwb.cli.storage.storage",
        "model-validation": "aiwb.cli.model_validation.model_validation",
    },
    help="Renesas AI Workbench CLI",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity for users to see more output.",
)
@click.option(
    "--debug",
    count=True,
    help="Add detailed information for developers to debug issues.",
)
@click.pass_context
def cli_group(ctx, verbose, debug):
    """Main CLI group function"""
    # Only elevate logging if -v provided here; otherwise keep level set by main()
    if verbose and verbose >= 1:
        logging.getLogger().setLevel(logging.INFO)
    if debug and debug >= 1:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.obj = Client(access_key=os.getenv("AIWB_ACCESS_KEY"), cloud=os.getenv("AIWB_CLOUD", "aws"))


@cli_group.command(help="AI Workbench CLI version.")
def version():
    print(__version__)
