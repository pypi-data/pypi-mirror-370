import click

from .cli import CLIGroup


@click.group(cls=CLIGroup, help="aiwb cli IDE subcommand")
@click.pass_obj
def cli(client):
    pass


@cli.command(help="Get AIWB IDE status.")
@click.option("--workbench-id", "workbench_id", type=int, help="Workbench ID")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def status(client, workbench_id, output):
    model = client.model("ide", workbench_id=workbench_id, output=output)
    model.status()


@cli.command(help="Delete AIWB IDE by workbench id.")
@click.option("--workbench-id", "workbench_id", type=int, help="Workbench ID")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def delete(client, workbench_id, output):
    model = client.model("ide", workbench_id=workbench_id, output=output)
    model.delete()


@cli.command(help="Stop AIWB IDE by workbench id.")
@click.option("--workbench-id", "workbench_id", type=int, help="Workbench ID")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def stop(client, workbench_id, output):
    model = client.model("ide", workbench_id=workbench_id, output=output)
    model.stop()


@cli.command(help="Launch AIWB IDE by workbench id.")
@click.option("--workbench-id", "workbench_id", type=int, help="Workbench ID")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def launch(client, workbench_id, output):
    model = client.model("ide", workbench_id=workbench_id, output=output)
    model.launch()


@cli.command(help="List AIWB IDE.")
@click.pass_obj
@click.option(
    "--filter",
    "filter_set",
    type=str,
    multiple=True,
    help='Workbench filters, (e.g. --filter created_by="ran.tao.ak@renesas.com")',
)
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def list(client, filter_set, output):
    filters = []
    for pair in filter_set:
        if pair.count("=") != 1:
            raise click.BadParameter(f"Invalid format for --filter: '{pair}'. Expected <key>=<value>.")
        key, value = pair.split("=", 1)
        filters.append((key.strip(), value.strip()))
    model = client.model("workbench", output=output)
    model.list(filters)
