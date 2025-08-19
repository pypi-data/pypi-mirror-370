from http import HTTPStatus

import click
from typing_extensions import Optional, Tuple

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.adapter.fovus_s3_adapter import FovusS3Adapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS, OUTPUTS
from fovus.constants.cli_constants import (
    ALLOW_PREEMPTIBLE,
    AUTO_DELETE_DAYS,
    BENCHMARKING_PROFILE_NAME,
    COMPUTING_DEVICE,
    CPU,
    DEBUG_MODE,
    DOCKER_HUB_PASSWORD,
    DOCKER_HUB_USERNAME,
    EMAIL_NOTIFICATION,
    EMPTY_FOLDER_LIST,
    ENABLE_HYPERTHREADING,
    GPU,
    IS_HYBRID_STRATEGY_ALLOWED,
    IS_RESUMABLE_WORKLOAD,
    IS_SINGLE_THREADED_TASK,
    IS_SUBJECT_TO_LICENSE_AVAILABILITY,
    JOB_ID,
    JOB_MAX_CLUSTER_SIZE_VCPU,
    JOB_NAME,
    LICENSE_CONSUMPTION_PROFILE,
    LICENSE_TIMEOUT_HOURS,
    MAX_GPU,
    MAX_VCPU,
    MIN_GPU,
    MIN_GPU_MEM_GIB,
    MIN_VCPU,
    MIN_VCPU_MEM_GIB,
    MONOLITHIC_OVERRIDE,
    OUTPUT_FILE_LIST,
    OUTPUT_FILE_OPTION,
    PARALLELISM_CONFIG_FILES,
    PARALLELISM_OPTIMIZATION,
    POST_PROCESSING_RUN_COMMAND,
    POST_PROCESSING_STORAGE_GIB,
    POST_PROCESSING_TASK_NAME,
    POST_PROCESSING_WALLTIME_HOURS,
    PROJECT_ID,
    REMOTE_INPUTS,
    RUN_COMMAND,
    SCALABLE_PARALLELISM,
    SCHEDULED_AT,
    SEARCH_OUTPUT_FILES,
    SEARCH_OUTPUT_KEYWORDS,
    STORAGE_GIB,
    SUPPORTED_CPU_ARCHITECTURES,
    TIME_TO_COST_PRIORITY_RATIO,
    TIMESTAMP,
    WALLTIME_HOURS,
)
from fovus.constants.fovus_api_constants import ApiMethod, UserSettings
from fovus.constants.util_constants import AutoDeleteAccess, WorkspaceRole
from fovus.exception.user_exception import UserException
from fovus.util.fovus_api_util import FovusApiUtil
from fovus.util.util import Util
from fovus.validator.fovus_api_validator import FovusApiValidator

IF_IS_SINGLE_THREADED_NOTE = "(or multiple single-threaded tasks on each compute node if isSingleThreadedTask is true)"
USED_FOR_OVERRIDING_JOB_CONFIG_VALUES = (
    "(Note: Used for overriding job config values. If this value is provided in the job "
    "config file, this argument is optional.)"
)
ANY_NUMBER_OF_EXPRESSIONS = "This option may be provided multiple times."
PREFERRED_SCHEDULED_AT_FORMATS = (
    "The default time zone is your local time zone. Acceptable formats include the following. "
    '1) ISO 8601 format: "YYYY-MM-DDThh:mm:ss[.mmm]TZD" (e.g., "2020-01-01T18:30:00-05:00"). '
    '2) Date only (defaults to upcoming 12AM your local time zone): "YYYY-MM-DD" (e.g., "2020-01-01"). '
    '3) Time only (defaults to next upcoming time your local time zone): "hh:mmTZD" or "hh:mm" or "hh:mm AM/PM/am/pm" '
    '(e.g., "18:30-05:00" or "18:30" or "6:30 PM"). '
    '4) Natural language time: "DD month YYYY HH:MM AM/PM/am/pm timezone" (e.g., "21 July 2013 10:15 pm PDT").'
)

