import os
import subprocess  # nosec

from tqdm import tqdm

from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.constants.cli_constants import PATH_TO_CONFIG_ROOT
from fovus.util.util import Util


def install_setup():
    commands = []
    previous_mount_storage_version = ""
    # https://github.com/awslabs/mountpoint-s3/releases
    current_mount_storage_version = "1.5.0"
    mount_storage_version_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.version")
    if os.path.exists(mount_storage_version_script_path):
        with open(mount_storage_version_script_path, encoding="utf-8") as file:
            previous_mount_storage_version = file.read().strip()

    if Util.is_windows():
        version_result = subprocess.run(["wsl", "--version"], capture_output=True, text=True, check=False)  # nosec
        status_result = subprocess.run(["wsl", "--status"], capture_output=True, text=True, check=False)  # nosec
        if "WSL version" not in (
            "".join(filter(lambda x: x != "\x00", version_result.stdout)).split(":")
        ) or 'Enable "Virtual Machine Platform" by running: wsl.exe --install --no-distribution' in (
            "".join(filter(lambda x: x != "\x00", status_result.stdout)).split("\n")
        ):
            commands = [
                "powershell Start-Process powershell -Verb runAs -ArgumentList "
                "'-Command dism.exe /online /enable-feature /featurename:Microsoft-Windows-"
                "Subsystem-Linux /all /norestart; Enable-WindowsOptionalFeature "
                "-FeatureName VirtualMachinePlatform -Online -N ; wsl --update ; "
                "wsl --set-default-version 2' -Wait"
            ] + commands

        result = subprocess.run(["wsl", "--list"], capture_output=True, text=True, check=False)  # nosec
        filtered_result = "".join(filter(lambda x: x != "\x00", result.stdout)).split("\n")
        if "Fovus-Ubuntu" not in filtered_result and "Fovus-Ubuntu (Default)" not in filtered_result:
            print("Initializing setup for Fovus Storage mount. It may take up to 5 minutes...")

            commands = commands + [
                "wsl --set-default-version 2",
                "curl -s -O https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64-root.tar.xz",
                "wsl --import Fovus-Ubuntu . jammy-server-cloudimg-amd64-root.tar.xz --version 2",
                "wsl -d Fovus-Ubuntu -u root -e rm jammy-server-cloudimg-amd64-root.tar.xz",
            ]
        else:
            print("Initializing setup for Fovus Storage mount. It may take up to 2 minutes...")

        result = subprocess.run(
            "wsl -d Fovus-Ubuntu -u root -e mount-s3 --version", capture_output=True, text=True, check=False
        )  # nosec
        if ("mount-s3" not in ("".join(filter(lambda x: x != "\x00", result.stdout)).split(" "))) or (
            previous_mount_storage_version != current_mount_storage_version
        ):
            commands = commands + [
                "wsl -d Fovus-Ubuntu -u root -e sudo apt-get update",
                "wsl -d Fovus-Ubuntu -u root -e sudo apt-get upgrade -y",
                "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y awscli",
                "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y python3-pip",
                "wsl -d Fovus-Ubuntu -u root -e sudo pip3 install fovus",
                (
                    # https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.deb
                    "wsl -d Fovus-Ubuntu -u root -e wget "
                    f"https://fovus-cli-dependencies.fovus.co/mount-storage/{current_mount_storage_version}/"
                    "ubuntu/mount-storage.deb"
                ),
                "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y ./mount-storage.deb",
                "wsl -d Fovus-Ubuntu -u root -e rm mount-storage.deb",
            ]

    elif Util.is_unix():
        print("Initializing setup for Fovus Storage mount. It may take up to 2 minutes...")
        try:
            distribution = subprocess.check_output(["lsb_release", "-is"]).decode().strip().lower()  # nosec
        except subprocess.CalledProcessError as error:
            print("Error while checking linux distribution:", error)

        if previous_mount_storage_version != current_mount_storage_version:
            if distribution == "centos":
                commands = [
                    "sudo yum upgrade -y",
                    "sudo yum install -y awscli",
                    "sudo yun install at",
                    "sudo service atd start",
                    # https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.rpm
                    (
                        "wget -q https://fovus-cli-dependencies.fovus.co/mount-storage/"
                        f"{current_mount_storage_version}/centos/mount-storage.rpm"
                    ),
                    "sudo yum install -y ./mount-storage.rpm",
                    "rm mount-storage.rpm*",
                ]
            elif distribution == "ubuntu":
                commands = [
                    "sudo apt-get upgrade -y",
                    "sudo apt-get install -y awscli",
                    "sudo apt install at",
                    "sudo service atd start",
                    (
                        "wget -q https://fovus-cli-dependencies.fovus.co/mount-storage/"
                        f"{current_mount_storage_version}/ubuntu/mount-storage.deb"
                    ),
                    "sudo apt-get install -y ./mount-storage.deb",
                    "rm mount-storage.deb*",
                ]

    if len(commands) > 0:
        total_iterations = len(commands)
        progress_bar = tqdm(total=total_iterations, desc="Setting up environments", unit="step")

        for command in commands:
            subprocess.run(
                command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )  # nosec
            # process = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # stdout, stderr = process.stdout.decode(), process.stderr.decode()
            # if stdout:
            #     print("STDOUT:", stdout)
            # if stderr:
            #     print("STDERR:", stderr)
            progress_bar.update(1)
        progress_bar.close()

        with open(mount_storage_version_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(current_mount_storage_version)

    Util.print_success_message(GENERIC_SUCCESS)
