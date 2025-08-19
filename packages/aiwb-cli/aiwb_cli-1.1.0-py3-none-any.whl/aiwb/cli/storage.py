# aiwb/cli/storage.py
import logging

from aiwb.core.client import Client

import click

from .cli import CLIGroup

logger = logging.getLogger(__name__)


@click.group(cls=CLIGroup, help="Commands to manage storage")
@click.pass_obj
def storage(client: Client):
    pass


@storage.command(name="list", help="List all items in the remote storage")
@click.pass_obj
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def list(client: Client, output):
    client.model("storage", output=output).list()


@storage.command(
    name="push", help="Upload contents from the local directory to remote storage"
)
@click.option("-d", "--directory", help="Local directory path")
@click.option("-f", "--file", help="Local file path")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def push(client: Client, output, directory, file):
    if not directory and not file:
        raise click.UsageError("You must provide either --directory or --file.")
    if directory and file:
        raise click.UsageError(
            "You must provide only one of --directory or --file, not both."
        )
    client.model("storage", output=output).push(directory, file)


@storage.command(
    name="pull", help="Download contents from remote storage to the local directory"
)
@click.option("-d", "--directory", help="Local directory path")
@click.option("-f", "--file", help="Local file path")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def pull(client: Client, output, directory, file):
    if not directory and not file:
        raise click.UsageError("You must provide either --directory or --file.")
    if directory and file:
        raise click.UsageError(
            "You must provide only one of --directory or --file, not both."
        )
    # Your logic here
    client.model("storage", output=output).pull(directory, file)


@storage.command(name="diff", help="Compare remote storage with the local directory")
@click.option("-d", "--directory", help="Local directory path")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def diff(client: Client, output, directory):
    if not directory:
        raise click.UsageError("You must provide --directory or -d")
    # Your logic here
    client.model("storage", output=output).diff(directory)
