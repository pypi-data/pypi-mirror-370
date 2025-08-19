import click

from fovus.commands.config.commands.open.config_open_command import config_open_command


@click.group("config")
def config_command():
    """Contains commands related to configuration."""


config_command.add_command(config_open_command)
