# coding=utf-8
from typing import Any

import os

from .pac import Pac

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPackage = str
TyPackages = list[str]
TyPath = str


class Pacs:

    @staticmethod
    def sh_path_by_path(
            packages: TyPackages, path: TyPath, log) -> Any:
        """ show directory
        """
        if not isinstance(packages, list):
            packages = [packages]
        for _package in packages:
            _path = Pac.sh_path_by_path(_package, path, log)
            if _path:
                return _path
        return ''

    @classmethod
    def sh_path_by_path_and_prefix(
            cls, packages: TyPackages, path: TyPath, log, prefix: TyPath = '') -> Any:
        # def sh_path_by_packs(
        """ show directory
        """
        if prefix:
            _path = os.path.join(prefix, path)
            # _dirname = os.path.dirname(_path)
            if os.path.exists(_path):
                return _path
        return cls.sh_path_by_path(packages, path, log)
