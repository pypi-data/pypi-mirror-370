import os
import shutil

import click
from termcolor import colored
from typing_extensions import Optional, Tuple

BYTES_IN_MEGABYTE = 1024**2
BYTES_IN_GIGABYTE = 1024**3

UNIX_OS_NAME = "posix"
WINDOWS_OS_NAME = "nt"

INCLUDE_EXCLUDE_PATHS_DELIMITER = ","


class Util:
    @staticmethod
    def parse_include_exclude_paths(include_exclude_paths_tuple: Tuple[str, ...]) -> Optional[list[str]]:
        include_exclude_paths_list = list(include_exclude_paths_tuple)

        results: list[str] = []

        # Separate any strings deliminated by ";" unless ";" is escaped with ";;"
        for path in include_exclude_paths_list:
            if INCLUDE_EXCLUDE_PATHS_DELIMITER not in path:
                results.append(path)
                continue

            current_path = ""
            escaped = False

            for char in path:
                if char == INCLUDE_EXCLUDE_PATHS_DELIMITER and not escaped:
                    escaped = True
                elif char == INCLUDE_EXCLUDE_PATHS_DELIMITER and escaped:
                    current_path += char
                    escaped = False
                elif escaped:
                    if current_path != "":
                        results.append(current_path)
                    current_path = char
                    escaped = False
                else:
                    current_path += char
                    escaped = False

            if current_path != "":
                results.append(current_path)

        if len(results) == 0:
            return None

        return results

    @staticmethod
    def convert_bytes_to_megabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_MEGABYTE

    @staticmethod
    def convert_bytes_to_gigabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_GIGABYTE

    @staticmethod
    def is_unix():
        return os.name == UNIX_OS_NAME

    @staticmethod
    def is_windows():
        return os.name == WINDOWS_OS_NAME

    @staticmethod
    def keep_prioritized_key_value_in_dict(dictionary, prioritized_key, fallback_key):
        if not dictionary.get(prioritized_key):
            dictionary[prioritized_key] = dictionary[fallback_key]
        del dictionary[fallback_key]

    @staticmethod
    def get_message_from_list(item_list, wrap_in="'"):
        if len(item_list) == 1:
            return f"{wrap_in}{item_list[0]}{wrap_in}"
        if len(item_list) == 2:
            return f"{wrap_in}{item_list[0]}{wrap_in} and {wrap_in}{item_list[1]}{wrap_in}"
        return (
            ", ".join([f"{wrap_in}{item}{wrap_in}" for item in item_list[:-1]])
            + f", and {wrap_in}{item_list[-1]}{wrap_in}"
        )

    @staticmethod
    def is_silenced() -> bool:
        return click.get_current_context().find_root().params.get("_silence", False)

    @staticmethod
    def is_nextflow_job() -> bool:
        return click.get_current_context().find_root().params.get("_nextflow", False)

    @staticmethod
    def confirm_action(message="Are you sure you want to continue?") -> bool:
        return Util.is_silenced() or input(f"{message} (y/n): ").lower() == "y"

    @staticmethod
    def print_success_message(message):
        print(colored(message, "green"))

    @staticmethod
    def print_warning_message(message):
        print(colored(message, "yellow"))

    @staticmethod
    def print_error_message(message):
        print(colored(message, "red"))

    @staticmethod
    def print_message_with_color(message, color="blue"):
        print(colored(message, color))

    @staticmethod
    def get_fovus_cli_path():
        fovus_cli_path = os.getenv("FOVUS_CLI_PATH") or shutil.which("fovus")

        assert fovus_cli_path, "Fovus CLI is not installed or not in PATH."

        return fovus_cli_path
