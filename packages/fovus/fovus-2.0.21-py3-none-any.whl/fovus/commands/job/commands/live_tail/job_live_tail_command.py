import click
from typing_extensions import Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.util.file_util import FileUtil


@click.command("live-tail")
@click.argument(
    "file_path",
    type=str,
)
@click.option("--job-id", type=str, help="The ID of the job to monitor the file from.")
@click.option(
    "--job-directory",
    type=str,
    help="The directory of the job to monitor the file from. The job directory must be initialized by the Fovus CLI.",
)
def job_live_tail_command(file_path: str, job_id: Union[str, None], job_directory: Union[str, None]):
    """
    Live tail a file from a running job.

    Either --job-id or --job-directory is required.

    FILE_PATH is the path of the relative path of the file you want to monitor inside the job (e.g.
    taskName/path/to/file.txt).
    """
    job_id = FileUtil.get_job_id(job_id, job_directory)

    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()
    fovus_api_adapter.live_tail_file(job_id, file_path)
