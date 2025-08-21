# -*- dbm: python ; coding: utf-8 -*-
import re
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Callable

import jinja2
import pandas as pd
from sqlalchemy import create_engine, MetaData, inspect, Integer, BigInteger, SmallInteger, Float, Numeric
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql.elements import quoted_name
from sqlalchemy.types import TypeDecorator

from yut import CaseInsensitiveDict, Obj, is_collection, o2d, is_execute_able, get_attr, set_attr, call_exp
from . import Op, QueryR


def extract_qc(params: dict | object | Obj, name: str) -> None | Obj:
    """
    从字典或对象中提取指定的查询条件值
    :param params: 包含多个查询条件的字典或对象，字典的格式为 name: (op,value)
    :param name: 条件名称
    :return: 如果没有对应名称的条件，返回None，否则返回Obj对象，包含attr,op,value三个属性.
    """
    v = get_attr(params, name)
    if v:
        if is_collection(v):
            op, value = v  # Op , value
        else:
            op, value = Op.EQU, v
        return Obj(attr=name, op=Op(op), value=value)
    return None


def qc_value(params: dict | object | Obj, name: str, none_as=None, take=False) -> None | Obj:
    value = get_attr(extract_qc(params, name), 'value')
    if take:
        set_attr(params, name, value)
    return value if value is not None else none_as


INTEGER_TYPES = (Integer, BigInteger, SmallInteger)


class PandasTypeMapper:
    """
    SQLAlchemy 类型到 pandas 类型的映射器
    """

    BASE_MAPPING = {
        Integer: pd.Int64Dtype(),
        BigInteger: pd.Int64Dtype(),
        SmallInteger: pd.Int64Dtype(),
        Float: float,
        Numeric: float,  # 或 'object' 保留 Decimal
    }

    # 特殊类型处理
    @staticmethod
    def map_type(sqlalchemy_type):
        """
        映射 SQLAlchemy 类型到 pandas 类型
        """
        """映射 SQLAlchemy 类型到 pandas 类型（安全处理字符串）"""
        # 检查直接匹配
        for base_type, pandas_type in PandasTypeMapper.BASE_MAPPING.items():
            if isinstance(sqlalchemy_type, base_type):
                return pandas_type

        # 处理 TypeDecorator
        if isinstance(sqlalchemy_type, TypeDecorator):
            return PandasTypeMapper.map_type(sqlalchemy_type.impl)

        # 处理具有 python_type 的类型
        if hasattr(sqlalchemy_type, 'python_type'):
            py_type = sqlalchemy_type.python_type
            if py_type == int:
                return pd.Int64Dtype()
            elif py_type == float:
                return float
            elif py_type == bool:
                return pd.BooleanDtype()
            elif py_type == str:
                return 'safe_string'  # 特殊标记
            elif py_type == datetime:
                return 'datetime64[ns]'
            elif py_type == date:
                return 'datetime64[ns]'
            elif py_type == time:
                return 'timedelta64[ns]'
            elif py_type == timedelta:
                return 'timedelta64[ns]'
            elif py_type == Decimal:
                return float

        return 'object'

    @staticmethod
    def get_column_types(query):
        """
        从 SQLAlchemy 查询中获取列类型映射
        """
        col_types = {}
        try:
            # 现代 SQLAlchemy (1.4+) 方式
            if hasattr(query, 'selected_columns'):
                for col in query.selected_columns:
                    col_types[col.key] = PandasTypeMapper.map_type(col.type)
            # 旧版本 SQLAlchemy 方式
            else:
                for col_desc in query.column_descriptions:
                    col_name = col_desc['name']
                    col_type = col_desc['type']
                    col_types[col_name] = PandasTypeMapper.map_type(col_type)
        except Exception as e:
            print(f"Warning: Failed to get column types - {str(e)}")
        return col_types

    @staticmethod
    def safe_string_conversion(series):
        """
        安全转换字符串类型，处理空值
        """
        # 处理空值
        if series.isnull().any():
            # 创建新的 StringArray 处理缺失值
            return pd.array(series.astype(str).replace('nan', pd.NA), dtype=pd.StringDtype())

        # 无空值时直接转换
        return series.astype(str)

    @staticmethod
    def convert_to_pandas_type(series, target_type):
        """
        安全转换 pandas 系列到目标类型
        """
        if target_type == 'safe_string':
            return PandasTypeMapper.safe_string_conversion(series)

        # 特殊处理日期时间类型
        if target_type == 'datetime64[ns]':
            return pd.to_datetime(series, errors='coerce')

        # 特殊处理时间差类型
        if target_type == 'timedelta64[ns]':
            if series.dtype == object:
                # 转换 time 对象为 timedelta
                return series.apply(
                    lambda x: pd.Timedelta(
                        hours=x.hour,
                        minutes=x.minute,
                        seconds=x.second
                    ) if isinstance(x, time) else pd.NaT
                )
            return series.astype('timedelta64[ns]', errors='ignore')

        # 标准转换
        try:
            return series.astype(target_type)
        except (TypeError, ValueError):
            return series.astype('object')

    @staticmethod
    def dataframe_as_types(df, col_types):
        # 应用精确类型转换
        for col_name in df.columns:
            if col_name in col_types:
                target_type = col_types[col_name]
                df[col_name] = PandasTypeMapper.convert_to_pandas_type(df[col_name], target_type)
        return df


