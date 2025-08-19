import os
import subprocess  # nosec
from datetime import datetime, timedelta

import click
from typing_extensions import Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.cli.helpers import install_setup
from fovus.config.config import Config
from fovus.constants.cli_constants import AWS_REGION, PATH_TO_CONFIG_ROOT
from fovus.util.util import Util


@click.command("mount")
@click.option(
    "--mount-storage-path",
    type=str,
    help="The path where Fovus Storage will be mounted. The default path is /fovus-storage/.",
)
@click.option(
    "--windows-drive",
    type=str,
    help='For Windows operating systems only. The drive where Fovus Storage will be mounted. The default drive is "M".',
)
def storage_mount_command(mount_storage_path: Union[str, None], windows_drive: Union[str, None]):
    r"""
    Mount Fovus Storage on your computer.

    Supported operating systems: Windows, Ubuntu, CentOS, and Redhat.

    Fovus Storage will be mounted as a network file system at /fovus-storage/ on Linux or
    <WindowsDrive>:\\fovus-storage\\ on Windows.

    Supported file operations: sequential & random read, sequential write, overwrite, delete

    Job files are read-only.

    The Fovus Storage network file system does not support modifying existing files directly.
    To modify a file, overwrite it instead. We recommend using Fovus Storage as a cloud archive
    instead of a working directory due to suboptimal performance and usability.
    """
    if Util.is_windows() or Util.is_unix():
        credentials_content = _get_mount_storage_credentials()
        install_setup()
        _mount_storage(credentials_content, mount_storage_path, windows_drive)
    else:
        print(f"Fovus mount storage is not available for your OS ({os.name}).")