WILDCARD_EXPLANATION = r"""
Supported wildcards:
    \* - matches any number of characters
    ? - matches any single character

E.g. out?/\*.txt matches any .txt file in folders out1, out2, etc.

E.g. folder???/file.txt matches folder001/file.txt, folder123/file.txt, etc.\n\n
"""


@click.command("create")
@click.argument(
    "job_config_file_path",
    type=str,
)
@click.argument(
    "job_directory",
    type=str,
)
@click.option(
    "--include-paths",
    "include_paths_tuple",
    metavar="include_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the JOB_DIRECTORY that will be uploaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. taskName/out?/\*.txt matches any .txt file in folders taskName/out1, taskName/out2, etc.

        E.g. taskName???/folder/file.txt matches taskName001/folder/file.txt, taskName123/folder/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --include-paths "path1" --include-paths "path2"

        E.g. --include-paths "path1,path2"
        """,
)
@click.option(
    "--exclude-paths",
    "exclude_paths_tuple",
    metavar="exclude_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the JOB_DIRECTORY that will not be uploaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. taskName/out?/\*.txt matches any .txt file in folders taskName/out1, taskName/out2, etc.

        E.g. taskName???/folder/file.txt matches taskName001/folder/file.txt, taskName123/folder/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --exclude-paths "path1" --exclude-paths "path2"

        E.g. --exclude-paths "path1,path2"
        """,
)
@click.option(
    "--project-name",
    type=str,
    help="The project name associated with your job. "
    + "If omitted, the default project will be used. Use 'None' to specify no project.",
)
@click.option(
    "--email-notification/--no-email-notification",
    default=None,
    help="Enable or disable email notification when the job is finished. "
    + "By default, your notification preference setting will be applied.",
)
@click.option(
    "--debug-mode",
    DEBUG_MODE,
    is_flag=True,
    type=bool,
    help="Keep compute nodes alive after each task execution until the task "
    + "walltimeHours is reached to allow additional time for interactive debugging via SSH.",
)
@click.option(
    "--auto-delete-days",
    AUTO_DELETE_DAYS,
    default=0,
    type=int,
    help=(
        "Set a number of days after which the job will be permanently deleted. The deletion timer starts immediately"
        " after the job completes, fails, or is terminated"
    ),
)
@click.option(
    "--benchmarking-profile-name",
    BENCHMARKING_PROFILE_NAME,
    type=str,
    help="Fovus will optimize the cloud strategies for your job execution, including determining the "
    + "optimal choices of virtual HPC infrastructure and computation parallelism, if applicable, based "
    + "upon the selected benchmarking profile. For the best optimization results, select the benchmarking "
    + "profile whose characteristics best resemble the workload under submission. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--computing-device",
    COMPUTING_DEVICE,
    type=click.Choice([CPU, GPU]),
    help=f"The target computing device(s) for running your workload. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--docker-hub-password",
    DOCKER_HUB_PASSWORD,
    type=str,
    help=(
        "The password for the Docker Hub account that shall be used to pull the 'imagePath' for containerized"
        " environments. If this flag is provided, then --docker-hub-username must be provided as well."
    ),
)
@click.option(
    "--docker-hub-username",
    DOCKER_HUB_USERNAME,
    type=str,
    help=(
        "The username for the Docker Hub account that shall be used to pull the 'imagePath' for containerized"
        " environments. If this flag is provided, then --docker-hub-password must be provided as well."
    ),
)
@click.option(
    "--job-name",
    JOB_NAME,
    type=str,
    help="The name of the job to be created. If a name is not provided, the job ID will be used.",
)
@click.option(
    "--is-single-threaded-task",
    IS_SINGLE_THREADED_TASK,
    type=bool,
    help="Set true if and only if each task uses only a single CPU thread (vCPU) at a maximum. "
    + "Setting it true allows multiple tasks to be deployed onto the same compute node to maximize the "
    + "task-level parallelism and the utilization of all CPU threads (vCPUs).",
)
@click.option(
    "--license-timeout-hours",
    LICENSE_TIMEOUT_HOURS,
    type=float,
    help="For license-required jobs, the maximum time the job is allowed to be waiting in a queue for "
    + "deployment when no license is available. A job will be terminated once the timeout timer expires. "
    + "Not applicable to license-free jobs. Format: Real (e.g., 1.5). Range: ≥1. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--monolithic-override",
    MONOLITHIC_OVERRIDE,
    type=str,
    nargs=4,
    multiple=True,
    help="Override a monolithic software environment. Provide VENDOR_NAME SOFTWARE_NAME LICENSE_FEATURE "
    + "NEW_LICENSE_COUNT. All four values are required to reference a monolithic "
    + "software and its license usage constraint. Currently, the only supported override for a monolithic "
    + "software environment is the license count, and as a result, only the "
    + f"license count is overridden. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--min-gpu",
    MIN_GPU,
    type=int,
    help="The minimum number of GPUs required to parallelize the execution of each task. Only values "
    + f"supported by the selected BP are allowed. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--max-gpu",
    MAX_GPU,
    type=int,
    help="The maximum number of GPUs allowed to parallelize the execution of each task. Only values "
    + f"supported by the selected BP are allowed. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--min-gpu-mem-gib",
    MIN_GPU_MEM_GIB,
    type=float,
    help="The minimum total size of GPU memory required to support the execution of each task, summing "
    + "the required memory size for each GPU. Format: Real (e.g., 10.5). Only values supported by the "
    + "selected BP are allowed. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--min-vcpu",
    MIN_VCPU,
    type=int,
    help=(
        "The minimum number of vCPUs required to parallelize the execution of each task "
        f"{IF_IS_SINGLE_THREADED_NOTE}. A vCPU refers to a thread "
        "of a CPU core. Only values supported by the selected BP are allowed. "
    )
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--job-max-cluster-size-vcpu",
    JOB_MAX_CLUSTER_SIZE_VCPU,
    type=int,
    help="The maximum cluster size in terms of the total number of vCPUs allowed for parallelizing task runs "
    + "in the job, which only takes into effect when isSingleThreadedTask is true. A default value of 0 means "
    + "no limit. ",
)
@click.option(
    "--max-vcpu",
    MAX_VCPU,
    type=int,
    help=(
        "The maximum number of vCPUs allowed to parallelize the execution of each task "
        f"{IF_IS_SINGLE_THREADED_NOTE}. A vCPU refers to a thread "
        "of a CPU core. Only values supported by the selected BP are allowed. "
    )
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--min-vcpu-mem-gib",
    MIN_VCPU_MEM_GIB,
    type=float,
    help=(
        "The minimum total size of system memory required to support the execution of each task "
        f"{IF_IS_SINGLE_THREADED_NOTE}, summing the "
        "required memory size for each vCPU. Format: Real (e.g., 10.5). Only values supported by the selected "
        "BP are allowed. "
    )
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--output-file-list",
    OUTPUT_FILE_LIST,
    type=str,
    multiple=True,
    help="Specify the output files to include or exclude from transferring back to the cloud storage "
    + "using relative paths from the working directory of each task.\n\n"
    + " ".join((
        r"""
        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. out?/\*.txt matches any .txt file in folders out1, out2, etc.

        E.g. folder???/file.txt matches folder001/file.txt, folder123/file.txt, etc.\n\n
        """,
        ANY_NUMBER_OF_EXPRESSIONS,
        USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
    )),
)
@click.option(
    "--output-file-option",
    OUTPUT_FILE_OPTION,
    type=click.Choice(["include", "exclude"]),
    help="Specify whether the output files in outputFileList should be included or excluded from "
    + "transferring back to the cloud storage after the job is completed. See outputFileList for more "
    + "information. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--remote-inputs",
    REMOTE_INPUTS,
    type=str,
    multiple=True,
    help=(
        "Provide the URL of or path to any file or folder in Fovus Storage. The files and folders specified "
        + "will be included under the working directory of each task as inputs for all tasks and will be excluded "
        + "from syncing back to Fovus Storage as job files. If the file or folder is from My Files of Fovus "
        + 'Storage, a short relative path works the same as the URL. The path to a folder must end with "/". '
        + " ".join((ANY_NUMBER_OF_EXPRESSIONS, USED_FOR_OVERRIDING_JOB_CONFIG_VALUES))
        + '\n\nE.g. "folderName/fileName.txt" is equivalent to'
        ' "https://app.fovus.co/files?path=folderName/fileName.txt"'
        + '\n\nE.g. "folderName/" is equivalent to "https://app.fovus.co/folders?path=folderName""'
    ),
)
@click.option(
    "--parallelism-config-files",
    PARALLELISM_CONFIG_FILES,
    type=str,
    multiple=True,
    help="Specify the configuration files that contain Fovus Environment Tokens, if any, using "
    + "relative paths from the working directory of each task. All Fovus Environment Tokens in the "
    + "configuration files specified will be resolved to values prior to task execution. "
    + " ".join((
        r"""
        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. out?/\*.txt matches any .txt file in folders out1, out2, etc.

        E.g. folder???/file.txt matches folder001/file.txt, folder123/file.txt, etc.\n\n
        """,
        ANY_NUMBER_OF_EXPRESSIONS,
        USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
    )),
)
@click.option(
    "--parallelism-optimization",
    PARALLELISM_OPTIMIZATION,
    type=bool,
    help="If enabled, Fovus will determine the optimal parallelism for parallelizing the computation of "
    + "each task to minimize the total runtime and cost based on the time-to-cost priority ratio (TCPR) "
    + "specified. To pass in the optimal parallelism to your software program, you can directly use the Fovus "
    + "environment tokens, e.g., $FovusOptVcpu, $FovusOptGpu, in your command lines or or in the input "
    + "configuration files specified by the parallelismConfigFiles job config field. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--run-command",
    RUN_COMMAND,
    type=str,
    help="Specify the command lines to launch each task. The same command lines will be executed under the "
    + f"working directory of each task. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--scalable-parallelism",
    SCALABLE_PARALLELISM,
    type=bool,
    help="A software program exhibits scalable parallelism if it can make use of more computing devices "
    + "(e.g., vCPUs and/or GPUs) to parallelize a larger computation task. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--scheduled-at",
    SCHEDULED_AT,
    type=str,
    help=f"The time at which the job is scheduled to be submitted. {PREFERRED_SCHEDULED_AT_FORMATS}",
)
@click.option(
    "--storage-gib",
    STORAGE_GIB,
    type=int,
    help=(
        "The total size of local SSD storage required to support the execution of each task "
        f"{IF_IS_SINGLE_THREADED_NOTE}. No need to include any storage space for the operating system. This is "
    )
    + "only for task storage. Format: Integer. Range: [1, 65536]. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--is-hybrid-strategy-allowed",
    IS_HYBRID_STRATEGY_ALLOWED,
    type=bool,
    help=f"""
    This option further enhances infrastructure scalability beyond multi-cloud-zone/region auto-scaling.
    If true, more HPC strategies than the most optimal one will be allowed in infrastructure provisioning
    to maximize tasks running in parallel according to resource availability. In case the optimal HPC strategy
    has insufficient resource availability across the applicable cloud zones and regions at the time, the 2nd
    optimal strategy will be added to availability searching and infrastructure provisioning, and then the 3rd
    so on and so forth, until all allowed tasks are running in parallel. The allowed HPC strategies are subject
    to default marginal time and cost constraints with respect to the optimal one to limit the potential time
    and cost inflation.
    {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}
    """,
)
@click.option(
    "--allow-preemptible",
    ALLOW_PREEMPTIBLE,
    type=bool,
    help=f"""
    Preemptible resources are subject to reclaim by cloud service providers, resulting in the possibility of
    interruption to running tasks. Interrupted tasks will be automatically re-queued and retried until completion.
    When enabled, cloud strategy optimization will take into account both on-demand and preemptible-based HPC
    strategies, using statistical models to analyze expected runtime and costs considering interruption probability,
    benchmarking performance, and pricing dynamics in real time. Preemptible resources will be prioritized if they
    are deemed optimal for your workload. When "Allow hybrid strategy" is also enabled,  both preemptible and
    on-demand-based HPC strategies may be leveraged according to their optimality and resource availability.
    {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}
    """,
)
@click.option(
    "--is-resumable-workload",
    IS_RESUMABLE_WORKLOAD,
    type=bool,
    help=f"""
    Indicates if the workload can save work in progress and resume from a saved session or checkpoint upon re-execution.
    This information allows cloud strategy optimization to better estimate runtime and costs when using preemptible
    resources, minimizing the impact of interruptions.
    {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}
    """,
)
@click.option(
    "--is-subject-to-license-availability",
    IS_SUBJECT_TO_LICENSE_AVAILABILITY,
    type=bool,
    help=f"""
    When enabled, Fovus will attempt to auto-switch the base
    license feature in case the specified one is unavailable
    or auto-adjust the maximum vCPU constraint in case the HPC
    license is insufficient to avoid license wait time.
    {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}
    """,
)
@click.option(
    "--enable-hyperthreading",
    ENABLE_HYPERTHREADING,
    type=bool,
    help="For the CPUs that support hyperthreading, enabling hyperthreading allows two threads (vCPUs) to run "
    + "concurrently on a single CPU core. For HPC workloads, disabling hyperthreading may potentially result "
    + "in performance benifits with respect to the same CPU cores (e.g., 32 threads - 32 cores with "
    + "hyperthreading disabled v.s. 64 threads - 32 cores with hyperthreading enabled), whereas enabling "
    + "hyperthreading may potentially result in cost benifits with respect to the same parallelism (e.g., 64 "
    + "threads - 32 cores with hyperthreading enabled v.s. 64 threads - 64 cores with hyperthreading disabled)."
    + " "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--supported-cpu-architectures",
    SUPPORTED_CPU_ARCHITECTURES,
    type=click.Choice(["x86-64", "arm-64"]),
    multiple=True,
    help="The CPU architecture(s) compatible with your workload. Running your workload on an incompatible "
    + "CPU architecture may result in a failed job. "
    + f"{ANY_NUMBER_OF_EXPRESSIONS} {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--time-to-cost-priority-ration",
    TIME_TO_COST_PRIORITY_RATIO,
    type=str,
    help="Fovus will optimize the cloud strategies for your job execution to minimize the total runtime "
    + "and cost based on the time-to-cost priority ratio (TCPR) specified below. TCPR defines the weights "
    + "(amount of importance) to be placed on time minimization over cost minimization on a relative scale. "
    + "In particular, a ratio of 1/0 or 0/1 will enforce cloud strategies to pursue the minimum achievable "
    + 'runtime or cost without consideration of cost or runtime, respectively. Format must be "num1/num2" '
    + "where num1 + num2 = 1, 0 <= num1 <= 1, and 0 <= num2 <= 1. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--license-consumption-profile",
    LICENSE_CONSUMPTION_PROFILE,
    type=str,
    help="licenseConsumptionProfile defines the pattern of license draw based on running conditions, "
    + "such as vCPU or GPU parallelism. When an LCP is specified, the license consumption constraints "
    + "for queue and auto-scaling will be automatically extracted based on the running conditions defined by "
    + "the optimal cloud strategy. licenseConsumptionProfile has a higher precedence than licenseCountPerTask."
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--walltime-hours",
    WALLTIME_HOURS,
    type=float,
    help="The maximum time each task is allowed to run. A task will be terminated without a condition "
    + "once the walltime timer expires. Format: Real (e.g., 1.5). Range: >0. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--post-processing-walltime-hours",
    POST_PROCESSING_WALLTIME_HOURS,
    type=float,
    help="The maximum time each task is allowed to run Post Processing Task. "
    + "A task will be terminated without a condition "
    + "once the walltime timer expires. Format: Real (e.g., 1.5). Range: >0. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--post-processing-storage-gib",
    POST_PROCESSING_STORAGE_GIB,
    type=int,
    help="The total size of local SSD storage required to support the execution of post processing task. "
    + "No need to include any storage space for the operating system. This is "
    + "only for task storage. Format: Integer. Range: [1, 65536]. "
    + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--post-processing-run-command",
    POST_PROCESSING_RUN_COMMAND,
    type=str,
    help="Specify the command lines to launch post processing task. "
    + "The same command lines will be executed under the "
    + f"working directory of post processing task. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
)
@click.option(
    "--post-processing-task-name",
    POST_PROCESSING_TASK_NAME,
    type=str,
    help="Specify the folder name of post processing task. " + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
)
@click.option(
    "--search-output-keywords",
    SEARCH_OUTPUT_KEYWORDS,
    type=str,
    multiple=True,
    help="Specify the keywords to be used during the keyword search at the end of each task. "
    + "The 'AND' logic is applied when multiple keywords are provided. "
    + " ".join((ANY_NUMBER_OF_EXPRESSIONS, USED_FOR_OVERRIDING_JOB_CONFIG_VALUES)),
)
@click.option(
    "--search-output-files",
    SEARCH_OUTPUT_FILES,
    type=str,
    multiple=True,
    help="The desire output files to be used during the keyword search.\n\n"
    + " ".join((
        r"""
        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. out?/\*.txt matches any .txt file in folders out1, out2, etc.

        E.g. folder???/file.txt matches folder001/file.txt, folder123/file.txt, etc.\n\n
        """,
        ANY_NUMBER_OF_EXPRESSIONS,
        USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
    )),
)
# Needed for Click command input
# pylint: disable=too-many-arguments
def job_create_command(
    job_config_file_path: str,
    job_directory: str,
    include_paths_tuple: Tuple[str, ...],
    exclude_paths_tuple: Tuple[str, ...],
    project_name: Optional[str],
    email_notification: Optional[bool],
    **job_options,
):
    """
    Upload files to Fovus and create a new job.

    Creates .fovus folder inside JOB_DIRECTORY, which contains data
    about the job and enables checking job status and downloading
    job files using the JOB_DIRECTORY.

    JOB_CONFIG_FILE_PATH is the file path to a Fovus job config JSON.
    Values given in this file will be used unless they are overridden
    by CLI input. The job config JSON must follow the structure given
    in the provided job config templates, which are generated when the
    fovus config open command is used and will be located in
    ~/.fovus/job_configs.

    JOB_DIRECTORY is the root directory of the job folder. A job
    folder contains one or multiple task folders. Each folder uploaded
    under the job folder will be considered a task of the job. Each
    task folder is a self-contained folder containing the necessary
    input files and scripts to run the task. For a job that has N
    tasks (e.g. a DOE job with N simulation tasks), N task folders
    must exist under the job folder and be uploaded.
    """
    include_paths = Util.parse_include_exclude_paths(include_paths_tuple)
    exclude_paths = Util.parse_include_exclude_paths(exclude_paths_tuple)

    job_options = {
        key: (None if len(value) == 0 else list(value)) if isinstance(value, tuple) else value
        for key, value in job_options.items()
    }

    print("Creating Fovus API adapter and Fovus S3 adapter and authenticating...")
    fovus_api_adapter = FovusApiAdapter()

    user_id = fovus_api_adapter.get_user_id()
    workspace_id = fovus_api_adapter.get_workspace_id()
    job_options[TIMESTAMP] = FovusApiUtil.generate_timestamp()
    job_options[JOB_ID] = FovusApiUtil.generate_job_id(job_options[TIMESTAMP], user_id)

    fovus_s3_adapter = FovusS3Adapter(
        fovus_api_adapter,
        root_directory_path=job_directory,
        job_id=job_options[JOB_ID],
        include_paths=include_paths,
        exclude_paths=exclude_paths,
    )
    Util.print_success_message(GENERIC_SUCCESS)

    _confirm_enable_debug_mode(job_options)
    _confirm_set_auto_delete_days(fovus_api_adapter, workspace_id, job_options)

    project_id = _find_project_id_from_name(fovus_api_adapter, project_name)

    print("Creating and validating create job request...")
    create_job_request = FovusApiAdapter.get_create_job_request(job_config_file_path, workspace_id, job_options)
    fovus_api_adapter.make_dynamic_changes_to_create_job_request(create_job_request)
    validator = FovusApiValidator(create_job_request, ApiMethod.CREATE_JOB, job_directory)
    validator.validate()
    Util.print_success_message(GENERIC_SUCCESS)

    create_job_request[EMAIL_NOTIFICATION] = _is_email_on_job_completion_enabled(fovus_api_adapter, email_notification)

    fovus_api_adapter.create_zombie_job_check_scheduler({
        "jobId": job_options[JOB_ID],
        "workspaceId": workspace_id,
    })

    skip_create_job_info_folder = Util.is_nextflow_job()
    is_workload_manager_used = fovus_api_adapter.is_workload_manager_used(create_job_request)

    empty_folderpath_list = fovus_s3_adapter.upload_job_files(
        skip_create_job_info_folder=skip_create_job_info_folder, is_workload_manager_used=is_workload_manager_used
    )
    create_job_request[EMPTY_FOLDER_LIST] = empty_folderpath_list

    create_job_request[PROJECT_ID] = project_id

    print("Creating job...")
    fovus_api_adapter.create_job(create_job_request)
    Util.print_success_message(GENERIC_SUCCESS)
    print(OUTPUTS)
    print(
        "\n".join((
            "Job name:",
            create_job_request["jobName"],
            "Job ID:",
            job_options[JOB_ID],
        ))
    )


