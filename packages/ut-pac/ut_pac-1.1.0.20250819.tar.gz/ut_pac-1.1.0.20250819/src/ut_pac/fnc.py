# coding=utf-8
from typing import Any

import inspect

TyClsName = Any
TyModName = Any
TyPacName = Any
TyPacModName = Any
TyFncName = Any


class Fnc:

    @staticmethod
    def sh_pacmod_name(fnc) -> TyPacModName:
        """
        show module name of function
        """
        return fnc.__module__

    @staticmethod
    def sh_mod_name(fnc) -> TyModName:
        """
        show module name of function
        """
        _mod_name = fnc.__module__
        parts = _mod_name.split('.')
        if len(parts) > 1:
            _mod_name = parts[1]
        return _mod_name

    @staticmethod
    def sh_pac_name(fnc) -> TyModName:
        """
        show module name of function
        """
        _mod_name = fnc.__module__
        parts = _mod_name.split('.')
        if len(parts) > 1:
            _pac_name = parts[0]
        else:
            _pac_name = ''
        return _pac_name

    @staticmethod
    def xsh_pac_name(fnc) -> TyPacName:
        """
        show package name of function
        """
        # Get the package name (if available)
        _mod = inspect.getmodule(fnc)
        _pac_name = _mod.__package__ if _mod else ''
        return _pac_name

    @staticmethod
    def sh_cls_name(fnc) -> TyClsName:
        """
        show class name of function
        """
        if hasattr(fnc, '__qualname__'):
            parts = fnc.__qualname__.split('.')
            if len(parts) > 1:
                _cls_name = parts[0]  # Class name
        else:
            _cls_name = ''
        return _cls_name

    @classmethod
    def sh_fnc_name(cls, fnc) -> TyFncName:
        """
        show class name of function
        """
        _pacmod_name = cls.sh_pacmod_name(fnc)
        _cls_name = cls.sh_cls_name(fnc)
        _fnc_name = '.'.join([_pacmod_name, _cls_name])
        return _fnc_name
