import os
import tempfile
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlparse

from vessl.openapi_client import OrmVolumeMountRequestSourceModelVolume
from vessl.openapi_client.models import (
    OrmVolumeMountRequest,
    OrmVolumeMountRequests,
    OrmVolumeMountRequestSourceArchiveFile,
    OrmVolumeMountRequestSourceCode,
    OrmVolumeMountRequestSourceDataset,
    OrmVolumeMountRequestSourceDatasetVersion,
    OrmVolumeMountRequestSourceObjectStorage,
    RunExecutionVolumeV2CreateAPIInput,
    StorageFile,
    VolumeFileCopyAPIInput,
    VolumeFileCreateAPIInput,
)
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.project import _get_project
from vessl.util import constant
from vessl.util.common import safe_cast
from vessl.util.constant import (
    DATASET_VERSION_HASH_LATEST,
    EXPERIMENT_WORKING_DIR,
    MOUNT_PATH_EMPTY_DIR,
    SOURCE_TYPE_ARCHIVE_FILE,
    SOURCE_TYPE_CODE,
    SOURCE_TYPE_DATASET,
    SOURCE_TYPE_DATASET_VERSION,
    SOURCE_TYPE_EMPTY_DIR,
    SOURCE_TYPE_MODEL_VOLUME,
    SOURCE_TYPE_OBJECT_STORAGE,
    SOURCE_TYPE_OUTPUT,
    TEMP_DIR,
)
from vessl.util.downloader import Downloader
from vessl.util.exception import (
    GitError,
    InvalidParamsError,
    InvalidVolumeFileError,
    VesslApiException,
)
from vessl.util.git_local import get_git_diff_path, get_git_ref, get_git_repo
from vessl.util.random import random_string
from vessl.util.tar import Tar
from vessl.util.uploader import Uploader
from vessl.util.volume import VolumeFileTransfer


def read_volume_file(volume_id: int, path: str) -> StorageFile:
    """Read a file in the volume.

    Args:
        volume_id(int): Volume ID.
        path(str): Path within the volume.

    Example:
        ```python
        vessl.read_volume_file(
            volume_id=123456,
            path="train.csv",
        )
        ```
    """
    return vessl_api.volume_file_read_api(volume_id=volume_id, path=path)


def list_volume_files(
    volume_id: int,
    need_download_url: bool = False,
    path: str = "",
    recursive: bool = False,
) -> List[StorageFile]:
    """List files in the volume.

    Args:
        volume_id(int): Volume ID.
        need_download_url(bool): True if you need a download URL, False
            otherwise. Defaults to False.
        path(str): Path within the volume. Defaults to root.
        recursive(bool): True if list files recursively, False otherwise.
            Defaults to False.

    Example:
        ```python
        vessl.list_volume_files(
            volume_id=123456,
        )
        ```
    """
    try:
        result = vessl_api.volume_file_list_api(
            volume_id=volume_id,
            recursive=recursive,
            path=path,
            need_download_url=need_download_url,
        ).results
    except VesslApiException as e:
        if path == "":
            result = []
        else:
            raise e

    return sorted(result, key=lambda x: x.path)


def create_volume_file(volume_id: int, is_dir: bool, path: str) -> StorageFile:
    """Create file in the volume.

    Args:
        volume_id(int): Volume ID.
        is_dir(bool): True if a file is directory, False otherwise.
        path(str): Path within the volume.

    Example:
        ```python
        vessl.create_volume_file(
            volume_id=123456,
            is_dir=False,
            path="models"
        )
        ```
    """
    result = vessl_api.volume_file_create_api(
        volume_id=volume_id,
        volume_file_create_api_input=VolumeFileCreateAPIInput(
            is_dir=is_dir,
            path=path,
        ),
    )
    assert isinstance(result, StorageFile)
    return result


def delete_volume_file(
    volume_id: int,
    path: str,
):
    """Delete file in the volume.

    Args:
        volume_id(int): Volume ID.
        path(str): Path within the volume.

    Example:
        ```python
        vessl.delete_volume_file(
            volume_id=123456,
            path="model.pth",
        )
        ```
    """
    vessl_api.volume_file_delete_api(
        volume_id=volume_id,
        path=path,
    )


