# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import os

from ut_log.log import Log, LogEq
from ut_pac.pac import Pac

TyAny = Any
TyArr = list[Any]
TyAoS = list[str]
TyAoA = list[TyArr]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoA = dict[Any, TyAoA]
TyDoInt = dict[str, int]
TyDoDoInt = dict[str, TyDoInt]
TyIntStr = int | str
TyPath = str
TyPathLike = os.PathLike
TyAoPath = list[TyPath]
TyBasename = str
TyTup = tuple[Any, ...]
TyIterAny = Iterator[Any]
TyIterPath = Iterator[TyPath]
TyIterTup = Iterator[TyTup]
TyStr = str
TyToS = tuple[str, ...]

TnAny = None | TyAny
TnArr = None | TyArr
TnAoA = None | TyAoA
TnDic = None | TyDic
TnInt = None | int
TnPath = None | TyPath
TnStr = None | str
TnTup = None | TyTup


class DoPath:

    @staticmethod
    def sh_path(d_path: TyDic, kwargs: TyDic) -> TyPath:
        LogEq.debug("d_path", d_path)
        _a_part: TyArr = []
        _package: TyStr = kwargs.get('package', '')
        for _k, _v in d_path.items():
            LogEq.debug("_k", _k)
            LogEq.debug("_v", _v)
            match _v:
                case 'key':
                    _val = kwargs.get(_k)
                    if _val:
                        _a_part.append(_val)
                case 'pac':
                    _val = Pac.sh_path_by_path(_package, _k, Log.log)
                    if _val:
                        _a_part.append(_val)
                case _:
                    _a_part.append(_k)
        LogEq.debug("_a_part", _a_part)
        if not _a_part:
            msg = f"a_part for d_path = {d_path} is undefined or empty"
            raise Exception(msg)
        return os.path.join(*_a_part)
