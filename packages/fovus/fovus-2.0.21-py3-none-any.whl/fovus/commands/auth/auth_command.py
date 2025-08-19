import click

from fovus.commands.auth.commands.login.auth_login_command import auth_login_command
from fovus.commands.auth.commands.logout.auth_logout_command import auth_logout_command
from fovus.commands.auth.commands.user.auth_user_command import auth_user_command


@click.group("auth")
def auth_command():
    """Contains commands related to authentication."""


auth_command.add_command(auth_login_command)
auth_command.add_command(auth_logout_command)
auth_command.add_command(auth_user_command)
