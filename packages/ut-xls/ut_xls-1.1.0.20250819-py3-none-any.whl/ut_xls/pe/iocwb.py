import pyexcelerate as pe

from typing import Any, TypeAlias
TyWb: TypeAlias = pe.Workbook


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = pe.Workbook(**kwargs)
        return wb
