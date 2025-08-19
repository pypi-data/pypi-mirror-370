import click
from typing_extensions import Tuple, Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.adapter.fovus_s3_adapter import FovusS3Adapter
from fovus.util.util import Util


@click.command("upload")
@click.argument(
    "local_path",
    type=str,
)
@click.argument(
    "fovus_path",
    type=str,
    required=False,
)
@click.option(
    "--include-paths",
    "include_paths_tuple",
    metavar="include_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the LOCAL_PATH that will be uploaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. taskName/out?/\*.txt matches any .txt file in folders taskName/out1, taskName/out2, etc.

        E.g. taskName???/folder/file.txt matches taskName001/folder/file.txt, taskName123/folder/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --include-paths "path1" --include-paths "path2"

        E.g. --include-paths "path1,path2"
        """,
)
@click.option(
    "--exclude-paths",
    "exclude_paths_tuple",
    metavar="exclude_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the LOCAL_PATH that will be uploaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. out?/\*.txt matches any .txt file in folders out1, out2, etc.

        E.g. folder???/file.txt matches folder001/file.txt, folder123/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --exclude-paths "path1" --exclude-paths "path2"

        E.g. --exclude-paths "path1,path2"
        """,
)
def storage_upload_command(
    local_path: str,
    fovus_path: Union[str, None],
    include_paths_tuple: Tuple[str, ...],
    exclude_paths_tuple: Tuple[str, ...],
):
    """
    Upload a file or folder to "My Files" in Fovus Storage.

    LOCAL_PATH is the path to a local file or folder that will be uploaded to Fovus Storage.

    FOVUS_PATH is the relative path within "My Files" in Fovus Storage where the targeted file(s) will be uploaded.
    This argument is optional.
    """
    include_paths = Util.parse_include_exclude_paths(include_paths_tuple)
    exclude_paths = Util.parse_include_exclude_paths(exclude_paths_tuple)

    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()
    fovus_s3_adapter = FovusS3Adapter(
        fovus_api_adapter,
        root_directory_path=local_path,
        fovus_path=fovus_path,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
    )
    fovus_s3_adapter.upload_storage_files()
