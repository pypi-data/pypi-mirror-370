# coding=utf-8
from typing import Any

import openpyxl as op

TyArr = list[Any]
TyDic = dict[Any, Any]
TyDoD = dict[Any, TyDic]

TnAny = None | Any


class DoDoWs:
    """ Manage Dictionary of Dictionaries of Worksheets.
    """
    @classmethod
    def write_workbook(cls, dod_sheet: TyDoD, path: str):
        """
        Recurse through the Dictionary while building a new one with
        new keys and old values; the old keys are translated to new
        ones by the keys Dictionary.
        """
        # def write_dod_sheet(cls, dod_sheet: TyDoD, path: str):
        workbook = op.Workbook(write_only=True)
        for name, d_sheet in dod_sheet.items():
            rows = d_sheet['rows']
            sheet = workbook.create_sheet()
            sheet.title = name
            for row in rows:
                sheet.append(row)
        workbook.save(path)
