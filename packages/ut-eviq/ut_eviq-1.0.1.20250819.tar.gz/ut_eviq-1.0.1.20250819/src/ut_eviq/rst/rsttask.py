"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from ka_uts_http.httpx_ import Request
from ka_uts_xls.wbop import WbOp
from ka_uts_xls.ioipathnm import IoiPathnmWbOp as IoiWbOp
from ka_uts_xls.ioowbpe import IooPathnmWbPe as IooWbPe
from ka_uts_xls.ioowbop import IooPathnmWbOp as IooWbOp

from umh_otev.srr.cfgtask import CfgTask
from umh_otev.srr.cfgutils import CfgUtils
from umh_otev.srr._task import _Task

# import pandas as pd
import openpyxl as op

from typing import Any
TyWbOp = op.Workbook

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyCmd = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnWbOp = None | TyWbOp


class Url:

    @classmethod
    def sh_base(cls, kwargs: TyDic) -> TyStr:
        _url_version: TyStr = kwargs.get('url_version', CfgTask.url_version)
        _url_type: TyStr = kwargs.get('url_type', 'sandbox')
        _url: TyStr = CfgTask.d_url[_url_type]['url']
        return f"{_url}://{_url_version}"


class EvToken:

    @staticmethod
    def get(kwargs: TyDic) -> TyAny:
        _base_url = Url.sh_base(kwargs)
        _url = f"{_base_url}/EVToken"
        _headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
        }
        _url_user = kwargs.get('url_user')
        _url_password = kwargs.get('url_password')
        _params = {
                'grant_type': 'password',
                'username': _url_user,
                'password': _url_password
        }
        return Request.get(_url, headers=_headers, params=_params)


class IqPartners:

    @staticmethod
    def export(
            d_response_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        _base_url = Url.sh_base(kwargs)
        _url = f"{_base_url}/IqPartners/GetPartnerByUniqueId"
        _access_token = d_response_evtoken['json']['access_token']
        # _token_type = d_response_evtoken['json']['token_type']
        _headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {_access_token}"
        }
        _uniqueId = dic['Eindeutige ID']
        _params = {
                'UniqueId': _uniqueId
        }
        return Request.get(_url, headers=_headers, params=_params)

    @staticmethod
    def upsert(
            d_resp_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        _base_url = Url.sh_base(kwargs)
        _url = f"{_base_url}/IqPartners/UpdatePartner"
        _access_token = d_resp_evtoken['json']['access_token']
        # _token_type = d_resp_evtoken['json']['token_type']
        _headers: TyDic = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {_access_token}"
        }
        _params: TyDic = {}
        _data: TyDic = {}
        return Request.post(_url, headers=_headers, params=_params, data=_data)

    @staticmethod
    def getoperationstatus(
            d_resp_evtoken: TyDic, dic: TyDic, kwargs: TyDic) -> TyAny:
        _base_url = Url.sh_base(kwargs)
        _url = f"{_base_url}/IqPartners/GetOperationStatus"
        _access_token = d_resp_evtoken['json']['access_token']
        # _token_type = d_resp_evtoken['json']['token_type']
        _headers: TyDic = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {_access_token}"
        }
        _operationid = dic.get('operationId')
        _params: TyDic = {
                'operationId': _operationid
        }
        return Request.get(_url, headers=_headers, params=_params)


class Task:

    @classmethod
    def evupadm(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Administration (create, update) of partners using the Rest API
        """
        _aod_evup_adm, _doaod_otev_adm_vfy = _Task.evup_adm(kwargs)

        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in _aod_evup_adm:
            _d_resp: TyDic = IqPartners.upsert(
                    _d_resp_evtoken, _dic, kwargs)
            _d_resp_dict: TyDic = _d_resp.get('dict', {})
            _errorlist = _d_resp_dict.get('ErrorList')
            if not _errorlist:
                return
            while True:
                _d_resp_evtoken = IqPartners.getoperationstatus(_d_resp_evtoken, _dic, kwargs)

        IooWbPe.write_wb_from_doaod(
                _doaod_otev_adm_vfy, CfgTask.out_path_otev_adm_vfy, **kwargs)

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Deletion of partners using the Rest API
        """
        _aod_evup_del, _doaod_otev_del_vfy0, _doaod_otev_del_vfy1 = _Task.evup_del(
                kwargs)

        if _aod_evup_del is not None:
            _d_resp_evtoken: TyDic = EvToken.get(kwargs)
            for _dic in _aod_evup_del:
                _d_resp: TyDic = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
                _d_resp_dict: TyDic = _d_resp.get('dict', {})

        IooWbPe.write_wb_from_doaod(
                _doaod_otev_del_vfy0, CfgTask.out_path_otev_del_vfy0, **kwargs)
        IooWbPe.write_wb_from_doaod(
                _doaod_otev_del_vfy1, CfgTask.out_path_otev_del_vfy1, **kwargs)

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using the Rest API
        """
        _aod_evup_adm, _doaod_otev_adm_vfy = _Task.evup_adm(kwargs)
        _aod_evup_del, _doaod_otev_del_vfy0, _doaod_otev_del_vfy1 = _Task.evup_del(
                kwargs)

        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in _aod_evup_adm:
            _d_resp: TyDic = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
            _d_resp_dict: TyDic = _d_resp.get('dict', {})

        if _aod_evup_del is not None:
            for _dic in _aod_evup_del:
                _d_resp = IqPartners.upsert(_d_resp_evtoken, _dic, kwargs)
                _d_resp_dict = _d_resp.get('dict', {})

        IooWbPe.write_wb_from_doaod(
                _doaod_otev_adm_vfy, CfgTask.out_path_otev_adm_vfy, **kwargs)
        IooWbOp.write_wb_from_doaod(
                _doaod_otev_del_vfy0, CfgTask.out_path_otev_del_vfy0, **kwargs)
        IooWbOp.write_wb_from_doaod(
                _doaod_otev_del_vfy1, CfgTask.out_path_otev_del_vfy1, **kwargs)

    @classmethod
    def evdoexp(cls, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing:
        Export EcoVadis data with the Rest API
        """
        _aod_evup_adm, _doaod_otev_adm_vfy = _Task.evup_adm(kwargs)

        _d_resp_evtoken: TyDic = EvToken.get(kwargs)
        for _dic in _aod_evup_adm:
            _d_resp: TyDic = IqPartners.upsert(
                    _d_resp_evtoken, _dic, kwargs)
            _d_resp_dict = _d_resp.get('dict', {})
            _aod_evup_adm = []
            for _key_en, _value in _d_resp_dict.items():
                _key_de = CfgUtils.d_evup_en2de.get(_key_en)
                if _key_de:
                    _dic[_key_de] = _value
                    _aod_evup_adm.append(_dic)

        _wb_evup_tmp: TnWbOp = IoiWbOp.load(
                "in_path_evup_tmp", kwargs, read_only=False)
        WbOp.update_wb_with_aod(_wb_evup_tmp, _aod_evup_adm, CfgTask.in_sheet_otev_adm)
        IooWbOp.write(_wb_evup_tmp, CfgTask.out_path_evup_adm, **kwargs)

        IooWbPe.write_wb_from_doaod(
                _doaod_otev_adm_vfy, CfgTask.out_path_otev_adm_vfy, **kwargs)
