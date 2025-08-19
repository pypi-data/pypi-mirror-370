# pylint: disable=too-many-lines
import copy
import io
import json
import logging
import os
import shlex
import time
from enum import Enum
from functools import lru_cache
from http import HTTPStatus
from operator import itemgetter

import dateparser
import paramiko  # type: ignore
import requests
from typing_extensions import Dict, Optional, Tuple, TypedDict, Union

from fovus.adapter.fovus_cognito_adapter import FovusCognitoAdapter
from fovus.constants.benchmark_constants import (
    BENCHMARK_NAME,
    BOUNDS,
    COMPARISONS,
    COMPREHENSIONS,
    INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS,
    IS_INVALID_CORRECTABLE,
)
from fovus.constants.cli_constants import (
    ALLOW_PREEMPTIBLE,
    BENCHMARKING_PROFILE_NAME,
    COMPUTING_DEVICE,
    CPU,
    DEBUG_MODE,
    DOCKER_HUB_PASSWORD,
    DOCKER_HUB_USERNAME,
    ENABLE_HYPERTHREADING,
    FOVUS_PROVIDED_CONFIGS,
    GPU,
    IS_RESUMABLE_WORKLOAD,
    IS_SEARCH_OUTPUT_KEYWORDS_ENABLED,
    IS_SINGLE_THREADED_TASK,
    JOB_CONFIG_CONTAINERIZED_TEMPLATE,
    JOB_ID,
    JOB_NAME,
    KEYWORD_SEARCH_INPUT,
    MAX_GPU,
    MAX_VCPU,
    MIN_GPU,
    MIN_GPU_MEM_GIB,
    MIN_VCPU,
    MONOLITHIC_OVERRIDE,
    PATH_TO_CONFIG_FILE_IN_REPO,
    SCALABLE_PARALLELISM,
    SCHEDULED_AT,
    SEARCH_OUTPUT_FILES,
    SEARCH_OUTPUT_KEYWORDS,
    SUPPORTED_CPU_ARCHITECTURES,
    TIMESTAMP,
    WALLTIME_HOURS,
)
from fovus.constants.fovus_api_constants import (
    ALLOW_WORKLOAD_MANAGEMENT,
    ANSYS_PERSONAL_ACCESS_TOKEN,
    BOUND_VALUE_CORRECTION_PRINT_ORDER,
    CONTAINERIZED,
    DEFAULT_TIMEZONE,
    ENVIRONMENT,
    HAS_WORKLOAD_MANAGER,
    IS_LICENSE_REQUIRED,
    JOB_STATUS,
    LICENSE_ADDRESS,
    LICENSE_CONSUMPTION_PROFILE_NAME,
    LICENSE_COUNT_PER_TASK,
    LICENSE_FEATURE,
    LICENSE_NAME,
    MONOLITHIC_LIST,
    PAYLOAD_AUTO_DELETE_DAYS,
    PAYLOAD_CONSTRAINTS,
    PAYLOAD_DEBUG_MODE,
    PAYLOAD_JOB_CONSTRAINTS,
    PAYLOAD_JOB_NAME,
    PAYLOAD_TASK_CONSTRAINTS,
    PAYLOAD_TIMESTAMP,
    PAYLOAD_WORKSPACE_ID,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    SOFTWARE_VERSIONS,
    TIMEOUT_SECONDS,
    VENDOR_NAME,
    Api,
    ApiMethod,
)
from fovus.exception.user_exception import NotSignedInException, UserException
from fovus.root_config import ROOT_DIR
from fovus.util.file_util import FileUtil
from fovus.util.fovus_api_util import FovusApiUtil
from fovus.util.util import Util


class AwsCognitoAuthType(Enum):
    USER_SRP_AUTH = "USER_SRP_AUTH"  # nosec


class UserAttribute(Enum):
    USER_ID = "custom:userId"


class UserInfo(TypedDict):
    email: str
    user_id: str
    workspace_name: str
    workspace_id: str


