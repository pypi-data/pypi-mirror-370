import click

from fovus.adapter.fovus_api_adapter import FovusApiAdapter


@click.command("user")
def auth_user_command():
    """View information about the current user."""
    fovus_api_adapter = FovusApiAdapter()
    fovus_api_adapter.print_user_info()