def _mount_storage(
    credentials_content,
    mount_storage_path: Union[str, None] = None,
    windows_drive: Union[str, None] = None,
):
    print("Mounting Fovus Storage...")
    fovus_api_adapter = FovusApiAdapter()
    user_id = fovus_api_adapter.get_user_id()
    workspace_id = fovus_api_adapter.get_workspace_id()
    workspace_region = Config.get(AWS_REGION)
    fovus_cli_path = Util.get_fovus_cli_path()

    if mount_storage_path:
        mount_storage_path = mount_storage_path.strip().replace("\\", "/")
        if not mount_storage_path.startswith("/"):
            mount_storage_path = "/" + mount_storage_path
        if not mount_storage_path.endswith("/"):
            mount_storage_path = mount_storage_path + "/"

    mounted_storage_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.path")
    if not mount_storage_path:
        if os.path.exists(mounted_storage_script_path):
            with open(mounted_storage_script_path, encoding="utf-8") as file:
                mount_storage_path = file.read().strip()
        else:
            mount_storage_path = "/fovus-storage/"

    print("Mount storage path:", mount_storage_path)
    subprocess.run(  # nosec
        "fovus storage unmount",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        shell=True,
    )

    if Util.is_unix():
        for mount_dir in ["files", "jobs"]:
            path = f"{mount_storage_path}{mount_dir}"
            if os.path.exists(path) and any(os.scandir(path)):
                print(f"{mount_storage_path} is not empty. The specified path must be an empty folder.")
                return

    with open(mounted_storage_script_path, "w", encoding="utf-8") as script_file:
        script_file.write(mount_storage_path)

    if workspace_region == "us-east-1":
        endpoint_url = "https://s3.amazonaws.com"
    else:
        endpoint_url = f"https://s3.{workspace_region}.amazonaws.com"

    mount_command = (
        f"mount-s3 fovus-{user_id}-{workspace_id}-{workspace_region} {mount_storage_path}files --prefix=files/ "
        f"--allow-delete --file-mode=0770 --dir-mode=0770 --endpoint-url {endpoint_url} "
        f"> /dev/null 2>&1 && mount-s3 fovus-{user_id}-{workspace_id}-{workspace_region} {mount_storage_path}jobs "
        "--prefix=jobs/ --allow-delete --file-mode=0550 --dir-mode=0550 "
        f"--endpoint-url {endpoint_url} > /dev/null 2>&1"
    )

    for directory in [
        "~/.aws",
        "~/.fovus",
        f"{mount_storage_path}files",
        f"{mount_storage_path}jobs",
    ]:
        if Util.is_windows():
            check_directory_command = [
                "wsl",
                "-d",
                "Fovus-Ubuntu",
                "-u",
                "root",
                "bash",
                "-c",
                f"[ -d {directory} ] && echo 'Exists' || echo 'Not Exists'",
            ]
            result = subprocess.run(check_directory_command, capture_output=True, text=True, check=False)  # nosec
            if result.stdout.strip() == "Not Exists":
                create_directory_command = [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    f"mkdir -p {directory}",
                ]
                subprocess.run(  # nosec
                    create_directory_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
        elif Util.is_unix():
            if not os.path.exists(os.path.expanduser(f"{directory}")):
                os.system(f"sudo mkdir -p {directory}")  # nosec
                os.system(f"sudo chmod 777 {directory}")  # nosec

    if Util.is_windows():
        for file_name in [".credentials", ".device_information"]:
            with open(os.path.join(PATH_TO_CONFIG_ROOT, file_name), encoding="utf-8") as file:
                fovus_credentials_content = file.read()
            subprocess.run(  # nosec
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    f"echo '{fovus_credentials_content.strip()}' > ~/.fovus/{file_name}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

        log_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "wsl_status.log")
        os.system(f"wsl --version > {log_script_path}")  # nosec
        os.system(f"wsl --status >> {log_script_path}")  # nosec
        os.system(f"wsl --list >> {log_script_path}")  # nosec

        subprocess.run(  # nosec
            [
                "wsl",
                "-d",
                "Fovus-Ubuntu",
                "-u",
                "root",
                "bash",
                "-c",
                f"echo '{credentials_content.strip()}' > ~/.aws/credentials",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        subprocess.run(  # nosec
            [
                "wsl",
                "-d",
                "Fovus-Ubuntu",
                "-u",
                "root",
                "bash",
                "-c",
                f"echo '{mount_command}' > /etc/profile.d/fovus-storage-init.sh",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        subprocess.run(  # nosec
            ["wsl", "-d", "Fovus-Ubuntu", "--shutdown"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        mounted_drive_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.drive")
        if not windows_drive:
            if os.path.exists(mounted_drive_script_path):
                with open(mounted_drive_script_path, encoding="utf-8") as file:
                    windows_drive = file.read().strip()
            else:
                windows_drive = "M"

        with open(mounted_drive_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(windows_drive)

        launch_wsl_script_content = rf"""Set shell = CreateObject("WScript.Shell")
        shell.Run "wsl -d Fovus-Ubuntu", 0
        Set FSO = CreateObject("Scripting.FileSystemObject")

        If FSO.DriveExists("{windows_drive}:\") Then
            WScript.Echo "{windows_drive}: drive is already mapped."
        Else
            shell.Run "cmd /c net use {windows_drive}: \\wsl.localhost\Fovus-Ubuntu /persistent:yes", 0
            WScript.Echo "WSL directory mapped to {windows_drive}: drive."
        End If
        """
        launch_wsl_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "launch_wsl.vbs")

        with open(launch_wsl_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(launch_wsl_script_content)

        subprocess.run(  # nosec
            f'cscript "{launch_wsl_script_path}"',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        # https://superuser.com/questions/263545/how-can-i-make-a-vb-script-execute-every-time-windows-starts-up
        os.path.expanduser(PATH_TO_CONFIG_ROOT)
        mount_fovus_storage_script_content = rf"""Set shell = CreateObject("WScript.Shell")
        shell.Run "cmd /c {fovus_cli_path} storage mount", 0"""
        startup_folder = os.path.join(
            os.getenv("APPDATA"),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )  # Use Win + R -> shell:startup
        mount_fovus_storage_script_path = os.path.join(startup_folder, "mount_fovus_storage.vbs")

        with open(mount_fovus_storage_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(mount_fovus_storage_script_content)

        # Set scheduler to run the mount_fovus_storage.vbl after 28 days to refresh credentials
        future_date = datetime.now() + timedelta(days=28)
        formatted_date = future_date.strftime("%x")
        command = rf"C:\Windows\System32\cscript.exe '{mount_fovus_storage_script_path}'"
        subprocess.run(  # nosec
            f'schtasks /create /tn "FovusMountStorageRefresh" /tr "{command}" /sc once '
            f"/st 00:00 /sd {formatted_date} /f",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )
        windows_path = mount_storage_path.replace("/", "\\")
        print(
            rf"Your Fovus Storage is successfully mounted under the path of {windows_drive}:{windows_path} as a "
            rf'network file system. The path to "My files" is {windows_drive}:{windows_path}files, '
            rf'and the path to "Job files" is {windows_drive}:{windows_path}jobs. Job files are read-only.'
            "\n\n"
            "The mounted network file system is optimized for high throughput read to large files by multiple "
            "clients in parallel and sequential write to new files by one client at a time subject to your network "
            "speed.\n"
            "NOTE: Job files under the mounted Fovus Storage are only synced upon job completion. While a job is "
            "running, an instant sync of job files to the mounted Fovus Storage can be triggered via Fovus web UI "
            'by clicking the refresh button on the job detail page over the "Files" tab.'
        )
        print(
            f"\033[93mA system reboot may be required. If you do not see a new {windows_drive}:\\ drive gets mounted "
            'under "This PC", please reboot your system for it to take effect.\033[0m'
        )
    elif Util.is_unix():
        subprocess.run(  # nosec
            f"echo '{credentials_content.strip()}' > ~/.aws/credentials",
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        fovus_storage_init_command = f"""
        export FOVUS_CLI_PATH="{fovus_cli_path}"
        "$FOVUS_CLI_PATH" storage mount || echo "Failed to mount Fovus Storage"
        """

        os.system(
            f"echo '{fovus_storage_init_command}' | sudo tee  /etc/profile.d/fovus-storage-init.sh > /dev/null 2>&1"
        )  # nosec
        #  https://www.redhat.com/sysadmin/linux-at-command
        os.system("atq | cut -f 1 | xargs atrm > /dev/null 2>&1")  # nosec
        os.system(f"echo '{fovus_storage_init_command}' | at 00:00 + 28 day > /dev/null 2>&1")  # nosec
        os.system(mount_command)  # nosec
        print(
            f"Your Fovus Storage is successfully mounted under the path of {mount_storage_path} as a network "
            f'file system (a system reboot may be needed). The path to "My files" is {mount_storage_path}files, '
            f'and the path to "Job files" is {mount_storage_path}jobs. Job files are read-only.'
            "\n\n"
            "The mounted network file system is optimized for high throughput read to large files by multiple "
            "clients in parallel and sequential write to new files by one client at a time subject to your network "
            "speed.\n"
            "NOTE: Job files under the mounted Fovus Storage are only synced upon job completion. While a job is "
            "running, an instant sync of job files to the mounted Fovus Storage can be triggered via Fovus web UI "
            'by clicking the refresh button on the job detail page over the "Files" tab.'
        )


def _get_mount_storage_credentials():
    fovus_api_adapter = FovusApiAdapter()
    user_id = fovus_api_adapter.get_user_id()
    workspace_id = fovus_api_adapter.get_workspace_id()

    mount_storage_credentials_body = fovus_api_adapter.get_mount_storage_credentials(
        FovusApiAdapter.get_mount_storage_credentials_request(user_id, workspace_id)
    )
    credentials_content = f"""
[default]
aws_access_key_id = {mount_storage_credentials_body["credentials"]["accessKeyId"]}
aws_secret_access_key = {mount_storage_credentials_body["credentials"]["secretAccessKey"]}
    """
    return credentials_content
