# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Any, Iterable, List, Tuple, Union

from mldesigner._compile._ignore_file import IgnoreFile


def _resolve_path(path: Path) -> Path:
    if not path.is_symlink():
        return path

    link_path = path.resolve()
    if not link_path.is_absolute():
        link_path = path.parent.joinpath(link_path).resolve()
    return _resolve_path(link_path)


def get_upload_files_from_folder(
    path: Union[str, os.PathLike], *, prefix: str = "", ignore_file: IgnoreFile = None
) -> List[str]:
    path = Path(path)
    upload_paths = []
    for root, _, files in os.walk(path, followlinks=True):
        upload_paths += list(
            traverse_directory(
                root,
                files,
                prefix=Path(prefix).joinpath(Path(root).relative_to(path)).as_posix(),
                ignore_file=ignore_file,
            )
        )
    return upload_paths


def traverse_directory(  # pylint: disable=unused-argument
    root: str,
    files: List[str],
    *,
    prefix: str,
    ignore_file: IgnoreFile,
    # keep this for backward compatibility
    **kwargs: Any,
) -> Iterable[Tuple[str, Union[str, Any]]]:
    """Enumerate all files in the given directory and compose paths for them to be uploaded to in the remote storage.
    e.g.

    [/mnt/c/Users/dipeck/upload_files/my_file1.txt,
    /mnt/c/Users/dipeck/upload_files/my_file2.txt] -->

        [(/mnt/c/Users/dipeck/upload_files/my_file1.txt, LocalUpload/<guid>/upload_files/my_file1.txt),
        (/mnt/c/Users/dipeck/upload_files/my_file2.txt, LocalUpload/<guid>/upload_files/my_file2.txt))]

    :param root: Root directory path
    :type root: str
    :param files: List of all file paths in the directory
    :type files: List[str]
    :keyword prefix: Remote upload path for project directory (e.g. LocalUpload/<guid>/project_dir)
    :paramtype prefix: str
    :keyword ignore_file: The .amlignore or .gitignore file in the project directory
    :paramtype ignore_file: azure.ai.ml._utils._asset_utils.IgnoreFile
    :return: Zipped list of tuples representing the local path and remote destination path for each file
    :rtype: Iterable[Tuple[str, Union[str, Any]]]
    """
    # Normalize Windows paths. Note that path should be resolved first as long part will be converted to a shortcut in
    # Windows. For example, C:\Users\too-long-user-name\test will be converted to C:\Users\too-lo~1\test by default.
    # Refer to https://en.wikipedia.org/wiki/8.3_filename for more details.
    root = Path(root).resolve().absolute()

    # filter out files excluded by the ignore file
    # TODO: inner ignore file won't take effect. A merged IgnoreFile need to be generated in code resolution.
    origin_file_paths = [
        root.joinpath(filename)
        for filename in files
        if not ignore_file.is_file_excluded(root.joinpath(filename).as_posix())
    ]

    result = []
    for origin_file_path in origin_file_paths:
        relative_path = origin_file_path.relative_to(root)
        result.append((_resolve_path(origin_file_path).as_posix(), Path(prefix).joinpath(relative_path).as_posix()))
    return result
