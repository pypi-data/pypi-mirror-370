# import builtins
from collections.abc import Callable
from typing import Any

from ut_aod.aod import AoD
from ut_dic.dic import Dic

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyKey = Any
TyKeys = Any | TyArr
TyTup = tuple[Any, ...]

TnAny = None | Any
TnAoD = None | TyAoD
TnArr = None | TyArr
TnBool = None | bool
TnCallable = None | TyCallable
TnDic = None | TyDic


class FoA:
    """
    Class for flatten of Arrays
    """
    @classmethod
    def flatten_merge_to_aod(cls, arr: TyArr, aod: TyAoD, key: str) -> TyAoD:
        if not arr:
            return aod
        _aod_list: TyAoD = []
        _aod_dict: TyAoD = []
        _aod_else: TyAoD = []
        for _item in arr:
            if isinstance(_item, list):
                _aod: TyAoD = []
                _aod = cls.flatten_merge_to_aod(_item, _aod, key)
                _aod_list.extend(_aod)
            elif isinstance(_item, dict):
                _aod = []
                _aod = FoD.flatten_to_aod(_item, _aod)
                _aod_dict.extend(_aod)
            else:
                # get last key by negative indexing
                _aod = AoD.merge_dic(aod, {key : _item})
                _aod_else.extend(_aod)
        aod = AoD.merge_aod(aod, _aod_list)
        aod = AoD.merge_aod(aod, _aod_dict)
        aod = AoD.merge_aod(aod, _aod_else)
        return aod

    @staticmethod
    def flattenx_keys(
            arr: TnArr, d_flatten: TnDic) -> Any:
        if arr is None:
            return arr
        if d_flatten is None:
            return arr[-1]
        sw: bool = d_flatten.get('sw_keys', False)
        if sw:
            sep: Any = d_flatten.get('sep_keys', '.')
            return sep.join(arr)
        return arr[-1]

    @classmethod
    def flattenx_merge_to_aod(
            cls, arr: TyArr, aod: TyAoD, keys: Any, d_flatten: TnDic) -> TyAoD:
        if not arr:
            return aod
        _aod_list: TyAoD = []
        _aod_dict: TyAoD = []
        _aod_else: TyAoD = []
        for _item in arr:
            if isinstance(_item, list):
                _aod: TyAoD = []
                _aod = cls.flattenx_merge_to_aod(_item, keys, _aod, d_flatten)
                _aod_list.extend(_aod)
            elif isinstance(_item, dict):
                _aod = []
                _aod = FoD.flattenx_to_aod(_item, keys, _aod, d_flatten)
                _aod_dict.extend(_aod)
            else:
                _key = cls.flattenx_keys(keys, d_flatten)
                _aod = AoD.merge_dic(
                        aod, {_key : _item})
                _aod_else.extend(_aod)
        aod = AoD.merge_aod(aod, _aod_list)
        aod = AoD.merge_aod(aod, _aod_dict)
        aod = AoD.merge_aod(aod, _aod_else)
        return aod


class FoD:
    """
    Class for flatten of Dictionaries
    """
    @classmethod
    def flatten_to_aod(
            cls, dic: TnDic, aod: TyAoD) -> TyAoD:
        if not dic:
            return aod
        _dic_else: TyDic = {}
        for _key, _val in dic.items():
            if isinstance(_val, dict):
                _aod: TyAoD = []
                aod = AoD.merge_aod(
                        aod,
                        cls.flatten_to_aod(_val, _aod))
            elif isinstance(_val, list):
                aod = FoA.flatten_merge_to_aod(_val, aod, _key)
            else:
                _dic_else[_key] = _val

        aod = AoD.merge_dic(aod, _dic_else)
        return aod

    @classmethod
    def flatten(cls, dic: TnDic) -> TyAoD:
        if not dic:
            return []
        _aod: TyAoD = []
        return cls.flatten_to_aod(dic, _aod)

    @classmethod
    def flatten_by_d2p(
            cls, dic: TnDic, d_meta: TnDic) -> TnAoD:
        if d_meta is None:
            return cls.flatten(dic)
        else:
            meta_key = d_meta['key']
            d_meta_kv = d_meta['kv']
            aod2p, d_other = Dic.split_by_key(dic, meta_key)
            aod: TyAoD = AoD.merge_dic(
                    cls.flatten(d_other),
                    AoD.to_dic_by_dic(aod2p, d_meta_kv))
            return aod

    @classmethod
    def flattenx_to_aod(
            cls, dic: TnDic, aod: TyAoD, keys: TyKeys, d_flatten: TnDic
    ) -> TyAoD:
        if not dic:
            return aod
        _dic_else: TyDic = {}
        for _key, _val in dic.items():
            if isinstance(_val, dict):
                _keys = keys.copy()
                _keys.append(_key)
                _aod: TyAoD = []
                aod = AoD.merge_aod(
                        _aod, cls.flattenx_to_aod(_val, _aod, _keys, d_flatten))
            elif isinstance(_val, list):
                _keys = keys.copy()
                _keys.append(_key)
                aod = FoA.flattenx_merge_to_aod(_val, aod, _keys, d_flatten)
            else:
                _key = FoA.flattenx_keys(keys, d_flatten)
                _dic_else[_key] = _val
        aod = AoD.merge_dic(aod, _dic_else)
        return aod

    @classmethod
    def flattenx_by_d2p(
            cls, dic: TnDic, d_meta: TnDic, d_flatten: TnDic) -> TnAoD:
        if d_meta is None:
            return cls.flattenx(dic, d_flatten)
        else:
            meta_key = d_meta['key']
            d_meta_kv = d_meta['kv']
            aod2p, d_other = Dic.split_by_key(dic, meta_key)
            aod: TyAoD = AoD.merge_dic(
                    cls.flattenx(d_other, d_flatten),
                    AoD.to_dic_by_dic(aod2p, d_meta_kv))
            return aod

    @classmethod
    def flattenx(cls, dic: TnDic, d_flatten: TnDic = None) -> TyAoD:
        if not dic:
            return []
        _aod: TyAoD = []
        if d_flatten is None:
            return cls.flatten_to_aod(dic, _aod)
        _sw_keys: bool = d_flatten.get('sw_keys', False)
        if _sw_keys:
            _keys: TyArr = []
            _aod = cls.flattenx_to_aod(dic, _aod, _keys, d_flatten)
        else:
            _aod = cls.flatten_to_aod(dic, _aod)
        # apply function
        _fnc: TnCallable = d_flatten.get("fnc")
        if not _fnc:
            return _aod
        _kwargs: TnDic = d_flatten.get("kwargs")
        aod: TyAoD = AoD.apply_function(_aod, _fnc, _kwargs)
        return aod
