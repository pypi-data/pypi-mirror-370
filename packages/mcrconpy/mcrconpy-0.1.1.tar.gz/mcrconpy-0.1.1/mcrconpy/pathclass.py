# -*- coding: utf-8 -*-
"""
`PathClass` in charge of managing the paths.
"""

import os
import re
import shutil
import platformdirs
from pathlib import Path

from typing import (
    Tuple,
    Union
)


class PathClass:

    __sep = os.path.sep

    @classmethod
    @property
    def separator(cls) -> str:
        """
        """
        return cls.__sep

    @classmethod
    @property
    def get_home(cls) -> str:
        """
        """
        return cls.expanduser("~")

    def get_desktop() -> str:
        """
        """
        return platformdirs.user_desktop_dir()

    def user_config_dir(
        name: str
    ) -> str:
        return platformdirs.user_config_dir(name)

    def user_log_dir(
        dir: str
    ) -> str:
        return platformdirs.user_log_dir(dir)

    def openfile(
        path: str
    ) -> None:
        """
        """
        os.startfile(path)

    def absolute_path(
        path: str
    ) -> str:
        """
        """
        return os.path.abspath(path=path)

    def delete_file(
        path: str
    ) -> bool:
        """
        """
        return os.remove(path)

    def delete_directory(
        path: str
    ) -> bool:
        """
        """
        try:
            shutil.rmtree(path=path)
            return True
        except Exception as e:
            print(e)
            return False

    def listdir(
        path: str = ""
    ) -> None:
        """
        """
        if path != "":
            return os.listdir(path)
        return os.listdir()

    def dirname(
        path: str
    ) -> str:
        """
        """
        return os.path.dirname(path)

    def basename(
        path: str
    ) -> str:
        """
        """
        return os.path.basename(path)

    def splitext(
        path: str
    ) -> Tuple[str]:
        """
        """
        return os.path.splitext(PathClass.basename(path))

    def expanduser(
        path: str
    ) -> str:
        return os.path.expanduser(path)

    def join(
        *path: str
    ) -> str:
        """
        """
        # return os.path.join(f"{os.path.sep}".join(*path))
        return os.path.join(*path)

    def exists(
        path: str
    ) -> bool:
        """
        """
        return os.path.exists(path)

    def realpath(
        path: str
    ) -> str:
        """
        """
        return os.path.realpath(path)

    def makedirs(
        path: str
    ) -> bool:
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        return PathClass.exists(path)

    def walk(
        path
    ) -> object:
        """
        """
        if PathClass.is_dir(path) is False:
            return
        return os.walk(path)

    def is_file(
        path: str
    ) -> bool:
        """
        """
        return os.path.isfile(path)

    def is_dir(
        path: str
    ) -> bool:
        """
        """
        return os.path.isdir(path)

    def get_files_recursive(
        extensions: Union[str, list],
        directory: str
    ) -> list:
        """
        Recursively scans a directory looking for valid files using extensions.

        Args
            extensions: string or list of strings with the extensions that will
                        be used to filter the files.
            directory: directory path.

        Returns
            list: list of `Path` instances.
        """
        results = []
        if isinstance(extensions, str):
            extensions = [extensions]

        dirPath = Path(directory)

        for ext in extensions:
            if ext.startswith("."):
                ext = ext.replace(".", "")
            pattern = rf'.*\.{ext}$'
            results += [
                            i
                            for i in PathClass.listdir(dirPath)
                            if re.findall(pattern, str(i), re.IGNORECASE)
                        ]

        results = list(set(results))

        return results
