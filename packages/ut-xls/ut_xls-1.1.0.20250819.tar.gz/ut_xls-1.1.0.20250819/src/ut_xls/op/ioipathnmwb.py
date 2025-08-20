from typing import Any, TypeAlias

import openpyxl as op

from ut_xls.op.ioipath import IoiPathWb
from ut_path.pathnm import PathNm

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyWs: TypeAlias = op.worksheet.worksheet.Worksheet

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyPathnm = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames
TnWb = None | TyWb
TnWs = None | TyWs
TnPath = None | TyPath


class IoiPathnmWb:

    @staticmethod
    def load(pathnm: TyPathnm, kwargs: TyDic, **kwargs_wb) -> TyWb:
        _path = PathNm.sh_path(pathnm, kwargs)
        return IoiPathWb.load(_path, **kwargs_wb)
