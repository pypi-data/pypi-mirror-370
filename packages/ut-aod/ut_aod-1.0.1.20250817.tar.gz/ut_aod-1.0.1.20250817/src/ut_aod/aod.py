# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any
import traceback

import copy
import csv
import pandas as pd
import polars as pl

import ut_dic.doc.DoC as DoC
import ut_log.log.Log as Log

TyPdDf = pd.DataFrame
TyPlDf = pl.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyTup = tuple[Any, ...]
TyAoT = list[TyTup]
TyBool = bool
TyCallable = Callable[..., Any]
TyDoA = dict[Any, TyArr]
TyDoD = dict[Any, TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoC = dict[str, TyCallable]
TyPath = str
TyIoD = Iterator[TyDic]
TyStr = str
TyToAoD = tuple[TyAoD, TyAoD]

TnAny = None | Any
TnArr = None | TyArr
TnAoA = None | TyAoA
TnCallable = None | TyCallable
TnDic = None | TyDic
TnAoD = None | TyAoD
TnStr = None | TyStr
TnDoAoD = None | TyDoAoD


class AoD:
    """
    Manage Array of Dictionaries
    """
    @staticmethod
    def add(aod: TyAoD, obj: Any) -> None:
        if isinstance(obj, dict):
            aod.append(obj)
        elif isinstance(obj, list):
            aod.extend(obj)
        else:
            _msg = f"AoD.add: object {obj} is not a dictionary or list"
            raise Exception(_msg)

    @staticmethod
    def append_unique(aod: TyAoD, item: TyDic) -> None:
        if aod is None:
            return
        if not item:
            return
        if item not in aod:
            aod.append(item)

    @staticmethod
    def apply_function(aod: TyAoD, fnc: TnCallable, kwargs: TnDic) -> TyAoD:
        _aod_new: TyAoD = []
        try:
            if not aod or not fnc:
                return aod
            for _dic in aod:
                _dic = fnc(_dic, kwargs)
                _aod_new.append(_dic)
            return _aod_new
        except Exception as e:
            Log.error(f"An ERROR occurred: {e}")
            Log.error(traceback.format_exc())
            return _aod_new

    @staticmethod
    def dic_found_with_empty_value(
            aod: TyAoD, key: str, sw_raise: bool = False) -> TyBool:
        # dic_value_is_empty(aod: TyAoD, key: str) -> TyBool:
        for _dic in aod:
            if not _dic[key]:
                if sw_raise:
                    msg = f"Value for key={key} for dictionary={_dic} is empty"
                    raise Exception(msg)
                return True
        return False

    @staticmethod
    def extend_if_not_empty(
          aod: TyAoD, dic: TnDic, key: TnAny, fnc: TyCallable) -> TyAoD:
        # if Dic.Value.is_empty(dic, key):
        #   return aod
        if not aod:
            aod_new: TyAoD = []
        else:
            aod_new = aod
        if not dic:
            return aod_new
        if not key:
            return aod_new
        if key not in dic:
            return aod_new
        _aod: TyAoD = fnc(dic[key])
        aod_new.extend(_aod)
        return aod_new

    @classmethod
    def merge_aod(
            cls, aod0: TnAoD, aod1: TnAoD, method: TyStr = 'unpack') -> TyAoD:
        if not aod0:
            if not aod1:
                return []
            return aod1
        if not aod1:
            return aod0
        match method:
            case 'unpack':
                return cls.merge_aod_unpack(aod0, aod1)
            case 'update':
                return cls.merge_aod_update(aod0, aod1)
            case _:
                return cls.merge_aod_other(aod0, aod1)

    @staticmethod
    def merge_aod_unpack(aod0: TyAoD, aod1: TyAoD) -> TyAoD:
        # def merge_aod_unpack(aod0: TyAoD, aod1: TyAoD) -> TyAoD:
        aod_new: TyAoD = []
        for _dic0 in aod0:
            for _dic1 in aod1:
                _dic_new = {**_dic0, **_dic1}
                aod_new.append(_dic_new)
        return aod_new

    @staticmethod
    def merge_aod_update(aod0: TyAoD, aod1: TyAoD) -> TyAoD:
        # def merge_aod_update(aod0: TyAoD, aod1: TyAoD) -> TyAoD:
        aod_new: TyAoD = []
        for _dic0 in aod0:
            _dic_new = copy.deepcopy(_dic0)
            for _dic1 in aod1:
                _dic_new.update(_dic1)
                aod_new.append(_dic_new)
        return aod_new

    @staticmethod
    def merge_aod_other(aod0: TyAoD, aod1: TyAoD) -> TyAoD:
        aod_new: TyAoD = []
        for _dic0 in aod0:
            _dic_new = copy.deepcopy(_dic0)
            for _dic1 in aod1:
                for key, value in _dic1.items():
                    _dic_new[key] = value
                aod_new.append(_dic_new)
        return aod_new

    @classmethod
    def merge_dic(cls, aod: TnAoD, dic: TnDic, method: TyStr = 'unpack') -> TyAoD:
        # def merge_dic(cls, aod: TnAoD, dic: TnDic, method: TyStr = 'unpack') -> TyAoD:
        if not aod:
            if not dic:
                return []
            return [dic]
        if not dic:
            return []
        return cls.merge_aod(aod, [dic], method)

    @staticmethod
    def nvl(aod: TnAoD) -> TyArr | TyAoD:
        """
        nvl function similar to SQL NVL function
        """
        if not aod:
            aod_new = []
        else:
            aod_new = aod
        return aod_new

    @classmethod
    def put(cls, aod: TyAoD, path: str, fnc_aod: TnCallable, df_type: TyStr) -> None:
        """
        Write transformed array of dictionaries to a csv file with an
        I/O function selected by a dataframe type in a function table.
        """
        _fnc_2_csv: TnCallable = cls.sh_fnc_2_csv(df_type)
        if _fnc_2_csv is None:
            return
        _fnc_2_csv(aod, path, fnc_aod)

    @staticmethod
    def sh_doaod_split_by_value_is_not_empty(
            aod: TyAoD, key: Any, key_n: Any, key_y: Any) -> TyDoAoD:
        _aod_y = []
        _aod_n = []
        for _dic in aod:
            if key in _dic:
                if _dic[key]:
                    _aod_y.append(_dic)
                else:
                    _aod_n.append(_dic)
            else:
                _aod_n.append(_dic)
        doaod = {}
        doaod[key_n] = _aod_n
        doaod[key_y] = _aod_y
        return doaod

    @staticmethod
    def sh_dod(aod: TyAoD, key: Any) -> TyDoD:
        dod: TyDoD = {}
        for dic in aod:
            value = dic[key]
            if value not in dod:
                dod[value] = {}
            for k, v in dic.items():
                dod[value][k] = v
        return dod

    @staticmethod
    def sh_key_value_found(aod: TnAoD, key: Any, value: Any) -> bool:
        # def sw_key_value_found(aod: TnAoD, key: Any, value: Any) -> bool:
        """
        find first dictionary whose key is equal to value
        """
        if not aod:
            return False
        for dic in aod:
            if dic[key] == value:
                return True
        return False

    @staticmethod
    def sh_unique(aod: TyAoD) -> TyAoD:
        # Convert aod into a list of dict_items
        aod_items = (tuple(d.items()) for d in aod)
        # Deduplicate elements
        aod_deduplicated = set(aod_items)
        # Convert the dict_items back to dicts
        aod_new = [dict(i) for i in aod_deduplicated]
        return aod_new

    @staticmethod
    def split_by_value_is_not_empty(aod: TyAoD, key: Any) -> TyToAoD:
        aod_y = []
        aod_n = []
        for _dic in aod:
            if key in _dic:
                if _dic[key]:
                    aod_y.append(_dic)
                else:
                    aod_n.append(_dic)
            else:
                aod_n.append(_dic)
        return aod_n, aod_y

    @staticmethod
    def to_aoa(aod: TnAoD, sw_keys: TyBool = True, sw_values: TyBool = True) -> TnAoA:
        if not aod:
            return None
        aoa: TyAoA = []
        if sw_keys:
            aoa.append(list(aod[0].keys()))
        if sw_values:
            for _dic in aod:
                aoa.append(list(_dic.values()))
        return aoa

    @staticmethod
    def to_aoa_of_keys_values(aod: TyAoD) -> TyAoA:
        """
        Migrate Array of Dictionaries to Array of Keys and Values
        """
        aoa: TyAoA = []
        if not aod:
            return aoa
        aoa.append(list(aod[0].keys()))
        for _dic in aod:
            aoa.append(list(_dic.values()))
        return aoa

    @staticmethod
    def to_aoa_of_values(aod: TyAoD) -> TyAoA:
        """
        Migrate Array of Dictionaries to Array of Values
        """
        _aoa: TyAoA = []
        if aod == []:
            return _aoa
        for _dic in aod:
            _aoa.append(list(_dic.values()))
        return _aoa

    @staticmethod
    def to_arr_of_key_values(aod: TyAoD, key: Any) -> TyArr:
        """
        Migrate Array of Dictionaries to Array of Key Values
        """
        arr: TyArr = []
        if aod == []:
            return arr
        for _dic in aod:
            for (_k, _v) in _dic.items():
                if _k == key:
                    arr.append(_v)
        return arr

    @staticmethod
    def to_csv_with_dictwriterows(aod: TyAoD, path: TyPath) -> None:
        # def csv_dictwriterows(aod: TyAoD, path: TyPath) -> None:
        aod = aod or []
        if not aod:
            return
        with open(path, 'w', newline='') as fd:
            writer = csv.DictWriter(fd, fieldnames=aod[0].keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(aod)

    @staticmethod
    def to_csv_with_pd(aod: TyAoD, path: TyPath, fnc_pd: TnCallable = None) -> None:
        # def pd_to_csv(aod: TyAoD, path: TyPath, fnc_pd: TnCall = None) -> None:
        aod = aod or []
        if not aod:
            return
        # pddf = pd.DataFrame.from_dict(aod)
        pddf = pd.DataFrame(aod)
        if fnc_pd is not None:
            pddf = fnc_pd(pddf)
        pddf.to_csv(path, index=False)

    @staticmethod
    def to_csv_with_pl(aod: TyAoD, path: TyPath, fnc_pl: TnCallable = None) -> None:
        # def pl_to_csv(aod: TyAoD, path: TyPath, fnc_pl: TnCallable = None) -> None:
        aod = aod or []
        if not aod:
            return
        # migrate aod to pandas dataframe and that to polars dataframe
        # pddf = pd.DataFrame.from_dict(aod)
        pddf = pd.DataFrame(aod)
        pldf = pl.from_pandas(pddf)
        if fnc_pl is not None:
            pldf = fnc_pl(pldf)
        pldf.write_csv(path, include_header=True)

    @staticmethod
    def to_dic_by_dic(
            aod: TnAoD, d_meta: TnDic = None) -> TyDic:
        """
        Migrate Array of Dictionaries to Dictionary by key-, value-name
        """
        if not aod or not d_meta:
            return {}
        dic_new: TyDic = {}
        for _dic in aod:
            dic_new[_dic[d_meta['k']]] = _dic[d_meta['v']]
        return dic_new

    @staticmethod
    def to_dic_by_ix(aod: TnAoD) -> TyDic:
        """
        Migrate Array of Dictionaries to Dictionary by key-, value-name
        """
        if not aod:
            return {}
        dic_new: TyDic = {}
        for _dic in aod:
            _aot: TyAoT = list(_dic.items())
            dic_new[_aot[0][1]] = _aot[1][1]
        return dic_new

    @staticmethod
    def to_doaod_by_key(aod: TnAoD, key: TnAny) -> TyDoAoD:
        """
        Migrate Array of Dictionaries to Array of Key Values
        """
        doaod: TyDoAoD = {}
        if not aod:
            return doaod
        if not key:
            return doaod
        for dic in aod:
            if key in dic:
                value = dic[key]
                if value not in doaod:
                    doaod[value] = []
                doaod[value].append(dic)
        return doaod

    @staticmethod
    def xto_dod_by_key(iter_dic, key: Any) -> TyDoD:
        """
        find first dictionary whose key is equal to value
        """
        dod: TyDoD = {}
        for _dic in iter_dic:
            _value = _dic[key]
            if _value in dod:
                _msg = (f"AoD.to_dod_by_key: "
                        f"Error key: {_value} "
                        f"allready exists in {dod}")
                Log.error(_msg)
            else:
                dod[_value] = _dic
        return dod

    @staticmethod
    def xto_doa_by_lc_of_keys(iter_dic: TyIoD, key0: Any, key1: Any) -> TyDoA:
        # def tolc_doa_by_keys(iter_dic: TyIoD, key0: Any, key1: Any) -> TyDoA:
        doa: TyDoA = {}
        for _dic in list(iter_dic):
            value0 = _dic[key0].lower()
            value1 = _dic[key1].lower()
            if value0 in doa:
                doa[value0].append(value1)
            else:
                doa[value0] = [value1]
        return doa

    @classmethod
    def to_unique_by_key(cls, aod: TyAoD, key: Any) -> TyAoD:
        """
        find first dictionary whose key is equal to value
        """
        aod_new: TyAoD = []
        for _dic in aod:
            _value = _dic.get(key)
            if not _value:
                continue
            if cls.sh_key_value_found(aod_new, key, _value):
                continue
            aod_new.append(_dic)
        return aod_new

    # @staticmethod
    # def write_xlsx_wb(aod: TyAoD, path: str, sheet_id: str) -> None:
    #     wb = Workbook()
    #     a_header = [list(aod[0].keys())]
    #     a_data = [list(d.values()) for d in aod]
    #     a_row = a_header + a_data
    #     wb.new_sheet(sheet_id, data=a_row)
    #     wb.save(path)

    # @classmethod
    # def sh_fnc_2_csv(cls, df_type):
    #     match df_type:
    #         case 'pd':
    #             return cls.pd_to_csv,
    #         case 'pl':
    #             return cls.pl_to_csv,
    #         case 'dw':
    #             return cls.csv_dictwriterows
    #         case '_':
    #             msg = (f'wrong df_type = {df_type}'
    #                    'valid df_type = pd,pl,dw')
    #             raise Exception(msg)

    @staticmethod
    def sh_fnc_2_csv(df_type) -> TnCallable:
        fnc: TnCallable = DoC.sh(DoCoAoD.doc, df_type)
        return fnc

    @staticmethod
    def union(aod1: TnAoD, aod2: TnAoD) -> TnAoD:
        if aod1 is None:
            aod = aod2
        elif aod2 is None:
            aod = aod1
        else:
            aod = aod1 + [item for item in aod2 if item not in aod1]
        return aod


class IoD:

    @staticmethod
    def to_dod_by_key(iter_dic: TyIoD, key: Any) -> TyDoD:
        """
        find first dictionary whose key is equal to value
        """
        dod: TyDoD = {}
        for _dic in iter_dic:
            _value = _dic[key]
            if _value in dod:
                _msg = (f"AoD.to_dod_by_key: "
                        f"Error key: {_value} "
                        f"allready exists in {dod}")
                Log.error(_msg)
            else:
                dod[_value] = _dic
        return dod

    @staticmethod
    def to_doa_by_lc_of_keys(iter_dic: TyIoD, key0: Any, key1: Any) -> TyDoA:
        # def tolc_doa_by_keys(iter_dic: TyIoD, key0: Any, key1: Any) -> TyDoA:
        doa: TyDoA = {}
        for _dic in list(iter_dic):
            value0 = _dic[key0].lower()
            value1 = _dic[key1].lower()
            if value0 in doa:
                doa[value0].append(value1)
            else:
                doa[value0] = [value1]
        return doa


class DoCoAoD:
    """
    Dictionary of callables of class AoD
    """
    doc: TyDoC = {
            'pd': AoD.to_csv_with_pd,
            'pl': AoD.to_csv_with_pl,
            'dw': AoD.to_csv_with_dictwriterows,
    }