def upload_volume_file(volume_id: int, path: str) -> StorageFile:
    """Upload file in the volume.

    Args:
        volume_id(int): Volume ID.
        path(str): Local file path to upload

    Example:
        ```python
        vessl.upload_volume_file(
            volume_id=123456,
            path="model.pth",
        )
        ```
    """
    return vessl_api.volume_file_uploaded_api(volume_id=volume_id, path=path)


def copy_volume_file(
    source_volume_id: Optional[int],
    source_path: str,
    dest_volume_id: Optional[int],
    dest_path: str,
    quiet: bool = False,
) -> Optional[List[StorageFile]]:
    """Copy file either from local to remote, remote to local, or remote to
    remote.

    Args:
        source_volume_id(Optional[int]): Source volume file id. If not
            specified, source is assumed to be local.
        source_path(str): If source_volume_id is empty, local source path.
            Otherwise, remote source path.
        dest_volume_id(Optional[int]): Destination volume file id. If not
            specified, destination is assumed to be local.
        dest_path(str): If dest_volume_id is empty, local destination path.
            Otherwise, remote destination path.
        quiet(bool): True if the muted output, False otherwise. Defaults to
            False.

    Example:
        ```python
        vessl.copy_volume_file(
            source_volume_id=123456,
            source_path="model.pth",
            dest_volume_id=123457,
            dest_path="model.pth",
        )
        ```
    """
    if source_volume_id is None and dest_volume_id:
        return VolumeFileTransfer(dest_volume_id).upload(source_path, dest_path)

    if dest_volume_id is None and source_volume_id:
        VolumeFileTransfer(source_volume_id).download(source_path, dest_path)
        return

    if source_volume_id and dest_volume_id:
        return _copy_volume_file_remote_to_remote(
            source_volume_id,
            source_path,
            dest_volume_id,
            dest_path,
        )


def _copy_volume_file_local_to_remote(
    source_path: str, dest_volume_id: int, dest_path: str
) -> List[StorageFile]:
    """Copy local to remote

    Behavior works like linux cp command
    - `source_path` is file
      - `dest_path` is not a directory: copy as file with new name
      - `dest_path` is directory: copy file into directory with original name
    - `source_path` is directory
      - `dest_path` is file: error
      - `dest_path` does not exist: create `dest_path` and copy contents of `source_path`
      - `dest_path` exists: copy `source_path` as subdirectory of `dest_path`
    """

    output = "Successfully uploaded {} out of {} file(s)."
    source_path = source_path.rstrip("/")

    try:
        dest_file = read_volume_file(dest_volume_id, dest_path)
    except VesslApiException:
        dest_file = None

    if not os.path.isdir(source_path):
        if dest_file and (dest_file.is_dir or dest_path.endswith("/")):
            dest_path = os.path.join(dest_path, os.path.basename(source_path))

        insecure_skip_tls_verify = safe_cast(os.environ.get('VESSL_INSECURE_SKIP_TLS_VERIFY'), bool, False)
        verify_tls = not insecure_skip_tls_verify
        uploaded_file = Uploader.upload(source_path, dest_volume_id, dest_path, verify_tls)

        print(output.format(1, 1))
        return [uploaded_file]

    if dest_file and not dest_file.is_dir:
        raise InvalidVolumeFileError(f"Destination path is not a directory: {dest_path}.")

    if dest_file and dest_file.is_dir:
        dest_path = os.path.join(dest_path, os.path.basename(source_path))

    insecure_skip_tls_verify = safe_cast(os.environ.get('VESSL_INSECURE_SKIP_TLS_VERIFY'), bool, False)
    verify_tls = not insecure_skip_tls_verify

    paths = Uploader.get_paths_in_dir(source_path)
    uploaded_files = Uploader.bulk_upload(source_path, paths, dest_volume_id, dest_path, verify_tls)

    print(output.format(len(uploaded_files), len(paths)))
    return uploaded_files


