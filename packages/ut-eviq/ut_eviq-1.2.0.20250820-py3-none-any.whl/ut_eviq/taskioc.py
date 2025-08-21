"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
# import ut_xls.pd.ioipathwb.IoiPathWb as PdIoiPathWb
# import ut_xls.op.ioopathwb.IooPathWb as OpIooPathWb
# import ut_xls.pe.ioopathwb.IooPathWb as PeIooPathWb

# import ut_eviq.utils.Evex as Evex
import ut_eviq.taskin.TaskIn as TaskIn
# import ut_eviq.rst as rst
import ut_eviq.xls as xls

# import pandas as pd
import openpyxl as op

from typing import Any, TypeAlias
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb


class TaskIoc:
    """
    Excel function class
    """
    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def evupadm(cls, kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        xls.TaskOut.evupadm(TaskIn.evupadm(kwargs), kwargs)

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        xls.TaskOut.evupdel(TaskIn.evupdel(kwargs), kwargs)

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> None:
        """
        EcoVadis Upload Processing:
        Regular Processing (create, update, delete) of partners using
          single Xlsx Workbook with a populated admin- or delete-sheet
          two xlsx Workbooks:
            the first one contains a populated admin-sheet
            the second one contains a populated delete-sheet
        """
        _sw_single_wb: TyBool = kwargs.get('sw_single_wb', True)
        if _sw_single_wb:
            # write single workbook which contains admin and delete worksheets
            xls.TaskOut.evupreg_reg_wb(TaskIn.evupreg(kwargs, kwargs))
        else:
            # write separate workbooks for admin and delete worksheets
            xls.TaskOut.evupreg_adm_del_wb(TaskIn.evupreg(kwargs, kwargs))

    @classmethod
    def evdomap(cls, kwargs: TyDic) -> None:
        """
        EcoVadis Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        xls.TaskOut.evdomap(TaskIn.evdomap(kwargs), kwargs)
