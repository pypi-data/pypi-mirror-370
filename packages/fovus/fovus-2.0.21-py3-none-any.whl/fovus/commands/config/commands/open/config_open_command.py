import os
import shutil
import subprocess  # nosec
from http import HTTPStatus

import click

from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.constants.cli_constants import (
    FOVUS_PROVIDED_CONFIGS,
    PATH_TO_CONFIG_FILE_IN_REPO,
    PATH_TO_CONFIG_FILE_LOCAL,
    PATH_TO_CONFIG_ROOT,
    PATH_TO_JOB_CONFIGS,
    PATH_TO_JOB_LOGS,
    PATH_TO_USER_CONFIGS,
    UNIX_OPEN,
    WINDOWS_EXPLORER,
)
from fovus.exception.user_exception import UserException
from fovus.root_config import ROOT_DIR
from fovus.util.util import Util


@click.command("open")
def config_open_command():
    """
    Open the Fovus CLI config folder, located at ~/.fovus.

    Adds config file templates and examples to the folder for reference.
    """
    _create_missing_directories()
    Util.print_success_message(GENERIC_SUCCESS)
    _create_missing_empty_config_files()
    Util.print_success_message(GENERIC_SUCCESS)

    print("Opening config folder...")

    if Util.is_windows():
        subprocess.run(
            [WINDOWS_EXPLORER, os.path.expanduser(PATH_TO_CONFIG_ROOT)],
            shell=False,
            check=False,
        )  # nosec
    elif Util.is_unix():
        subprocess.run(
            [UNIX_OPEN, os.path.expanduser(PATH_TO_CONFIG_ROOT)],
            shell=False,
            check=False,
        )  # nosec
    else:
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            "Missing class name",
            "Unsupported operating system. Only Windows and Unix are supported.",
        )
    Util.print_success_message(GENERIC_SUCCESS)


def _create_missing_directories():
    print("Creating missing config directories (if any)")
    for directory in (
        PATH_TO_CONFIG_ROOT,
        PATH_TO_JOB_CONFIGS,
        PATH_TO_USER_CONFIGS,
        PATH_TO_JOB_LOGS,
    ):
        if not os.path.exists(os.path.expanduser(directory)):
            os.makedirs(os.path.expanduser(directory), exist_ok=True)


def _create_missing_empty_config_files():
    print("Creating missing empty config files (if any)")
    for config in FOVUS_PROVIDED_CONFIGS.values():
        empty_config_json_file_path = os.path.abspath(os.path.join(ROOT_DIR, config[PATH_TO_CONFIG_FILE_IN_REPO]))
        shutil.copy(empty_config_json_file_path, config[PATH_TO_CONFIG_FILE_LOCAL])