def _copy_volume_file_remote_to_local(
    source_volume_id: int,
    source_path: str,
    dest_path: str,
    quiet: bool = False,
) -> None:
    """Copy remote to local

    Behavior works like linux cp command
    - `source_path` is file
      - `dest_path` is not a directory: copy as file with new name
      - `dest_path` is directory: copy file into directory with original name
    - `source_path` is directory
      - `dest_path` is file: error
      - `dest_path` does not exist: create `dest_path` and copy contents of `source_path` (like cp -r)
      - `dest_path` exists: copy `source_path` as subdirectory of `dest_path`
    """

    try:
        source_file = read_volume_file(source_volume_id, source_path)
    except VesslApiException:
        if os.path.isfile(dest_path):
            # Case where `source_path` is a directory and `dest_path` is an
            # existing filename
            raise InvalidVolumeFileError(f"Destination path is not a directory: {dest_path}.")

        files = list_volume_files(
            volume_id=source_volume_id,
            need_download_url=True,
            path=source_path,
            recursive=True,
        )

        Downloader.download(source_path, dest_path, *files, quiet=quiet)
        return

    file_name = os.path.basename(source_file.path)
    if os.path.isdir(dest_path):
        dest_path = os.path.join(dest_path, file_name)

        if os.path.isdir(dest_path):
            # Case where `source_path` is "a.txt", `dest_path` is "dir/", and
            # "dir/a.txt/" exists as a directory
            raise InvalidParamsError(
                f"Cannot overwrite directory {dest_path} with non-directory {file_name}."
            )

    Downloader.download(source_path, dest_path, source_file, quiet=quiet)


def _copy_volume_file_remote_to_remote(
    source_volume_id: int,
    source_path: str,
    dest_volume_id: int,
    dest_path: str,
) -> None:
    if source_volume_id != dest_volume_id:
        raise InvalidVolumeFileError("Files can only be copied within the same volume.")

    resp = vessl_api.volume_file_copy_api(
        volume_id=source_volume_id,
        volume_file_copy_api_input=VolumeFileCopyAPIInput(
            dest_path=dest_path,
            source_dataset_version="latest",
            source_path=source_path,
        ),
    )
    if resp.should_copy_from_local:
        with tempfile.TemporaryDirectory() as tmpdirname:
            VolumeFileTransfer(source_volume_id).download(source_path, tmpdirname)
            VolumeFileTransfer(dest_volume_id).upload(tmpdirname, dest_path)

    print(f"Successfully copied.")


def _print_volume_mount_requests_tree(
    requests: OrmVolumeMountRequests,
):
    print("Mount Info:")
    for request in requests.requests:
        if request.source_type == SOURCE_TYPE_ARCHIVE_FILE:
            print(f"ㄴ {request.mount_path} -> (Uploaded)")
        if request.source_type == SOURCE_TYPE_CODE:
            print(
                f"ㄴ {request.mount_path} -> Code [{request.code.git_provider}@{request.code.git_owner}/{request.code.git_repo}@{request.code.git_ref}]"
            )
        if request.source_type == SOURCE_TYPE_DATASET:
            print(f"ㄴ {request.mount_path} -> Dataset [{request.dataset.dataset_name}]")
        if request.source_type == SOURCE_TYPE_DATASET_VERSION:
            print(
                f"ㄴ {request.mount_path} -> Dataset [{request.dataset_version.dataset_name}@{request.dataset_version.dataset_version_hash}]"
            )
        if request.source_type == SOURCE_TYPE_MODEL_VOLUME:
            print(
                f"ㄴ {request.mount_path} -> Model [{request.model_volume.model_repository_name}/{request.model_volume.model_number}{request.model_volume.sub_path}]"
            )
        if request.source_type == SOURCE_TYPE_OUTPUT:
            print(f"ㄴ {request.mount_path} -> (output)")
        if request.source_type == SOURCE_TYPE_OBJECT_STORAGE:
            print(
                f"ㄴ {request.mount_path} -> Object Storage({request.object_storage.mode}) [{request.object_storage.bucket_path}]"
            )


