"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from ut_path.pathnm import PathNm

import ut_xls.op.ioipathwb.IoiPathWb as OpIoiPathWb
# import ut_xls.pd.ioipathwb.IoiPathWb as PdIoiPathWb
import ut_xls.op.ioopathwb.IooPathWb as OpIooPathWb
import ut_xls.pe.ioopathwb.IooPathWb as PeIooPathWb

import ut_eviq.cfg.Cfg as Cfg

# import pandas as pd
import openpyxl as op

from typing import Any, TypeAlias
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb


class TaskIoc:
    @classmethod
    def evupadm(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_adm, _sheet_adm)

        _out_path_evup_adm = PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs)
        OpIooPathWb.write(_wb_evup_adm, _out_path_evup_adm)

        _out_path_evin_adm_vfy = PathNm.sh_path(_cfg.OutPath.evin_adm_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_adm_vfy, _out_path_evin_adm_vfy)

    @classmethod
    def evupdel(cls, tup_del: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _aod_evup_del, _doaod_evin_del_vfy = tup_del
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_del(
                _in_path_evup_tmp, _aod_evup_del, _sheet_del)

        _out_path_evup_del = PathNm.sh_path(_cfg.OutPath.evup_del, kwargs)
        OpIooPathWb.write(_wb_evup_del, _out_path_evup_del)

        _out_path_evin_del_vfy = PathNm.sh_path(_cfg.OutPath.evin_del_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_del_vfy, _out_path_evin_del_vfy)

    @classmethod
    def evupreg_reg_wb(
            cls,
            tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD],
            kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _wb_evup_reg: TnOpWb = OpIoiPathWb.sh_wb_reg(
           _in_path_evup_tmp, _aod_evup_adm, _aod_evup_del, _sheet_adm, _sheet_del)

        _out_path_evup_reg = PathNm.sh_path(_cfg.OutPath.evup_reg, kwargs)
        OpIooPathWb.write(_wb_evup_reg, _out_path_evup_reg)

        _doaod_evin_vfy = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        _out_path_evin_reg_vfy = PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_vfy, _out_path_evin_reg_vfy)

    @classmethod
    def evupreg_adm_del_wb(
            cls,
            tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD],
            kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evup_tmp = PathNm.sh_path(_cfg.InPath.evup_tmp, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_adm, _sheet_adm)

        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, _aod_evup_del, _sheet_del)

        _out_path_evup_adm = PathNm.sh_path(_cfg.OutPath.evup_adm, kwargs)
        OpIooPathWb.write(_wb_evup_adm, _out_path_evup_adm)

        _out_path_evup_del = PathNm.sh_path(_cfg.OutPath.evup_del, kwargs)
        OpIooPathWb.write(_wb_evup_del, _out_path_evup_del)

        _out_path_evin_reg_vfy = PathNm.sh_path(_cfg.OutPath.evin_reg_vfy, kwargs)
        _doaod_evin_vfy = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_vfy, _out_path_evin_reg_vfy)

    @classmethod
    def evdomap(cls, aod_evex: TyAoD, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _cfg = kwargs.get('Cfg', Cfg)

        _out_path_evex = PathNm.sh_path(_cfg.OutPath.evex, kwargs)
        _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)
        PeIooPathWb.write_wb_from_aod(aod_evex, _out_path_evex, _sheet_exp)
