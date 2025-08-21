# -*- logics.py: python ; coding: utf-8 -*-
import os
from decimal import Decimal

import pandas as pd
from pandas import DataFrame
from sqlalchemy import literal
from sqlalchemy.sql.functions import func

from yus import UnitType, ChooseMode, DisplayAttitude
from yui.ydict import DictLoader, DictFetcher
from yus import Op, QueryR, ColumnSpec
from yus.dbm import extract_qc, Selection, MetaDb
from yus_demo_models import get_qm, create_selections, get_db, NAME_SPACE
from yut import m64_dec, safe_div, Obj, get_attr


def show_progress(text, *args):
    print('*')
    print('*' * 100)
    print(f'* {text}\t', *args)
    print('*' * 100)
    print('*')


class NDW_DictLoader(DictLoader):

    def __init__(self):
        super().__init__(NAME_SPACE)

    def load_enum_dict(self, enum_key) -> dict:
        if enum_key == '$enum':  # 返回枚举类型列表
            df = get_qm().get_selection('DW_ENUM').query().dataframe()
            return {r.ENUM_KEY: r.ENUM_NAME for r in df.itertuples()}
        else:
            df = get_qm().get_selection('DW_DICT').query(ENUM_KEY=enum_key, DISABLE_FLAG=0).dataframe()
            return {r.CODE: r.DISP_TEXT for r in df.itertuples()}

    def load_dim_dict(self, dim_key) -> dict:
        if dim_key == '$dim':  # 返回统计类型列表
            df = get_qm().get_selection('DW_DIM').query().dataframe()
            return {r.DM_KEY: r.DIMENSION for r in df.itertuples()}
        else:
            df = get_qm().get_selection('DW_DIM_CODE').query(DM_KEY=dim_key, DISABLE_FLAG=0).dataframe()
            return {r.DIM_CODE: r.DISP_TEXT for r in df.itertuples()}


_default_dict_loader = NDW_DictLoader()


def init_env():
    show_progress('[yus_demo.init_env]', '初始化运行环境')
    env_key = 'YUS_DATABASE_URL'
    MetaDb.DEFAULT_DATABASE_URI = m64_dec(os.environ.get(env_key))
    print(f' -- 从系统变量 {env_key} 获取数据库连接URI:', MetaDb.DEFAULT_DATABASE_URI)
    for k, v in create_selections().items():
        get_qm().register_selection(k, v)
    print(f'注册默认的Selection,共 {get_qm().selection_count()} 个.')
    DictFetcher.instance().set_loader(_default_dict_loader)


def load_orgs(schema) -> list[Obj]:
    df_org = get_qm().get_selection('DW_ORG').query(ORG_SCHEMA=schema).dataframe()
    return [Obj(ORG_NO=r.ORG_NO,
                ORG_NAME=r.ORG_NAME,
                ORG_SHORT=r.ORG_SHORT,
                ORG_PATH=r.ORG_PATH,
                ORG_SCHEMA=r.ORG_SCHEMA,
                UNIT_CODE=r.UNIT_CODE,
                LEVEL=r.LEVEL,
                TREE_CODE=r.TREE_CODE,
                IS_LEAF=r.IS_LEAF,
                UNIT_RANK=r.UNIT_RANK,
                UNIT_ROLE=r.UNIT_ROLE,
                ) for r in df_org.itertuples()]


def simple_query():
    show_progress('[yus_demo.simple_query]', '单表查询，简单条件')
    yr, mth, schema = 2025, 5, 1
    print(f'{yr}年{mth}月组织机构人数统计(按业务体系):')
    df_org = get_qm().get_selection('DW_ORG').query(ORG_SCHEMA=schema).dataframe()
    org_psn = get_qm().get_selection('DW_ORG_PSN')
    for r in df_org.itertuples():
        df_psn = org_psn.query(ORG_NO=r.ORG_NO, YR=2025, MTH=5)
        print(f'{r.ORG_NO}-{r.ORG_SHORT:30}{r.ORG_PATH:<20}:\t {df_psn.dataframe().shape[0]}')