def _configure_volume_mount_requests(
    dataset_mounts: Optional[List[str]],
    git_ref_mounts: Optional[List[str]],
    git_diff_mount: Optional[str],
    archive_file_mount: Optional[str],
    object_storage_mounts: Optional[List[str]],
    root_volume_size: Optional[str],
    working_dir: Optional[str],
    output_dir: Optional[str],
    model_mounts: Optional[List[str]] = None,
    local_files: Optional[List[str]] = None,
    use_vesslignore: Optional[bool] = True,
    upload_local_git_diff: bool = False,
    **kwargs,
) -> OrmVolumeMountRequests:
    requests = [
        _configure_volume_mount_request_empty_dir(),
        _configure_volume_mount_request_output(output_dir),
    ]

    if local_files:
        requests.extend(
            _configure_volume_mount_request_local_files(local_files, use_vesslignore, **kwargs)
        )

    if not git_ref_mounts and git_diff_mount is None and archive_file_mount is None:
        # No information for code mount is given - user is creating new experiment from CLI.
        # Generate VolumeMountRequest from projectRepository and local working directory
        requests.extend(_configure_volume_mount_request_local_git(upload_local_git_diff, **kwargs))
    else:
        # Explicit information for code mount is given - user is reproducing experiment from CLI.
        if git_ref_mounts:
            requests.extend(
                _configure_volume_mount_request_codes(git_ref_mounts, git_diff_mount, **kwargs)
            )
        if archive_file_mount is not None:
            requests.append(
                _configure_volume_mount_request_archive_file(archive_file_mount, **kwargs)
            )

    if dataset_mounts is not None:
        requests.extend(_configure_volume_mount_request_datasets(dataset_mounts, **kwargs))

    if model_mounts is not None:
        requests += [
            _configure_volume_mount_request_model(model_mount, **kwargs)
            for model_mount in model_mounts
        ]

    if object_storage_mounts is not None:
        requests.extend(_configure_volume_mount_request_object_storages(object_storage_mounts))

    requests = OrmVolumeMountRequests(
        root_volume_size=root_volume_size,
        working_dir=working_dir,
        requests=requests,
    )
    _print_volume_mount_requests_tree(requests)
    return requests


def _configure_volume_mount_request_datasets(
    dataset_mounts: List[str], should_add_project_datasets=True, **kwargs
) -> List[OrmVolumeMountRequest]:
    from vessl.dataset import read_dataset, read_dataset_version

    dataset_mount_map: Dict[int, OrmVolumeMountRequest] = {}
    if should_add_project_datasets:
        project = _get_project(**kwargs)
        for project_dataset in project.project_datasets:
            mount_path = project_dataset.mount_path
            dataset = project_dataset.dataset

            dataset_mount_map[dataset.id] = OrmVolumeMountRequest(
                source_type=SOURCE_TYPE_DATASET,
                mount_path=mount_path,
                dataset=OrmVolumeMountRequestSourceDataset(
                    dataset_id=dataset.id,
                    dataset_name=dataset.name,
                ),
            )

    for dataset_mount in dataset_mounts:
        mount_path, dataset_path = dataset_mount.split(":", 1)
        mount_path = os.path.join(mount_path, "")  # Ensure path ends in /

        organization_name = _get_organization_name(**kwargs)
        dataset_name = dataset_path
        dataset_version_hash = DATASET_VERSION_HASH_LATEST

        if "@" in dataset_path:
            # Example: mnist@3d1e0f91c
            dataset_name, dataset_version_hash = dataset_path.rsplit("@", 1)

        if "/" in dataset_name:
            # Example: org1/mnist@3d1e0f91c
            organization_name, dataset_name = dataset_name.split("/", 1)

        dataset = read_dataset(dataset_name, organization_name=organization_name)

        if not dataset.is_version_enabled:
            dataset_mount_map[dataset.id] = OrmVolumeMountRequest(
                source_type=SOURCE_TYPE_DATASET,
                mount_path=mount_path,
                dataset=OrmVolumeMountRequestSourceDataset(
                    dataset_id=dataset.id,
                    dataset_name=dataset_name,
                ),
            )

        if dataset_version_hash != DATASET_VERSION_HASH_LATEST:
            dataset_version_hash = read_dataset_version(
                dataset.id, dataset_version_hash
            ).version_hash  # Get full version hash from truncated one given by input

            dataset_mount_map[dataset.id] = OrmVolumeMountRequest(
                source_type=SOURCE_TYPE_DATASET_VERSION,
                mount_path=mount_path,
                dataset_version=OrmVolumeMountRequestSourceDatasetVersion(
                    dataset_id=dataset.id,
                    dataset_name=dataset_name,
                    dataset_version_hash=dataset_version_hash,
                ),
            )

    return list(dataset_mount_map.values())


def _configure_volume_mount_request_model(model_mount: str, **kwargs) -> OrmVolumeMountRequest:
    from vessl.model import read_model

    mount_path, model_path = model_mount.split(":", 1)
    model_repository_name, model_number = model_path.split("/", 1)

    mount_path = os.path.join(mount_path, "")  # Ensure path ends in /

    model = read_model(repository_name=model_repository_name, model_number=model_number, **kwargs)

    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_MODEL_VOLUME,
        mount_path=mount_path,
        model_volume=OrmVolumeMountRequestSourceModelVolume(
            sub_path="/",
            model_repository_name=model.model_repository.name,
            model_number=model.number,
        ),
    )


