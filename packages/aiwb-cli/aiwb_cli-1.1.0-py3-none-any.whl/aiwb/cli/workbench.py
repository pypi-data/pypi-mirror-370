import click
import sys

from .cli import CLIGroup
from aiwb.core import Client


@click.group(cls=CLIGroup, help="Commands to manage workbench.")
@click.pass_obj
def cli(client: Client):
    pass


@cli.command(help="List AIWB workbenches.")
@click.pass_obj
@click.option(
    "--filter",
    "filter_set",
    type=str,
    multiple=True,
    help='Workbench filters, (e.g. --filter created_by="ran.tao.ak@renesas.com")',
)
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def list(client: Client, filter_set, output):
    filters = []
    for pair in filter_set:
        if pair.count("=") != 1:
            raise click.BadParameter(f"Invalid format for --filter: '{pair}'. Expected <key>=<value>.")
        key, value = pair.split("=", 1)
        filters.append((key.strip(), value.strip()))
    model = client.model("workbench", output=output)
    model.list(filters)


@cli.command(help="Delete AIWB workbenches.")
@click.pass_obj
@click.option("--id", "ids", type=int, help="Workbench id")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def delete(client: Client, ids, output):
    model = client.model("workbench", output=output)
    model.delete(ids)


@cli.command(help="Create AIWB workbenches.")
@click.pass_obj
@click.option("-n", "--name", type=str, required=True, help="Workbench name")
@click.option(
    "--size",
    type=str,
    required=True,
    help="Workbench instance size, oneof=('4c8g', 8c16g')",
)
@click.option("--sdk", type=str, required=True, help="Workbench SDK version")
@click.option("--description", type=str, help="Workbench description")
@click.option("--storage-size", type=int, default=20, help="Storage size, default: 20")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def create(client: Client, name, size, sdk, description, storage_size, output):
    if len(name) > 32:
        click.echo("workbench name is over the limit (>32).")
        sys.exit(1)
    if description and len(description) > 128:
        click.echo("workbench description is over the limit (>128).")
        sys.exit(1)
    if storage_size and (storage_size > 1000 or storage_size < 20):
        click.echo("storage size is invalid, (20<x<1000).")
        sys.exit(1)
    model = client.model("workbench")
    if size not in model.instance_size:
        click.echo(f"size should be in {str(model.instance_size.keys())}")
        sys.exit(1)
    if sdk not in model.sdk_info:
        click.echo(f"sdk version should be in {model.sdk_info}")
        sys.exit(1)
    client.model("workbench", output=output).create(name, size, sdk, description, storage_size)
