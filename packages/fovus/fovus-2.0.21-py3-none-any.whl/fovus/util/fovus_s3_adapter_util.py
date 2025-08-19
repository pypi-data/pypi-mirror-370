from typing_extensions import Union

from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.util.util import Util

NUM_DECIMAL_POINTS_FILESIZE = 4


class FovusS3AdapterUtil:
    @staticmethod
    def print_pre_operation_information(
        operation: str, file_count: int, file_size_bytes: int, task_count: Union[int, None] = None
    ):
        print(f"Beginning {operation}:")

        if isinstance(task_count, int):
            print(f"\tTask count:\t{task_count}")

        print(f"\tFile count:\t{file_count}")
        total_file_size_gigabytes = round(Util.convert_bytes_to_gigabytes(file_size_bytes), NUM_DECIMAL_POINTS_FILESIZE)
        total_file_size_megabytes = round(Util.convert_bytes_to_megabytes(file_size_bytes), NUM_DECIMAL_POINTS_FILESIZE)
        print(f"\tFile size:\t{total_file_size_megabytes} MB ({total_file_size_gigabytes} GB)")

    @staticmethod
    def print_post_operation_success(operation, is_success):
        if is_success:
            Util.print_success_message(f"{GENERIC_SUCCESS} {operation} complete.")
        else:
            Util.print_error_message(f"Failed {operation}")

        if operation == "Download":
            print(
                "Note: The download function operates as a sync. If a local file exists with the same path relative to "
                + "the job folder as a file in the cloud, and the two files are identical, it was not re-downloaded "
            )