def field_types(query):
    """
    从 SQLAlchemy 查询中获取列类型映射
    """
    try:
        # 现代 SQLAlchemy (1.4+) 方式
        if hasattr(query, 'selected_columns'):
            return {col.key: col.type for col in query.selected_columns}
        # 旧版本 SQLAlchemy 方式
        else:
            return {col_desc['name']: col_desc['type'] for col_desc in query.column_descriptions}
    except Exception as e:
        print(f"Warning: Failed to get column types - {str(e)}")
        return {}


class Selection:
    def __init__(self,
                 db,
                 title=None,
                 comment=None,
                 tables=None,
                 columns=None,
                 joins=None,
                 group_bys=None,
                 order_bys=None,
                 make_q=None,
                 convert_rec=None,
                 post_process=None,
                 ext_comments: dict = None,
                 unit_spec: dict = None,
                 ):
        self.db = db
        self.title = title
        self.comment = comment
        self.session = None
        self.tables = tables
        self.columns = columns
        self.joins = joins
        self.group_bys = group_bys
        self.order_bys = order_bys
        self.make_q = make_q
        self.convert_record = convert_rec
        self.post_process = post_process
        self.ext_comments = ext_comments if ext_comments else {}  # 附加的备注，如用在sum、count等聚合函数生成的字段
        self.unit_spec = unit_spec
        self._cls_dict = {}
        self.query_args = []
        self.query_kwargs = {}
        self._conditions = CaseInsensitiveDict()  # 专门使用的查询条件，形如 "key": (Op,value)
        self._result = None
        self.setup()

    def setup(self):
        # 创建model_class字典
        self._cls_dict = {chr(ord('a') + i): self.db.model_class(name) for i, name in enumerate(self.tables)}

    def set_make_q(self, make_q):
        self.make_q = make_q

    def set_convert_rec(self, rc):
        self.convert_record = rc

    def set_post_process(self, pp):
        self.post_process = pp

    def _column_list(self):
        return [self.f(col) for col in self.columns]

    def add_ext_comments(self, **kwargs):
        self.ext_comments.update(**kwargs)

    def add_unit_spec(self, col, **kwargs):
        self.unit_specs[col] = kwargs

    def column_spec(self) -> list:
        def col_comment(col):
            if self.ext_comments.get(col.key):  # 优先使用ext_comments,以便局部修改默认值
                return self.ext_comments[col.key]
            attr = 'comment'
            if hasattr(col, attr):
                return getattr(col, attr)
            return None

        ret = [{'key': c.key,
                'name': c.name,
                'title': col_comment(c),# 反射出的字段描述通常放在comment中，赋值给title属性
                'comment': col_comment(c),
                'dtype': f"{c.type}" if c.type is not None else None,
                'table': f"{c.table}" if c.table is not None else None,
                } for c in self._column_list()]

        # 允许ext_comment中补充不在columns中的列附注，如后处理时对dataframe增加列，因此需要添加ext_comment中没有包含在ret中的元素
        for ec_key, ec_value in self.ext_comments.items():
            if ec_key not in [r['key'] for r in ret]:
                ret.append({'key': ec_key, 'name': ec_key, 'comment': ec_value, 'dtype': None, 'table': None})

        # 补充设置 unit spec
        for c in ret:
            if self.unit_spec:
                u_spec = self.unit_spec.get(c['key'])
                if u_spec:
                    c.update(u_spec)  # 将u_spec中的key-value平铺到 col_spec 中

        return ret

    def t_keys(self):
        return self._cls_dict.keys()

    def cls_attr(self, t_key, attr):
        for cls in [self.t(t_key)] if t_key else self._cls_dict.values():  # 给了表标识,明确使用，否则取第一个匹配的列名
            # 忽略大小写，逐个判断
            for key in cls.__dict__:
                if key.lower() == attr.lower().strip():
                    return getattr(cls, key)
        print(f'MetaDb.cls_attr(): attribute access failed , no such attr: {t_key} - {attr}')
        return None

    def t(self, key):
        r = self._cls_dict.get(key)
        if r:
            return r
        elif isinstance(key, int):  # 也允许使用下标索引
            return list(self._cls_dict.values())[key]
        elif key in self.tables:  # 直接使用表名也可以
            index = self.tables.index(key)
            return list(self._cls_dict.values())[index]
        return None

    def f(self, element):
        # 传入的是可调用对象，执行调用，返回结果
        if callable(element):  # 允许使用lambda动态返回属性对象(如使用func.sum().label()等)，也允许使用字符列名
            return element(self)
        if type(element) is quoted_name:
            element = str(element)
        if type(element) is not str:  # 传入的不是字符串，直接返回
            return element
        tokens = element.split('.')
        if len(tokens) == 1:  # 没有表前缀
            return self.cls_attr(t_key=None, attr=tokens[0].strip())
        else:
            return self.cls_attr(tokens[0].strip(), tokens[1].strip())

    def result(self):
        return self._result

    def __getattr__(self, item):
        cls = self._cls_dict.get(item)
        return cls if cls else object.__getattribute__(self, item)

    def push_conditions(self, o, clear=True):
        if clear:
            self._conditions.clear()
        if o is None:
            return
        if isinstance(o, dict):
            self._conditions.update(o)
        else:
            self._conditions.update(o.__dict__)

    def get_conditions(self) -> list[Obj]:
        ret = [self.get_condition(key) for key in self._conditions]
        return [o for o in ret if o is not None]

    def get_condition(self, attr: str):
        return extract_qc(self._conditions, attr)

    def add_join(self, q, *f_exps, outer=False):
        """
        添加表间连接
        :param q:
        :param f_exps:
        :param outer: 是否为 outer join，默认为 False，创建 inner join 。
        :return:
        """
        lgs = f_exps if len(f_exps) > 1 else [  # 只给出了一个参数，默认关联前两张表，字段名相同
            list(self.t_keys())[0] + f".{f_exps[0]}",
            list(self.t_keys())[1] + f".{f_exps[0]}"]
        lg = [self.f(ex) for ex in lgs]
        args = [f"(lg[{i * 2}] == lg[{i * 2 + 1}])" for i in range(int(len(lgs) / 2))]
        fn = q.outerjoin if outer else q.join
        return fn(lg[1].table, eval('&'.join(args)))

    def add_filter(self, query, column, value=None, op: Op = Op.EQU):
        if column is None:
            return query
        field = self.f(column)
        if not field:
            print(f'[Selection.add_filter]: 没有找到{column}对应的属性,也不是有效的表达式，忽略filter条件。')
            return query
        if value is None:
            return query
        operator = op if isinstance(op, Op) else Op(op)
        return operator.filter_q(query, field, value)

    def _create_query(self) -> Query:
        if self.session is None:
            self.session = self.db.Session()
        q = self.session.query()
        if self.columns:
            for col in self.columns:
                q = q.add_column(self.f(col))
        else:
            for key_table in self.tables:
                q = q.add_entity(self.t(key_table))
        if self.joins:
            for join in self.joins:
                if type(join[-1]) == bool:  # 最后一个参数：是否外连接
                    outer = join[-1]
                    j_args = join[:-1]
                else:
                    outer = False
                    j_args = join
                q = self.add_join(q, *j_args, outer=outer)
        if self.group_bys:
            for gb in self.group_bys:
                q = q.group_by(self.f(gb))
        if self.order_bys:
            for ob in self.order_bys:
                q = q.order_by(self.f(ob))

        return q

    def _add_kw_filters(self, q, kwargs):
        if not kwargs:
            return q
        for k, v in kwargs.items():
            if v is None:
                continue
            if is_collection(v):
                op, value = v  # Op , value
            else:
                op, value = Op.EQU, v
            q = self.add_filter(q, k, value, op)
        return q

    def query(self, make_q=None, convert_rec=None, post_process=None, distinct=False,*args, **kwargs) -> QueryR:
        """
        执行查询。调用者可传入3个回调函数，分别用于组装query、转换结果集的记录、对完整结果集的后处理.
        查询结果以DataFrame类型保存到_result属性中，可以使用result()方法获取。
        :param make_q: 用于组装query的回调函数，对应的签名为 (q:Query,qs:Selection,*args,**kwargs)->Query。其中：
            q - 待组装的query对象，应采用链式处理返回;
            ss - Selection对象自身，可用于处理反射类、反射属性等；
            args,kwargs - 外部调用者传递给q_maker函数的动态参数，通常用于查询条件
        :param convert_rec: 行记录转换回调函数，对应的签名为 (qs:Selection,r,index:int)->Any。其中：
            r - 行记录对象,query.all()返回的行元素
            index - 记录在结果集中的序号
        :param post_process: 后处理回调函数，对应的签名为 (qs:Selection,result:DataFrame)->Any。
            返回结果将被保存在result属性中，可以用result()方法多次获取。
        :param distinct: 执行查询时是否增加distinct()
        :param args:
        :param kwargs:
        :return:
        """

        def to_record(rec, index):
            if self.convert_record:  # 回调
                return self.convert_record(self, rec, index)
            else:
                return rec

        # 准备钩子函数
        if make_q:
            self.set_make_q(make_q)
        if convert_rec:
            self.set_convert_rec(convert_rec)
        if post_process:
            self.set_post_process(post_process)

        # 将参数放入上下文中
        if args:
            self.query_args.clear()
            self.query_args.extend(args)
        if kwargs:
            self.query_kwargs.clear()
            self.query_kwargs.update(kwargs)
        try:
            # 创建query对象
            q = self._create_query()
            # 回调 maker 得到完整的query
            if self.make_q:
                q = self.make_q(q, self, *args, **kwargs)
            else:
                q = self._add_kw_filters(q, kwargs)
            set_attr(self, 'sql', f"{q}")

            col_types = field_types(q)
            if distinct:
                q = q.distinct()
            # 获取查询结果并转换
            records = [to_record(result, index) for index, result in enumerate(q.all())]
        finally:
            self.session.close()

        dtypes = {col: 'Int64' for col in col_types if isinstance(col_types[col], INTEGER_TYPES)}
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.astype(dtypes)

        # 后处理
        if self.post_process and records:  # 仅在有返回结果时调用
            df = self.post_process(self, df)
            if df is None:
                raise NotImplementedError('指定了后处理方法，但没有返回结果集', self.post_process)

        self._result = QueryR(df, self.column_spec())
        return self._result

    def dataset(self):
        return self._result


