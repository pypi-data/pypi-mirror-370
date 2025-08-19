from mypy_boto3_s3.type_defs import ObjectTypeDef

from fovus.constants.util_constants import SERVER_ERROR_PREFIX, SUCCESS_STATUS_CODES
from fovus.exception.system_exception import SystemException
from fovus.exception.user_exception import UserException
from fovus.util.file_util import FileUtil


class AwsUtil:
    @staticmethod
    def confirm_successful_response(response, source):
        response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if response_status_code not in SUCCESS_STATUS_CODES:
            if str(response_status_code).startswith(SERVER_ERROR_PREFIX):
                raise SystemException(response_status_code, source)
            raise UserException(response_status_code, source)

    @staticmethod
    def handle_client_error(error, source):
        response_status_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
        if error.response["Error"]["Code"] == "InternalError":
            raise SystemException(response_status_code, error, source)
        raise UserException(response_status_code, error, source)

    @staticmethod
    def is_expired_token_error(error):
        return "ExpiredToken" in str(error)

    @staticmethod
    def get_s3_object_list_info(s3_object_list: list[ObjectTypeDef], s3_prefix: str, include_list, exclude_list):
        objects_to_download = []
        total_size_bytes = 0
        tasks = set()
        for s3_object in s3_object_list:
            object_path = AwsUtil.get_s3_object_key_without_prefix(s3_object, s3_prefix)
            if FileUtil.should_ignore_path(object_path) or not FileUtil.include_exclude_allows_path(
                object_path, include_list, exclude_list
            ):
                continue
            total_size_bytes += s3_object["Size"]
            objects_to_download.append(s3_object)
            if len(object_path.split("/")) > 1:
                tasks.add(object_path.split("/")[0])
        return objects_to_download, total_size_bytes, len(tasks)

    @staticmethod
    def _update_task_count(job_count, s3_object, s3_prefix):
        object_path = AwsUtil.get_s3_object_key_without_prefix(s3_object, s3_prefix)

        object_path_list = object_path.split("/")
        if len(object_path_list) > 1:
            job_count.add(object_path_list[0])

    @staticmethod
    def get_all_directories(objects_list, prefix, include_list, exclude_list):
        directories = set()
        for s3_object in objects_list:
            object_path = AwsUtil.get_s3_object_key_without_prefix(s3_object, prefix)
            if FileUtil.should_ignore_path(object_path) or not FileUtil.include_exclude_allows_path(
                object_path, include_list, exclude_list
            ):
                continue
            path = AwsUtil.get_s3_object_key_without_prefix(s3_object, prefix).split("/")[:-1]
            directories.add("/".join(path))
        for directory in directories.copy():
            for i in range(len(directory.split("/"))):
                directories.add("/".join(directory.split("/")[:i]))
        return directories

    @staticmethod
    def s3_object_is_directory(s3_object):
        return s3_object["Key"].endswith("/")

    @staticmethod
    def get_s3_object_hash(s3_object):
        return s3_object["ETag"].strip('"')

    @staticmethod
    def get_s3_object_key_without_prefix(s3_object, prefix):
        start_idex = len(prefix) if prefix.endswith("/") else len(prefix) + 1
        return s3_object["Key"][start_idex:]
