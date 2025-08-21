# -*- __init__.py: python ; coding: utf-8 -*-
import base64
import datetime
import json
import os
from decimal import Decimal

import pandas as pd

b64_char = r"0123456789KLMNOPQRSTABCDEFGHIJefghijklmnopqrstuvwxUVWXYZabcdyz+/="
m64_char = r"fehimgjlnk1025734896LKNOSMPRTQBADEICFHJGVUXYcWZbdaporqvstwxuzy.$^"


def has_attr(obj, attr):
    if obj is None:
        return False
    if isinstance(obj, dict):
        return obj.get(attr) is not None
    else:
        return hasattr(obj, attr)


def get_attr(obj, attr, no_attr=None):
    """
    返回对象的给定属性
    :param obj: 对象/dict
    :param attr: 属性名/key
    :param no_attr: 如果属性不存在，返回本值
    :return:
    """
    if obj is None:
        return no_attr
    if isinstance(obj, dict):
        return obj.get(attr, no_attr)
    else:
        return getattr(obj, attr) if hasattr(obj, attr) else no_attr


def set_attr(obj, attr, value):
    if obj is None:
        return
    if isinstance(obj, dict):
        obj[attr] = value
    else:
        setattr(obj, attr, value)


def set_default_values(o, **kwargs):
    """
    使用给出的名值对设置对象的属性值。
    若kwargs中的key不在o的原属性中，直接在o中添加属性及属性值，若已存在key属性，仅在原有属性值为None时才使用新值。
    :param o:
    :param kwargs:
    :return:
    """
    for attr in kwargs:
        if not hasattr(o, attr):
            setattr(o, attr, kwargs[attr])
        else:
            if getattr(o, attr) is None:
                setattr(o, attr, kwargs[attr])
    return o


def copy_obj(o_tar, o_src, skip_keys=None):
    """
    复制对象属性值到另外的对象中
    :param o_tar: 目标对象
    :param o_src: 源对象
    :param skip_keys: 忽略的属性(list)
    :return:
    """
    if skip_keys is None:
        skip_keys = []
    keys = o_src.keys() if isinstance(o_src, dict) else o_src.__dict__.keys()
    for key in keys:
        if key not in skip_keys and not key.startswith('__'):
            v = get_attr(o_src, key)
            set_attr(o_tar, key, v)
    return o_tar


def format_date(d):
    if not d or pd.isna(d):
        return None
    return ('%s' % d)[:10]


def format_datetime(d, fmt='%Y-%m-%d %H:%M:%S.%f'):
    if not d or pd.isna(d):
        return ''
    import datetime
    if d is datetime.date:
        return datetime.datetime.strftime(d, fmt)
    else:
        return d


def format_id(n, fmt='%06d'):
    if n is None or pd.isna(n):
        return ''
    else:
        return fmt % n


def format_percent(n, fmt='%.2f%%'):
    if n is None or pd.isna(n):
        return ''
    else:
        return fmt % to_float(n)


def format_year_mth(d):
    ret = ''
    s = format_date(d)
    if s and len(s) == 10:
        ret = s[2:4] + s[5:7]
    return ret


def format_obj(obj, exp, use_repr=False):
    """
    对象属性表达式做格式化转换，支持使用repr。
    例如 obj.name='ABC', obj.id=1000
    format_obj(obj,'{id} - {name}') 返回 '1000 - ABC'
    :param obj: 对象
    :param exp: 表达式，如'{attr}'
    :param use_repr: 替换变量时是否用repr
    :return:
    """
    if obj is None:
        return exp
    dv = obj if isinstance(obj, dict) else obj.__dict__
    if use_repr:
        dv = {k: repr(v) for k, v in dv.items()}
    f_exp = f"f\"{exp}\""
    return eval(f_exp, dv)


def to_float(o, none_value=0.0) -> float:
    if o is None or pd.isna(o):
        return none_value
    text = str(o).replace(',', '').replace('%', '').replace(' ', '')
    return float(text) if text else none_value


def to_int(o, none_value=0) -> int:
    if o is None or pd.isna(o):
        return none_value
    text = str(o).replace(',', '').replace('%', '').replace(' ', '')
    return int(text) if text else none_value


def to_date(d_str):
    return to_datetime(d_str, '%Y-%m-%d')


def to_timestamp(dt_str, fmt='%Y-%m-%d %H:%M:%S.%f'):
    return to_datetime(dt_str, fmt)


def to_datetime(d_str, fmt='%Y-%m-%d %H:%M:%S'):
    import datetime
    if not d_str or pd.isna(d_str):
        return None
    if hasattr(d_str, 'strip'):
        ds = d_str.strip()
        if len(ds) >= 10:
            ds = ds[:10]
        return datetime.datetime.strptime(ds, fmt)
    else:
        return d_str


def safe_sum(*val):
    total = 0.0
    if len(val) == 1:
        lst = val[0]
    else:
        lst = val
    for v in lst:
        total += to_float(v)
    return total


def safe_add(a, b):
    return to_float(a, none_value=0) + to_float(b, none_value=0)


def safe_diff(a, b):
    return to_float(a, none_value=0) - to_float(b, none_value=0)


