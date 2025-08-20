import openpyxl as op

from typing import Any, TypeAlias
TyWb: TypeAlias = op.workbook.workbook.Workbook
TnWb = None | TyWb


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = op.Workbook(**kwargs)
        return wb
