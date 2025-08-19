import click
from typing_extensions import Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS, OUTPUTS
from fovus.util.file_util import FileUtil


@click.command("status")
@click.option("--job-id", type=str, help="The ID of the job whose status will be retrieved.")
@click.option(
    "--job-directory",
    type=str,
    help=(
        "The directory of the job whose status will be fetched. The job directory must be initialized by the Fovus CLI."
    ),
)
def job_status_command(job_id: Union[str, None], job_directory: Union[str, None]):
    """
    Get a job's status.

    Either --job-id or --job-directory is required.
    """
    job_id = FileUtil.get_job_id(job_id, job_directory)

    print("Getting job current status...")
    fovus_api_adapter = FovusApiAdapter()
    job_current_status = fovus_api_adapter.get_job_current_status(job_id)
    print(GENERIC_SUCCESS)
    print(OUTPUTS)
    print("\n".join(("Job ID", job_id, "Job current status:", job_current_status)))
