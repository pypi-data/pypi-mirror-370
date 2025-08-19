import operator
import time
from http import HTTPStatus
from math import trunc

import boto3
import requests
from botocore.config import Config as s3_config
from typing_extensions import Any, Union

from fovus.config.config import Config
from fovus.constants.benchmark_constants import (
    BENCHMARK_NAME,
    BOUNDS,
    CORRECTABLE_LIST_COMPREHENSION,
    CPU_MEM_RANGE_BOUNDS,
    CPU_RANGE_BOUNDS,
    DEFAULT_BOOLEANS_TO_VALIDATE,
    DEFAULT_LOWER_BOUNDS_TO_VALIDATE,
    DEFAULT_UPPER_BOUNDS_TO_VALIDATE,
    DEFAULT_WITHIN_BOUNDS_TO_VALIDATE,
    GPU_LOWER_BOUNDS_TO_VALIDATE,
    GPU_UPPER_BOUNDS_TO_VALIDATE,
    GPU_WITHIN_BOUNDS_TO_VALIDATE,
    HYPERTHREADING_DISABLED,
    HYPERTHREADING_ENABLED,
    INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS,
    INCORRECTABLE_LIST_COMPREHENSION,
    IS_INVALID_CORRECTABLE,
    IS_INVALID_INCORRECTABLE,
    LIST_BENCHMARKING_FIELD_BY_CREATE_JOB_REQUEST_FIELD,
)
from fovus.constants.cli_constants import (
    API_DOMAIN_NAME,
    AWS_REGION,
    COMPUTING_DEVICE,
    CPU,
    ENABLE_HYPERTHREADING,
    GPU,
    SUPPORTED_CPU_ARCHITECTURES,
)
from fovus.constants.fovus_api_constants import (
    BODY,
    ERROR_MESSAGE,
    ERROR_MESSAGE_LIST,
    GPU_RANGE,
    PAYLOAD_CONSTRAINTS,
    PAYLOAD_JOB_CONSTRAINTS,
    STATUS_CODE,
    SUPPORTED_PROCESSOR_ARCHITECTURES,
    TIMEOUT_SECONDS,
    Api,
    ApiMethod,
)
from fovus.constants.util_constants import (
    SERVER_ERROR_PREFIX,
    SUCCESS_STATUS_CODES,
    USER_ERROR_PREFIX,
)
from fovus.exception.system_exception import SystemException
from fovus.exception.user_exception import NotSignedInException, UserException
from fovus.util.file_util import FileUtil
from fovus.util.util import Util

NO_ERROR_MESSAGE = "No error message provided"
MILLISECONDS_IN_SECOND = 1000


