import click
from typing_extensions import Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.util.file_util import FileUtil


@click.command("terminate")
@click.argument("job_directory", type=Union[str, None], default=None, required=False)
@click.option(
    "--job-id",
    type=str,
    help=(
        "The ID of the job to terminate. This is only required if JOB_DIRECTORY has not been initialized by"
        " the Fovus CLI."
    ),
)
def job_terminate_command(
    job_id: Union[str, None],
    job_directory: Union[str, None],
):
    """
    Terminate a running job in Fovus.

    This command will stop the job and release any resources associated with it.
    """
    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()

    job_id = FileUtil.get_job_id(job_id, job_directory)
    fovus_api_adapter.terminate_job(job_id)

    print(f"Job {job_id} has been terminated successfully.")
