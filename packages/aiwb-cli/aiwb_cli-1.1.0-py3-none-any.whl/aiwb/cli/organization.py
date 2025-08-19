import click

from aiwb.core import Client
from .cli import CLIGroup


@click.group(cls=CLIGroup, help="Commands to manage organizations.")
@click.pass_obj
def organization(client: Client):
    pass


@organization.command(help="List the organizations.")
@click.pass_obj
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def list(client: Client, output):
    client.model("organization", output=output).list()


@organization.command(help="Show the detail of an organization.")
@click.pass_obj
@click.option("-n", "--name", type=str, required=True, help="Organization name.")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def describe(client: Client, name, output):
    client.model("organization", output=output).describe(name)


@organization.command(help="Create an organization.")
@click.option("-n", "--name", required=True, type=str, help="Organization name.")
@click.option("--domain-regex", "domain_regex", required=True, help="Domain regex of the organization.")
@click.option("--description", required=True, help="Description of the organization.")
@click.option("--admin-oid", help="Unique Entra ID object ID of the organization's admin.")
@click.option("--user-principal-name", help="Admin's Entra ID user principal name.")
@click.option("--email", help="Admin's email.")
@click.option("--logo-file", type=click.File("rb"), help="Path to logo image file.")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def create(client: Client, logo_file,output, **kwargs):
    data = {}

    for key, value in kwargs.items():
        if not value:
            continue
        if isinstance(value, str):
            # On windows, if we use --domain-regex './*', the value received here is "'./*'". So we strip it the outer quotes.
            data[key] = value.strip("'\"") if key == "domain_regex" else value.strip()
        else:
            data[key] = value

    client.model("organization", output=output).create(data, logo_file)


@organization.command(help="Update an organization.")
@click.option("-n", "--name", "organization_name", required=True, type=str, help="Organization name.")
@click.option("--description", help="Description of the organization.")
@click.option("--domain-regex", help="Domain regex of the organization.")
@click.option("--logo-file", type=click.File("rb"), help="Path to logo image file.")
@click.option("--delete-logo", is_flag=True, help="Delete the organization's current logo.")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def update(client: Client, organization_name, logo_file, delete_logo, output, **kwargs):
    data = {}

    for key, value in kwargs.items():
        if not value:
            continue
        if isinstance(value, str):
            # On windows, if we use --domain-regex './*', the value received here is "'./*'". So we strip it the outer quotes.
            data[key] = value.strip("'\"") if key == "domain_regex" else value.strip()
        else:
            data[key] = value

    if logo_file and delete_logo:
        click.echo("Ignoring --delete-logo since --logo-file is provided.")
        delete_logo = False

    if not data and not logo_file and not delete_logo:
        raise click.UsageError("Input is not provided, nothing to update.")

    client.model("organization", output=output).update(organization_name, data, logo_file, delete_logo=delete_logo)


@organization.command(help="Delete an organization.")
@click.option("-n", "--name", "organization_name", type=str, required=True, help="Organization name.")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def delete(client: Client, organization_name, output):
    client.model("organization", output=output).delete(organization_name)
