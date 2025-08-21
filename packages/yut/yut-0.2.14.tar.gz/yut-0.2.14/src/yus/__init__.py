# -*- __init__.py: python ; coding: utf-8 -*-
import base64
import pickle
from enum import Enum

from pandas import DataFrame
from sqlalchemy import or_
from sqlalchemy.orm import Query

from yut import json_dump, copy_obj, get_attr, json_load, set_attr


class UnitType:
    """
    字段单元代表符号
    不要声明为枚举类型，方便json传递时直接使用字面量名称
    """
    TEXT = '*'  # 文本
    SWITCH = '!'  # 开关
    NUMBER = '.'  # 小数
    CURRENCY = '$'  # 金额
    INT = '#'  # 整数
    DATE = 'd'  # 日期
    TIME = 't'  # 日期时间
    YEAR = 'y'  # 年份
    YEAR_MONTH = 'm'  # 年月
    CHOOSE = '@'  # 字典或码表选择
    LOOKUP = '?'  # 对照映射
    PERCENT = '%'  # 百分比
    CLOCK = 'cl'  # 时刻
    RICH_TEXT = 'rt'  # 长文本


class ChooseMode:
    """
    选择单元的具体选取模式
    不要声明为枚举类型，方便json传递时直接使用字面量名称
    """
    LIST = 0
    RADIO = 1
    CHECK = 2


class DisplayAttitude:
    """
    显示调性，方便json传递时直接使用字面量名称
    """
    NEGATIVE = '--'  # 阴性: 消极/反向/负面/异常/出错
    WEAK_NEGATIVE = '-'  # 弱阴 - 预警
    NEUTRAL = '='  # 中性
    WEAK_POSITIVE = '+'  # 弱阳
    POSITIVE = '++'  # 阳性: 积极/正向/正面/正常/无差错
    INACTIVE = '~'  # 失能：处于无效/失效状态


class Op(Enum):
    EQU = '='
    GE = '>='  # >=
    GT = '>'  # >
    LE = '<='  # <=
    LT = '<'  # <
    NEQ = '!='  # !=
    BETWEEN = '~'
    IN = '@'
    NOT_IN = '!@'  # not in
    LIKE = '*'
    NOT_LIKE = '!*'
    LIKE_IN = '**'  # like A or like B or like C ...

    def text(self):
        return {
            Op.EQU: '等于',
            Op.GE: '不低于',
            Op.GT: '高于',
            Op.LE: '不高于',
            Op.LT: '小于',
            Op.NEQ: '不等于',
            Op.BETWEEN: '范围',
            Op.IN: '属于',
            Op.NOT_IN: '不属于',
            Op.LIKE: '匹配',
            Op.NOT_LIKE: '不匹配',
            Op.LIKE_IN: '用"|"分隔的多值匹配',
        }.get(self)

    def filter_q(self, query: Query, field, value) -> Query:
        if self == Op.LIKE_IN and isinstance(value, str):  # LIKE_IN 支持'',''分割的多个str自动转换
            value = value.split('|')
        d = {
            Op.EQU: lambda q, a, v: q.filter(a == v),
            Op.GE: lambda q, a, v: q.filter(a >= v),
            Op.GT: lambda q, a, v: q.filter(a > v),
            Op.LE: lambda q, a, v: q.filter(a <= v),
            Op.LT: lambda q, a, v: q.filter(a < v),
            Op.NEQ: lambda q, a, v: q.filter(a != v),
            Op.BETWEEN: lambda q, a, v: q.filter(a.between(v[0], v[1])),
            Op.IN: lambda q, a, v: q.filter(a.in_(v)),
            Op.NOT_IN: lambda q, a, v: q.filter(not a.in_(v)),
            Op.LIKE: lambda q, a, v: q.filter(a.like(f'%{v}%')),
            Op.NOT_LIKE: lambda q, a, v: q.filter(not a.like(f'%{v}%')),
            Op.LIKE_IN: lambda q, a, v: q.filter(or_(*[a.like(f'%{vv}%') for vv in v])),
        }
        return d[self](query, field, value)

    def query_df(self, data_frame: DataFrame, column_name: str, value) -> DataFrame:
        if self == Op.LIKE_IN and isinstance(value, str):  # LIKE_IN 支持逗号分割的多个str自动转换
            value = value.split('|')
        d = {
            Op.EQU: lambda df, a, v: df.query(f"{a} == @v"),
            Op.GE: lambda df, a, v: df.query(f"{a} >= @v"),
            Op.GT: lambda df, a, v: df.query(f"{a} > @v"),
            Op.LE: lambda df, a, v: df.query(f"{a} <= @v"),
            Op.LT: lambda df, a, v: df.query(f"{a} < @v"),
            Op.NEQ: lambda df, a, v: df.query(f"{a} != @v"),
            Op.LIKE: lambda df, a, v: df.query(f'{a}.str.contains(@v, na=False)'),
            Op.IN: lambda df, a, v: df.query(f'{a} in @v'),
            Op.BETWEEN: lambda df, a, v: df.query(f"@v[0] <= {a} <= @v[1]"),
            Op.LIKE_IN: lambda df, a, v: df.query(
                '|'.join([f'{a}.str.contains(@v[{i}],na=False)' for i, vv in enumerate(v)])),
        }
        return d[self](data_frame, column_name, value)


class ColumnSpec:
    def __init__(self, **kwargs):
        copy_obj(self, kwargs)
        self.name = get_attr(self, 'name')
        self.title = get_attr(self, 'title', '')
        self.comment = get_attr(self, 'comment', '')
        if not self.title:
            self.title = max(self.title, self.comment)
        if not self.comment:
            self.comment = max(self.title, self.comment)
        self.dtype = get_attr(self, 'dtype')
        self.utype = get_attr(self, 'utype')
        self.link_to = get_attr(self, 'link_to')
        self.key = get_attr(self, 'key', self.name)

    def is_link(self):
        return self.link_to is not None

    def __repr__(self):
        s = ', '.join(["%s=%r" % (k, v) for k, v in self.__dict__.items()])
        return f'<ColumnSpec "{self.key}": {s}>'

    @staticmethod
    def from_obj(o):
        if isinstance(o, ColumnSpec):
            return o
        if isinstance(o, dict):
            return ColumnSpec(**o)
        else:
            return ColumnSpec(**o.__dict__)


def set_attr_to_specs(specs, col_name, attr, value):
    sp = None
    if type(specs) is dict:
        sp = specs[col_name]
    else:
        ss = [s for s in specs if s.name == col_name]
        if len(ss) == 1:
            sp = ss[0]
    if sp:
        set_attr(sp, attr, value)


class QueryR:
    def __init__(self, dataframe, columns_specs):
        self._dataframe = dataframe
        self._column_specs = columns_specs

    def dataframe(self) -> DataFrame:
        return self._dataframe

    def column_specs(self):
        return self._column_specs

    def encode(self):
        """
        将query查询得到的结果（_result:DataFrame）转换为json，包含以下内容:
        'spec': 对应Selection的column_spec
        'data': 序列化+base64编码后的查询结果对象
        :return:
        """
        encoded_obj = base64.b64encode(pickle.dumps(self._dataframe)).decode('utf-8')
        return {'spec': json_dump(self._column_specs),
                'data': encoded_obj,
                }

    @staticmethod
    def decode(json):
        spec = json_load(json['spec'], cls=ColumnSpec)
        decoded_obj = base64.b64decode(json['data'].encode('utf-8'))  # base64.b64encode返回的是字节数据，需要转为utf-8字符串。
        df = pickle.loads(decoded_obj)
        return QueryR(df, spec)