class MetaDb:
    DEFAULT_MODEL_TPL = 'db_models.ptl'
    DEFAULT_DATABASE_URI = 'sqlite:///:memory:'

    def __init__(self, database_url=None, echo=False):
        if database_url:
            self.database_url = database_url
        else:
            self.database_url = MetaDb.DEFAULT_DATABASE_URI
        self.engine = create_engine(self.database_url, echo=echo)
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine, views=True)
        self.Base = automap_base(metadata=self.meta)
        self.Base.prepare()
        self._table_unique_cols = {}
        self._table_name_map = {t.name.upper(): t.name for t in self.meta.sorted_tables}  # 为了忽略大小写，建立大写表名与原始表名之间的映射
        self.map_tables()
        self.Session = sessionmaker(bind=self.engine)

    def map_tables(self):
        cls_names = set(self.Base.classes.keys())
        tab_names = set([t.name for t in self.meta.sorted_tables])
        diff_names = tab_names - cls_names
        if diff_names:
            print('WARNING:', f'表{diff_names}未能自动映射为model类，请仔细检查这些表是否定义了主键。')
        for table_name in self.Base.classes.keys():
            # 将 Automap 反射出的类其数据库实例默认为不可改变，将其转换为可更改实例值的ORM类
            self.Base.classes[table_name].__table__.info['autoload'] = True
        # 获得每个table的主键/唯一键/唯一索引
        for t in self.Base.metadata.sorted_tables:
            unique_cols = []
            if t.primary_key.columns:
                unique_cols.append([col.name for col in t.primary_key.columns])  # 主键
            for index in t.indexes:  # 唯一索引
                if index.unique:
                    unique_cols.append([col.name for col in index.columns])
            for constraint in t.constraints:  # 唯一约束
                if hasattr(constraint, 'columns') and constraint.__class__.__name__ == 'UniqueConstraint':
                    unique_cols.append([col.name for col in constraint.columns])
            self._table_unique_cols[t.name] = unique_cols

    def foreign_keys(self, tab_name):
        inspector = inspect(self.engine)
        return inspector.get_foreign_keys(self.m_table_name(tab_name))

    def m_table_name(self, tab_name: str):
        return self._table_name_map[tab_name.upper()]

    def m_class_name(self, tab_name: str):
        table_name = self.m_table_name(tab_name).capitalize()
        return f'_{table_name}'

    def tables(self):
        return self.meta.sorted_tables

    def table(self, table_name):
        # return self.meta.tables[self.m_table_name(table_name)]
        return CaseInsensitiveDict(self.meta.tables)[table_name]

    def table_unique_columns(self, table_name):
        # return self._table_unique_cols[self.m_table_name(table_name)]
        return CaseInsensitiveDict(self._table_unique_cols)[table_name]

    def model_class(self, table_name):
        # return self.Base.classes[self.m_table_name(table_name)]
        return CaseInsensitiveDict(self.Base.classes)[table_name]

    def _save_records(self, table_name, records, on_exists, on_without, pkey_columns=None):
        def single_record(r):
            record_in_db = None
            # 逐条规则检查
            for uq_cols in unique_rules:
                do_query = False
                q = session.query(cls)
                for key_col in uq_cols:  # 逐个字段拼筛选条件
                    if r.get(key_col):
                        fld = getattr(cls, key_col)
                        q = q.filter(fld == r[key_col])
                        do_query = True
                if do_query:
                    record_in_db = q.first()
                    if record_in_db:
                        break
            if record_in_db and on_exists:
                on_exists(session, r, record_in_db)
            elif on_without:
                on_without(session, r, record_in_db)

        session = self.Session()
        # 检查r在数据库中对应的的记录是否存在，如果存在则执行on_exists，否则执行on_without
        # 通过数据库表的唯一约束规则对应的字段（集合）作为查询条件判断是否存在
        unique_rules = self.table_unique_columns(table_name) if not pkey_columns else [pkey_columns]
        cls = self.model_class(table_name)

        # 逐条记录处理，批量提交
        for rec in records if isinstance(records, list) else [records]:
            single_record(rec)

        session.commit()
        session.close()

    def insert_or_update(self, table_name, records, pkey_columns=None):
        def copy_r(o, r):
            for key, value in r.items():
                setattr(o, key, value)
            return o

        def exec_exists(session, r, record_in_db):
            print(f'记录已经存在,UPDATE : {r}')
            copy_r(record_in_db, r)

        def exec_without(session, r, record_in_db):
            print(f'插入新记录: {r}')
            new_record = copy_r(self.model_class(table_name)(), r)
            session.add(new_record)

        self._save_records(table_name, records, exec_exists, exec_without, pkey_columns)

    def delete(self, table_name, records, pkey_columns=None):
        def exec_exists(session, r, record_in_db):
            print(f'找到并删除: {r}')
            session.delete(record_in_db)

        self._save_records(table_name, records, exec_exists, on_without=None, pkey_columns=pkey_columns)

    def generate_code(self, tpl_file=DEFAULT_MODEL_TPL, py_filename=None, save_to_file=False, name_pattern=None,
                      **kwargs):
        tables = []
        for name in self.Base.classes.keys():
            if not name_pattern:
                tables.append(self.table(name))
            elif re.match(name_pattern, name):
                tables.append(self.table(name))

        if not py_filename:
            py_filename = 'metadb_autogen.py'

        # 渲染模板
        context = {'meta': self,
                   'tables': tables,
                   'tpl_file': tpl_file,
                   'py_filename': py_filename,
                   'create_time': datetime.now(),
                   }
        context.update(kwargs)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("../../templates"))
        rendered_code = env.get_template(tpl_file).render(**context)
        # 保存到文件
        if save_to_file:
            with open(py_filename, 'w', encoding='utf-8') as file:
                file.write(rendered_code)
        return rendered_code

    def tables_summary(self):
        ret = []
        for table in self.tables():
            o_table = o2d(table, ['key', 'name', 'comment', 'description', ])
            o_table['columns'] = [
                o2d(c, ['key',
                        'name',
                        'comment',
                        'description',
                        '*type',
                        'primary_key',
                        'nullable',
                        '*autoincrement',
                        'unique',
                        ]) for c in table.columns]
            o_table['uniques'] = self.table_unique_columns(table.name)
            o_table['foreign_keys'] = self.foreign_keys(table.name)
            ret.append(o_table)
        return ret


