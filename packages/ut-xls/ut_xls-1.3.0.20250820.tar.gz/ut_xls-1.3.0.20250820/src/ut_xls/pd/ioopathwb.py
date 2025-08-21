from typing import Any, TypeAlias

import pandas as pd

import ut_dic.dic.Dic as Dic
import ut_path.path.Path as Path

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]


class IooPathPdDf:

    @staticmethod
    def write_pd_from_dopdf(dodf: TyDoPdDf, path: str) -> None:
        _a_key: TyArr = Dic.show_sorted_keys(dodf)
        if not _a_key:
            return
        Path.mkdir_from_path(path)
        writer = pd.ExcelWriter(path, engine='openpyxl')
        for _key in _a_key:
            _df: TyPdDf = dodf[_key]
            _df.to_excel(writer, sheet_name=_key)
        writer.close()
