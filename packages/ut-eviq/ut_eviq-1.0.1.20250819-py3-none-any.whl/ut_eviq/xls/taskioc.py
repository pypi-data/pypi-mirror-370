"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from ut_path.pathnm import PathNm

from ut_xls.op.ioipathwb import IoiPathWb as OpIoiPathWb
from ut_xls.pd.ioipathwb import IoiPathWb as PdIoiPathWb
from ut_xls.op.ioopathwb import IooPathWb as OpIooPathWb
from ut_xls.pe.ioopathwb import IooPathWb as PeIooPathWb

from .utils import Evex
from .taskin import TaskIn
from .cfg import Cfg

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
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _out_path_evup_adm = PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs)
        _out_path_evin_adm_vfy = PathNm.sh_path(_cfg.OutPath.evin_adm_vfy, kwargs)

        _aod_evup_adm, _doaod_evin_adm_vfy = TaskIn.evupadm(kwargs)
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_adm, _sheet_adm)
        OpIooPathWb.write(_wb_evup_adm, _out_path_evup_adm)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_adm_vfy, _out_path_evin_adm_vfy)

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _out_path_evup_del = PathNm.sh_path(_cfg.OutPath.evup_del, kwargs)
        _out_path_evin_del_vfy = PathNm.sh_path(_cfg.OutPath.evin_del_vfy, kwargs)

        _aod_evup_del, _doaod_evin_del_vfy = TaskIn.evupdel(kwargs)
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_del(
                _in_path_evup_tmp, _aod_evup_del, _sheet_del)
        OpIooPathWb.write(_wb_evup_del, _out_path_evup_del)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_del_vfy, _out_path_evin_del_vfy)

    @classmethod
    def evupreg_reg_wb(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _out_path_evup_reg = PathNm.sh_path(_cfg.OutPath.evup_reg, kwargs)
        _out_path_evin_reg_vfy = PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs)

        (_aod_evup_adm, _doaod_evin_adm_vfy,
         _aod_evup_del, _doaod_evin_del_vfy) = TaskIn.evupreg(kwargs)
        _wb_evup_reg: TnOpWb = OpIoiPathWb.sh_wb_reg(
               _in_path_evup_tmp, _aod_evup_adm, _aod_evup_del, _sheet_adm, _sheet_del)
        OpIooPathWb.write(_wb_evup_reg, _out_path_evup_reg)
        _doaod_evin_vfy = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_vfy, _out_path_evin_reg_vfy)

    @classmethod
    def evupreg_adm_del_wb(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _out_path_evup_adm = PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs)
        _out_path_evup_del = PathNm.sh_path(_cfg.OutPath.evup_del, kwargs)
        _out_path_evin_reg_vfy = PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs)

        (_aod_evup_adm, _doaod_evin_adm_vfy,
         _aod_evup_del, _doaod_evin_del_vfy) = TaskIn.evupreg(kwargs)
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_adm, _sheet_adm)
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_del, _sheet_del)

        OpIooPathWb.write(_wb_evup_adm, _out_path_evup_adm)
        OpIooPathWb.write(_wb_evup_del, _out_path_evup_del)
        _doaod_evin_vfy = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_vfy, _out_path_evin_reg_vfy)

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
          single Xlsx Workbook with a populated admin- or delete-sheet
          two xlsx Workbooks:
            the first one contains a populated admin-sheet
            the second one contains a populated delete-sheet
        """
        _sw_single_wb: TyBool = kwargs.get('sw_single_wb', True)
        if _sw_single_wb:
            # write single workbook which contains admin and delete worksheets
            cls.evupreg_reg_wb(kwargs)
        else:
            # write separate workbooks for admin and delete worksheets
            cls.evupreg_adm_del_wb(kwargs)

    @classmethod
    def evdomap(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _out_path_evex = PathNm.sh_path(_cfg.OutPath.evex, kwargs)
        _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)
        _d_ecv_iq2umh_iq = _cfg.Utils.d_ecv_iq2umh_iq
        _aod_evex: TnAoD = PdIoiPathWb.read_wb_to_aod(
            _in_path_evex, _sheet_exp, **cls.kwargs_wb)
        _aod_evex_new = Evex.map(_aod_evex, _d_ecv_iq2umh_iq)
        PeIooPathWb.write_wb_from_aod(
            _aod_evex_new, _out_path_evex, _sheet_exp)