class QueryManager:
    DEFAULT_NAME_SPACE = 'default'
    _instance = {}

    def __init__(self, name_space=DEFAULT_NAME_SPACE):
        self._name_space = name_space
        self._ds_dict = {}
        self._qmaker = {}

    def get_selection(self, ds_key) -> Selection:
        selection = self._ds_dict.get(ds_key)
        if isinstance(selection, str):
            selection = call_exp(selection)
            self._ds_dict[ds_key] = selection
        return selection

    def register_selection(self, ds_key: str, selection: str | Selection):
        # if isinstance(selection, str):
        #     selection = yut.call_exp(selection)
        self._ds_dict[ds_key] = selection

    def register_qmaker(self, ds_key: str, maker: Callable):
        self._qmaker[ds_key] = maker

    def get_qmaker(self, ds_key):
        return self._qmaker.get(ds_key)

    def name_space(self):
        return self._name_space

    def query_selection(self, ds_key=None, selection=None, condition: dict = None, convert_rec=None, post_process=None):

        def default_qmaker(q, qs: Selection, **kwargs):
            for c in qs.get_conditions():
                if c is not None:
                    q = qs.add_filter(q, qs.f(c.attr), c.value, c.op)
            ext_maker = self.get_qmaker(ds_key) if ds_key else None
            if ext_maker and is_execute_able(ext_maker):  # ds_key存在查询扩展编排器
                q = ext_maker(q, qs, qc=condition, **kwargs)
            return q

        if selection is None:
            selection = self.get_selection(ds_key)
        if selection is None:
            raise KeyError(f'无法获取Selection: ds_key={ds_key}')
        selection.push_conditions(condition, clear=True)
        qr: QueryR = selection.query(make_q=default_qmaker,
                                     convert_rec=convert_rec,
                                     post_process=post_process,
                                     ds_key=ds_key)
        return qr

    def selection_count(self):
        return len(self._ds_dict)

    @staticmethod
    def instance(name_space=DEFAULT_NAME_SPACE):
        fac = QueryManager._instance.get(name_space)
        if fac is None:
            fac = QueryManager(name_space)
            QueryManager._instance[name_space] = fac
        return fac
