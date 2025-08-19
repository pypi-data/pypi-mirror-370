import click

from fovus.commands.projects.commands.list.projects_list_command import (
    projects_list_command,
)


@click.group("projects")
def projects_command():
    """Contains commands related to projects."""


projects_command.add_command(projects_list_command)