# Only 200, 201, 202, 4XX, and 5XX status codes are returned from the API.
class FovusApiUtil:  # pylint: disable=too-few-public-methods
    @staticmethod
    def confirm_successful_response(body: Any, status_code: int, source: str) -> Any:
        if STATUS_CODE in body:
            status_code = body[STATUS_CODE]
        if status_code not in SUCCESS_STATUS_CODES:
            if status_code == HTTPStatus.UNAUTHORIZED:
                FileUtil.remove_credentials()
                raise NotSignedInException(source)
            if str(status_code).startswith(USER_ERROR_PREFIX):
                raise UserException(status_code, source, FovusApiUtil._get_error_message(body))
            if str(status_code).startswith(SERVER_ERROR_PREFIX):
                raise SystemException(status_code, source, FovusApiUtil._get_error_message(body))
        if BODY in body:
            return body[BODY]
        return body

    @staticmethod
    def _get_error_message(body: Any) -> str:
        if isinstance(body, str):
            return body
        if ERROR_MESSAGE in body:
            return body[ERROR_MESSAGE]
        if ERROR_MESSAGE_LIST in body:
            return body[ERROR_MESSAGE_LIST]
        return NO_ERROR_MESSAGE

    @staticmethod
    def generate_job_id(timestamp: str, user_id: str) -> str:
        return f"{timestamp}-{user_id}"

    @staticmethod
    def generate_timestamp() -> str:
        return str(trunc(time.time() * MILLISECONDS_IN_SECOND))

    @staticmethod
    def get_s3_info(temporary_credentials_body):
        return (
            boto3.client(
                "s3",
                aws_access_key_id=temporary_credentials_body["credentials"]["accessKeyId"],
                aws_secret_access_key=temporary_credentials_body["credentials"]["secretAccessKey"],
                aws_session_token=temporary_credentials_body["credentials"]["sessionToken"],
                region_name=(
                    temporary_credentials_body["s3Region"]
                    if "s3Region" in temporary_credentials_body
                    else Config.get(AWS_REGION)
                ),
                config=s3_config(
                    retries={"max_attempts": 10, "mode": "standard"}, max_pool_connections=100  # Increase the pool size
                ),
            ),
            temporary_credentials_body["authorizedBucket"],
            temporary_credentials_body["authorizedFolder"],
        )

    @staticmethod
    def get_software_vendor(software_map, software_name):
        for vendor in software_map.keys():
            if software_name in software_map[vendor]:
                return vendor
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            FovusApiUtil.__name__,
            f"Software {software_name} not found in list of available software, unable to retrieve version.",
        )

    @staticmethod
    def should_fill_vendor_name(monolithic_list_item):
        return monolithic_list_item.get("softwareName") and not monolithic_list_item.get("vendorName")

    @staticmethod
    def get_benchmark_validations_config(request):
        lower_bounds_to_validate = DEFAULT_LOWER_BOUNDS_TO_VALIDATE
        upper_bounds_to_validate = DEFAULT_UPPER_BOUNDS_TO_VALIDATE
        within_bounds_to_validate = DEFAULT_WITHIN_BOUNDS_TO_VALIDATE
        boolean_values_to_validate = DEFAULT_BOOLEANS_TO_VALIDATE
        if request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE] == GPU:
            lower_bounds_to_validate.extend(GPU_LOWER_BOUNDS_TO_VALIDATE)
            upper_bounds_to_validate.extend(GPU_UPPER_BOUNDS_TO_VALIDATE)
            within_bounds_to_validate.extend(GPU_WITHIN_BOUNDS_TO_VALIDATE)

        # Correctable bounds must be single values, not lists (see constants).
        return {
            "Minimum": {
                BOUNDS: lower_bounds_to_validate,
                IS_INVALID_CORRECTABLE: operator.lt,
                CORRECTABLE_LIST_COMPREHENSION: min,
                IS_INVALID_INCORRECTABLE: operator.gt,
                INCORRECTABLE_LIST_COMPREHENSION: max,
                INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS: FovusApiUtil._allowed_range_by_hyperthreading_enabled_message,
            },
            "Maximum": {
                BOUNDS: upper_bounds_to_validate,
                IS_INVALID_CORRECTABLE: operator.gt,
                CORRECTABLE_LIST_COMPREHENSION: max,
                IS_INVALID_INCORRECTABLE: operator.lt,
                INCORRECTABLE_LIST_COMPREHENSION: min,
                INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS: FovusApiUtil._allowed_range_by_hyperthreading_enabled_message,
            },
            "InVCpu": {
                BOUNDS: within_bounds_to_validate,
                IS_INVALID_INCORRECTABLE: lambda current_value, benchmarking_profile_item_bound: set(
                    benchmarking_profile_item_bound
                ).isdisjoint(range(current_value[0], current_value[1] + 1)),
                INCORRECTABLE_LIST_COMPREHENSION: lambda x: x,
                INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS: lambda keys, supported_values, hyperthreading_enabled: (
                    "The "
                    f"provided range defined by {Util.get_message_from_list(keys)} must contain at least one of the "
                    f"supported values {FovusApiUtil._when_hyperthreading_enabled_message(hyperthreading_enabled)}: "
                    f"{supported_values}."
                ),
            },
            "Boolean": {
                BOUNDS: boolean_values_to_validate,
                IS_INVALID_CORRECTABLE: operator.ne,
                CORRECTABLE_LIST_COMPREHENSION: lambda x: x,
            },
        }

    @staticmethod
    def _allowed_range_by_hyperthreading_enabled_message(keys, supported_values, _hyperthreading_enabled):
        return (
            f"Allowed range for {Util.get_message_from_list(keys)}: [{min(supported_values)}, {max(supported_values)}]."
        )

    @staticmethod
    def _when_hyperthreading_enabled_message(hyperthreading_enabled):
        return f"when hyperthreading is {'enabled' if hyperthreading_enabled else 'disabled'}"

    @staticmethod
    def get_benchmark_profile_bounds(
        benchmarking_profile_item,
        bound_to_validate,
        request,
        source: str,
    ) -> Union[list[int], list[bool]]:
        computing_device = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE]
        computing_devices = ["cpu", "gpu"] if computing_device == GPU else ["cpu"]
        supported_cpu_architectures = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][SUPPORTED_CPU_ARCHITECTURES]
        hyperthreading_enabled = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ENABLE_HYPERTHREADING]

        # May be list of valid values, dict with "Min" and "Max" keys, or boolean value.
        benchmarking_profile_bounds = benchmarking_profile_item[
            LIST_BENCHMARKING_FIELD_BY_CREATE_JOB_REQUEST_FIELD[bound_to_validate]
        ]
        if bound_to_validate in CPU_MEM_RANGE_BOUNDS:
            min_mem: int
            max_mem: int

            architecture_found = False
            for cpu_architecture in supported_cpu_architectures:
                for current_computing_device in computing_devices:
                    architecture = current_computing_device + "-" + cpu_architecture

                    if architecture not in benchmarking_profile_bounds:
                        continue

                    try:
                        min_mem = min(min_mem, benchmarking_profile_bounds[architecture]["min"])
                        max_mem = max(max_mem, benchmarking_profile_bounds[architecture]["max"])
                    except NameError:
                        min_mem = benchmarking_profile_bounds[architecture]["min"]
                        max_mem = benchmarking_profile_bounds[architecture]["max"]
                    architecture_found = True

            if not architecture_found:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    source,
                    f"{SUPPORTED_CPU_ARCHITECTURES} {supported_cpu_architectures} is invalid for benchmarking profile "
                    + f"{benchmarking_profile_item['benchmarkName']}",
                )

            return [min_mem, max_mem]

        if bound_to_validate in CPU_RANGE_BOUNDS:
            new_bounds: list[int] = []

            architecture_found = False
            for cpu_architecture in supported_cpu_architectures:
                for current_computing_device in computing_devices:
                    architecture = current_computing_device + "-" + cpu_architecture

                    if architecture not in benchmarking_profile_bounds:
                        continue

                    new_bounds.extend(
                        benchmarking_profile_bounds[architecture][
                            HYPERTHREADING_ENABLED if hyperthreading_enabled else HYPERTHREADING_DISABLED
                        ]
                    )
                    architecture_found = True

            if not architecture_found:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    source,
                    f"{SUPPORTED_CPU_ARCHITECTURES} {supported_cpu_architectures} is invalid for benchmarking profile "
                    + f"{benchmarking_profile_item['benchmarkName']}",
                )

            return new_bounds

        if isinstance(benchmarking_profile_bounds, dict):
            return list(benchmarking_profile_bounds.values())

        return benchmarking_profile_bounds

    @staticmethod
    def get_benchmark_bound_scaler(enable_hyperthreading, bp_hyperthreading):
        bound_scaler = 1
        if enable_hyperthreading and bp_hyperthreading:
            bound_scaler = 1
        if not enable_hyperthreading and bp_hyperthreading:
            bound_scaler = 0.5
        if enable_hyperthreading and not bp_hyperthreading:
            bound_scaler = 2
        if not enable_hyperthreading and not bp_hyperthreading:
            bound_scaler = 1
        return bound_scaler

    @staticmethod
    def print_benchmark_hyperthreading_info(enable_hyperthreading):
        enable_hyperthreading_print = "disabled"
        threads_per_cpu_message = "1 thread (vCPU) per core can be used on all CPUs."
        if enable_hyperthreading:
            enable_hyperthreading_print = "enabled"
            threads_per_cpu_message = "2 threads (vCPU) per core can be used on CPUs that support hyperthreading."
        print(f"Hyperthreading is {enable_hyperthreading_print}. {threads_per_cpu_message}")

    # pylint: disable=too-many-positional-arguments
    @staticmethod
    def get_corrected_value_message(
        validation_type,
        benchmarking_profile_name,
        bound_to_validate,
        benchmarking_profile_item_bound,
        hyperthreading_enabled,
        current_value,
    ):
        message = (
            f"{validation_type} value allowed by '{benchmarking_profile_name}' for "
            f"{bound_to_validate} is {benchmarking_profile_item_bound}"
        )
        if bound_to_validate in CPU_RANGE_BOUNDS:
            hyperthreading_enabled_print = "enabled" if hyperthreading_enabled else "disabled"
            message += f" given that hyperthreading is {hyperthreading_enabled_print}"
        message += f". Overriding current value of {current_value} with {benchmarking_profile_item_bound}."
        return message

    @staticmethod
    def validate_computing_device(input_computing_device, benchmarking_profile_item):
        computing_device_should_be = ""
        if (
            GPU_RANGE not in benchmarking_profile_item or not benchmarking_profile_item[GPU_RANGE]
        ) and input_computing_device == GPU:
            computing_device_should_be = CPU
        if (
            GPU_RANGE in benchmarking_profile_item and benchmarking_profile_item[GPU_RANGE]
        ) and input_computing_device == CPU:
            computing_device_should_be = GPU

        if computing_device_should_be:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FovusApiUtil.__name__,
                f"Invalid value for {COMPUTING_DEVICE}. "
                + FovusApiUtil.get_formatted_benchmark_supported_message(
                    benchmarking_profile_item[BENCHMARK_NAME], "computing devices", [computing_device_should_be]
                ),
            )

    @staticmethod
    def validate_cpu_architectures(input_cpu_architectures, benchmarking_profile_item):
        supported_architectures = []
        valid_input_cpu_architectures = []
        for supported_computing_device_and_architecture in benchmarking_profile_item[SUPPORTED_PROCESSOR_ARCHITECTURES]:
            supported_architecture = supported_computing_device_and_architecture.split("-", maxsplit=1)[1]
            supported_architectures.append(supported_architecture)
            if supported_architecture in input_cpu_architectures:
                valid_input_cpu_architectures.append(supported_architecture)

        if valid_input_cpu_architectures:
            if len(valid_input_cpu_architectures) < len(input_cpu_architectures):
                print(
                    f"Create job request contains values for {SUPPORTED_CPU_ARCHITECTURES} not supported by the "
                    f"benchmarking profile {benchmarking_profile_item[BENCHMARK_NAME]}. "
                    "\n\t- "
                    + FovusApiUtil.get_formatted_benchmark_supported_message(
                        benchmarking_profile_item[BENCHMARK_NAME], "CPU architectures", supported_architectures
                    )
                    + "\n\t- The following request values have been removed: "
                    f"{list(set(input_cpu_architectures) - set(valid_input_cpu_architectures))}"
                )
            return

        raise UserException(
            HTTPStatus.BAD_REQUEST,
            FovusApiUtil.__name__,
            f"Invalid value of {SUPPORTED_CPU_ARCHITECTURES}. "
            + FovusApiUtil.get_formatted_benchmark_supported_message(
                benchmarking_profile_item[BENCHMARK_NAME], "CPU architectures", supported_architectures
            ),
        )

    @staticmethod
    def get_license_consuption_profile_list(license_consumption_profiles):
        profile_list = []
        for feature_map in license_consumption_profiles.values():
            for profiles in feature_map.values():
                profile_list.extend(profiles)
        return profile_list

    @staticmethod
    def get_formatted_benchmark_supported_message(benchmark_name, field_readable, supported_values: tuple):
        return (
            f"The benchmarking profile '{benchmark_name}' only supports the "
            f"following {field_readable}: {supported_values}."
        )

    @staticmethod
    def get_api_address(api: Api, api_method: ApiMethod):
        return "/".join((Config.get(API_DOMAIN_NAME), api.value, api_method.value))

    @staticmethod
    def get_software_license_relationship(
        software_license_relationships, vendor_name, license_id, software_name=None
    ) -> dict:
        for item in software_license_relationships:
            if (
                item["licenseId"] == license_id
                and item["vendorName"] == vendor_name
                and (software_name is None or item["softwareName"] == software_name)
            ):
                return item
        return {}

    @staticmethod
    def get_valid_licenses(license_list) -> list:
        valid_licenses = []
        for license_info in license_list:
            valid_licenses.append(
                {
                    "licenseName": license_info["licenseName"],
                    "licenseAddress": FovusApiUtil.get_license_address(
                        license_info.get("licensePort"),
                        license_info.get("licenseIp"),
                        None,
                        license_info.get("ansysWebLicensingGroupId"),
                    ),
                }
            )
        return valid_licenses

    @staticmethod
    def get_license_address(
        license_port=None,
        license_ip=None,
        license_id=None,
        group_id=None,
    ) -> str:
        if group_id:
            return f"{group_id}-{license_ip}"
        if not license_port and license_ip:
            return license_ip
        if license_port and not license_ip:
            return license_port
        if license_id:
            return f"{license_id}@{license_port}@{license_ip}"
        return f"{license_port}@{license_ip}"

    @staticmethod
    def get_registered_software(software_license_relationships, vendor_name, license_id) -> list:
        registered_software = []
        for item in software_license_relationships:
            if item["licenseId"] == license_id and item["vendorName"] == vendor_name:
                registered_software.append(item["softwareName"])
        return registered_software

    @staticmethod
    def get_registered_vendors(software_license_relationships, license_id) -> list:
        registered_vendors = []
        for item in software_license_relationships:
            if item["licenseId"] == license_id:
                registered_vendors.append(item["vendorName"])
        return registered_vendors

    @staticmethod
    def step_up_session(headers: dict, request, source: str) -> None:
        response = requests.post(
            FovusApiUtil.get_api_address(Api.USER, ApiMethod.STEP_UP_SESSION),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, source)

    @staticmethod
    def print_project_names(projects):
        if len(projects) == 0:
            print("No projects available.")
            return

        print("Valid project names (sorted by creation time):")
        for project in projects:
            print(f"  {project['name']}")

        print("  None")
