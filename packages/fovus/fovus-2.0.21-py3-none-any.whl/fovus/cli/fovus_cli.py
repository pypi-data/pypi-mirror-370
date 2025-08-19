#!/usr/bin/env python3
import logging
import os
import sys
import time

import click
import pkg_resources  # type: ignore
import requests
from packaging import version

from fovus.adapter.fovus_cognito_adapter import FovusCognitoAdapter
from fovus.cli.ssl import configure_ssl_env
from fovus.commands.auth.auth_command import auth_command
from fovus.commands.config.config_command import config_command
from fovus.commands.job.job_command import job_command
from fovus.commands.projects.projects_command import projects_command
from fovus.commands.storage.storage_command import storage_command
from fovus.config.config import Config
from fovus.constants.cli_constants import PATH_TO_LOGS
from fovus.constants.util_constants import UTF8

OK_RETURN_STATUS = 0
ERROR_RETURN_STATUS = 1

BASIC_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


def _confirm_latest_version():
    try:
        response = requests.get("https://pypi.org/pypi/fovus/json", timeout=5)
        data = response.json()
        latest_version = data["info"]["version"]
    except (requests.RequestException, KeyError):
        print("Unable to check for latest version.")
        return

    try:
        current_version = pkg_resources.get_distribution("fovus").version
    except pkg_resources.DistributionNotFound:
        print("Unable to check for latest version.")
        return

    if version.parse(current_version) < version.parse(latest_version):
        print(
            "===================================================\n"
            + f"  A new version of Fovus CLI ({latest_version}) is available.\n"
            + f"  Your current version is {current_version}\n"
            + "  Update using: pip install --upgrade fovus\n"
            + "==================================================="
        )


@click.group()
@click.option(
    "--silence",
    "-s",
    "_silence",
    is_flag=True,
    type=bool,
    help="Disable interactive CLI prompts and automatically dismiss warnings.",
)
@click.option(
    "--nextflow",
    "-nf",
    "_nextflow",
    is_flag=True,
    type=bool,
    help="Enable for nextflow job submission.",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    type=bool,
    help="Enable additional logs for debugging purposes.",
)
def cli(
    _silence: bool,
    _nextflow: bool,
    debug: bool,
):
    configure_ssl_env()

    logger = logging.getLogger()

    log_path = os.path.join(PATH_TO_LOGS, time.strftime("%Y-%m-%d_%H-%M-%S.log"))
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    file_handler = logging.FileHandler(log_path, mode="a", encoding=UTF8)
    file_handler.setFormatter(BASIC_FORMATTER)

    log_level = logging.DEBUG if debug else logging.INFO

    logger.setLevel(log_level)
    file_handler.setLevel(log_level)

    logger.addHandler(file_handler)

    _confirm_latest_version()

    is_gov = FovusCognitoAdapter.get_is_gov()
    Config.set_is_gov(is_gov)


cli.add_command(auth_command)
cli.add_command(storage_command)
cli.add_command(job_command)
cli.add_command(projects_command)
cli.add_command(config_command)


def main() -> int:
    try:
        # pylint: disable=no-value-for-parameter
        cli()
        return OK_RETURN_STATUS
    except Exception as exc:  # pylint: disable=broad-except
        print(exc)
        logging.critical("An unhandled exception occurred in main.")
        logging.exception(exc)
        return ERROR_RETURN_STATUS


if __name__ == "__main__":
    sys.exit(main())