def _configure_volume_mount_request_local_files(
    local_files: List[str], use_vesslignore: bool, **kwargs
) -> List[OrmVolumeMountRequest]:
    project = _get_project(**kwargs)

    volume_mount_requests: List[OrmVolumeMountRequest] = []
    for local_file in local_files:
        if ":" in local_file:
            local_path, remote_path = local_file.split(":")
            if not remote_path.startswith("/"):
                remote_path = f"{EXPERIMENT_WORKING_DIR}{remote_path}"
        else:
            local_path = local_file
            remote_path = f"{EXPERIMENT_WORKING_DIR}local"

        cwd = os.path.abspath(local_path)
        gzip_file_full_path = os.path.abspath(
            os.path.join(TEMP_DIR, f"{project.name}_{random_string()}.tar.gz")
        )

        print(f"Uploading... [{cwd} -> {remote_path}]")
        if use_vesslignore:
            Tar.gzip_using_vesslignore(gzip_file_full_path, cwd)
        else:
            Tar.gzip(gzip_file_full_path, cwd)
        vft = VolumeFileTransfer(volume_id=project.volume_id)
        file_path = vft.upload(gzip_file_full_path, os.path.basename(gzip_file_full_path))
        if file_path is None:
            raise Exception("Failed to upload file. Please try again.")

        print(f"Upload completed successfully.")
        os.remove(gzip_file_full_path)

        volume_mount_requests.append(
            _configure_volume_mount_request_archive_file(
                archive_file_mount=f"{remote_path}:{file_path[0]['path']}"
            )
        )

    return volume_mount_requests


def _configure_volume_mount_request_local_git(
    upload_local_git_diff, **kwargs
) -> List[OrmVolumeMountRequest]:
    project = _get_project(**kwargs)

    local_git_owner, local_git_repo = None, None
    try:
        local_git_owner, local_git_repo = get_git_repo()
    except GitError:
        pass

    volume_mount_requests: List[OrmVolumeMountRequest] = []
    used_mount_paths = set()
    for repo in project.project_repositories:
        mount_path = f"{EXPERIMENT_WORKING_DIR}{repo.git_repo}"
        if mount_path in used_mount_paths:
            mount_path = f"{EXPERIMENT_WORKING_DIR}{repo.git_repo}-{repo.git_owner}"

        git_mount_info = f"github/{repo.git_owner}/{repo.git_repo}/latest"
        git_diff_path = None
        if (
            upload_local_git_diff
            and repo.git_owner == local_git_owner
            and repo.git_repo == local_git_repo
        ):
            # Current working directory is one of the project repository.
            # Mount VolumeSourceCode with potential uncommitted changes
            git_diff_path = get_git_diff_path(project)
            git_mount_info = git_mount_info.replace("latest", get_git_ref())
        volume_mount_requests.append(
            _configure_volume_mount_request_code(
                git_ref_mount=f"{mount_path}:{git_mount_info}",
                git_diff_mount=None if git_diff_path is None else f"{mount_path}:{git_diff_path}",
            )
        )

    return volume_mount_requests


def _configure_volume_mount_request_codes(
    git_ref_mounts: List[str], git_diff_mount: str, **kwargs
) -> List[OrmVolumeMountRequest]:
    return [
        _configure_volume_mount_request_code(git_ref_mount, git_diff_mount, **kwargs)
        for git_ref_mount in git_ref_mounts
    ]


def _configure_volume_mount_request_code(
    git_ref_mount: str, git_diff_mount: str, **kwargs
) -> OrmVolumeMountRequest:
    # Generate OrmVolumeMountRequestSourceCode from git_ref_mount
    # ref_mount_info = <provider>/<owner>/<repo>/<commit>
    ref_mount_path, ref_mount_info = git_ref_mount.split(":", 1)
    code_info = ref_mount_info.split("/", 3)

    vmr_source_code = OrmVolumeMountRequestSourceCode(
        git_provider=code_info[0],
        git_owner=code_info[1],
        git_repo=code_info[2],
        git_ref=code_info[3],
    )

    # Add optional git_diff parameter if git_diff_mount has same mount path
    if git_diff_mount is not None:
        diff_mount_path, diff_mount_file = git_diff_mount.split(":", 1)
        if ref_mount_path == diff_mount_path:
            vmr_source_code.git_diff_file = diff_mount_file

    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_CODE,
        mount_path=ref_mount_path,
        code=vmr_source_code,
    )