def safe_mul(a, b, none_value=0):
    if a and b:
        return a * b
    else:
        return none_value


def safe_div(a, b, zero_div=None, none_as=None):
    if a is None or b is None:
        return none_as
    try:
        if isinstance(a, Decimal):
            a = to_float(a)
        if isinstance(b, Decimal):
            b = to_float(b)
        return a / b
    except ZeroDivisionError:
        return zero_div


def safe_percent(a, b, delta=False):
    if b is None:
        return None
    if abs(b) < 0.001:
        return None
    a = to_float(a)
    b = to_float(b)
    if delta:
        return (a / b - 1) * 100
    else:
        return a / b * 100


def is_execute_able(f):
    """
    判断一个名称是否为可执行类型即：FunctionType,MethodType,LambdaType
    :param f:
    :return:
    """
    import types
    return isinstance(f, types.FunctionType) or isinstance(f, types.MethodType) or isinstance(f, types.LambdaType)


def is_collection(o):
    """
    判断对象是否为集合类型，包括list,tuple,set和dict
    :param o:
    :return:
    """
    return isinstance(o, (list, tuple, set, dict))


def create_instance(mod_name, cls_name, *args, **kwargs):
    """
    :param mod_name: 模块名称
    :param cls_name: 类名称或函数名称
    :param args: 实例化或函数调用的参数表
    :param kwargs: 实例化或函数调用的参数表
    :return:
    """
    mod = __import__(mod_name, globals(), locals(), [cls_name])
    proc = getattr(mod, cls_name)
    if is_execute_able(proc):  # 是函数
        return proc(*args, **kwargs)
    else:  # 实例化类
        return proc(*args, **kwargs)


def call_func(mod_name, func_name, *args, **kwargs):
    """
    根据模块名称和函数/类名称调用函数或创建对象。
    :param mod_name: 模块名称，如 'yut.gui'
    :param func_name: 函数或类名称，如 'create_button' 或 'HoveredButton'
    :param args:
    :param kwargs:
    :return:
    """
    mod = __import__(mod_name, globals(), locals(), [func_name])
    fn = getattr(mod, func_name)
    return fn(*args, **kwargs)


def call_exp(exp: str):
    """
    动态加载包并执行表达式,如:
        a = call_exp('yut.format_date("2024-01-01")')
        o = call_exp('yut.Record(id=100,value=2.0)'

    :param exp: 带完整模块名称的函数及参数
    :return: 函数执行结果
    """
    import re

    def split_args(text: str):
        pattern = r" *(?P<name>.*?)\((?P<args>.*)\)$"
        m = re.search(pattern, text)
        if m:
            return m.group('name'), m.group('args')
        else:
            return None, None

    def split_mod_fn(text: str):
        pattern = r'(?P<mod>.*(?<!\.)\.)?(?P<fn>[^.]+)$'
        m = re.search(pattern, text)
        if m:
            m_mod, m_fn = m.group('mod'), m.group('fn')
            if m_mod:
                m_mod = m_mod[:-1]  # 去掉'.'
            return m_mod, m_fn
        else:
            return None, None

    name, args = split_args(exp)
    if name:
        mod_name, fn_name = split_mod_fn(name)
        if mod_name:
            mod = __import__(mod_name, globals(), locals(), [fn_name])
            _fn_tmp_ = getattr(mod, fn_name)
            return eval(f"_fn_tmp_({args})")
        elif fn_name:  # 不需要import,直接使用default package
            return eval(f"{fn_name}({args})")
    return None


def same_year(d1, d2):
    if not d1 or not d2:
        return ''
    if str(d1)[:4] == str(d2)[:4]:
        return '是'
    return ''


def birth_age(birth, today=None):
    import datetime
    if birth is None:
        return 0
    birth_day = birth
    if isinstance(birth, str):
        birth_day = to_date(birth)
    today_d = today if today else datetime.date.today()
    birth_d = datetime.date(birth_day.year, today_d.month, today_d.day)
    if birth_day <= birth_d:
        age = today_d.year - birth_day.year
    else:
        age = today_d.year - birth_day.year - 1
    return age


def year_date_pair(date):
    """
    返回给定日期对应的年初和年末日期。如： year_date_pair('2024-11-20') -> (2024-01-01,2024-12-31)
    :param date: 日期，可以是str或datetime.date
    :return: (datetime.date,datetime.date)
    """
    y = to_date(date).year
    return to_date('%4d-01-01' % y), to_date('%4d-12-31' % y)


def month_date_pair(y, m):
    """
    返回给定年,月对应的月初和月末日期。如： month_date_pair(2024,11) -> (2024-11-01,2024-11-30)
    :param y: 年份
    :param m: 月度
    :return: (datetime.date,datetime.date)
    """
    import datetime
    start_date = to_date('%4d-%02d-01' % (y, m))
    if m >= 12:
        end_date = to_date('%4d-%02d-01' % (y + 1, 1))
    else:
        end_date = to_date('%4d-%02d-01' % (y, m + 1))
    end_date = end_date - datetime.timedelta(days=1)
    return start_date, end_date