class FovusApiAdapter:
    user_id: str
    workspace_id: str
    fovus_cognito_adapter: FovusCognitoAdapter

    def __init__(self, fovus_cognito_adapter: Union[FovusCognitoAdapter, None] = None):
        if fovus_cognito_adapter is None:
            self.fovus_cognito_adapter = FovusCognitoAdapter()
        else:
            self.fovus_cognito_adapter = fovus_cognito_adapter

        self.user_id = self._get_user_id()
        self.workspace_id = self._get_workspace_id()

    def create_job(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        # replace ' with FOVUS_SINGLE_QUOTE to avoid JSON parsing error
        request["workload"]["runCommand"] = request["workload"]["runCommand"].replace("'", "FOVUS_SINGLE_QUOTE")
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.CREATE_JOB),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def create_zombie_job_check_scheduler(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.CREATE_ZOMBIE_JOB_CHECK_SCHEDULER),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_user_info(self) -> UserInfo:
        workspace = self.get_workspace()
        claims = self.fovus_cognito_adapter.get_claims()

        return {
            "email": claims["email"],
            "user_id": self.user_id,
            "workspace_name": workspace["name"],
            "workspace_id": self.workspace_id,
        }

    def print_user_info(self, title: Union[str, None] = None) -> UserInfo:
        user_info = self.get_user_info()
        print("------------------------------------------------")

        if title is not None:
            print(f"  {title}", "", sep="\n")

        print(
            "  User information:",
            "",
            f"  Email: {user_info['email']}",
            f"  User ID: {user_info['user_id']}",
            f"  Workspace Name: {user_info['workspace_name']}",
            f"  Workspace ID: {user_info['workspace_id']}",
            "------------------------------------------------",
            sep="\n",
        )
        return user_info

    def make_dynamic_changes_to_create_job_request(self, request):
        self._make_dynamic_changes_to_software(request)
        self._validate_container_info(request)
        self._validate_software_manager(request)
        self._validate_license_info(request)
        self._validate_benchmarking_profile(request)
        self._convert_scheduled_at_format(request)
        self._validate_scalable_parallelism(request)
        self._confirm_enable_preemptible_support(request)
        self._validate_keyword_search_input(request)

    def is_workload_manager_used(self, request):
        if MONOLITHIC_LIST not in request[ENVIRONMENT]:
            return False

        return any([
            monolithic_list_item.get(ALLOW_WORKLOAD_MANAGEMENT, False)
            for monolithic_list_item in request[ENVIRONMENT][MONOLITHIC_LIST]
        ])

    def _validate_software_manager(self, request):
        if MONOLITHIC_LIST not in request[ENVIRONMENT]:
            return

        # When a workload manager is used, only one software is allowed
        all_software_used = {item[SOFTWARE_NAME] for item in request[ENVIRONMENT][MONOLITHIC_LIST]}
        is_workload_manager_used = self.is_workload_manager_used(request)

        if not is_workload_manager_used:
            return

        if len(all_software_used) > 1:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "When workload management is enabled, the job must include only one selected software.",
            )

        is_workload_management_partially_enabled = any(
            monolithic_list_item.get(ALLOW_WORKLOAD_MANAGEMENT, None) == False
            for monolithic_list_item in request[ENVIRONMENT][MONOLITHIC_LIST]
        )

        if is_workload_management_partially_enabled:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Workload management cannot be partially disabled for some license features. To disable workload"
                " management, please set 'allowWorkloadManagement' to false explicitly for all license features in"
                " the job config file.",
            )

    def _validate_keyword_search_input(self, request: Dict):
        keyword_search_input = request.get(KEYWORD_SEARCH_INPUT)

        if keyword_search_input is None:
            request[IS_SEARCH_OUTPUT_KEYWORDS_ENABLED] = False
            return

        search_keywords = keyword_search_input.get(SEARCH_OUTPUT_KEYWORDS)
        search_files = keyword_search_input.get(SEARCH_OUTPUT_FILES)

        if not search_keywords and not search_files:
            request[IS_SEARCH_OUTPUT_KEYWORDS_ENABLED] = False
            request.pop(KEYWORD_SEARCH_INPUT)
            return

        if not search_keywords or not search_files:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Invalid input for keyword search."
                + " At least one keyword and file must be provided for keyword search.",
            )

        request[IS_SEARCH_OUTPUT_KEYWORDS_ENABLED] = True

    def _confirm_enable_preemptible_support(self, request):
        max_walltime_allowed = 3
        max_walltime_allowed_for_resumable_workload = 7 * 24  # 7 days
        if ALLOW_PREEMPTIBLE not in request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS]:
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ALLOW_PREEMPTIBLE] = False
            print("Autofilling 'allowPreemptible' with default value of False.")
        if IS_RESUMABLE_WORKLOAD not in request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS]:
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][IS_RESUMABLE_WORKLOAD] = False
            print("Autofilling 'isResumableWorkload' with default value of False.")
        if request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ALLOW_PREEMPTIBLE]:
            if Util.confirm_action(
                message="Enabling preemptible resources will restrict the maximum task Walltime allowed to "
                + f"{max_walltime_allowed_for_resumable_workload} hours if the workload under "
                + f"submission is resumable, otherwise, {max_walltime_allowed} hours if not "
                + "resumable. Preemptible resources are subject to reclaim by "
                + "cloud service providers, resulting in the possibility of "
                + "interruption to task run. Enabling preemptible resources will allow cloud strategy optimization to "
                + "estimate, based on the interruption probability, the expected cost saving that can be statistically "
                + "achieved by leveraging preemptible resources. In case the expected saving is meaningful,  "
                + "preemptible resources will be prioritized for use during the infrastructure provisioning. "
                + "Any interrupted tasks due to the reclaim of preemptible resources will be re-queued for "
                + "re-execution to ensure job completion. PLEASE NOTE that the expected cost saving is estimated "
                + "in the statistical sense. So there is a chance that such savings may not be realized at the "
                + "individual task or job level.\n\nAre you sure you want to allow preemptible resources?",
            ):
                request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ALLOW_PREEMPTIBLE] = True
                is_resumable_workload = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][IS_RESUMABLE_WORKLOAD]
                max_walltime = (
                    max_walltime_allowed_for_resumable_workload
                    if is_resumable_workload is True
                    else max_walltime_allowed
                )
                print("Preemptible resources are allowed")
                if request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][WALLTIME_HOURS] > max_walltime:
                    raise UserException(
                        HTTPStatus.BAD_REQUEST,
                        self.__class__.__name__,
                        f"When allowing preemptible resources, Walltime must be <= {max_walltime} hours "
                        + f"if resumable workload is {is_resumable_workload}.",
                    )
            else:
                request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ALLOW_PREEMPTIBLE] = False
                request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][IS_RESUMABLE_WORKLOAD] = False
                print("Preemptible resources are not allowed")

    def _validate_container_info(self, request: Dict):
        # Validation for containerized jobs: check if image path is empty
        if CONTAINERIZED in request[ENVIRONMENT]:
            image_path = request[ENVIRONMENT][CONTAINERIZED]["imagePath"]
            if not image_path or (isinstance(image_path, str) and image_path.strip() == ""):
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    "Containerized job requires a non-empty image path. "
                    + "Please provide a valid image path in the job configuration.",
                )
            # Check if dockerHubUsername is present, then dockerHubPassword must also be present
            docker_hub_username = request[ENVIRONMENT][CONTAINERIZED].get("dockerHubUsername", "")
            docker_hub_password = request[ENVIRONMENT][CONTAINERIZED].get("dockerHubPassword", "")
            if docker_hub_username and not docker_hub_password:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    "If 'dockerHubUsername' is provided, 'dockerHubPassword' must also be provided "
                    + "in the job configuration.",
                )

    def _validate_license_info(self, request):
        print("Validating license...")

        if MONOLITHIC_LIST not in request[ENVIRONMENT]:
            Util.print_message_with_color(
                "Request is for a containerized job. Filling missing/empty vendorName fields is not required.", "blue"
            )
            self._ensure_is_single_threaded_task_filled(request)
            return

        list_software_response = self.list_software()
        license_list = self.list_licenses(request[PAYLOAD_WORKSPACE_ID])
        software_license_relationships = self.list_software_license_relationships(request[PAYLOAD_WORKSPACE_ID])

        for _, monolithic_list_item in enumerate(copy.deepcopy(request[ENVIRONMENT][MONOLITHIC_LIST])):
            software_name = monolithic_list_item[SOFTWARE_NAME]
            vendor_name = monolithic_list_item[VENDOR_NAME]
            feature_name = monolithic_list_item[LICENSE_FEATURE]

            software = list_software_response.get(vendor_name, {}).get(software_name, {})
            if not software.get(IS_LICENSE_REQUIRED, False):
                continue

            if LICENSE_ADDRESS not in monolithic_list_item and LICENSE_NAME not in monolithic_list_item:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    f"licenseAddress or licenseName must be present for the software '{software_name}'.",
                )

            is_license_valid = False
            for license_info in license_list:
                if (
                    LICENSE_ADDRESS in monolithic_list_item
                    and monolithic_list_item[LICENSE_ADDRESS]
                    == FovusApiUtil.get_license_address(
                        license_info.get("licensePort"),
                        license_info.get("licenseIp"),
                        None,
                        license_info.get("ansysWebLicensingGroupId"),
                    )
                ) or (
                    LICENSE_NAME in monolithic_list_item
                    and monolithic_list_item[LICENSE_NAME] == license_info["licenseName"]
                ):
                    # check for personal auth token
                    if (
                        "licenseManagerType" in license_info
                        and license_info["licenseManagerType"] == "ANSYS_WEB_LICENSING"
                        and ANSYS_PERSONAL_ACCESS_TOKEN not in monolithic_list_item
                    ):
                        raise UserException(
                            HTTPStatus.BAD_REQUEST,
                            self.__class__.__name__,
                            f"ansysPersonalAccessToken must be present for the license '{license_info['licenseName']}'",
                        )

                    # check for vendor
                    license_relation_from_vendor = FovusApiUtil.get_software_license_relationship(
                        software_license_relationships, vendor_name, license_info["licenseId"]
                    )
                    if len(license_relation_from_vendor) == 0:
                        registered_vendor = FovusApiUtil.get_registered_vendors(
                            software_license_relationships, license_info["licenseId"]
                        )
                        raise UserException(
                            HTTPStatus.BAD_REQUEST,
                            self.__class__.__name__,
                            f"Vendor {vendor_name} is not registered with the"
                            + f" license name '{license_info['licenseName']}'."
                            + f" Registered vendors: {registered_vendor}"
                            + " Follow this link to register: "
                            + f"https://app.fovus.co/licenses/{license_info['licenseId']}",
                        )

                    # check for software
                    license_relation_from_software = FovusApiUtil.get_software_license_relationship(
                        software_license_relationships, vendor_name, license_info["licenseId"], software_name
                    )
                    if len(license_relation_from_software) == 0:
                        registered_software = FovusApiUtil.get_registered_software(
                            software_license_relationships, vendor_name, license_info["licenseId"]
                        )
                        raise UserException(
                            HTTPStatus.BAD_REQUEST,
                            self.__class__.__name__,
                            f"Software {software_name} is not registered "
                            + f"with the license name '{license_info['licenseName']}'."
                            + f" Registered softwares: {registered_software}"
                            + " Follow this link to register: "
                            + f"https://app.fovus.co/licenses/{license_info['licenseId']}",
                        )
                    license_features = license_relation_from_software["licenseFeatures"]

                    if (
                        "supportedVersions" in license_relation_from_software
                        and monolithic_list_item[SOFTWARE_VERSION]
                        not in license_relation_from_software["supportedVersions"]
                    ):
                        raise UserException(
                            HTTPStatus.BAD_REQUEST,
                            self.__class__.__name__,
                            f"Software version '{monolithic_list_item[SOFTWARE_VERSION]}' for license name "
                            + f"""'{license_info["licenseName"]}' is not valid. """
                            + "Valid software versions: "
                            + str(license_relation_from_software["supportedVersions"]),
                        )

                    # check for license feature
                    if feature_name not in license_features:
                        raise UserException(
                            HTTPStatus.BAD_REQUEST,
                            self.__class__.__name__,
                            f"feature {feature_name} is not registered with the license name"
                            + f" '{license_info['licenseName']}' and software '{software_name}'."
                            + f" Registered features: {str(license_features)}."
                            f" Follow this link to register: https://app.fovus.co/licenses/{license_info['licenseId']}",
                        )
                    is_license_valid = True
                    break

            if not is_license_valid:
                if LICENSE_ADDRESS in monolithic_list_item:
                    raise UserException(
                        HTTPStatus.BAD_REQUEST,
                        self.__class__.__name__,
                        f"The licenseAddress '{monolithic_list_item[LICENSE_ADDRESS]}' is not registered "
                        + "in your workspace. Only the licenses that have been registered in "
                        + "your workspace can be used for job submission."
                        + f" Registered licenses include: {str(FovusApiUtil.get_valid_licenses(license_list))}."
                        + "Administrators can register new licenses at https://app.fovus.co/licenses",
                    )
                if LICENSE_NAME in monolithic_list_item:
                    raise UserException(
                        HTTPStatus.BAD_REQUEST,
                        self.__class__.__name__,
                        f"The licenseName '{monolithic_list_item[LICENSE_NAME]}' is not registered "
                        + "in your workspace. Only the licenses that have been registered in"
                        + " your workspace can be used for job submission."
                        + f" Registered licenses include: {str(FovusApiUtil.get_valid_licenses(license_list))}."
                        + "Administrators can register new licenses at https://app.fovus.co/licenses",
                    )

    def _validate_scalable_parallelism(self, request):
        scalable_parallelism = request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][SCALABLE_PARALLELISM]
        min_vcpu = request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MIN_VCPU]
        max_vcpu = request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_VCPU]
        min_gpu = request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MIN_GPU]
        max_gpu = request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_GPU]
        benchmark_profile_name = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][BENCHMARKING_PROFILE_NAME]
        computing_device = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE]

        if computing_device == CPU and not scalable_parallelism and min_vcpu != max_vcpu:
            Util.print_message_with_color(
                f"Scalable parallelism is false for Benchmarking profile '{benchmark_profile_name}'. The value of "
                + "maxvCpu must be equal to that of minvCpu to define a user-specified parallelism. Overriding "
                + f"maxvCpu ({max_vcpu}) with minvCpu ({min_vcpu}).",
                "blue",
            )
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_VCPU] = min_vcpu

        if computing_device == GPU and not scalable_parallelism and min_gpu != max_gpu:
            Util.print_message_with_color(
                f"Scalable parallelism is false for Benchmarking profile '{benchmark_profile_name}'. The value of "
                + "maxGpu must be equal to that of minGpu to define a user-specified parallelism. Overriding maxGpu "
                + f"({max_gpu}) with minGpu ({min_gpu}).",
                "blue",
            )
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_GPU] = min_gpu

    def _ensure_is_single_threaded_task_filled(self, request):
        if (
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE] == CPU
            and IS_SINGLE_THREADED_TASK not in request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS]
        ):
            Util.print_message_with_color(
                f"Field '{IS_SINGLE_THREADED_TASK}' is now required in '{PAYLOAD_TASK_CONSTRAINTS}' for create job "
                f"requests where '{COMPUTING_DEVICE}' is '{CPU}' and one of the following is true:"
                f"\n\t- Job environment is '{CONTAINERIZED}'"
                f"\n\t- Job environment is monolithic and any software in '{MONOLITHIC_LIST}' "
                "does not require a license."
                f"\nAutofilling '{IS_SINGLE_THREADED_TASK}' with default value of False.",
                "blue",
            )
            request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][IS_SINGLE_THREADED_TASK] = False

    def _make_dynamic_changes_to_software(self, request):
        print("Validating software...")
        if MONOLITHIC_LIST not in request[ENVIRONMENT]:
            Util.print_message_with_color(
                "Request is for a containerized job. Filling missing/empty vendorName fields is not required.", "blue"
            )
            self._ensure_is_single_threaded_task_filled(request)
            return

        license_consumption_profiles = self.get_license_consumption_profiles(request[PAYLOAD_WORKSPACE_ID])
        list_software_response = self.list_software()

        for i, monolithic_list_item in enumerate(copy.deepcopy(request[ENVIRONMENT][MONOLITHIC_LIST])):
            software_name = monolithic_list_item[SOFTWARE_NAME]
            software_version = monolithic_list_item[SOFTWARE_VERSION]
            software_vendor = monolithic_list_item[VENDOR_NAME]
            allow_workload_management = monolithic_list_item.get(ALLOW_WORKLOAD_MANAGEMENT, None)

            valid_software_names = []
            is_valid_software_name = False
            for valid_software_vendor in list_software_response:
                if software_name in list_software_response[valid_software_vendor]:
                    is_valid_software_name = True
                    if (
                        software_version
                        in list_software_response[valid_software_vendor][software_name][SOFTWARE_VERSIONS]
                    ):
                        software_supported_architectures = list_software_response[valid_software_vendor][software_name][
                            SOFTWARE_VERSIONS
                        ][software_version]
                        for architecture in request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][
                            SUPPORTED_CPU_ARCHITECTURES
                        ]:
                            if architecture not in software_supported_architectures:
                                raise UserException(
                                    HTTPStatus.BAD_REQUEST,
                                    self.__class__.__name__,
                                    "Supported Cpu architectures '"
                                    + request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][SUPPORTED_CPU_ARCHITECTURES]
                                    + f"' for software name '{software_name}' and version '{software_version}' is not "
                                    + f"valid. Valid Supported Cpu architectures for version '{software_version}' : "
                                    + str(software_supported_architectures),
                                )

                        if valid_software_vendor != software_vendor:
                            print(
                                f"Replacing vendor name '{software_vendor}' with "
                                f"'{valid_software_vendor}' for monolithic list item {monolithic_list_item}."
                            )
                            request[ENVIRONMENT][MONOLITHIC_LIST][i][VENDOR_NAME] = valid_software_vendor
                        if list_software_response[valid_software_vendor][software_name][IS_LICENSE_REQUIRED]:
                            if IS_SINGLE_THREADED_TASK not in request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS]:
                                request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][IS_SINGLE_THREADED_TASK] = False
                            self._confirm_required_fields_for_licensed_software(
                                monolithic_list_item, license_consumption_profiles
                            )

                        has_workload_manager = list_software_response[valid_software_vendor][software_name].get(
                            HAS_WORKLOAD_MANAGER, False
                        )
                        if allow_workload_management and not has_workload_manager:
                            print(
                                f"Software '{software_name}' from vendor '{valid_software_vendor}' does not support"
                                f" Workload Manager. Disabling workload manager for {monolithic_list_item}."
                            )
                            request[ENVIRONMENT][MONOLITHIC_LIST][i][ALLOW_WORKLOAD_MANAGEMENT] = False
                        elif allow_workload_management is None and has_workload_manager:
                            print(
                                f"Software '{software_name}' from vendor '{valid_software_vendor}' supports Workload"
                                f" Manager. Enabling workload manager for {monolithic_list_item} by default. To"
                                " disable, please set 'allowWorkloadManagement' to false explicitly in the job config"
                                " file."
                            )
                            request[ENVIRONMENT][MONOLITHIC_LIST][i][ALLOW_WORKLOAD_MANAGEMENT] = True
                        break  # Successful validation of current list item.
                    raise UserException(
                        HTTPStatus.BAD_REQUEST,
                        self.__class__.__name__,
                        f"Software version '{software_version}' for software name '{software_name}' is not valid. "
                        + "Valid software versions: "
                        + str(list_software_response[valid_software_vendor][software_name][SOFTWARE_VERSIONS]),
                    )
                valid_software_names.append(
                    {valid_software_vendor: list(list_software_response[valid_software_vendor].keys())}
                )
            if not is_valid_software_name:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    f"Software name '{software_name}' is not valid. "
                    + "Valid software vendors and names (format: [{vendor: [name, ...]}, ...]): "
                    + str(valid_software_names),
                )

    def _confirm_required_fields_for_licensed_software(self, monolithic_list_item, license_consumption_profiles):
        error_messages = []
        if not monolithic_list_item.get(LICENSE_ADDRESS) and not monolithic_list_item.get(LICENSE_NAME):
            error_messages.append(f"Non-empty '{LICENSE_NAME}' or '{LICENSE_ADDRESS}'")
        if not monolithic_list_item.get(LICENSE_FEATURE):
            error_messages.append(f"Non-empty '{LICENSE_FEATURE}'")

        if not monolithic_list_item.get(LICENSE_COUNT_PER_TASK) and not monolithic_list_item.get(
            LICENSE_CONSUMPTION_PROFILE_NAME
        ):
            error_messages.append(f"Must required '{LICENSE_COUNT_PER_TASK}' or '{LICENSE_CONSUMPTION_PROFILE_NAME}'.")

        if monolithic_list_item.get(LICENSE_CONSUMPTION_PROFILE_NAME):
            software_key = f"{monolithic_list_item[SOFTWARE_NAME]}#{monolithic_list_item[VENDOR_NAME]}"
            profile_list = FovusApiUtil.get_license_consuption_profile_list(license_consumption_profiles)
            if software_key not in license_consumption_profiles:
                error_messages.append(
                    f"Invalid license consumption profile: '{LICENSE_CONSUMPTION_PROFILE_NAME}' for software `"
                    + f"{monolithic_list_item[SOFTWARE_NAME]}'."
                )
            elif monolithic_list_item.get(LICENSE_CONSUMPTION_PROFILE_NAME) not in profile_list:
                error_messages.append(
                    "Invalid license consumption profile: '"
                    + f"{monolithic_list_item.get(LICENSE_CONSUMPTION_PROFILE_NAME)}'. "
                    + f"Valid license consumption profiles: {profile_list}"
                )
            elif (
                monolithic_list_item.get(LICENSE_FEATURE)
                and monolithic_list_item.get(LICENSE_FEATURE) not in license_consumption_profiles[software_key]
            ):
                feature_list = []
                for feature_map in license_consumption_profiles.values():
                    for feature, profiles in feature_map.items():
                        if monolithic_list_item.get(LICENSE_CONSUMPTION_PROFILE_NAME) in profiles:
                            feature_list.append(feature)
                error_messages.append(
                    f"Invalid license feature '{monolithic_list_item.get(LICENSE_FEATURE)}'. "
                    + f"'{monolithic_list_item.get(LICENSE_CONSUMPTION_PROFILE_NAME)}' profile only supports these "
                    + f"features: {feature_list}"
                )
        elif (
            not isinstance(monolithic_list_item.get(LICENSE_COUNT_PER_TASK), int)
            or monolithic_list_item.get(LICENSE_COUNT_PER_TASK) < 0
        ):
            error_messages.append(f"Non-negative integer '{LICENSE_COUNT_PER_TASK}'")
        if error_messages:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                f"The following are required for {MONOLITHIC_LIST} item {monolithic_list_item} "
                "in order for license queue and auto-scaling to take effect:"
                + "\n\t- "
                + "\n\t- ".join(error_messages),
            )

    def _validate_benchmarking_profile(self, request):  # pylint: disable=too-many-locals
        benchmarking_profile_name = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][BENCHMARKING_PROFILE_NAME]
        hyperthreading_enabled = request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][ENABLE_HYPERTHREADING]
        print(
            f"Validating the benchmarking profile '{benchmarking_profile_name}' and "
            "updating values if necessary and possible..."
        )
        list_benchmark_profile_response = self.list_benchmarking_profile(request[PAYLOAD_WORKSPACE_ID])
        valid_benchmarking_profile_names = []
        for current_benchmarking_profile in list_benchmark_profile_response:
            current_benchmarking_profile_name = current_benchmarking_profile[BENCHMARK_NAME]
            valid_benchmarking_profile_names.append(current_benchmarking_profile_name)
            if benchmarking_profile_name == current_benchmarking_profile_name:
                validations_config = FovusApiUtil.get_benchmark_validations_config(request)
                FovusApiUtil.print_benchmark_hyperthreading_info(hyperthreading_enabled)
                FovusApiUtil.validate_computing_device(
                    request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE],
                    current_benchmarking_profile,
                )
                FovusApiUtil.validate_cpu_architectures(
                    request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][SUPPORTED_CPU_ARCHITECTURES],
                    current_benchmarking_profile,
                )
                corrected_value_messages = {}
                for validation_type in validations_config:  # pylint: disable=consider-using-dict-items
                    for bound_to_validate in validations_config[validation_type][BOUNDS]:
                        current_value = itemgetter(*bound_to_validate)(  # Multiple values may be retrieved.
                            request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS]
                        )
                        benchmarking_profile_bounds = FovusApiUtil.get_benchmark_profile_bounds(
                            current_benchmarking_profile,
                            bound_to_validate,
                            request,
                            source=self.__class__.__name__,
                        )
                        for is_invalid, comprehension in zip(COMPARISONS, COMPREHENSIONS):
                            if is_invalid in validations_config[validation_type]:
                                benchmarking_profile_item_bound = validations_config[validation_type][comprehension](
                                    benchmarking_profile_bounds
                                )
                                if validations_config[validation_type][is_invalid](
                                    current_value, benchmarking_profile_item_bound
                                ):
                                    if is_invalid == IS_INVALID_CORRECTABLE:
                                        bound_to_validate = bound_to_validate[
                                            0  # Correctable bounds are single values stored in tuples.
                                        ]
                                        corrected_value_messages[bound_to_validate] = (
                                            FovusApiUtil.get_corrected_value_message(
                                                validation_type,
                                                benchmarking_profile_name,
                                                bound_to_validate,
                                                benchmarking_profile_item_bound,
                                                hyperthreading_enabled,
                                                current_value,
                                            )
                                        )
                                        request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][
                                            bound_to_validate
                                        ] = benchmarking_profile_item_bound
                                    else:
                                        raise UserException(
                                            HTTPStatus.BAD_REQUEST,
                                            self.__class__.__name__,
                                            f"Invalid value of {current_value} for "
                                            f"{Util.get_message_from_list(bound_to_validate)} with "
                                            f"benchmarking profile '{benchmarking_profile_name}'. "
                                            + validations_config[validation_type][
                                                INCORRECTABLE_ERROR_MESSAGE_FROM_BOUNDS
                                            ](bound_to_validate, benchmarking_profile_bounds, hyperthreading_enabled),
                                        )
                for bound_value_correction in BOUND_VALUE_CORRECTION_PRINT_ORDER:
                    if bound_value_correction in corrected_value_messages:
                        print(corrected_value_messages[bound_value_correction])
                return  # Successful validation.

        raise UserException(
            HTTPStatus.BAD_REQUEST,
            self.__class__.__name__,
            f"Invalid benchmarking profile: '{benchmarking_profile_name}'. "
            + f"Valid benchmarking profiles: {valid_benchmarking_profile_names}",
        )

    def _convert_scheduled_at_format(self, request):
        job_scheduled_at = request.get(SCHEDULED_AT)
        if job_scheduled_at:
            print("Converting value for scheduledAt to ISO 8601 (if needed)...")
            scheduled_at_iso = dateparser.parse(
                job_scheduled_at,
                settings={
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "TO_TIMEZONE": DEFAULT_TIMEZONE,
                    "PREFER_DATES_FROM": "future",
                },
            )
            if not scheduled_at_iso:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    f"Invalid value of '{job_scheduled_at}' for '{SCHEDULED_AT}'. See --help for recommended formats.",
                )
            print(f"Create job scheduled at: {scheduled_at_iso.isoformat()}")
            request[SCHEDULED_AT] = scheduled_at_iso.isoformat()

    def get_file_download_token(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.FILE, ApiMethod.GET_FILE_DOWNLOAD_TOKEN),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_mount_storage_credentials(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.FILE, ApiMethod.GET_MOUNT_STORAGE_CREDENTIALS),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_file_upload_token(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.FILE, ApiMethod.GET_FILE_UPLOAD_TOKEN),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_temporary_s3_upload_credentials(self):
        upload_credentials = self.get_file_upload_token(
            FovusApiAdapter.get_file_upload_download_token_request(self.workspace_id)
        )
        return FovusApiUtil.get_s3_info(upload_credentials)

    def get_temporary_s3_download_credentials(self, job_id):
        download_credentials = self.get_file_download_token(
            FovusApiAdapter.get_file_upload_download_token_request(self.workspace_id, job_id)
        )
        return FovusApiUtil.get_s3_info(download_credentials)

    def get_job_current_status(self, job_id):
        job_info = self.get_job_info(FovusApiAdapter.get_job_info_request(self.workspace_id, job_id))
        return job_info[JOB_STATUS]

    def get_job_info(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.GET_JOB_INFO),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_software(self):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.SOFTWARE, ApiMethod.LIST_SOFTWARE),
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_licenses(self, workspace_id):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.LICENSE, ApiMethod.LIST_LICENSES),
            params={"workspaceId": workspace_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_software_license_relationships(self, workspace_id):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.LICENSE, ApiMethod.LIST_SOFTWARE_LICENSE_RELATIONSHIPS),
            params={"workspaceId": workspace_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_license_consumption_profiles(self, workspace_id):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.LICENSE, ApiMethod.GET_LICENSE_CONSUMPTION_PROFILE),
            params={"workspaceId": workspace_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_benchmarking_profile(self, workspace_id):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.BENCHMARK, ApiMethod.LIST_BENCHMARK_PROFILE),
            params={"workspaceId": workspace_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_workspace_settings(self, workspace_id):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.WORKSPACE, ApiMethod.GET_WORKSPACE_SETTINGS),
            params={"workspaceId": workspace_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def start_sync_file(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.FILE, ApiMethod.START_SPECIFY_FILE_SYNC),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def get_sync_file_status(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.FILE, ApiMethod.GET_SPECIFY_FILE_SYNC_STATUS),
            params=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return response.json()

    def get_list_runs(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.LIST_RUNS),
            json=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def step_up_session(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        FovusApiUtil.step_up_session(headers, request, self.__class__.__name__)

    def _get_user_id(self) -> str:
        claims = self.fovus_cognito_adapter.get_claims()
        return claims[UserAttribute.USER_ID.value]

    def get_user_id(self) -> str:
        return self.user_id

    @lru_cache
    def get_workspace(self) -> dict:
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(
                Api.WORKSPACE,
                ApiMethod.LIST_WORKSPACES,
            ),
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        res = FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

        try:
            workspace = res[0]
        except Exception as exc:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Unable to retrieve workspace. Please check that you have a workspace.",
            ) from exc

        if not isinstance(workspace, dict):
            raise UserException(HTTPStatus.INTERNAL_SERVER_ERROR, self.__class__.__name__, "Invalid workspace type")

        sso_provider_id = workspace.get("ssoProviderId")
        role = workspace["user"]["role"]
        if sso_provider_id and role != "SUPPORT":
            workspace_sso_tokens = self.fovus_cognito_adapter.load_workspace_sso_tokens()
            if workspace_sso_tokens is None or sso_provider_id not in workspace_sso_tokens:
                FileUtil.remove_credentials()
                raise NotSignedInException()
        return workspace

    def _get_workspace_id(self) -> str:
        workspace = self.get_workspace()
        return workspace["workspaceId"]

    def get_workspace_id(self) -> str:
        return self.workspace_id

    def get_workspace_role(self) -> str:
        workspace = self.get_workspace()
        return workspace["role"]

    def delete_job(self, job_id_tuple: Tuple[str, ...]):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.DELETE_JOB),
            json={"workspaceId": self.workspace_id, "jobIdList": job_id_tuple},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        json_response = response.json()
        if "deletedJobIds" in json_response and len(json_response["deletedJobIds"]) > 2:
            print(f"Jobs {json_response['deletedJobIds']} are deleted successfully.")
        return FovusApiUtil.confirm_successful_response(json_response, response.status_code, self.__class__.__name__)

    def get_user_setting(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.USER, ApiMethod.GET_USER_SETTING),
            params=request,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )

        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_projects(self, request):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.get(
            FovusApiUtil.get_api_address(Api.PROJECT, ApiMethod.LIST_PROJECTS),
            headers=headers,
            params=request,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    def list_active_projects(self):
        workspace = self.get_workspace()
        projects = self.list_projects(
            {"workspaceId": workspace["workspaceId"], "costCenterId": workspace["user"].get("costCenterId", None)}
        )
        active_project = list(filter(lambda project: project["status"] == "ACTIVE", projects))
        return active_project

    def _download_ssh_key_content(self, job_id: str):
        s3_client, s3_bucket, _s3_prefix = self.get_temporary_s3_download_credentials(job_id)
        response = s3_client.get_object(
            Bucket=s3_bucket,
            Key=f"ssh-keys/{self.workspace_id}-{self.user_id}.pem",
        )
        key_content = response["Body"].read().decode("utf-8")
        return key_content

    def _ssh_live_tail(self, job_id: str, private_key_content: str, hostname: str, file_path: str):
        print("Establishing connection...")
        pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key_content))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=22, username=job_id, pkey=pkey)

        tail_cmd = f"tail -f /compute_workspace/{shlex.quote(file_path)}"  # nosec B601
        _, stdout, stderr = ssh.exec_command(tail_cmd)  # nosec B601
        try:
            for line in iter(stdout.readline, ""):
                print(line, end="")
            for line in iter(stderr.readline, ""):
                if "No such file or directory" in line:
                    Util.print_error_message(
                        f"Task {file_path.split('/')[0]} is not running."
                        + "Only a file of a running task can be live tailed. "
                        + "Please check your job ID and task name and try again."
                    )
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception:  # pylint: disable=broad-except
            print(f"The Task where the file {file_path} belongs is not running. Please check your file path and try.")
        finally:
            ssh.close()

    def live_tail_file(self, job_id: str, file_path: str):
        job_current_status = self.get_job_current_status(job_id)
        if job_current_status != "Running":
            Util.print_error_message(f"Job {job_id} is not running. Please check your job ID and try again.")
            return
        key_content = self._download_ssh_key_content(job_id)
        list_runs = self.get_list_runs(self.get_list_runs_request(workspace_id=self.workspace_id, job_id=job_id))
        task_name = file_path.split("/")[0]
        for run in list_runs["runList"]:
            if run["taskName"] == task_name and len(run["computeNodeDnsList"]) != 0:
                compute_node_dns = run["computeNodeDnsList"][0]
                self._ssh_live_tail(job_id, key_content, compute_node_dns, file_path)

    def sync_job_files(self, job_id: str, include_paths: Optional[list[str]], exclude_paths: Optional[list[str]]):
        job_current_status = self.get_job_current_status(job_id)
        if job_current_status != "Running":
            return

        if include_paths is None and exclude_paths is None:
            include_paths = ["*"]
        try:
            print("Syncing job files...")
            response = self.start_sync_file(
                self.start_sync_file_request(
                    workspace_id=self.workspace_id,
                    job_id=job_id,
                    paths=[],
                    include_list=include_paths,
                    exclude_list=exclude_paths,
                )
            )
            attempts = 0
            max_attempts = 100
            success = False

            while attempts < max_attempts:
                success = self.get_sync_file_status(
                    self.get_sync_file_status_request(
                        workspace_id=self.workspace_id, job_id=job_id, triggered_time=response
                    )
                )
                if success:
                    break
                attempts += 1
                time.sleep(2)
            print("Syncing completed")
        except BaseException as exc:
            logging.exception("Failed to sync job files")
            logging.exception(exc)
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Unable to sync the job files. Make sure given inputs are correct",
            ) from exc

    def terminate_job(self, job_id: str):
        headers = self.fovus_cognito_adapter.get_authorization_header()
        response = requests.post(
            FovusApiUtil.get_api_address(Api.JOB, ApiMethod.TERMINATE_JOB),
            json={"workspaceId": self.workspace_id, "jobId": job_id},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        return FovusApiUtil.confirm_successful_response(response.json(), response.status_code, self.__class__.__name__)

    @staticmethod
    def get_create_job_request(job_config_file_path: str, workspace_id: str, job_options: dict):
        with FileUtil.open(os.path.expanduser(job_config_file_path)) as job_config_file:
            create_job_request = json.load(job_config_file)
            FovusApiAdapter._add_create_job_request_remaining_fields(create_job_request, workspace_id, job_options)
            FovusApiAdapter._apply_cli_overrides_to_request(create_job_request, job_options)
            FovusApiAdapter._apply_computing_device_overrides(create_job_request)
            return create_job_request

    @staticmethod
    def _add_create_job_request_remaining_fields(create_job_request, workspace_id: str, job_options: dict):
        create_job_request[PAYLOAD_DEBUG_MODE] = job_options[DEBUG_MODE]
        create_job_request[PAYLOAD_AUTO_DELETE_DAYS] = job_options[PAYLOAD_AUTO_DELETE_DAYS]
        create_job_request[PAYLOAD_TIMESTAMP] = job_options[TIMESTAMP]
        create_job_request[PAYLOAD_WORKSPACE_ID] = workspace_id
        if job_options.get(JOB_NAME):
            create_job_request[PAYLOAD_JOB_NAME] = job_options[JOB_NAME]
        else:
            create_job_request[PAYLOAD_JOB_NAME] = job_options[JOB_ID]

    @staticmethod
    def _apply_cli_overrides_to_request(create_job_request, job_options: dict):
        print("Applying CLI overrides to create job request...")
        FovusApiAdapter._apply_single_field_overrides(create_job_request, job_options)
        FovusApiAdapter._apply_monolithic_list_overrides(create_job_request, job_options)
        FovusApiAdapter._apply_containerized_overrides(create_job_request, job_options)

    @staticmethod
    def _apply_single_field_overrides(create_job_request, job_options: dict):
        # The empty create job request is used to reference keys in the event that the provided config is not complete
        # and CLI arguments are being used to replace the remaining values.
        with FileUtil.open(
            os.path.join(
                ROOT_DIR, FOVUS_PROVIDED_CONFIGS[JOB_CONFIG_CONTAINERIZED_TEMPLATE][PATH_TO_CONFIG_FILE_IN_REPO]
            ),
        ) as empty_job_config_file:
            empty_create_job_request = json.load(empty_job_config_file)
            del empty_create_job_request[ENVIRONMENT]

            FovusApiAdapter._apply_overrides_to_root_keys(create_job_request, empty_create_job_request, job_options)
            for empty_sub_dict, create_job_request_sub_dict in FovusApiAdapter._get_deepest_sub_dict_pairs(
                empty_create_job_request, create_job_request
            ):
                FovusApiAdapter._apply_cli_overrides_to_sub_dict(
                    create_job_request_sub_dict, empty_sub_dict, job_options
                )

    @staticmethod
    def _apply_containerized_overrides(create_job_request, job_options: dict):
        environment = create_job_request[ENVIRONMENT]
        if CONTAINERIZED in environment:
            docker_hub_username = job_options.get(DOCKER_HUB_USERNAME)
            docker_hub_password = job_options.get(DOCKER_HUB_PASSWORD)
            containerized_env = environment[CONTAINERIZED]
            if docker_hub_username:
                containerized_env["dockerHubUsername"] = docker_hub_username
                Util.print_message_with_color(
                    f"CLI override found for dockerHubUsername. Overriding default value with '{docker_hub_username}'.",
                    "blue",
                )
            if docker_hub_password:
                containerized_env["dockerHubPassword"] = docker_hub_password
                Util.print_message_with_color(
                    "CLI override found for dockerHubPassword. Overriding default value.",
                    "blue",
                )

    @staticmethod
    def _apply_monolithic_list_overrides(create_job_request, job_options: dict):
        environment = create_job_request[ENVIRONMENT]
        if MONOLITHIC_LIST in environment and job_options[MONOLITHIC_OVERRIDE]:
            for monolithic in environment[MONOLITHIC_LIST]:
                for vendor_name, software_name, license_feature, new_license_count_per_task in job_options[
                    MONOLITHIC_OVERRIDE
                ]:
                    if (
                        monolithic[VENDOR_NAME] == vendor_name
                        and monolithic[SOFTWARE_NAME] == software_name
                        and monolithic[LICENSE_FEATURE] == license_feature
                    ):
                        Util.print_message_with_color(
                            f"CLI override found for monolithic item with keys: {vendor_name}, {software_name}, and "
                            f"{license_feature}. Overriding default license count per task of "
                            f"{monolithic[LICENSE_COUNT_PER_TASK]} with {new_license_count_per_task}.",
                            "blue",
                        )
                        monolithic[LICENSE_COUNT_PER_TASK] = int(new_license_count_per_task)

    @staticmethod
    def _apply_overrides_to_root_keys(create_job_request, empty_create_job_request, job_options: dict):
        for key in empty_create_job_request:
            if not isinstance(key, dict):
                new_value = job_options.get(key)
                if new_value:
                    Util.print_message_with_color(
                        f"CLI override found for key: {key}. Overriding default value of "
                        f"'{create_job_request.get(key)}' "
                        f"with '{new_value}'.",
                        "blue",
                    )
                    create_job_request[key] = new_value

    @staticmethod
    def _get_deepest_sub_dict_pairs(empty_create_job_request, create_job_request):
        sub_dict_pairs = []
        for key in empty_create_job_request.keys():
            if isinstance(empty_create_job_request[key], dict):
                if key not in create_job_request:
                    create_job_request[key] = {}
                sub_sub_dict_pairs = FovusApiAdapter._get_deepest_sub_dict_pairs(
                    empty_create_job_request[key], create_job_request[key]
                )
                if sub_sub_dict_pairs:
                    sub_dict_pairs.extend(sub_sub_dict_pairs)
                else:
                    sub_dict_pairs.append((empty_create_job_request[key], create_job_request[key]))
        return sub_dict_pairs

    @staticmethod
    def _apply_cli_overrides_to_sub_dict(sub_dict, empty_sub_dict, job_options: dict):
        for sub_dict_parameter_key in empty_sub_dict.keys():
            cli_dict_value = job_options.get(sub_dict_parameter_key)
            if job_options[sub_dict_parameter_key] is not None:
                Util.print_message_with_color(
                    f"CLI override found for key: {sub_dict_parameter_key}. Overriding default job config value of "
                    f"{sub_dict.get(sub_dict_parameter_key)} with {job_options[sub_dict_parameter_key]}.",
                    "blue",
                )
                if isinstance(cli_dict_value, str) and cli_dict_value.isdigit():
                    cli_dict_value = int(cli_dict_value)
                sub_dict[sub_dict_parameter_key] = cli_dict_value

    @staticmethod
    def _apply_computing_device_overrides(create_job_request):
        value_was_overridden = False
        computing_device = create_job_request[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][COMPUTING_DEVICE]
        Util.print_message_with_color(
            f"Computing device is {computing_device}. Overriding related constraints if needed...", "blue"
        )
        if computing_device == CPU:
            for field in [MIN_GPU, MAX_GPU, MIN_GPU_MEM_GIB]:
                current_field_value = create_job_request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][field]
                if current_field_value != 0:
                    Util.print_message_with_color(
                        f"Overriding current {field} value of {current_field_value} with 0.", "blue"
                    )
                    value_was_overridden = True
                    create_job_request[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][field] = 0
        if not value_was_overridden:
            Util.print_success_message("No overrides necessary.")

    @staticmethod
    def get_file_upload_download_token_request(workspace_id: str, job_id=None, duration_seconds=3600):
        return {
            "workspaceId": workspace_id,
            "durationSeconds": duration_seconds,
            "jobId": "" if job_id is None else job_id,
            "storageType": "FOVUS_STORAGE" if job_id is None else "JOB_STORAGE",
        }

    @staticmethod
    def get_job_info_request(workspace_id: str, job_id):
        return {"workspaceId": workspace_id, "jobId": job_id}

    @staticmethod
    def get_mount_storage_credentials_request(user_id: str, workspace_id: str):
        return {"userId": user_id, "workspaceId": workspace_id}

    @staticmethod
    def start_sync_file_request(
        workspace_id: str,
        job_id: str,
        paths: list[str],
        include_list: Optional[list[str]],
        exclude_list: Optional[list[str]],
    ):
        return {
            "workspaceId": workspace_id,
            "jobId": job_id,
            "paths": paths,
            "includeList": include_list,
            "excludeList": exclude_list,
        }

    @staticmethod
    def get_sync_file_status_request(workspace_id: str, job_id: str, triggered_time: str):
        return {"workspaceId": workspace_id, "jobId": job_id, "triggeredTime": triggered_time}

    @staticmethod
    def get_list_runs_request(workspace_id: str, job_id: str):
        return {
            "current": "0",
            "limit": -1,
            "workspaceId": workspace_id,
            "jobId": job_id,
            "filterOptions": {"runStatus": "Running"},
        }
