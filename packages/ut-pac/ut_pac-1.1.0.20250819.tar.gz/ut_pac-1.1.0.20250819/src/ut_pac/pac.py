# coding=utf-8
from typing import Any

import os
import importlib.resources

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPackage = str
TyPackages = list[str]
TyPath = str
TnPath = None | TyPath


class Pac:

    @staticmethod
    def sh_path(package: TyPackage) -> Any:
        return str(importlib.resources.files(package))

    @staticmethod
    def sh_path_by_path(
            package: TyPackage, path: TyPath, log) -> Any:
        # def sh_path_by_pack(
        """ show directory
        """
        _path = str(importlib.resources.files(package).joinpath(path))
        if not _path:
            # print(f"path {path} does not exist in package {package}")
            log.error(f"path {path} does not exist in package {package}")
            return ''
        if os.path.exists(_path):
            # print(f"path {_path} exists")
            log.debug(f"path {_path} exists")
            return _path
        # print(f"path {_path} does not exist")
        log.error(f"path {_path} does not exist")
        return ''

    @classmethod
    def sh_path_by_path_and_prefix(
            cls, package: TyPackage, path: TyPath, log, prefix: TyPath = '') -> Any:
        # def sh_path_by_pack(
        """
        show directory
        """
        return cls.sh_path_by_path(package, os.path.join(prefix, path), log)