def _confirm_enable_debug_mode(job_options: dict):
    if job_options.get(DEBUG_MODE):
        print(
            "In debug mode, compute nodes will stay alive after each task execution until the task walltime is "
            + "reached to allow addtional time for debugging via SSH. Make sure to terminate your task or job "
            + "manually after debugging to avoid unnecessary charges for the additional time."
        )
        print("Are you sure you want to enable debug mode? (y/n):")
        if input() == "y":
            job_options[DEBUG_MODE] = True
            Util.print_success_message("Debug mode enabled")
        else:
            job_options[DEBUG_MODE] = False
            print("Debug mode disabled")


def _confirm_set_auto_delete_days(fovus_api_adapter, workspace_id, job_options: dict):
    min_delete_days = 1
    max_delete_days = 1095  # 3 years

    is_auto_delete_present = False
    if job_options.get(AUTO_DELETE_DAYS) and str(job_options.get(AUTO_DELETE_DAYS)).isdigit():
        is_auto_delete_present = True

    is_default_timer_applied = False
    workspace_settings = fovus_api_adapter.get_workspace_settings(workspace_id)
    auto_delete_settings = workspace_settings["autoDeleteSettings"]
    if auto_delete_settings["isEnabled"]:
        if auto_delete_settings["autoDeleteAccess"] == AutoDeleteAccess.ADMIN:
            if not is_auto_delete_present:
                job_options[AUTO_DELETE_DAYS] = auto_delete_settings["defaultDays"]
                is_default_timer_applied = True
                if job_options[AUTO_DELETE_DAYS] != 0:
                    Util.print_warning_message(
                        f"Default auto-delete timer of {job_options.get(AUTO_DELETE_DAYS)} days"
                        + " has been applied to all submitted jobs by the admin."
                    )
            else:
                workspace_role = fovus_api_adapter.get_workspace_role()
                if workspace_role != WorkspaceRole.ADMIN:
                    job_options[AUTO_DELETE_DAYS] = auto_delete_settings["defaultDays"]
                    is_default_timer_applied = True
                    if job_options[AUTO_DELETE_DAYS] != 0:
                        Util.print_warning_message(
                            f"Default auto-delete timer of {job_options.get(AUTO_DELETE_DAYS)} days"
                            + " has been applied to all submitted jobs by the admin. Any user-defined "
                            + "auto-delete timer will be ignored."
                        )
        elif not is_auto_delete_present:
            job_options[AUTO_DELETE_DAYS] = auto_delete_settings["defaultDays"]
            is_default_timer_applied = True
            if job_options[AUTO_DELETE_DAYS] != 0:
                Util.print_warning_message(
                    f"Default auto-delete timer of {job_options.get(AUTO_DELETE_DAYS)} days"
                    + " has been applied to all submitted jobs by the admin."
                )
    elif is_auto_delete_present and not auto_delete_settings["isEnabled"]:
        job_options[AUTO_DELETE_DAYS] = 0
        Util.print_warning_message(
            "Auto-delete timer is disabled by the admin. Any user-defined " + "auto-delete timer will be ignored."
        )
        return

    if not is_default_timer_applied and job_options.get(AUTO_DELETE_DAYS):
        if (
            not str(job_options.get(AUTO_DELETE_DAYS)).isdigit()
            or int(job_options.get(AUTO_DELETE_DAYS, 0)) < min_delete_days
            or int(job_options.get(AUTO_DELETE_DAYS, 0)) > max_delete_days
        ):
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                "Missing class name",
                f"Invalid scheduled delete days value of {job_options.get(AUTO_DELETE_DAYS)} for "
                + f"'{AUTO_DELETE_DAYS}'. Scheduled delete days value must be a positive number"
                + f" and in a range of [{min_delete_days}, {max_delete_days}].",
            )
        if Util.confirm_action(
            message="This job will be submitted with an auto-delete timer that is set to"
            + f" {job_options.get(AUTO_DELETE_DAYS)} days. The auto-delete timer starts"
            + " to tick upon job completion or termination. The job will be permanently "
            + "deleted when the timer expires.Are you sure you want to continue? (y/n):",
        ):
            Util.print_success_message("Auto-delete is configured")
        else:
            job_options[AUTO_DELETE_DAYS] = 0
            Util.print_error_message("Auto-delete is not configured")


