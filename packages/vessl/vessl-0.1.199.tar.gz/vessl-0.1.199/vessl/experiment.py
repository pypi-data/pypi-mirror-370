import os
from typing import List, Optional

from vessl.openapi_client import DistributedExperimentCreateAPIInput
from vessl.openapi_client.models import (
    ExperimentCreateAPIInput,
    InfluxdbWorkloadLog,
    OrmHyperparameter,
    ResponseExperimentInfo,
    ResponseExperimentListResponse,
    StorageFile,
)
from vessl import vessl_api
from vessl.kernel_cluster import read_cluster
from vessl.kernel_resource_spec import (
    _configure_custom_kernel_resource_spec,
    read_kernel_resource_spec,
)
from vessl.organization import _get_organization_name
from vessl.project import _get_project_name
from vessl.util import logger
from vessl.util.common import safe_cast
from vessl.util.constant import MOUNT_PATH_OUTPUT, SOURCE_TYPE_OUTPUT
from vessl.util.exception import (
    InvalidParamsError,
    VesslApiException,
)
from vessl.volume import (
    _configure_volume_mount_requests,
    copy_volume_file,
    list_volume_files,
)


def read_experiment(
    experiment_number: int,
    **kwargs,
) -> ResponseExperimentInfo:
    """Read experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): experiment number.

    Example:
        ```python
        vessl.read_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_read_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def read_experiment_by_id(experiment_id: int) -> ResponseExperimentInfo:
    result = vessl_api.experiment_read_by_idapi(experiment_id=experiment_id)
    assert isinstance(result, ResponseExperimentInfo)
    return result


def update_experiment(experiment_number: int, message: str, **kwargs):
    """Update experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): experiment number.
        message(str): message of experiment to update.

    Example:
        ```python
        vessl.update_experiment(
            experiment_number=23,
            message="Update # of hidden layer 32->64",
        )
        ```
    """
    return vessl_api.experiment_update_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        experiment_update_api_input={"message": message},
    )


def list_experiments(
    statuses: List[str] = None,
    **kwargs,
) -> List[ResponseExperimentListResponse]:
    """List experiments in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        statuses(List[str]): A list of status filter. Defaults to None.

    Example:
        ```python
        vessl.list_experiments(
            statuses=["completed"]
        )
        ```
    """
    statuses = (
        [",".join(statuses)] if statuses else None
    )  # since openapi-generator uses repeating params instead of commas

    query_keys = set(["limit", "offset"])
    query_kwargs = {k: v for k, v in kwargs.items() if k in query_keys}

    return vessl_api.experiment_list_api(
        statuses=statuses,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        **query_kwargs,
    ).results


def create_experiment(
    cluster_name: str,
    start_command: str,
    cluster_node_names: List[str] = None,
    kernel_resource_spec_name: str = None,
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: str = None,
    gpu_type: str = None,
    gpu_limit: int = None,
    kernel_image_url: str = None,
    docker_credentials_id: Optional[int] = None,
    *,
    message: str = None,
    termination_protection: bool = False,
    hyperparameters: List[str] = None,
    secrets: List[str] = None,
    dataset_mounts: List[str] = None,
    model_mounts: List[str] = None,
    git_ref_mounts: List[str] = None,
    git_diff_mount: str = None,
    local_files: List[str] = None,
    use_vesslignore: bool = True,
    upload_local_git_diff: bool = False,
    archive_file_mount: str = None,
    object_storage_mounts: List[str] = None,
    root_volume_size: str = None,
    working_dir: str = None,
    output_dir: str = MOUNT_PATH_OUTPUT,
    worker_count: int = 1,
    framework_type: str = None,
    service_account: str = "",
    **kwargs,
) -> ResponseExperimentInfo:
    """Create experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`. You can also configure git info by passing
    `git_branch` or `git_ref` as `**kwargs`. Pass `use_git_diff=True` if
    you want to run experiment with uncommitted changes and pass
    `use_git_diff_untracked=True` if you want to run untracked changes(only
    valid if `use_git_diff` is set).

    Args:
        cluster_name(str): Cluster name(must be specified before other options).
        cluster_node_names(List[str]): Node names. The experiment will run on
            one of these nodes. Defaults to None(all).
        start_command(str): Start command to execute in experiment container.
        kernel_resource_spec_name(str):  Resource type to run an experiment (for
            managed cluster only). Defaults to None.
        processor_type(str) cpu or gpu (for custom cluster only). Defaults to
            None.
        cpu_limit(float): Number of vCPUs (for custom cluster only). Defaults to
            None.
        memory_limit(str): Memory limit in GiB (for custom cluster only).
            Defaults to None.
        gpu_type(str): GPU type (for custom cluster only). Defaults to None.
        gpu_limit(int): Number of GPU cores (for custom cluster only). Defaults
            to None.
        kernel_image_url(str): Kernel docker image URL. Defaults to None.
        docker_credentials_id(int): Docker credential id. Defaults to None.
        message(str): Message. Defaults to None.
        termination_protection(bool): True if termination protection is enabled,
            False otherwise. Defaults to False.
        hyperparameters(List[str]): A list of hyperparameters. Defaults to None.
        secrets(List[str]): A list of secrets in form "KEY=VALUE". Defaults to None.
        dataset_mounts(List[str]): A list of dataset mounts. Defaults to None.
        model_mounts(List[str]): A list of model mounts. Defaults to None.
        git_ref_mounts(List[str]): A list of git repository mounts. Defaults to
            None.
        git_diff_mount(str): Git diff mounts. Defaults to None.
        local_files(List[str]): A list of local files to upload. Defaults to
            None.
        use_vesslignore(bool): True if local files matching glob patterns
            in .vesslignore files should be ignored. Patterns apply relative to
            the directory containing that .vesslignore file.
        upload_local_git_diff(bool): True if local git diff to upload, False
            otherwise. Defaults to False.
        archive_file_mount(str): Local archive file mounts. Defaults to None.
        object_storage_mounts(List[str]): Object storage mounts. Defaults to None.
        root_volume_size(str): Root volume size. Defaults to None.
        working_dir(str): Working directory path. Defaults to None.
        output_dir(str): Output directory path. Defaults to "/output/".
        worker_count(int): Number of workers(for distributed experiment only).
            Defaults to 1.
        framework_type(str): Specify "pytorch" or "tensorflow" (for distributed
            experiment only). Defaults to None.
        service_account(str): Service account name. Defaults to "".

    Example:
        ```python
        vessl.create_experiment(
            cluster_name="aws-apne2",
            kernel_resource_spec_name="v1.cpu-4.mem-13",
            kernel_image_url="public.ecr.aws/vessl/kernels:py36.full-cpu",
            dataset_mounts=["/input/:mnist"]
            start_command="pip install requirements.txt && python main.py",
        )
        ```
    """
    cluster = read_cluster(cluster_name)

    # Only allow service_account when the cluster is user-managed
    if cluster.is_vessl_managed and service_account:
        raise InvalidParamsError(
            "--service-account: only supported when running experiment in user-managed clusters"
        )

    kernel_resource_spec = kernel_resource_spec_id = None
    if kernel_resource_spec_name:
        kernel_resource_spec_id = read_kernel_resource_spec(
            cluster.id,
            kernel_resource_spec_name,
        ).id
    else:
        kernel_resource_spec = _configure_custom_kernel_resource_spec(
            processor_type,
            cpu_limit,
            memory_limit,
            gpu_type,
            gpu_limit,
        )

    volume_mount_requests = _configure_volume_mount_requests(
        dataset_mounts=dataset_mounts,
        git_ref_mounts=git_ref_mounts,
        git_diff_mount=git_diff_mount,
        archive_file_mount=archive_file_mount,
        object_storage_mounts=object_storage_mounts,
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        output_dir=output_dir,
        model_mounts=model_mounts,
        local_files=local_files,
        use_vesslignore=use_vesslignore,
        upload_local_git_diff=upload_local_git_diff,
        **kwargs,
    )
    if worker_count > 1:
        return vessl_api.distributed_experiment_create_api(
            organization_name=_get_organization_name(**kwargs),
            project_name=_get_project_name(**kwargs),
            distributed_experiment_create_api_input=DistributedExperimentCreateAPIInput(
                cluster_id=cluster.id,
                hyperparameters=[
                    OrmHyperparameter(key=key, value=str(value))
                    for key, value in map(
                        lambda hyperparameter: hyperparameter.split("="),
                        (hyperparameters or []),
                    )
                ],
                framework_type=framework_type,
                image_url=kernel_image_url,
                docker_credentials_id=docker_credentials_id,
                message=message,
                worker_replicas=worker_count,
                worker_resource_spec=kernel_resource_spec,
                worker_resource_spec_id=kernel_resource_spec_id,
                start_command=start_command,
                termination_protection=termination_protection,
                volumes=volume_mount_requests,
                service_account_name=service_account,
            ),
        )

    organization_name = _get_organization_name(**kwargs)
    cluster_node_ids = None
    if not cluster.is_savvihub_managed and cluster_node_names:
        nodes = vessl_api.custom_cluster_node_list_api(
            organization_name=organization_name,
            cluster_id=cluster.id,
        ).nodes
        cluster_node_ids = [node.id for node in nodes if node.name in cluster_node_names]

    all_hyperparameters: List[OrmHyperparameter] = [
        OrmHyperparameter(key=key, value=str(value))
        for key, value in map(
            lambda hyperparameter: hyperparameter.split("="),
            (hyperparameters or []),
        )
    ] + [
        OrmHyperparameter(key=key, value=str(value), secret=True)
        for key, value in map(
            lambda secret: secret.split("="),
            (secrets or []),
        )
    ]

    return vessl_api.experiment_create_api(
        organization_name=organization_name,
        project_name=_get_project_name(**kwargs),
        experiment_create_api_input=ExperimentCreateAPIInput(
            cluster_id=cluster.id,
            cluster_node_ids=cluster_node_ids,
            hyperparameters=all_hyperparameters,
            image_url=kernel_image_url,
            docker_credentials_id=docker_credentials_id,
            message=message,
            resource_spec=kernel_resource_spec,
            resource_spec_id=kernel_resource_spec_id,
            start_command=start_command,
            termination_protection=termination_protection,
            volumes=volume_mount_requests,
            service_account_name=service_account,
        ),
    )


def list_experiment_logs(
    experiment_number: int,
    tail: int = 200,
    worker_number: int = 0,
    after: int = 0,
    **kwargs,
) -> List[InfluxdbWorkloadLog]:
    """List experiment logs in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_name (int): Experiment number.
        tail (int): The number of lines to display from the end. Display all if
            -1. Defaults to 200.
        worker_number (int): Override default worker number (for distributed
            experiments only). Defaults to 0.
        after (int): The number of starting lines to display from the start.
            Defaults to 0.

    Example:
        ```python
        vessl.list_experiment_logs(
            experiment_number=23,
        )
        ```
    """
    if tail == -1:
        tail = None

    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_distributed:
        str_worker_number = safe_cast(worker_number, str, "0")
        return vessl_api.distributed_experiment_logs_api(
            experiment_number=experiment_number,
            limit=tail,
            organization_name=_get_organization_name(**kwargs),
            project_name=_get_project_name(**kwargs),
            distributed_number=worker_number,
        ).logs[str_worker_number]

    return vessl_api.experiment_logs_api(
        experiment_number=experiment_number,
        limit=tail,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        after=after,
    ).logs


def list_experiment_output_files(
    experiment_number: int,
    need_download_url: bool = False,
    recursive: bool = True,
    worker_number: int = 0,
    **kwargs,
) -> List[StorageFile]:
    """List experiment output files in the default organization/project. If you
    want to override the default organization/project, then pass
    `organization_name` or `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.
        need_download_url(bool): True if you need a download URL, False
            otherwise. Defaults to False.
        recursive(bool): True if list files recursively, False otherwise.
            Defaults to True.
        worker_number(int): Override default worker number (for distributed
            experiments only). Defaults to 0.

    Example:
        ```python
        vessl.list_experiment_output_files(
            experiment_number=23,
        )
        ```
    """
    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_local:
        volume_id = experiment.local_execution_spec.output_volume_id
        return list_volume_files(
            volume_id=volume_id,
            need_download_url=need_download_url,
            path="",
            recursive=recursive,
        )

    if experiment.is_distributed:
        worker_replicas = experiment.distributed_spec.pytorch_spec.worker_replicas
        if worker_number >= worker_replicas:
            raise InvalidParamsError(
                "worker-number: should be less than {}".format(worker_replicas)
            )

        mounts = experiment.volume_mounts_list[worker_number].mounts
    else:
        mounts = experiment.volume_mounts.mounts

    for volume_mount in mounts:
        if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
            base_path = volume_mount.volume.sub_path
            try:
                files = list_volume_files(
                    volume_id=volume_mount.volume.volume_id,
                    need_download_url=need_download_url,
                    path=base_path,
                    recursive=recursive,
                )
            except VesslApiException:
                files = []
            for file in files:
                file.path = os.path.relpath(f"/{file.path}", base_path)
            return files

    logger.info("No output volume mounted")


def download_experiment_output_files(
    experiment_number: int,
    dest_path: str = os.path.join(os.getcwd(), "output"),
    worker_number: int = 0,
    **kwargs,
) -> None:
    """Download experiment output files in the default organization/project.
    If you want to override the default organization/project, then pass
    `organization_name` or `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.
        dest_path(str): Local download path. Defaults to "./output".
        worker_number(int): Override default worker number (for distributed
            experiments only). Defaults to 0.

    Example:
        ```python
        vessl.download_experiment_output_files(
            experiment_number=23,
        )
        ```
    """
    experiment = read_experiment(experiment_number, **kwargs)

    if experiment.is_local:
        volume_id = experiment.local_execution_spec.output_volume_id
        return copy_volume_file(
            source_volume_id=volume_id,
            source_path="/.",
            dest_volume_id=None,
            dest_path=dest_path,
        )
    if experiment.is_distributed:
        worker_replicas = experiment.distributed_spec.pytorch_spec.worker_replicas
        if worker_number >= worker_replicas:
            raise InvalidParamsError(
                "worker-number: should be less than {}".format(worker_replicas)
            )

        for volume_mount in experiment.volume_mounts_list[worker_number].mounts:
            if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
                return copy_volume_file(
                    source_volume_id=volume_mount.volume.volume_id,
                    source_path="/.",
                    dest_volume_id=None,
                    dest_path=dest_path,
                )
    else:
        for volume_mount in experiment.volume_mounts.mounts:
            if volume_mount.source_type == SOURCE_TYPE_OUTPUT:
                return copy_volume_file(
                    source_volume_id=volume_mount.volume.volume_id,
                    source_path="/.",
                    dest_volume_id=None,
                    dest_path=dest_path,
                )

    logger.info("No output volume mounted")


def terminate_experiment(experiment_number: int, **kwargs) -> ResponseExperimentInfo:
    """Terminate experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.

    Example:
        ```python
        vessl.terminate_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_terminate_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )


def list_github_code_refs(workload_id: int):
    return vessl_api.git_hub_code_refs_api(
        workload_id=workload_id,
    )


def delete_experiment(experiment_number: int, **kwargs):
    """Delete experiment in the default organization/project. If you want to
    override the default organization/project, then pass `organization_name` or
    `project_name` as `**kwargs`.

    Args:
        experiment_number(int): Experiment number.

    Example:
        ```python
        vessl.delete_experiment(
            experiment_number=23,
        )
        ```
    """
    return vessl_api.experiment_delete_api(
        experiment_number=experiment_number,
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    )
