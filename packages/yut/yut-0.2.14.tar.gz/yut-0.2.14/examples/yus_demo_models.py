# -*- ndw_models.py: python ; coding: utf-8 -*-
# ***********************************************************************
# 创建数据model对应的单表Selection对象
# 本代码由程序通过反射数据库表结构自动生成，模板文件： db_models.ptl (V1.0)
# 生成时间: 2025-06-12 23:26:52.988021
# ***********************************************************************
from yus.dbm import QueryManager, MetaDb, Selection

_ndw_db = None
NAME_SPACE = 'NDW'


def get_db():
    global _ndw_db
    if _ndw_db is None:
        _ndw_db = MetaDb(echo=False)
    return _ndw_db


def get_qm() -> QueryManager:
    return QueryManager.instance('NDW')


def create_selections():
    db = get_db()
    return {

        # DW_ORG -> DW_ORG  - 机构 
        "DW_ORG": Selection(
            db=db,
            title='机构',
            tables=['dw_org'],
            columns=[
                'ORG_NO',  # 机构号
                'ORG_NAME',  # 机构名称
                'ORG_SHORT',  # 机构简称
                'ORG_PATH',  # 机构路径
                'ORG_SCHEMA',  # 体系性质
                'UNIT_CODE',  # 单元代码
                'TREE_CODE',  # 层级码
                'IS_LEAF',  # 叶节点
                'LEVEL',  # 层级
                'UNIT_RANK',  # 规格
                'UNIT_ROLE',  # 经营定位
                'OPEN_YM',  # 设立年月
                'CLOSE_YM',  # 失效年月
                'DISABLE_FLAG',  # 失效标记
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_PDT -> DW_PDT  - 产品名录 
        "DW_PDT": Selection(
            db=db,
            title='产品名录',
            tables=['dw_pdt'],
            columns=[
                'PDT_CODE',  # 产品代号
                'PDT_NAME',  # 产品名称
                'PDT_TITLE',  # 开票品名
            ]
        ),
        # DW_PAY -> DW_PAY  - 支出 
        "DW_PAY": Selection(
            db=db,
            title='支出',
            tables=['dw_pay'],
            columns=[
                'ORG_NO',  # 机构号
                'PAY_CODE',  # 费用代码
                'YR',  # 年度
                'Y_TOTAL',  # 全年数值
                'M01',  # 1月数值
                'M02',  # 2月数值
                'M03',  # 3月数值
                'M04',  # 4月数值
                'M05',  # 5月数值
                'M06',  # 6月数值
                'M07',  # 7月数值
                'M08',  # 8月数值
                'M09',  # 9月数值
                'M10',  # 10月数值
                'M11',  # 11月数值
                'M12',  # 12月数值
            ]
        ),
        # DW_ORG_PSN -> DW_ORG_PSN  - 人员配属 
        "DW_ORG_PSN": Selection(
            db=db,
            title='人员配属',
            tables=['dw_org_psn'],
            columns=[
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'MTH',  # 月份
                'EMPL_NO',  # 工号
                'DEPT_NO',  # 部门号
                'MGR_DUTY',  # 管理责任
                'JOB_PART',  # 兼岗属性
                'RES_RATIO',  # 资源配比
            ]
        ),
        # DW_DICT -> DW_DICT  - 枚举值 
        "DW_DICT": Selection(
            db=db,
            title='枚举值',
            tables=['dw_dict'],
            columns=[
                'ENUM_KEY',  # 枚举KEY
                'CODE',  # 码值
                'NAME',  # 名称
                'DISP_TEXT',  # 显示文字
                'ICON',  # 图标信息
                'DISP_ORDER',  # 显示次序
                'REMARK',  # 备注
                'DISABLE_FLAG',  # 失效标记
            ]
        ),
        # DW_PSN -> DW_PSN  - 员工 
        "DW_PSN": Selection(
            db=db,
            title='员工',
            tables=['dw_psn'],
            columns=[
                'PSN_RID',  # 员工记录ID
                'YR',  # 年度
                'MTH',  # 月份
                'EMPL_NO',  # 工号
                'EMPL_NAME',  # 姓名
                'GENDER',  # 性别
                'MOBILE_PHONE',  # 手机号码
                'EMAIL',  # 邮箱
                'ETHNIC',  # 民族
                'BIRTH_DATE',  # 出生日期
                'ORIGIN_CITY',  # 籍贯
                'ID_NUM',  # 身份证号
                'LST_EDU',  # 最后学历
                'FST_EDU',  # 第一学历
                'MAJOR',  # 专业
                'GRD_SCHOOL',  # 毕业学校
                'GRD_DATE',  # 毕业时间
                'RELATION',  # 雇佣关系
                'TRIAL',  # 试用标记
                'JOB',  # 职位
                'JOB_TITLE',  # 职位头衔
                'JOB_TYPE',  # 职种
                'JOB_LEVEL',  # 职级
                'EMPL_STATE',  # 在职状态
                'ENTRY_DATE',  # 入职日期
                'TRANS_DATE',  # 转正日期
                'QUIT_DATE',  # 离职日期
                'ONSITE',  # 用工场所
                'WORK_CITY',  # 工作地点
                'LIVING_ADDR',  # 居住地址
                'FAMILY_ADDR',  # 家庭地址
                'PAYROLL_ORG',  # 发薪单位
            ]
        ),
        # DW_SCT_PDT -> DW_SCT_PDT  - 销售明细 
        "DW_SCT_PDT": Selection(
            db=db,
            title='销售明细',
            tables=['dw_sct_pdt'],
            columns=[
                'PDT_CODE',  # 产品代号
                'SCT_ID',  # 销售合同ID
                'AMOUNT',  # 金额
            ]
        ),
        # DW_DIM_CODE -> DW_DIM_CODE  - 统计码 
        "DW_DIM_CODE": Selection(
            db=db,
            title='统计码',
            tables=['dw_dim_code'],
            columns=[
                'DM_KEY',  # 统计维度号
                'DIM_CODE',  # 统计码
                'DIM_NAME',  # 统计码名称
                'DISP_TEXT',  # 显示文字
                'DISP_ORDER',  # 显示次序
                'REMARK',  # 备注
                'CAS_CODE',  # 级联码值
                'DISABLE_FLAG',  # 失效标记
            ]
        ),
        # DW_AR -> DW_AR  - 应收款 
        "DW_AR": Selection(
            db=db,
            title='应收款',
            tables=['dw_ar'],
            columns=[
                'AR_ID',  # 应收ID
                'AR_NUM',  # 应收标识号
                'SCT_ID',  # 销售合同ID
                'CUS_NO',  # 客户号
                'BIZ_TYPE',  # 经营类别
                'AMT_TYPE',  # 款项性质
                'AMOUNT',  # 应收金额
                'REC_TERM',  # 履约条件
                'AMT_PCT',  # 占比
                'INC_FLAG',  # 回款标记
                'AR_STATE',  # 催收状态
                'AR_DATE',  # 应回款日期
                'PLN_DATE',  # 计划回款日期
                'ACT_DATE',  # 实际回款日期
                'ACT_AMOUNT',  # 已回款金额
                'PLN_DESC',  # 计划说明
                'DEMAND_DESC',  # 催收说明
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_CUS -> DW_CUS  - 客户 
        "DW_CUS": Selection(
            db=db,
            title='客户',
            tables=['dw_cus'],
            columns=[
                'CUS_NO',  # 客户号
                'CUS_NAME',  # 客户名称
                'CUS_SHORT',  # 客户简称
                'CUS_TYPE',  # 客户分类
                'ENT_NAT',  # 企业性质
                'CUS_RANK',  # 服务等级
                'RSP_ORG',  # 负责单位
                'RSP_DEPT',  # 负责部门
                'CUS_MGR',  # 客户经理
                'REGION',  # 所属区域
                'SALES_CHNL',  # 渠道
                'ADDRESS',  # 联系地址
                'CUS_CONTACT',  # 客户联系人
                'OPEN_YEAR',  # 拓展年度
                'BIZ_STATE',  # 商务状态
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
                'REMARK',  # 备注
            ]
        ),
        # DW_BOP -> DW_BOP  - 商机 
        "DW_BOP": Selection(
            db=db,
            title='商机',
            tables=['dw_bop'],
            columns=[
                'BOP_ID',  # 商机ID
                'ORG_NO',  # 机构号
                'BOP_NAME',  # 商机名称
                'BOP_SHORT',  # 商机简称
                'BOP_DESC',  # 商机描述
                'LOB',  # 业务线
                'SALES_CHNL',  # 渠道
                'SALES',  # 销售人员
                'SALE_SPTS',  # 支持人员
                'CUS_NAME',  # 客户名称
                'CUS_NO',  # 客户号
                'REG_DATE',  # 登记日期
                'EST_SDATE',  # 预计启动时间
                'EXP_TIME',  # 期望上线时间
                'BOP_STATE',  # 商机状态
                'PROGRESS',  # 所处阶段
                'PRGS_DESC',  # 进展描述
                'EST_AMOUNT',  # 预估金额
                'FINAL_CUS',  # 最终用户名称
                'SOURCE',  # 商机来源
                'BUY_PTN',  # 选型方式
                'PEERS',  # 主要竞争对手
                'CMP_DESC',  # 竞争情况概述
                'NXT_ACTION',  # 行动计划
                'EST_OPPO',  # 估计签单机率
                'EST_DESC',  # 评估依据
                'DEC_MAKER',  # 决策人及其职位
                'RL_PSNS',  # 干系人
                'FIN_CONTRACTOR',  # 最终签约厂商
                'REMARK',  # 备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
                'HBY_ITEM_ID',  # 伙伴云数据ID
            ]
        ),
        # DW_DIM -> DW_DIM  - 统计维度 
        "DW_DIM": Selection(
            db=db,
            title='统计维度',
            tables=['dw_dim'],
            columns=[
                'DM_KEY',  # 统计维度号
                'DIMENSION',  # 统计维度名称
                'CASCADE_KEY',  # 级联维度
                'REMARK',  # 备注
            ]
        ),
        # DW_DEPT -> DW_DEPT  - 部门 
        "DW_DEPT": Selection(
            db=db,
            title='部门',
            tables=['dw_dept'],
            columns=[
                'ORG_NO',  # 机构号
                'DEPT_NO',  # 部门号
                'DEPT_NAME',  # 部门名称
                'DEPT_SHORT',  # 部门简称
                'TREE_CODE',  # 层级码
                'IS_LEAF',  # 叶节点
                'DISABLE_FLAG',  # 失效标记
            ]
        ),
        # DW_INC_PLN -> DW_INC_PLN  - 收款计划 
        "DW_INC_PLN": Selection(
            db=db,
            title='收款计划',
            tables=['dw_inc_pln'],
            columns=[
                'IPLN_ID',  # 收款计划ID
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'MTH',  # 月份
                'CUS_NO',  # 客户号
                'AR_TITLE',  # 款项内容
                'AMOUNT',  # 计划收款金额
                'SCT_NO',  # 销售合同号
                'AR_NUM',  # 应收标识号
                'DEPT_NO',  # 负责部门
                'OWNER',  # 负责人
                'EST_OPPO',  # 估计回款机率
                'EST_DESC',  # 估计说明
                'INC_FLAG',  # 回收结果
                'INC_AMOUNT',  # 实际收款金额
                'ACT_DESC',  # 进展说明
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_IX_BOOK -> DW_IX_BOOK  - 业绩台账 
        "DW_IX_BOOK": Selection(
            db=db,
            title='业绩台账',
            tables=['dw_ix_book'],
            columns=[
                'PM_ID',  # 台账记录ID
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'IX_CODE',  # 指标代码
                'P_DATE',  # 日期
                'DIR',  # 方向
                'AMOUNT',  # 数额
                'ITEM_DESC',  # 摘要
                'REF_NO',  # 业务参考号
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
                'DESC',  # 备注
            ]
        ),
        # DW_RESP -> DW_RESP  - 资源投入计划 
        "DW_RESP": Selection(
            db=db,
            title='资源投入计划',
            tables=['dw_resp'],
            columns=[
                'YR',  # 年度
                'ORG_NO',  # 机构号
                'RP_CODE',  # 资源投向编码
                'PWDAY',  # 计划资源投放人日
            ]
        ),
        # DW_RP_CODE -> DW_RP_CODE  - 资源投向 
        "DW_RP_CODE": Selection(
            db=db,
            title='资源投向',
            tables=['dw_rp_code'],
            columns=[
                'RP_CODE',  # 资源投向编码
                'RP_NAME',  # 资源投向名称
                'RP_DESC',  # 资源投向描述
                'LOB',  # 业务线
                'TREE_CODE',  # 层级码
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_WHR -> DW_WHR  - 工时 
        "DW_WHR": Selection(
            db=db,
            title='工时',
            tables=['dw_whr'],
            columns=[
                'YR',  # 年度
                'MTH',  # 月份
                'EMPL_NO',  # 工号
                'RP_CODE',  # 资源投向编码
                'WHR_DCL',  # 报工数
                'WHR_APR',  # 核准数
                'PSN_RID',  # 员工记录ID
            ]
        ),
        # DW_BFS -> DW_BFS  - 配套采购 
        "DW_BFS": Selection(
            db=db,
            title='配套采购',
            tables=['dw_bfs'],
            columns=[
                'SCT_ID',  # 销售合同ID
                'PCT_ID',  # 采购合同ID
                'SALE_AMOUNT',  # 售出金额
                'INC_FLAG',  # 回款标记
                'REMARK',  # 备注
            ]
        ),
        # DW_AP -> DW_AP  - 应付款 
        "DW_AP": Selection(
            db=db,
            title='应付款',
            tables=['dw_ap'],
            columns=[
                'AP_ID',  # 应付记录ID
                'PCT_ID',  # 采购合同ID
                'SPLR_ID',  # 供应商ID
                'AP_DATE',  # 应付日期
                'AP_AMOUNT',  # 应付金额
                'INV_NUM',  # 发票号
                'INV_STATE',  # 发票状态
                'INV_REMARK',  # 发票备注
                'CLEAR_FLAG',  # 结算标记
                'PY_ID',  # 付款记录ID
            ]
        ),
        # DW_IX_PV -> DW_IX_PV  - 指标计划值 
        "DW_IX_PV": Selection(
            db=db,
            title='指标计划值',
            tables=['dw_ix_pv'],
            columns=[
                'IX_CODE',  # 指标代码
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'Y_TOTAL',  # 全年数值
                'M01',  # 1月数值
                'M02',  # 2月数值
                'M03',  # 3月数值
                'M04',  # 4月数值
                'M05',  # 5月数值
                'M06',  # 6月数值
                'M07',  # 7月数值
                'M08',  # 8月数值
                'M09',  # 9月数值
                'M10',  # 10月数值
                'M11',  # 11月数值
                'M12',  # 12月数值
                'Q1',  # 1季度数值
                'Q2',  # 2季度数值
                'Q3',  # 3季度数值
                'Q4',  # 4季度数值
                'H1',  # 上半年数
                'H2',  # 下半年数
                'MY01',  # 1月累计
                'MY02',  # 2月累计
                'MY03',  # 3月累计
                'MY04',  # 4月累计
                'MY05',  # 5月累计
                'MY06',  # 6月累计
                'MY07',  # 7月累计
                'MY08',  # 8月累计
                'MY09',  # 9月累计
                'MY10',  # 10月累计
                'MY11',  # 11月累计
                'MY12',  # 12月累计
            ]
        ),
        # DW_AR_MATCH -> DW_AR_MATCH  - 应收对账 
        "DW_AR_MATCH": Selection(
            db=db,
            title='应收对账',
            tables=['dw_ar_match'],
            columns=[
                'INC_ID',  # 收款记录ID
                'AR_ID',  # 应收ID
                'INC_AMOUNT',  # 回款金额
            ]
        ),
        # DW_BPAY -> DW_BPAY  - 采购付款记录 
        "DW_BPAY": Selection(
            db=db,
            title='采购付款记录',
            tables=['dw_bpay'],
            columns=[
                'PY_ID',  # 付款记录ID
                'PCT_ID',  # 采购合同ID
                'PDATE',  # 付款日期
                'AMOUNT',  # 付款金额
                'ITEM_DESC',  # 摘要
                'MATCH_FLAG',  # 银行对账标识
                'VCH_NUM',  # 记账凭证号
                'BOOK_AMOUNT',  # 记账金额
                'REMARK',  # 备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_IX -> DW_IX  - 指标项 
        "DW_IX": Selection(
            db=db,
            title='指标项',
            tables=['dw_ix'],
            columns=[
                'IX_CODE',  # 指标代码
                'IX_NAME',  # 指标名称
                'DISP_TEXT',  # 显示文字
                'IX_DESC',  # 指标描述
                'SUM_DIMS',  # 汇总维度
                'IX_EXPR',  # 计算表达式
                'DISP_ORDER',  # 显示次序
                'CALC_BATCH',  # 计算批次
                'DISABLE_FLAG',  # 失效标记
            ]
        ),
        # DW_PSN_MTH -> DW_PSN_MTH  - 人月数 
        "DW_PSN_MTH": Selection(
            db=db,
            title='人月数',
            tables=['dw_psn_mth'],
            columns=[
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'MTH',  # 月份
                'PM_TOTAL',  # 全口径人月
                'PM_STD',  # 可比口径人月
                'PM_REGULAR',  # 常规人月
                'PM_INTERN',  # 实习生人月
                'PM_OUTSRC',  # 外包人月
                'PM_ONSITE',  # 驻场人月
            ]
        ),
        # DW_IX_FV -> DW_IX_FV  - 指标执行值 
        "DW_IX_FV": Selection(
            db=db,
            title='指标执行值',
            tables=['dw_ix_fv'],
            columns=[
                'IX_CODE',  # 指标代码
                'ORG_NO',  # 机构号
                'YR',  # 年度
                'Y_TOTAL',  # 全年数值
                'M01',  # 1月数值
                'M02',  # 2月数值
                'M03',  # 3月数值
                'M04',  # 4月数值
                'M05',  # 5月数值
                'M06',  # 6月数值
                'M07',  # 7月数值
                'M08',  # 8月数值
                'M09',  # 9月数值
                'M10',  # 10月数值
                'M11',  # 11月数值
                'M12',  # 12月数值
                'Q1',  # 1季度数值
                'Q2',  # 2季度数值
                'Q3',  # 3季度数值
                'Q4',  # 4季度数值
                'H1',  # 上半年数
                'H2',  # 下半年数
                'MY01',  # 1月累计
                'MY02',  # 2月累计
                'MY03',  # 3月累计
                'MY04',  # 4月累计
                'MY05',  # 5月累计
                'MY06',  # 6月累计
                'MY07',  # 7月累计
                'MY08',  # 8月累计
                'MY09',  # 9月累计
                'MY10',  # 10月累计
                'MY11',  # 11月累计
                'MY12',  # 12月累计
            ]
        ),
        # DW_SCT -> DW_SCT  - 销售合同 
        "DW_SCT": Selection(
            db=db,
            title='销售合同',
            tables=['dw_sct'],
            columns=[
                'SCT_ID',  # 销售合同ID
                'CUS_NO',  # 客户号
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
                'TERMS',  # 主要条款
                'ORG_NOM',  # 署名单位
                'ORG_SALE',  # 签约单位
                'DEPT_SALE',  # 签约部门
                'ORG_EXEC',  # 履约单位
                'DEPT_EXEC',  # 履约部门
                'ORG_BOOK',  # 核算单位
                'BIZ_OWNER',  # 商务经办人
                'PFM_OWNER',  # 业绩归属人
                'DOC_OWNER',  # 档案负责人
                'DOC_STATE',  # 归档状态
                'REMARK',  # 备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
                'PA_NAME',  # 甲方署名单位
                'ACT_USER',  # 实际用户
            ]
        ),
        # DW_SPLR -> DW_SPLR  - 供应商 
        "DW_SPLR": Selection(
            db=db,
            title='供应商',
            tables=['dw_splr'],
            columns=[
                'SPLR_ID',  # 供应商ID
                'SPLR_NO',  # 供应商编号
                'SPLR_NAME',  # 供应商名称
                'SPLR_SHORT',  # 供应商简称
                'SPLR_TYPE',  # 供应商分类
                'SPLR_STATE',  # 合作状态
                'FST_YEAR',  # 开始合作年份
                'PUR_TYPE',  # 采购分类
                'PUR_PDT',  # 主要采购产品
                'STD_PRICE',  # 基准价格
                'PUR_TERMS',  # 商务条件
                'SPLR_RANK',  # 供应商评级
                'BANK',  # 开户行
                'ACCOUNT_NO',  # 账号
                'ADDR',  # 地址
                'TEL',  # 联系电话
                'SPLR_CONTACT',  # 联系人
                'REMARK',  # 备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_ENUM -> DW_ENUM  - 枚举类型 
        "DW_ENUM": Selection(
            db=db,
            title='枚举类型',
            tables=['dw_enum'],
            columns=[
                'ENUM_KEY',  # 枚举KEY
                'ENUM_NAME',  # 枚举名称
                'V_TYPE',  # 值类型
                'REMARK',  # 备注
            ]
        ),
        # DW_PCT -> DW_PCT  - 采购合同 
        "DW_PCT": Selection(
            db=db,
            title='采购合同',
            tables=['dw_pct'],
            columns=[
                'PCT_ID',  # 采购合同ID
                'SPLR_ID',  # 供应商ID
                'PCT_NO',  # 采购合同号
                'PCT_TITLE',  # 采购合同名称
                'PUR_TYPE',  # 采购分类
                'PUR_PDT',  # 主要采购产品
                'AMOUNT',  # 合同金额
                'ISSUE_YEAR',  # 签约年份
                'ISSUE_DATE',  # 签约日期
                'SDATE',  # 开始日期
                'EDATE',  # 到期日期
                'OP_SCT_NO',  # 对方合同号
                'PCT_STATE',  # 采购合同状态
                'TERMS',  # 主要条款
                'ORG_NOM',  # 署名单位
                'ORG_SALE',  # 签约单位
                'DEPT_SALE',  # 签约部门
                'ORG_EXEC',  # 履约单位
                'DEPT_EXEC',  # 履约部门
                'ORG_BOOK',  # 核算单位
                'BIZ_OWNER',  # 商务经办人
                'DOC_OWNER',  # 档案负责人
                'DOC_STATE',  # 归档状态
                'REMARK',  # 备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_BOP_TRACE -> DW_BOP_TRACE  - 商机跟进 
        "DW_BOP_TRACE": Selection(
            db=db,
            title='商机跟进',
            tables=['dw_bop_trace'],
            columns=[
                'TR_ID',  # 商机跟进ID
                'BOP_ID',  # 商机ID
                'TRC_DATE',  # 跟进日期
                'TRC_MAN',  # 跟进人员
                'COMM_TYPE',  # 客户沟通方式
                'TRC_DESC',  # 情况概述
                'BOP_DESC',  # 详情
                'HBY_ITEM_ID',  # 伙伴云数据ID
                'HBY_BOP_ITEM_ID',  # 伙伴云商机数据ID
            ]
        ),
        # DW_INC -> DW_INC  - 收款记录 
        "DW_INC": Selection(
            db=db,
            title='收款记录',
            tables=['dw_inc'],
            columns=[
                'INC_ID',  # 收款记录ID
                'CUS_NO',  # 客户号
                'SCT_ID',  # 销售合同ID
                'INC_DATE',  # 收款日期
                'AMOUNT',  # 收款金额
                'ITEM_DESC',  # 摘要
                'INV_STATE',  # 发票状态
                'INV_NUM',  # 发票号
                'MATCH_FLAG',  # 银行对账标识
                'VCH_NUM',  # 记账凭证号
                'BOOK_AMOUNT',  # 记账金额
                'REMARK',  # 收款备注
                'DIM_1',  # 统计1
                'DIM_2',  # 统计2
                'DIM_3',  # 统计3
            ]
        ),
        # DW_DOC -> DW_DOC  - 合同档案 
        "DW_DOC": Selection(
            db=db,
            title='合同档案',
            tables=['dw_doc'],
            columns=[
                'DR_ID',  # 档案记录ID
                'SCT_ID',  # 销售合同ID
                'PCT_ID',  # 采购合同ID
                'DOC_FLAG',  # 分类标记
                'DOC_LABEL',  # 档案标签
                'DOC_CONTENT',  # 档案内容
            ]
        ),
    }
