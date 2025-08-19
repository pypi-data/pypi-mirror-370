import fnmatch
import hashlib
import json
import os
import re
from http import HTTPStatus

import click
from mypy_boto3_s3.type_defs import ObjectTypeDef
from typing_extensions import Any, Callable, Union

from fovus.constants.cli_constants import (
    FOVUS_JOB_INFO_FOLDER,
    JOB_DATA_FILENAME,
    JOB_ID,
    PATH_TO_CREDENTIALS_FILE,
    PATH_TO_DEVICE_INFORMATION_FILE,
    PATH_TO_WORKSPACE_SSO_TOKENS_FILE,
)
from fovus.constants.util_constants import UTF8
from fovus.exception.user_exception import UserException
from fovus.util.util import Util

# Allowed characters: a-z, A-Z, 0-9, _, -, ., !, (, )
# They are accepted in both Windows and Linux
VALID_TASK_FOLDER_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.!\(\)\+]+$")


class FileUtil:
    @staticmethod
    def get_job_id(job_id: Union[str, None], job_directory: Union[str, None]) -> str:
        if job_id is not None:
            return job_id

        if job_directory is not None:
            print(
                "Job ID not specified. Attempting to find job ID in "
                + os.path.join(job_directory, FOVUS_JOB_INFO_FOLDER, JOB_DATA_FILENAME)
                + "..."
            )
            job_data_file_path = os.path.join(job_directory, FOVUS_JOB_INFO_FOLDER, JOB_DATA_FILENAME)
            if os.path.exists(job_data_file_path):
                with FileUtil.open(job_data_file_path) as file:
                    job_data = json.load(file)
                    return job_data.get(JOB_ID)

        raise click.BadParameter(
            message=(
                "Missing job ID. This can be provided as an argument (via --job-id) or through the job data "
                "file, which is automatically generated in the "
                "'job_directory/.fovus' directory when a job is created from the CLI."
            )
        )

    # pylint: disable=too-many-locals
    @staticmethod
    def remove_device_information() -> None:
        try:
            os.remove(PATH_TO_DEVICE_INFORMATION_FILE)
        except FileNotFoundError:
            pass

    @staticmethod
    def remove_credentials() -> None:
        try:
            os.remove(PATH_TO_CREDENTIALS_FILE)
        except FileNotFoundError:
            pass

        try:
            os.remove(PATH_TO_WORKSPACE_SSO_TOKENS_FILE)
        except FileNotFoundError:
            pass

    @staticmethod
    def get_files_in_job_directory(
        root_directory_path, include_input_list, exclude_input_list
    ) -> tuple[list, list, list, int, int]:
        invalid_dirs: list[str] = []
        local_filepath_list = []
        local_folderpath_list = []
        total_file_size_bytes = 0

        for directory_path, dirs, filenames in os.walk(root_directory_path):
            is_any_file_included = False

            for file in filenames:
                local_filepath = os.path.join(directory_path, file)
                if FileUtil.should_ignore_path(file) or not FileUtil.include_exclude_allows_path(
                    os.path.relpath(local_filepath, root_directory_path), include_input_list, exclude_input_list
                ):
                    continue

                if not VALID_TASK_FOLDER_REGEX.match(file):
                    invalid_dirs.append(file)
                    continue

                local_filepath_list.append(local_filepath)
                total_file_size_bytes += os.path.getsize(local_filepath)
                is_any_file_included = True

            dirs[:] = [
                dirname
                for dirname in dirs
                if not FileUtil.should_ignore_path(dirname)
                and FileUtil.include_exclude_allows_path(
                    os.path.relpath(os.path.join(directory_path, dirname), root_directory_path) + os.path.sep,
                    False,
                    exclude_input_list,
                )
            ]

            if os.path.samefile(directory_path, root_directory_path):
                continue

            dirname = os.path.basename(directory_path)

            if not VALID_TASK_FOLDER_REGEX.match(dirname):
                invalid_dirs.append(dirname)
                continue

            local_relative_folderpath = os.path.relpath(directory_path, root_directory_path)

            if is_any_file_included or FileUtil.include_exclude_allows_path(
                local_relative_folderpath + os.path.sep, include_input_list, exclude_input_list
            ):
                local_relative_folderpath_split = local_relative_folderpath.split(os.path.sep)

                for i in range(len(local_relative_folderpath_split)):
                    current_local_relative_folderpath = os.path.join(*local_relative_folderpath_split[: i + 1])
                    if current_local_relative_folderpath not in local_folderpath_list:
                        local_folderpath_list.append(current_local_relative_folderpath)

        if len(invalid_dirs) > 0:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FileUtil.__name__,
                "Folder and file names must only contain the following characters: "
                + "a–z, A–Z, 0–9, hyphen (-), underscore (_), period (.), exclamation mark (!), and parentheses (()).\n"
                + "The following names are invalid:\n"
                + "\n".join(invalid_dirs),
            )

        task_directories = [dirname for dirname in local_folderpath_list if os.path.sep not in dirname]

        empty_folderpath_list = [
            local_folderpath
            for local_folderpath in local_folderpath_list
            if all(
                not local_folderpath == os.path.dirname(os.path.relpath(local_filepath, root_directory_path))
                for local_filepath in local_filepath_list
            )
            and all(
                not local_folderpath == os.path.dirname(current_local_folderpath)
                for current_local_folderpath in local_folderpath_list
            )
        ]

        return (
            local_filepath_list,
            local_folderpath_list,
            empty_folderpath_list,
            len(task_directories),
            total_file_size_bytes,
        )

    @staticmethod
    def get_files_in_storage_directory(root_directory_path: str, include_input_list, exclude_input_list):
        if os.path.isfile(root_directory_path):
            basename = os.path.basename(root_directory_path)
            if not VALID_TASK_FOLDER_REGEX.match(basename):
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    FileUtil.__name__,
                    "Folder and file names must only contain the following characters: "
                    + "a–z, A–Z, 0–9, hyphen (-), underscore (_), period (.), exclamation mark (!), "
                    "and parentheses (()).\n" + "The following names are invalid:\n" + basename,
                )

            return [root_directory_path], os.path.getsize(root_directory_path)

        invalid_dirs: list[str] = []
        local_filepath_list = []
        total_file_size_bytes = 0

        for directory_path, dirs, filenames in os.walk(root_directory_path):
            for file in filenames:
                local_filepath = os.path.join(directory_path, file)
                if FileUtil.should_ignore_path(file) or not FileUtil.include_exclude_allows_path(
                    os.path.relpath(local_filepath, root_directory_path), include_input_list, exclude_input_list
                ):
                    continue

                if not VALID_TASK_FOLDER_REGEX.match(file):
                    invalid_dirs.append(file)
                    continue

                local_filepath_list.append(local_filepath)
                total_file_size_bytes += os.path.getsize(local_filepath)

            dirname = os.path.basename(directory_path)

            if not VALID_TASK_FOLDER_REGEX.match(dirname):
                invalid_dirs.append(dirname)

            dirs[:] = [
                dirname
                for dirname in dirs
                if not FileUtil.should_ignore_path(dirname)
                and FileUtil.include_exclude_allows_path(
                    os.path.relpath(os.path.join(directory_path, dirname), root_directory_path) + os.path.sep,
                    False,
                    exclude_input_list,
                )
            ]

        if len(invalid_dirs) > 0:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FileUtil.__name__,
                "Folder and file names must only contain the following characters: "
                + "a–z, A–Z, 0–9, hyphen (-), underscore (_), period (.), exclamation mark (!), and parentheses (()).\n"
                + "The following names are invalid:\n"
                + "\n".join(invalid_dirs),
            )
        return local_filepath_list, total_file_size_bytes

    @staticmethod
    def should_ignore_path(file_name):
        if FileUtil._path_contains_directory(file_name, FOVUS_JOB_INFO_FOLDER):
            return True
        if Util.is_unix():
            return FileUtil._is_swap_or_hidden_file_unix(file_name)
        if Util.is_windows():
            return FileUtil._is_temp_or_hidden_file_windows(file_name)
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            FileUtil.__name__,
            "Unsupported operating system. Only Windows and Unix are supported.",
        )

    @staticmethod
    def include_exclude_allows_path(file_relative_path, include_list, exclude_list):
        file_relative_path = FileUtil.windows_to_unix_path(file_relative_path)

        if include_list and not FileUtil._should_include_file(file_relative_path, include_list):
            return False
        if exclude_list and FileUtil._should_exclude_file(file_relative_path, exclude_list):
            return False
        return True

    @staticmethod
    def _should_include_file(file_name: str, include_input_list: list[str]):
        for include_input in include_input_list:
            if include_input.endswith("/"):
                include_input += "*"

            if fnmatch.fnmatch(file_name, include_input):
                return True
        return False

    @staticmethod
    def _should_exclude_file(file_name, exclude_input_list):
        for exclude_input in exclude_input_list:
            if fnmatch.fnmatch(file_name, exclude_input):
                return True
        return False

    @staticmethod
    def _path_contains_directory(filepath, directory):
        return directory in filepath.split(os.path.sep)

    @staticmethod
    def directory_contains_directory(directory_path, directory):
        return directory in os.listdir(directory_path)

    @staticmethod
    def _is_swap_or_hidden_file_unix(filepath):
        is_ds_store = os.path.basename(filepath).startswith(".DS_Store")
        is_swap = os.path.basename(filepath).endswith("~")
        return is_ds_store or is_swap

    @staticmethod
    def _is_temp_or_hidden_file_windows(filepath):  # pylint: disable=unused-argument
        return False  # TODO

    @staticmethod
    def open(filepath, mode="r", encoding=UTF8):
        if mode.startswith("r") and not FileUtil.file_exists(filepath):
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FileUtil.__name__,
                f"File does not exist: {filepath}",
            )
        if "b" in mode:
            return open(filepath, mode)  # pylint: disable=unspecified-encoding
        return open(filepath, mode, encoding=encoding)

    @staticmethod
    def file_exists(filepath):
        return os.path.exists(filepath)

    @staticmethod
    def get_s3_object_hash(s3_object):
        return s3_object["ETag"].strip('"')

    @staticmethod
    def get_file_hash(filepath):
        with FileUtil.open(filepath, "rb") as file:
            return hashlib.md5(file.read(), usedforsecurity=False).hexdigest()

    @staticmethod
    def compare_s3_hash(
        filepath: str,
        s3_object: ObjectTypeDef,
        cache_file_data: Callable[[str, ObjectTypeDef], Any],
    ) -> bool:
        s3_object_hash = FileUtil.get_s3_object_hash(s3_object)

        if len(s3_object_hash) == 32:
            return FileUtil.cache_file_data_if_equal(
                s3_object_hash, FileUtil.get_file_hash(filepath), filepath, s3_object, cache_file_data
            )

        s3_sync_upload_hash = FileUtil.get_multipart_upload_s3_hash(filepath, chunk_size=1024 * 1024 * 8)

        if FileUtil.cache_file_data_if_equal(s3_sync_upload_hash, s3_object_hash, filepath, s3_object, cache_file_data):
            return True

        client_upload_hash = FileUtil.get_multipart_upload_s3_hash(filepath, chunk_size=1024 * 1024 * 5)

        if FileUtil.cache_file_data_if_equal(client_upload_hash, s3_object_hash, filepath, s3_object, cache_file_data):
            return True

        return FileUtil.cache_file_data_if_equal(
            s3_object_hash, FileUtil.get_file_hash(filepath), filepath, s3_object, cache_file_data
        )

    @staticmethod
    def cache_file_data_if_equal(
        hash_1: str,
        hash_2: str,
        local_file_path: str,
        s3_object: ObjectTypeDef,
        cache_file_data: Callable[[str, ObjectTypeDef], Any],
    ) -> bool:
        if hash_1 == hash_2:
            cache_file_data(local_file_path, s3_object)
            return True
        return False

    @staticmethod
    def get_multipart_upload_s3_hash(filepath: str, chunk_size: int) -> str:
        md5_bytes_list: list[bytes] = []

        with FileUtil.open(filepath, "rb") as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                md5_bytes_list.append(hashlib.md5(data, usedforsecurity=False).digest())

        if len(md5_bytes_list) < 1:
            return ""

        if len(md5_bytes_list) == 1:
            return md5_bytes_list[0].hex()

        concatenated_md5_bytes = b"".join(md5_bytes_list)
        s3_md5_string = hashlib.md5(concatenated_md5_bytes, usedforsecurity=False).hexdigest()
        s3_hash = "-".join([s3_md5_string, str(len(md5_bytes_list))])

        return s3_hash

    @staticmethod
    def create_missing_directories(local_root_directory_path, directories):
        for directory in directories:
            local_directory_path = os.path.join(local_root_directory_path, directory)
            os.makedirs(local_directory_path, exist_ok=True)

    @staticmethod
    def windows_to_unix_path(path):
        if Util.is_windows():
            return path.replace("\\", "/")

        return path
