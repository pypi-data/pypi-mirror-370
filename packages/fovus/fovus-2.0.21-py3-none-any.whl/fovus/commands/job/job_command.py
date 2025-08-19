import click

from fovus.commands.job.commands.create.job_create_command import job_create_command
from fovus.commands.job.commands.delete.job_delete_command import job_delete_command
from fovus.commands.job.commands.download.job_download_command import (
    job_download_command,
)
from fovus.commands.job.commands.live_tail.job_live_tail_command import (
    job_live_tail_command,
)
from fovus.commands.job.commands.status.job_status_command import job_status_command
from fovus.commands.job.commands.sync_files.job_sync_command import job_sync_command
from fovus.commands.job.commands.terminate.job_terminate_command import (
    job_terminate_command,
)


@click.group("job")
def job_command():
    """Contains commands related to jobs."""


job_command.add_command(job_create_command)
job_command.add_command(job_delete_command)
job_command.add_command(job_download_command)
job_command.add_command(job_status_command)
job_command.add_command(job_live_tail_command)
job_command.add_command(job_sync_command)
job_command.add_command(job_terminate_command)