def inc_date(d_str, days=1):
    d = to_date(d_str)
    dt = d + datetime.timedelta(days=days)
    return format_date(dt)


class Obj:
    def __init__(self, **kwargs):
        for k in kwargs:
            v = kwargs[k]
            setattr(self, k, v)

    def __attr_values(self, use_repr=False, skip_prefix='__'):
        ret = ''
        for attr in self.__dict__:
            if not attr.startswith(skip_prefix):
                if use_repr:
                    ret += ' %s=%s;' % (attr, getattr(self, attr).__repr__())
                else:
                    ret += ' %s=%s;' % (attr, getattr(self, attr))
        return ret

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.__attr_values(use_repr=False))

    def from_obj(self, o):
        if hasattr(o, '__dict__'):
            for attr in o.__dict__:
                if not attr.startswith('__'):
                    setattr(self, attr, getattr(o, attr))
        elif isinstance(o, dict):  # 从字典复制对象
            for k in o.keys():
                v = o.get(k)
                if v is not None:
                    setattr(self, k, v)
                else:
                    setattr(self, k, None)
        return self


def d2o(d, cls=Obj):
    o = cls()
    for k in d.keys():
        v = d.get(k)
        if v is not None:
            setattr(o, k, v)
        else:
            setattr(o, k, None)
    return o


def o2d(o, keys=None):
    """
    将对象属性值转换为字典
    :param o: 待转换的对象
    :param keys: 需要包含的属性，默认为None，表示所有属性
    :return:
    """
    d = {}
    if keys is None:
        keys = o.__dict__.keys()
    for k in keys:
        if k.startswith('*'):  # 使用属性值的str，不是对象
            attr = k[1:]
            d[attr] = str(getattr(o, attr))
        else:
            d[k] = getattr(o, k)
    return d


def r2d(r):
    if hasattr(r, '_asdict'):
        return CaseInsensitiveDict(r._asdict())
    else:
        return CaseInsensitiveDict(r.__dict__)


def json_dump(obj, indent=2, skip_prefix='__', ensure_ascii=False):
    """
    对象或对象集合转换为json串
    :param obj:
    :param indent:
    :param skip_prefix:
    :param ensure_ascii:
    :return:
    """
    from json import JSONEncoder

    class Encoder(JSONEncoder):
        def default(self, o):
            if type(o) in [tuple, set]:
                return list(o)
            if hasattr(o, '__dict__'):
                d = {}
                for key in o.__dict__:
                    if not key.startswith(skip_prefix):
                        value = getattr(o, key)
                        d[key] = value
                return d
            else:
                return str(o)

    return json.dumps(obj, cls=Encoder, indent=indent, ensure_ascii=ensure_ascii)


def json_load(s, cls=Obj):
    """
    从json串中解析对象（或对象集合）
    :param s:
    :param cls:
    :return:
    """
    o = json.loads(s, strict=False)
    o_type = type(o)
    if o_type in (list, tuple, set):
        return [d2o(oo, cls) for oo in o]
    elif o_type == dict:
        return {oo.key: d2o(oo, cls) for oo in o}
    else:
        return d2o(o)


# 大小写无关的字典
class CaseInsensitiveDict(dict):
    """
    大小写无关的字典
    """

    def __getitem__(self, key):
        for k in self.keys():
            if k.lower() == key.lower():
                return dict.__getitem__(self, k)
        raise KeyError(key)

    def __getattr__(self, key):
        for k in self.keys():
            if k.lower() == key.lower():
                return dict.__getitem__(self, k)
        return dict.__getattribute__(self, key)


def change_file_ext(file_name, tar_ext):
    if tar_ext[0] == '.':
        tar_ext = tar_ext[1:]
    fn, ext = os.path.splitext(file_name)
    if ext == tar_ext:
        return f'{fn}_{ext}.{tar_ext}'
    else:
        return f'{fn}.{tar_ext}'


def m64_enc(s: str) -> str:
    bt = base64.b64encode(s.encode('utf-8')).decode('utf-8')
    ret = ''.join([m64_char[b64_char.index(ch)] for ch in bt])
    return base64.b64encode(ret.encode('utf-8')).decode('utf-8')


def m64_dec(s: str, esc='?') -> str:
    if not s:
        return ''
    if s.startswith(esc):  # 明文存储
        return s[len(esc):]
    mt = base64.b64decode(s).decode('utf-8')
    ret = ''.join([b64_char[m64_char.index(ch)] for ch in mt])
    return base64.b64decode(ret).decode('utf-8')


def sec_hms(seconds: int) -> str:
    """
    将秒按照时分秒显示
    :param seconds: 秒
    :return: f'{h:3d}h{m:02d}m{s:02d}s'
    """
    if seconds < 60:
        return f'{seconds:3d}s'
    elif seconds < 3600:
        m = int(seconds / 60)
        s = int(seconds % 60)
        return f'{m:3d}m{s:d}s'
    else:
        h = int(seconds / 3600)
        m = int((seconds % 3600) / 60)
        s = int(seconds % 60)
        return f'{h:3d}h{m:02d}m{s:02d}s'