def group_month(df, col_date, col_amount, col_groups: list, fn_mth_col=lambda m: f"M{m:02d}"):
    """
    将按照日期纵向排列的数据表转为按照月份横向排列的数据表.
    :param df: 源表
    :param col_date: 日期列名称
    :param col_amount: 金额/数值列名称
    :param col_groups: 分组列集合（日期之外的其它分组列名）
    :param fn_mth_col: 月份列名转换函数
    :return: 包含col_groups以及1-12月列名的横表
    """
    temp_col_name = '_MTH_'
    # 确保日期列是datetime类型
    df[col_date] = pd.to_datetime(df[col_date])
    # 增加月份临时列
    df[temp_col_name] = df[col_date].dt.month

    # 按col_groups和_MTH_分组，计算每月金额
    col_groups.append(temp_col_name)
    df_m = df.groupby(col_groups)[col_amount].sum().unstack()
    df_m = df_m.fillna(0)

    # 重命名月份列
    df_m.columns = [fn_mth_col(col) for col in df_m.columns]

    # 确保所有月份都存在（1-12月），如果某月没有数据则填充为0
    for month in range(1, 13):
        col_name = fn_mth_col(month)
        if col_name not in df_m.columns:
            df_m[col_name] = 0

    # 重新排序列，确保顺序正确（1月到12月）
    df_m = df_m[[fn_mth_col(m) for m in range(1, 13)]]

    # 重置索引，使col_groups成为列
    df_m = df_m.reset_index()

    return df_m


def income_report(params) -> QueryR:
    def m_col(m):
        return f'M{m:02d}'

    def new_row(df_source, disp_ord, tag) -> DataFrame:
        df_target = df_source.copy()
        df_target['ORD'] = disp_ord
        df_target['TAG'] = tag
        return df_target

    def percent(va, vb):
        ret = safe_div(va, vb, none_as=0)
        return ret

    year = get_attr(extract_qc(params, 'YEAR'), 'value')
    orgs = get_attr(extract_qc(params, 'ORG_EXEC'), 'value')
    biz_types = get_attr(extract_qc(params, 'BIZ_TYPE'), 'value')
    units = get_attr(extract_qc(params, 'UNITS'), 'value', 10000)

    show_progress('[yus_demo.income_report]', f'年度回款统计: year={year};orgs={orgs};biz_types={biz_types}')
    ss_inc = Selection(db=get_db(),
                       title='年度回款统计',
                       tables=['dw_inc', 'dw_sct'],
                       columns=['a.INC_DATE',
                                'b.ORG_EXEC' if orgs else literal("10000").label('ORG_EXEC'),
                                lambda ss: func.sum(ss.a.AMOUNT / units).label('AMOUNT'),
                                ],
                       joins=[('a.SCT_ID', 'b.SCT_ID')],
                       unit_spec={
                           'BIZ_TYPE': {'utype': UnitType.CHOOSE, 'mode': ChooseMode.LIST,
                                        'dict_value': "{0:'自营',1:'代购',2:'驻场'}"},
                           'AMOUNT': {'utype': UnitType.CURRENCY},
                       },
                       group_bys=['a.INC_DATE', 'b.ORG_EXEC'],
                       order_bys=['b.ORG_EXEC'],
                       )

    qm = get_qm()
    qc = {'INC_DATE': [Op.BETWEEN, (f'{year}-01-01', f'{year}-12-31')]}
    # 查询条件
    if orgs:
        qc.update({'b.ORG_EXEC': [Op.IN, orgs]})
    if biz_types:
        qc.update({'b.BIZ_TYPE': [Op.IN, biz_types]})

    df = qm.query_selection(selection=ss_inc, condition=qc).dataframe()
    # print(df.to_string())

    df = group_month(df, col_date='INC_DATE', col_amount='AMOUNT', col_groups=['ORG_EXEC'], fn_mth_col=m_col)

    # 4行：当月、当月累计、当月占全年、月累计占全年
    df_m = new_row(df, 0, 'INC')
    df_y = new_row(df_m, 10, 'INC.Y')
    df_p = new_row(df_m, 20, 'INC.P')
    df_yp = new_row(df_m, 30, 'INC.YP')

    # 逐月计算累计值
    for month in range(1, 13):
        cm, pm = m_col(month), m_col(month - 1)
        if month == 1:
            df_y[cm] = df_y[cm]  # M01累计=M01
        else:
            df_y[cm] = df_y[pm] + df_m[cm]
    # 计算占比
    for month in range(1, 13):
        cm, ym = m_col(month), m_col(12)
        df_p[cm] = percent(df_m[cm], df_y[ym]) * 100
        df_yp[cm] = percent(df_y[cm], df_y[ym]) * 100

    # 合并各行
    result = pd.concat([df_m, df_y, df_p, df_yp], ignore_index=True)
    # 排序,年累计行会排在后面
    result = result.sort_values(['ORG_EXEC', 'ORD'])
    column_specs = [
        ColumnSpec(name='ORG_EXEC', comment='业务单元', utype=UnitType.LOOKUP, lookup_key='yut_demo.OrgLookup',
                   format='{name}'),

    ]
    column_specs.extend(
        [ColumnSpec(name=m_col(m), comment=f'{m}月', utype=UnitType.CURRENCY) for m in range(1, 13)])
    column_specs.extend([ColumnSpec(name='ORD', comment='显示次序', utype=UnitType.INT, ),
                         ColumnSpec(name='TAG', comment='项目', utype=UnitType.CHOOSE,
                                    dict_value="{'INC':'月回款','INC.Y':'累计回款','INC.P':'月占比%','INC.YP':'累计占比%'}",
                                    format='{name}'), ])
    return QueryR(result, column_specs)


