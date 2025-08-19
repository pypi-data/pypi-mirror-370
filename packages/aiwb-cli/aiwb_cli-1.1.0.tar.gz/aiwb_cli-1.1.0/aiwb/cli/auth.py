import logging

import click

logger = logging.getLogger(__name__)


@click.command(help="Log in to AI Workbench.")
@click.pass_obj
def login(client):
    client.generate_auth_token()


@click.command(help="Log out to remove access to AI Workbench.")
@click.pass_obj
def logout(client):
    client.revoke_auth_token()


@click.command(help="Show the current authenticated user info.")
@click.pass_obj
def whoami(client):
    client.user_info()
