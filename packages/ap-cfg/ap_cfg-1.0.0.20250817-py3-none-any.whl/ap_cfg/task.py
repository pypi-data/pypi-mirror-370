"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from collections.abc import Callable

from ut_dic.doc import DoC
from .setup import Setup

from typing import Any
TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyCmd = str
TyDoAoD = dict[Any, TyAoD]
TyStr = str
TyTup = tuple[Any]
TyTask = Any
TyDoC = dict[str, TyCallable]

TnDic = None | TyDic


class Task:
    """
    General Task class
    """
    """
    Dictionary of callables of class Setup or Email
    """
    doc: TyDoC = {
        'setup': Setup.setup,
    }

    @classmethod
    def do(cls, kwargs: TyDic) -> None:
        """
        Select the task method from the task command table for the given
        command (value of 'cmd' in kwargs) and execute the selected method.
        """
        DoC.ex_cmd(cls.doc, kwargs)
