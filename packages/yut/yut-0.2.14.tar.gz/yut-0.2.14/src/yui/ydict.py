# -*- ydict.py: python ; coding: utf-8 -*-
#####################################################
# 数据字典及其存取
#####################################################
from enum import Enum

from yui import TranslateDirection
from yut import get_attr, has_attr


class DictType(Enum):
    VALUE = 0
    ENUM = 1
    DIM = 2


class DictLoader:
    def __init__(self, name_space):
        self._name_space = name_space

    def load(self, dict_type: DictType, dict_key: str):
        return {}

    def name_space(self):
        return self._name_space


class DictFetcher:
    AttrEnumKey = 'enum_key'
    AttrDimKey = 'dim_key'
    AttrDictValue = 'dict_value'

    _INSTANCE = None

    def __init__(self, loader: DictLoader = None):
        self._dicts = {}  # 正向 code -> text 字典
        self._re_dicts = {}  # 反向 text -> code 字典
        self.loader = loader

    def add_dict(self, group, a_dict):
        self._dicts[group] = a_dict  # 正向
        self._re_dicts[group] = {v: k for k, v in a_dict.items()}

    def groups(self):
        return list(self._data().keys())

    def _data(self):
        return self._dicts

    def get(self, group_type: DictType, group_key, direction=TranslateDirection.TO_TEXT):
        cached_dicts = self._dicts if direction == TranslateDirection.TO_TEXT else self._re_dicts
        m_dict = cached_dicts.get(group_key)
        if m_dict is None:
            m_dict = self._load_dict(group_type, group_key)
            if m_dict:
                self.add_dict(group_key, m_dict)
        return cached_dicts.get(group_key)

    def get_dict(self, obj):
        """
        字典加载函数
        :param obj:
        :return:
            根据Obj的特定属性决定加载或者直接解析dict的值，然后返回字典对象。
            :param obj: obj：
                'dict_value': 若obj存在dict_value属性，直接返回属性值;
                'enum_key': 若obj存在enum_key属性，按照属性值加载枚举字典;
                'dim_key': 若obj存在dim_key属性，按照属性值加载统计码字典;
            :return:
        """
        group_key = None
        group_type = DictType.VALUE
        if has_attr(obj, self.AttrDictValue):
            dict_value = get_attr(obj, self.AttrDictValue)
            return dict_value if isinstance(dict_value, dict) else eval(dict_value)
        if has_attr(obj, self.AttrEnumKey):
            group_type, group_key = DictType.ENUM, get_attr(obj, self.AttrEnumKey)
        elif self.loader and has_attr(obj, self.AttrDimKey):
            group_type, group_key = DictType.DIM, get_attr(obj, self.AttrDimKey)
        return self.get(group_type, group_key)

    def set_loader(self, loader):
        self.loader = loader

    def _load_dict(self, group_type: DictType, group_key):
        if self.loader:
            return self.loader.load(group_type, group_key)
        else:
            return {}

    @staticmethod
    def instance():
        if DictFetcher._INSTANCE is None:
            DictFetcher._INSTANCE = DictFetcher()
        return DictFetcher._INSTANCE
