# coding=utf-8
from typing import Any

import os
from .pac import Pac

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPackage = str
TyPath = str
TnPath = None | TyPath


class Cls:

    @staticmethod
    def sh_path_of_pac_by_path(cls_app, log, path: TyPath) -> Any:
        """
        show directory
        """
        _package = cls_app.__module__.split(".")[0]
        return Pac.sh_path_by_path(_package, path, log)

    @staticmethod
    def sh_path_of_pac_by_paths(cls_app, log, *paths: TyPath) -> Any:
        """
        show directory
        """
        _package = cls_app.__module__.split(".")[0]
        _path = os.sep.join(paths)
        return Pac.sh_path_by_path(_package, log, _path)