def _find_project_id_from_name(fovus_api_adapter: FovusApiAdapter, project_name: Optional[str] = None) -> Optional[str]:
    active_projects = fovus_api_adapter.list_active_projects()

    if project_name is None:
        project_setting = fovus_api_adapter.get_user_setting(
            {"workspaceId": fovus_api_adapter.workspace_id, "key": UserSettings.DEFAULT_PROJECT_ID.value}
        )

        default_project_id = project_setting.get("value", None)
        if default_project_id is not None:
            print("Project name is not provided. Attempting to use your default project...")
            matched_projects = [project for project in active_projects if project["projectId"] == default_project_id]
            if len(matched_projects) == 0:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    "Missing class name",
                    "Your configured default project was archived and is no longer available. "
                    + "Please update it on Fovus website or specify a different project name. "
                    + "To see valid project names, run 'fovus projects list'.",
                )
            print(f"Project '{matched_projects[0]['name']}' will be used.")
        return default_project_id
    print(f"Found project name: {project_name}. Validating project name...")
    if project_name.lower() == "none":
        print("Project name is 'None'. This job will not be associated with any project.")
        return None
    if len(active_projects) == 0:
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            "Missing class name",
            "No projects are available. Please contact your cost center admin to create a new project.",
        )
    matched_projects = [project for project in active_projects if project["name"] == project_name]
    if len(matched_projects) == 0:
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            "Missing class name",
            f"Project name '{project_name}' is not found. "
            + "Please provide a valid project name. To see valid project names, run 'fovus projects list'.",
        )
    project_id = matched_projects[0]["projectId"]
    return project_id


def _is_email_on_job_completion_enabled(fovus_api_adapter: FovusApiAdapter, email_notification: Optional[bool]) -> bool:
    if email_notification:
        print("Email notification is enabled for job.")
        return True

    if email_notification is False:
        print("Email notification is disabled for job.")
        return False

    job_notification_setting = fovus_api_adapter.get_user_setting(
        {"workspaceId": fovus_api_adapter.workspace_id, "key": UserSettings.IS_JOB_NOTIFICATION_ENABLED.value}
    )
    is_notification_enabled = job_notification_setting.get("value", False)

    print(
        "Email notification setting is not provided. "
        + f"Apply your user default setting '{'Enabled' if is_notification_enabled else 'Disabled'}'..."
    )

    return is_notification_enabled