def selection_sct_list() -> Selection:
    show_progress('[yus_demo.selection_sct_list]',
                  '复杂查询：合同列表，包含已回款金额、余额的计算以及合同与客户的引用关系')
    # 复杂查询：合同列表，包含已回款金额、余额的计算以及合同与客户的引用关系
    sct_tables = ['dw_sct', 'dw_cus', 'dw_inc']
    sct_columns = [
        'SCT_ID',  # 销售合同ID
        'CUS_NO',  # 客户号
        'b.CUS_SHORT',  # 客户简称
        'b.CUS_TYPE',  # 客户类型
        'SCT_NO',  # 销售合同号
        'SCT_TITLE',  # 合同名称
        'AMOUNT',  # 合同金额
        'BUY_AMOUNT',  # 代购金额
        'LOB',  # 业务线
        'BIZ_TYPE',  # 经营类别
        'ISSUE_YEAR',  # 签约年份
        'ISSUE_DATE',  # 签约日期
        'SDATE',  # 开始日期
        'EDATE',  # 到期日期
        'OP_SCT_NO',  # 对方合同号
        'SCT_STATE',  # 合同状态
        # 'TERMS',  # 主要条款
        'ORG_NOM',  # 署名单位
        'ORG_SALE',  # 签约单位
        # 'DEPT_SALE',  # 签约部门
        'ORG_EXEC',  # 履约单位
        # 'DEPT_EXEC',  # 履约部门
        'ORG_BOOK',  # 核算单位
        # 'BIZ_OWNER',  # 商务经办人
        # 'PFM_OWNER',  # 业绩归属人
        # 'DOC_OWNER',  # 档案负责人
        # 'DOC_STATE',  # 归档状态
        # 'REMARK',  # 备注
        # 'DIM_1',  # 统计1
        # 'DIM_2',  # 统计2
        # 'DIM_3',  # 统计3
        # 'PA_NAME',  # 甲方署名单位
        # 'ACT_USER',  # 实际用户
        lambda qs: func.sum(qs.f('c.AMOUNT')).label('INC_AMOUNT'),  # 已回款金额
    ]
    sct_joins = [
        ('a.CUS_NO', 'b.CUS_NO'),
        ('a.SCT_ID', 'c.SCT_ID', True),  # 与回款表必须使用外连接
    ]
    sct_ext_comments = {
        'CUS_NO': '客户号',
        'CUS_SHORT': '客户简称',
        'CUS_TYPE': '客户类型',
        'INC_AMOUNT': '已回款金额',
        'BALANCE': '合同余额',
    }
    sct_unit_spec = {
        'BIZ_TYPE': {'utype': UnitType.CHOOSE, 'mode': ChooseMode.LIST,
                     'dict_value': "{0:'自营',1:'代购',2:'驻场'}",
                     'attitude': {DisplayAttitude.WEAK_NEGATIVE: ['1'],
                                  DisplayAttitude.WEAK_POSITIVE: ['2'],
                                  # AttitudeToken.POSITIVE: ['0'],
                                  }
                     },
        'SCT_ID': {'utype': UnitType.INT, 'leading_zero': 6,
                   'link_to': 'yut_demo.show_contract({_value}, False)'},
        'CUS_ID': {'utype': UnitType.INT, 'format': '%08d',
                   'link_to': 'nmis.app.show_custom({value},{CUST_NO},{CUST_NAME})'},
        'CUS_TYPE': {'utype': UnitType.CHOOSE, 'mode': ChooseMode.LIST, 'dim_key': 'CUS.TYPE', },
        'SCT_NO': {'utype': UnitType.TEXT,
                   'link_to': 'yut_demo.show_contract({_value}, True)'},
        'INC_AMOUNT': {'utype': UnitType.CURRENCY},
        'BALANCE': {'utype': UnitType.CURRENCY, 'attitude_color': True},
        'ISSUE_YEAR': {'utype': UnitType.YEAR},
        'LOB': {'utype': UnitType.CHOOSE, 'mode': ChooseMode.LIST, 'dim_key': 'BIZ.LOB', },
        'SCT_STATE': {'utype': UnitType.CHOOSE, 'mode': ChooseMode.LIST, 'enum_key': 'SCT_STATE',
                      'attitude': {DisplayAttitude.NEGATIVE: [9],
                                   DisplayAttitude.WEAK_POSITIVE: [3],
                                   DisplayAttitude.WEAK_NEGATIVE: [2],
                                   DisplayAttitude.POSITIVE: [4],
                                   }},
        'INC_RATE': {'utype': UnitType.PERCENT},
        'ORG_NOM': {'utype': UnitType.LOOKUP, 'lookup_key': 'yut_demo.OrgLookup', 'multi_value': False},
        'ORG_SALE': {'utype': UnitType.LOOKUP, 'lookup_key': 'yut_demo.OrgLookup', 'multi_value': False},
        'ORG_EXEC': {'utype': UnitType.LOOKUP, 'lookup_key': 'yut_demo.OrgLookup', 'multi_value': False},
        'ORG_BOOK': {'utype': UnitType.LOOKUP, 'lookup_key': 'yut_demo.OrgLookup', 'multi_value': False},

    }

    def sct_post_process(sel, df):
        df['BALANCE'] = df.AMOUNT - df.INC_AMOUNT.fillna(Decimal(0.0))  # 后处理方法增加余额列
        df['INC_RATE'] = df.apply(
            lambda x: Decimal(safe_div(x.INC_AMOUNT, x.AMOUNT, zero_div=0.0, none_as=0.0)) * Decimal(100.0),
            axis=1)  # 后处理方法增加回款百分比
        sel.add_ext_comments(INC_RATE='回款比例')  # 可以在后处理中增加列附注INC_RATE，也可以在创建Selection时由ext_comments预先指定
        # 以下处理附带的查询条件
        for attr in ['BALANCE', 'INC_RATE']:
            c = sel.get_condition(attr)
            if c:
                df = c.op.query_df(df, c.attr, c.value)
        df['INC_AMOUNT'] = df['INC_AMOUNT'].fillna(Decimal(0.0))  # 将NaN视为0
        return df

    def q_maker(q, s, *args, **kwargs):
        q = s.add_filter(q, s.a.ISSUE_YEAR, kwargs['year'], Op.IN)
        q = s.add_filter(q, 'a.BIZ_TYPE', kwargs['biz_type'], Op.LIKE)
        q = s.add_filter(q, 'a.AMOUNT', kwargs['amount'], Op.BETWEEN)
        q = q.order_by(s.a.CUS_NO, s.a.SCT_NO)
        return q

    ss_sct = Selection(
        db=get_db(),
        title='销售合同',
        comment='带大字段的销售合同',
        tables=sct_tables,
        columns=sct_columns,
        joins=sct_joins,
        ext_comments=sct_ext_comments,
        unit_spec=sct_unit_spec,
        group_bys=['a.SCT_ID'],
        order_bys=['a.SCT_NO'],
        make_q=q_maker,
        post_process=sct_post_process,
    )
    return ss_sct


def init_models():
    get_qm().register_selection('sct_list', 'yus_demo.selection_sct_list()')


def query_sct_list(qc) -> QueryR:
    json = get_qm().query_selection(ds_key='sct_list', condition=qc).encode()
    return QueryR.decode(json)


def generate_model():
    show_progress('[yus_demo.generate_model]', '从数据库反射生成model文件')
    meta_db = MetaDb(echo=True)
    meta_db.generate_code(py_filename=r'yus_demo_models.py',
                          save_to_file=True,
                          name_pattern='[dD][wW]_.',
                          name_space='NDW')


if __name__ == '__main__':
    init_env()
    # generate_model()
    init_models()
    # simple_query()
    # for org in load_orgs(1):
    #     print(org)
    qr = income_report({'YEAR': (Op.EQU, 2024),
                        'ORG_EXEC': (Op.IN, ['10002', '10003', '10007']),
                        })
    print(qr.dataframe().to_string())
    qr = query_sct_list({'ISSUE_YEAR': (Op.IN, (2024, 2025)),
                         'BIZ_TYPE': (Op.LIKE, '%'),
                         'AMOUNT': (Op.GT, 0.1),
                         })
    print(qr.dataframe().to_string())
