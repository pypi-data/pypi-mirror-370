import click
from typing_extensions import Tuple

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.util.util import Util


@click.command("delete")
@click.argument(
    "job_id",
    type=str,
    nargs=-1,
)
def job_delete_command(job_id: Tuple[str, ...]):
    """
    Delete job records and files.

    This action cannot be undone.

    JOB_ID is The ID of the job to delete. Multiple job IDs may be provided.
    """
    num_jobs = len(job_id)

    if not Util.confirm_action(
        message=f"Are you sure you want to permanently delete {num_jobs} job{'' if num_jobs == 1 else 's'}? (y/n):",
    ):
        return

    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()
    print("Deleting job...")
    fovus_api_adapter.delete_job(job_id)
    Util.print_success_message(GENERIC_SUCCESS)
