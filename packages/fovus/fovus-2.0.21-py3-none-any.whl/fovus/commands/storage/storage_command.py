import click

from fovus.commands.storage.commands.download.storage_download_command import (
    storage_download_command,
)
from fovus.commands.storage.commands.mount.storage_mount_command import (
    storage_mount_command,
)
from fovus.commands.storage.commands.unmount.storage_unmount_command import (
    storage_unmount_command,
)
from fovus.commands.storage.commands.upload.storage_upload_command import (
    storage_upload_command,
)


@click.group("storage")
def storage_command():
    """Contains commands related to storage."""


storage_command.add_command(storage_mount_command)
storage_command.add_command(storage_unmount_command)
storage_command.add_command(storage_upload_command)
storage_command.add_command(storage_download_command)