def _configure_volume_mount_request_archive_file(
    archive_file_mount: str,
) -> OrmVolumeMountRequest:
    mount_path, archive_file_path = archive_file_mount.split(":", 1)

    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_ARCHIVE_FILE,
        mount_path=mount_path,
        archive_file=OrmVolumeMountRequestSourceArchiveFile(
            archive_file=archive_file_path,
        ),
    )


def _configure_volume_mount_request_object_storage(
    object_storage_mount: str,
) -> OrmVolumeMountRequest:
    mode, path = object_storage_mount.split("@", 1)
    mount_path, bucket_path = path.split(":", 1)

    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_OBJECT_STORAGE,
        mount_path=mount_path,
        object_storage=OrmVolumeMountRequestSourceObjectStorage(
            mode=mode,
            bucket_path=bucket_path,
        ),
    )


def _configure_volume_mount_request_object_storages(
    object_storage_mounts: List[str], **kwargs
) -> List[OrmVolumeMountRequest]:
    return [
        _configure_volume_mount_request_object_storage(object_storage_mount, **kwargs)
        for object_storage_mount in object_storage_mounts
    ]


def _configure_volume_mount_request_empty_dir() -> OrmVolumeMountRequest:
    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_EMPTY_DIR,
        mount_path=MOUNT_PATH_EMPTY_DIR,
    )


def _configure_volume_mount_request_output(output_dir: str) -> OrmVolumeMountRequest:
    return OrmVolumeMountRequest(
        source_type=SOURCE_TYPE_OUTPUT,
        mount_path=output_dir,
    )


@dataclass
class VolumePathRef:
    # type is one of: ("sv", "volume", "local")
    type: str

    # "sv://" reference
    sv_id: int = 0
    sv_path: str = ""

    # "volume://" reference
    storage_name: str = ""
    volume_name: str = ""
    volume_path: str = ""

    # local path
    local_path: str = ""


def parse_volume_url(volume_url: str, raise_if_not_exists: bool = False) -> VolumePathRef:
    """
    Parse volume URLs with these formats:

    - sv://<volume ID>/<path inside volume>
    - volume://<storage name>/<volume name>
    - {localPath}

    Returns one of the following types.

    - Tuple["sv", Tuple[str, str]]:
        Returned if this URL is a 'sv://' volume.
        Tuple of ((volume ID), (path inside volume)).

    - Tuple["volume", Tuple[str, str]]:
        Returned if this URL is a 'volume://' volume.
        (storage_name, volume_name) tuple.

    - Tuple["local", str]:
        Returned if this URL is not a URL, but actually a local path.
        Local path in the running host.
    """

    if volume_url.startswith("sv://"):
        u = urlparse(volume_url)
        volume_id = int(u.netloc.split(":", 1)[0])
        path = u.path.lstrip("/")
        return VolumePathRef(
            type=constant.VOLUME_TYPE_SV,
            sv_id=volume_id,
            sv_path=path,
        )

    if volume_url.startswith("volume://"):
        u = urlparse(volume_url)
        # urlparse("volume://stg/vol/sub1/sub2")
        # -> { netloc: "stg", path: "/vol/sub1/sub2" }
        storage_name = u.netloc
        paths = u.path.lstrip("/").split("/", maxsplit=1)
        volume_name = paths[0]
        volume_path = paths[1] if len(paths) > 1 else ""
        return VolumePathRef(
            type=constant.VOLUME_TYPE_VOLUME,
            storage_name=storage_name,
            volume_name=volume_name,
            volume_path=volume_path,
        )

    if not os.path.exists(volume_url) and raise_if_not_exists:
        raise InvalidVolumeFileError(f"No such file: {os.path.abspath(volume_url)}")

    return VolumePathRef(type=constant.VOLUME_TYPE_LOCAL, local_path=volume_url)


def create_run_execution_volume_v2(storage_name: str, volume_name: str, origin_path: str):
    vessl_api.run_execution_volume_v2_create_api(
        run_execution_volume_v2_create_api_input=RunExecutionVolumeV2CreateAPIInput(
            storage_name=storage_name,
            volume_name=volume_name,
            origin_path=origin_path,
        )
    )
