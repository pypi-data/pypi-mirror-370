# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import List, Optional, Union

from mldesigner._constants import AML_IGNORE_SUFFIX, GIT_IGNORE_SUFFIX

from ._pathspec import GitWildMatchPattern, normalize_file


# TODO: Put this file along with "_pathspec.py" and "_utils.py" into a separate package, comment that they
# come from azure.ai.ml package
class IgnoreFile(object):
    def __init__(self, file_path: Optional[Union[str, os.PathLike]] = None):
        """Base class for handling .gitignore and .amlignore files.

        :param file_path: Relative path, or absolute path to the ignore file.
        """
        path = Path(file_path).resolve() if file_path else None
        self._path = path
        self._path_spec = None

    def exists(self) -> bool:
        """Checks if ignore file exists.
        :return: True if file exists. False Otherwise
        :rtype: bool
        """
        return self._file_exists()

    def _file_exists(self) -> bool:
        return self._path and self._path.exists()

    @property
    def base_path(self) -> Path:
        return self._path.parent

    def _get_ignore_list(self) -> List[str]:
        """Get ignore list from ignore file contents.

        :return: The lines of the ignore file
        :rtype: List[str]
        """
        if not self.exists():
            return []
        if self._file_exists():
            with open(self._path, "r", encoding="utf-8") as fh:
                return [line.rstrip() for line in fh if line]
        return []

    def _create_pathspec(self) -> List[GitWildMatchPattern]:
        """Creates path specification based on ignore list.

        :return: Path specification
        :rtype: List[GitWildMatchPattern]
        """
        return [GitWildMatchPattern(ignore) for ignore in self._get_ignore_list()]

    def _get_rel_path(self, file_path: Union[str, os.PathLike]) -> Optional[str]:
        """Get relative path of given file_path.

        :param file_path: A file path
        :type file_path: Union[str, os.PathLike]
        :return: file_path relative to base_path, if computable. None otherwise
        :rtype: Optional[str]
        """
        file_path = Path(file_path).absolute()
        try:
            # use os.path.relpath instead of Path.relative_to in case file_path is not a child of self.base_path
            return os.path.relpath(file_path, self.base_path)
        except ValueError:
            # 2 paths are on different drives
            return None

    def is_file_excluded(self, file_path: Union[str, os.PathLike]) -> bool:
        """Checks if given file_path is excluded.

        :param file_path: File path to be checked against ignore file specifications
        :type file_path: Union[str, os.PathLike]
        :return: Whether the file is excluded by ignore file
        :rtype: bool
        """
        # TODO: current design of ignore file can't distinguish between files and directories of the same name
        if self._path_spec is None:
            self._path_spec = self._create_pathspec()
        if not self._path_spec:
            return False
        file_path = self._get_rel_path(file_path)
        if file_path is None:
            return True

        norm_file = normalize_file(file_path)
        matched = False
        for pattern in self._path_spec:
            if pattern.include is not None:
                if pattern.match_file(norm_file) is not None:
                    matched = pattern.include

        return matched

    @property
    def path(self) -> Union[Path, str]:
        return self._path


class AmlIgnoreFile(IgnoreFile):
    def __init__(self, directory_path: Union[Path, str]):
        file_path = Path(directory_path).joinpath(AML_IGNORE_SUFFIX)
        super(AmlIgnoreFile, self).__init__(file_path)


class GitIgnoreFile(IgnoreFile):
    def __init__(self, directory_path: Union[Path, str]):
        file_path = Path(directory_path).joinpath(GIT_IGNORE_SUFFIX)
        super(GitIgnoreFile, self).__init__(file_path)


def get_ignore_file(directory_path: Union[Path, str]) -> IgnoreFile:
    """Finds and returns IgnoreFile object based on ignore file found in directory_path.

    .amlignore takes precedence over .gitignore and if no file is found, an empty
    IgnoreFile object will be returned.

    The ignore file must be in the root directory.

    :param directory_path: Path to the (root) directory where ignore file is located
    :type directory_path: Union[Path, str]
    :return: The IgnoreFile found in the directory
    :rtype: IgnoreFile
    """
    aml_ignore = AmlIgnoreFile(directory_path)
    git_ignore = GitIgnoreFile(directory_path)

    if aml_ignore.exists():
        return aml_ignore
    if git_ignore.exists():
        return git_ignore
    return IgnoreFile()


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]
    """Component-specific ignore file used for ignoring files in a component directory.

    :param directory_path: The directory path for the ignore file.
    :type directory_path: Union[str, Path]
    :param additional_includes_file_name: Name of the additional includes file in the root directory to be ignored.
    :type additional_includes_file_name: str
    :param skip_ignore_file: Whether to skip the ignore file, defaults to False.
    :type skip_ignore_file: bool
    :param extra_ignore_list: List of additional ignore files to be considered during file exclusion.
    :type extra_ignore_list: List[~azure.ai.ml._utils._asset_utils.IgnoreFile]
    :raises ValueError: If additional include file is not found.
    :return: The ComponentIgnoreFile object.
    :rtype: ComponentIgnoreFile
    """

    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        additional_includes_file_name: Optional[str] = None,
        skip_ignore_file: bool = False,
        extra_ignore_list: Optional[List[IgnoreFile]] = None,
    ):
        self._base_path = Path(directory_path)
        self._extra_ignore_list: List[IgnoreFile] = extra_ignore_list or []
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_includes_file_name = additional_includes_file_name
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = None if skip_ignore_file else get_ignore_file(directory_path).path
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)

    def exists(self) -> bool:
        """Check if the ignore file exists.

        :return: True
        :rtype: bool
        """
        return True

    @property
    def base_path(self) -> Path:
        """Get the base path of the ignore file.

        :return: The base path.
        :rtype: Path
        """
        # for component ignore file, the base path can be different from file.parent
        return self._base_path

    def rebase(self, directory_path: Union[str, Path]) -> "ComponentIgnoreFile":
        """Rebase the ignore file to a new directory.

        :param directory_path: The new directory path.
        :type directory_path: Union[str, Path]
        :return: The rebased ComponentIgnoreFile object.
        :rtype: ComponentIgnoreFile
        """
        self._base_path = directory_path
        return self

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Check if a file should be excluded based on the ignore file rules.

        :param file_path: The file path.
        :type file_path: Union[str, Path]
        :return: True if the file should be excluded, False otherwise.
        :rtype: bool
        """
        if self._additional_includes_file_name and self._get_rel_path(file_path) == self._additional_includes_file_name:
            return True
        for ignore_file in self._extra_ignore_list:
            if ignore_file.is_file_excluded(file_path):
                return True
        return super(ComponentIgnoreFile, self).is_file_excluded(file_path)

    def merge(self, other_path: Path) -> "ComponentIgnoreFile":
        """Merge the ignore list from another ComponentIgnoreFile object.

        :param other_path: The path of the other ignore file.
        :type other_path: Path
        :return: The merged ComponentIgnoreFile object.
        :rtype: ComponentIgnoreFile
        """
        if other_path.is_file():
            return self
        return ComponentIgnoreFile(other_path, extra_ignore_list=self._extra_ignore_list + [self])

    def _get_ignore_list(self) -> List[str]:
        """Retrieves the list of ignores from ignore file

        Override to add custom ignores.

        :return: The ignore rules
        :rtype: List[str]
        """
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        return super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES
