import click

from fovus.adapter.fovus_cognito_adapter import FovusCognitoAdapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.util.util import Util


@click.command("logout")
def auth_logout_command():
    """End the current session and log out."""
    print("Logging out...")
    FovusCognitoAdapter.sign_out()
    Util.print_success_message(GENERIC_SUCCESS)
