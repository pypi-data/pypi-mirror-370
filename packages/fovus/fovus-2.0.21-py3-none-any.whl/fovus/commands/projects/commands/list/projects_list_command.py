import click

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.util.fovus_api_util import FovusApiUtil


@click.command("list")
def projects_list_command():
    """List all valid project names of your cost center."""
    fovus_api_adapter = FovusApiAdapter()
    active_projects = fovus_api_adapter.list_active_projects()
    FovusApiUtil.print_project_names(active_projects)
