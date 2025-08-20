from typing import Any

# import os

import ut_log.log.LogEq as LogEq
import ut_path.path.Path as Path

TyDic = dict[Any, Any]
TyPath = str

TnDic = None | TyDic
TnPath = None | TyPath


class PathNm:

    @staticmethod
    def sh_path(pathnm: str, kwargs: TyDic) -> TyPath:
        _path: TyPath = kwargs.get(pathnm, '')
        LogEq.debug("_path", _path)
        _path = Path.sh_path_by_tpl_and_d_pathnm2datetype(
                _path, pathnm, kwargs)
        return _path
