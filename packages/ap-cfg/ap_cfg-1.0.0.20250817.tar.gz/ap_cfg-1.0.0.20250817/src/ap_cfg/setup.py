"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
import os
import shutil

from ut_log.log import Log, LogEq
from ut_path.path import Path, DoPath
from ut_ioc.yaml_ import Yaml_

from typing import Any

TyAny = Any
TyDic = dict[Any, Any]
TyDoD = dict[Any, TyDic]
TyAoD = list[TyDic]
TyAoDoD = list[TyDoD]
TyPath = str
TnAny = None | TyAny


class Setup:
    """
    Setup function class
    """
    @staticmethod
    def copytree(src: Any, dst: Any) -> None:
        """
        Copy source path tree to destination path tree while preserving timestamps,
        and allow existing destination.
        """
        if not src:
            return
        if not os.path.exists(dst):
            os.makedirs(dst)
        # Copy the entire directory tree
        try:
            shutil.copytree(
                    src, dst, copy_function=shutil.copy2, dirs_exist_ok=True)
            msg = f"Directory tree copied from {src} to {dst}"
            Log.debug(msg)
        except Exception as e:
            msg = f"Could not copy Directory tree from {src} to {dst}"
            raise Exception(msg) from e

    @classmethod
    def sh_path_for_loc(cls, dod_copy, loc, kwargs: TyDic) -> TyPath:
        _d_copy = dod_copy.get(loc, [])
        if not _d_copy:
            msg = f"{loc}-array for _d_copy = {_d_copy} is empty"
            raise Exception(msg)
        _path = DoPath.sh_path(_d_copy, kwargs)
        if not _path:
            msg = f"{loc}-path for _d_copy = {_d_copy} is undefined or empty"
            raise Exception(msg)
        return _path

    @classmethod
    def setup(cls, kwargs: TyDic) -> None:
        _aodod_copy: TyAny = kwargs.get('aodod_copy', [])
        LogEq.debug("_aodod_copy", _aodod_copy)
        if not _aodod_copy:
            _in_path_aodod_copy: TyPath = kwargs.get('in_path_aodod_copy', '')
            _path: TyPath = Path.sh_path_by_tpl_pac_sep(_in_path_aodod_copy, kwargs)
            _aodod_copy = Yaml_.read_with_safeloader(_path)
            if not _aodod_copy:
                raise Exception(f"Content of yaml file = {_path} is undefined or empty")

        LogEq.debug("_aodod_copy", _aodod_copy)
        for _dod_copy in _aodod_copy:
            LogEq.debug("_dod_copy", _dod_copy)
            _src_path = cls.sh_path_for_loc(_dod_copy, 'src', kwargs)
            _dst_path = cls.sh_path_for_loc(_dod_copy, 'dst', kwargs)
            LogEq.debug("_src_path", _src_path)
            LogEq.debug("_dst_path", _dst_path)
            cls.copytree(_src_path, _dst_path)
