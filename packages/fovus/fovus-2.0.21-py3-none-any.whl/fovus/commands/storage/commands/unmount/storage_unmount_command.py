import os
import subprocess  # nosec

import click

from fovus.constants.cli_constants import PATH_TO_CONFIG_ROOT
from fovus.util.util import Util


@click.command("unmount")
def storage_unmount_command():
    """Unmount Fovus Storage from your computer."""
    if Util.is_windows() or Util.is_unix():
        _unmount_storage()
    else:
        print(f"Fovus unmount storage is not available for your OS ({os.name}).")


def _unmount_storage():
    print("Unmounting Fovus Storage...")
    mount_storage_path = "/fovus-storage/"
    mounted_storage_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.path")
    if os.path.exists(mounted_storage_script_path):
        with open(mounted_storage_script_path, encoding="utf-8") as file:
            mount_storage_path = file.read().strip()

    if Util.is_windows():
        drive_name = "M"
        mounted_drive_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.drive")
        old_mounted_drive_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mounted_drive.txt")
        if os.path.exists(mounted_drive_script_path):
            with open(mounted_drive_script_path, encoding="utf-8") as file:
                drive_name = file.read().strip()
        # Todo: Remove this after 2 months
        elif os.path.exists(old_mounted_drive_script_path):
            with open(old_mounted_drive_script_path, encoding="utf-8") as file:
                drive_name = file.read().strip()
        current_dir = os.getcwd()
        if current_dir and current_dir.startswith(f"{drive_name}:"):
            print("Current directory:", current_dir)
            print(
                f"Unmounting Fovus Storage cannot be performed under {drive_name}:\\. "
                f"This command must be issued from a path outside {drive_name}:\\. "
            )
            return
        error_count = 0
        for mount_dir in ["files", "jobs"]:
            result = subprocess.run(
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    f"umount {mount_storage_path}{mount_dir}",
                ],
                capture_output=True,
                text=True,
                check=False,
                shell=True,
            )  # nosec
            if result.stderr:
                if "target is busy" in result.stderr.strip():
                    error_count += 1
                    print("Mount point is busy!")

        if error_count > 0:
            return

        subprocess.run(  # nosec
            [
                "wsl",
                "-d",
                "Fovus-Ubuntu",
                "-u",
                "root",
                "bash",
                "-c",
                "sudo rm /etc/profile.d/fovus-storage-init.sh",
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
                "sudo rm ~/.aws/credentials",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        subprocess.run(  # nosec
            'schtasks /delete /tn "FovusMountStorageRefresh" /f',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )

        launch_wsl_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "launch_wsl.vbs")
        subprocess.run(  # nosec
            f'del "{launch_wsl_script_path}"',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )

        startup_folder = os.path.join(
            os.getenv("APPDATA"),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )  # Use Win + R -> shell:startup
        mount_fovus_storage_script_path = os.path.join(startup_folder, "mount_fovus_storage.vbs")
        subprocess.run(  # nosec
            f'del "{mount_fovus_storage_script_path}"',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )

        subprocess.run(  # nosec
            f"net use {drive_name}: /delete /persistent:yes",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )
        subprocess.run(  # nosec
            f"powershell NET USE {drive_name}: /DELETE",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )
        print("Fovus Storage successfully unmounted!")
    elif Util.is_unix():
        error_count = 0
        for mount_dir in ["files", "jobs"]:
            result = subprocess.run(
                f"sudo umount {mount_storage_path}{mount_dir}",
                capture_output=True,
                text=True,
                check=False,
                shell=True,
            )  # nosec
            if result.stderr:
                print(result.stderr.strip())
                if "target is busy" in result.stderr.strip():
                    error_count += 1
                    print("Mount point is busy!")

        if error_count > 0:
            return
        os.system("atq | cut -f 1 | xargs atrm > /dev/null 2>&1")  # nosec
        os.system("sudo rm /etc/profile.d/fovus-storage-init.sh > /dev/null 2>&1")  # nosec
        os.system("sudo rm ~/.aws/credentials > /dev/null 2>&1")  # nosec
        print("Fovus Storage successfully unmounted!")
