# -*- ndw_ui.py: python ; coding: utf-8 -*-
import datetime
import os
import sys
from datetime import datetime

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import Qt, QFont, QColor, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit, QHBoxLayout, QToolBar, QSplashScreen

import yus_demo
from yui import img, get_app, pop_info, Theme, create_layout, create_button, create_toolbar, \
    create_tool_button, LookupViewType, TranslateDirection, create_default_app, load_icon, show_in_center, \
    create_layout_widget, get_mainwindow, set_current_theme, current_theme
from yui.wdg import YWidgetPages, YLink, YWindow, YNavPanel, YLogo, TabInfo, TabSetting
from yui.yfield import YFdCriteria
from yui.yform import YForm
from yui.ylookup import YLookup, YLookupDialog, YViewBuilder
from yui.ymodel import PandasModel, col_spec, add_qc_value, translate_olist
from yui.ytable import YTableWidget
from yus import ColumnSpec, Op, UnitType
from yus_demo import query_sct_list
from yus_demo_models import get_qm
from yut import get_attr


def show_app():
    cur_app = get_app()
    pop_info(cur_app.children())


def switch_theme():
    import qtmodern.styles as style
    if current_theme == Theme.DARK:
        style.light(get_app())
        set_current_theme(Theme.LIGHT)
    else:
        style.dark(get_app())
        set_current_theme(Theme.DARK)


class DemoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setLayout(create_layout(layout_flag='V'))
        self.layout().addWidget(QLabel('Demo Widget'))
        self.layout().addWidget(QTextEdit(text='Hello World!'))


def add_pages(widget):
    pages: YWidgetPages = getattr(widget, 'pages')
    for i in range(pages.page_count(), pages.page_count() + 3):
        pages.add_page(YLink(f'示例{i + 1}', target=new_widget(i)))


def add_win_page(widget):
    pages: YWidgetPages = getattr(get_mainwindow(), 'pages')
    pages.switch_page(pages.add_page(YLink(widget.title, target=widget)))


def new_widget(index):
    wp = create_layout_widget(layout_flag='V')
    wp.layout().addWidget(QLabel(f'测试窗体{index + 1}'))
    wp.layout().addWidget(QTextEdit('- 文本内容: <b>Hello</b> World!<br>' * (index + 1)))
    return wp


def setup_ui(widget: YWindow):
    layout = create_layout('V')
    tbar = create_toolbar(
        [
            create_button('打开', icon_file=img.P_OPEN, trigger=show_app, flat=True),
            create_button('增加', icon_file=img.P_JOIN, trigger=lambda: add_pages(widget), flat=True),
            create_button(text='系统', icon_file=img.P_HTML, trigger=show_app),
            create_tool_button(icon_file=img.P_REFRESH, trigger=switch_theme),
        ]
    )
    layout.addWidget(tbar)
    ws = [new_widget(i) for i in range(2)]
    pages = YWidgetPages(YLink('列表', icon=img.P_DOC2, target=ws[0]),
                         YLink('卡片', target=lambda: new_widget(1)),
                         YLink('详情', target=DemoWidget),
                         YLink('图形', icon=img.P_CHART, target='yut_demo.DemoWidget()'),
                         {'title': '附件', 'icon': img.P_ATTACH, 'target': 'yut_demo.new_widget(3)'},
                         '其它',
                         parent=widget,
                         close_able=True,
                         tab_alignment=Qt.AlignmentFlag.AlignCenter,
                         show_single_tab=True,
                         )
    pw: QWidget = pages.widget(5)  # 其它页对应的widget,默认为QWidget+VBox布局
    pw.layout().addWidget(QLabel('其它内容-系统环境变量'))
    pw.layout().addWidget(QTextEdit('<br>'.join([f' - {k} = {v}' for k, v in os.environ.items()])))

    layout.addWidget(pages)
    widget.content().setLayout(layout)

    setattr(widget, 'pages', pages)


def about():
    pop_info('关于本系统')


def show_widget(win, link: YLink):
    pages = getattr(win, 'pages')
    if pages:
        pages.add_page(link, auto_switch=True)


def create_main_window():
    m_win = YWindow(parent=None, full_left=True)
    hbox = QHBoxLayout()
    hbox.addWidget(QLabel('演示程序的标题'), alignment=Qt.AlignmentFlag.AlignCenter)
    m_win.title_bar().setLayout(hbox)
    setup_ui(m_win)
    nav = YNavPanel(parent=m_win)
    nav.add_links(YLink('NDW', icon=img.P_4_SQUARE, tip_text='数据中台', ),
                  [
                      YLink('人员', icon=img.P_TWO_PERSONS, tip_text='显示人员信息'),
                      YLink('业绩', icon=img.P_GOAL, target="yut_demo.income_summary()",
                            tip_text='回款签单业绩跟踪'),
                      YLink('客户', icon=img.P_CUSTOM, tip_text='客户信息',
                            target='yut_demo.new_widget(3)', ),
                      YLink('合同', icon=img.P_CONTRACT, tip_text='销售合同',
                            target='yut_demo.sct_table()', ),
                      YLink('数据', icon=img.P_DB, tip_text='上传数据'),
                      YLink('系统', icon=img.P_SETTING, tip_text='设置系统参数'),
                  ],
                  logo=YLogo(img_file=img.P_TREE, on_click=about),
                  )
    nav.add_links(YLink('OKR', icon=img.P_DIAMOND),
                  [
                      YLink('月报', icon=img.P_TODO, tip_text='月报工具'),
                      YLink('指标', icon=img.P_GOAL, tip_text='经营指标', target=lambda: new_widget(2)),
                  ],
                  logo=YLogo(img_file=img.I_FAP, on_click=about),
                  )

    nav.toLink.connect(lambda lnk: show_widget(m_win, lnk))
    layout = create_layout(layout_flag='H')
    layout.addWidget(nav)
    m_win.left_widget().setFixedWidth(80)
    m_win.left_widget().setLayout(layout)
    m_win.left_widget().setVisible(True)
    return m_win


def income_summary():
    def inc_role_handler(role, index, col_name, dat):
        row_dat = index.model().data_of_row(index.row())
        high_light = row_dat['TAG'] == 'INC.Y' and col_name.startswith('M')
        is_percent = row_dat['TAG'] in ('INC.YP', 'INC.P') and col_name.startswith('M')
        large_font = dat == 'INC.Y' or (high_light and col_name == 'M12')

        if role == Qt.ItemDataRole.DisplayRole and is_percent:
            return f"{dat:.2f}%"
        if role == Qt.ItemDataRole.FontRole and large_font:
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)  # 比默认字体大
            return font
        if role == Qt.ItemDataRole.ForegroundRole and high_light:
            return QColor(0x00, 0xD0, 0xA0)
        return None

    def query_income(qc) -> PandasModel:
        qr = yus_demo.income_report(qc)
        return PandasModel(qr.dataframe(), qr.column_specs(), custom_style_handler=inc_role_handler)

    specs = get_qm().get_selection('sct_list').column_spec()
    q_criteria = {
        TabInfo('查询条件', layout_flag='H'): [
            YFdCriteria(column_spec=ColumnSpec(name='YEAR', comment='年度', utype=UnitType.YEAR),
                        op=Op.EQU,
                        value=(2025, 2025)),
            YFdCriteria(column_spec=col_spec(specs, 'BIZ_TYPE', format='{name}', layout_flag='H'),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'ORG_EXEC', multi_value=True),
                        op=Op.IN,
                        value=None),
        ],
    }
    qc_value = add_qc_value(dict(), 'YEAR', Op.EQU, datetime.today().year)
    qc_value = add_qc_value(qc_value, 'BIZ_TYPE', Op.IN, (0, 2))
    wdg = YTableWidget(title='年度回款统计表',
                       fn_query=query_income,
                       query_specs=q_criteria,
                       query_condition=qc_value,
                       query_form_orientation=Qt.Orientation.Vertical,
                       query_form_layout='V',
                       display_columns=['ORG_EXEC', 'TAG', 'M01', 'M02', 'M03', 'M04', 'M05', 'M06', 'M07', 'M08',
                                        'M09', 'M10', 'M11', 'M12'],
                       sortable=False,
                       )

    return wdg


def sct_table():
    def query_sct(qc) -> PandasModel:
        qr = query_sct_list(qc)
        return PandasModel(qr.dataframe(), qr.column_specs())

    specs = get_qm().get_selection('sct_list').column_spec()

    q_criteria = {
        TabInfo('基本要素', layout_flag='V'): [
            YFdCriteria(column_spec=col_spec(specs, 'ISSUE_YEAR'),
                        op=Op.BETWEEN,
                        value=(2025, 2025)),
            YFdCriteria(column_spec=col_spec(specs, 'SCT_NO'),
                        op=Op.LIKE,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'SCT_TITLE'),
                        op=Op.LIKE,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'BIZ_TYPE'),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'SCT_STATE'),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'CUS_TYPE'),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'CUS_SHORT'),
                        op=Op.LIKE,
                        value=None),
        ],
        TabInfo('管理信息', layout_flag='V'): [
            YFdCriteria(column_spec=col_spec(specs, 'LOB'),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'ORG_NOM', multi_value=True),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'ORG_SALE', multi_value=True),
                        op=Op.IN,
                        value=None),
            YFdCriteria(column_spec=col_spec(specs, 'ORG_EXEC', multi_value=True),
                        op=Op.IN,
                        value=None),
        ],
    }
    qc_value = add_qc_value(dict(), 'ISSUE_YEAR', Op.BETWEEN, (2025, 2025))
    # qc_value = add_qc_value(dict(), 'BIZ_TYPE', yui.Op.EQU, 0)

    wdg = YTableWidget(title='销售合同列表',
                       fn_query=query_sct,
                       query_specs=q_criteria,
                       query_condition=qc_value,
                       query_form_orientation=Qt.Orientation.Horizontal,
                       query_form_layout='V',
                       hidden_columns=['BUY_AMOUNT', 'OP_SCT_NO'],
                       summary=['AMOUNT', 'INC_AMOUNT', 'BALANCE'],
                       )
    tbar: QToolBar = wdg.findChild(QToolBar, 'toolbar_left')
    tbar.addSeparator()
    tbar.addWidget(create_button('关于', trigger=about, icon_file=img.P_ATTACH))

    tbar: QToolBar = wdg.findChild(QToolBar, 'toolbar_right')
    tbar.addSeparator()
    tbar.insertWidget(tbar.actions()[0], create_button('汇总表', trigger=about, icon_file=img.P_SUM_1, flat=True))
    tbar.addWidget(create_tool_button('图表', trigger=about, icon_file=img.P_CHART_BAR))

    return wdg


class OrgLookup(YLookup):
    _orgs = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._orgs.extend(yus_demo.load_orgs(1))  # 只加载经营体系

    def create_dialog(self) -> YLookupDialog:
        dlg = YLookupDialog(title='选择组织机构',
                            view_type=LookupViewType.Tree,
                            view_builder=YViewBuilder(
                                headers={'机构': '[{ORG_NO}] - {ORG_SHORT}',
                                         '名称': '{ORG_NAME}',
                                         '备注': '{UNIT_CODE}/{TREE_CODE}:{ORG_PATH}', },
                                loader=self.load_org_tree,
                                item_icon_file=img.P_BULLET3,
                                leaf_icon_file=img.P_ORG,
                            ),
                            multi_selection=self.multi_value,
                            )
        return dlg

    def load_org_tree(self, par_org):
        tree_code = get_attr(par_org, "TREE_CODE")
        level = get_attr(par_org, "LEVEL")
        if not tree_code:
            tree_code = ''
            level = 1
        return [o for o in self._orgs if o.TREE_CODE.startswith(tree_code) and o.LEVEL == level + 1]

    def to_text(self, value):
        return translate_olist(TranslateDirection.TO_TEXT, self.dialog_lookup_field(), value, self._orgs)

    def to_value(self, text):
        return translate_olist(TranslateDirection.TO_VALUE, self.dialog_lookup_field(), text, self._orgs)

    def dialog_lookup_field(self):
        return '{ORG_NO}', '{ORG_SHORT}'


def show_contract(sct_id, edit=False):
    form = sct_form(sct_id, edit)
    add_win_page(form)


def sct_form(sct_id, edit=False):
    ds_key = 'DW_SCT'  # 注意使用了不同的数据集，包含合同文本等大字段
    qc = add_qc_value(dict(), 'SCT_ID', Op.EQU, sct_id)
    qr = get_qm().query_selection(ds_key, condition=qc)
    model = PandasModel(qr.dataframe(), qr.column_specs())
    form = YForm(column_specs=model.column_specs(),
                 page_def=TabSetting(
                     TabInfo('基本信息', layout_flag='F'),
                     TabInfo('执行情况', layout_flag='F'),
                     TabInfo('管理信息', layout_flag='G2'),
                     TabInfo('合同文本', layout_flag='V'),
                     stretch=False, ),
                 title='编辑销售合同' if edit else '查看销售合同',
                 caption='#[{SCT_ID}] - {SCT_NO}',
                 read_only=not edit,
                 model=model, )
    form.add_fields(
        ['SCT_ID', 'SCT_NO', 'BIZ_TYPE', 'CUS_NO', 'SCT_TITLE', 'AMOUNT',
         'ISSUE_YEAR', 'ISSUE_DATE', ], 0)
    form.add_fields(
        ['OP_SCT_NO', 'SCT_STATE', 'LOB', 'SDATE', 'EDATE', ], 1)
    return form


def initialize_system():
    splash.showMessage("yus_demo.init_env()...", Qt.AlignBottom | Qt.AlignHCenter)
    yus_demo.init_env()
    splash.showMessage("连接数据库...", Qt.AlignBottom | Qt.AlignHCenter)
    yus_demo.init_models()
    # time.sleep(2)  # 替换为实际初始化代码


class InitThread(QThread):
    finished = Signal()

    def run(self):
        initialize_system()
        self.finished.emit()


if __name__ == '__main__':
    # import ctypes
    #
    # set_console = ctypes.windll.kernel32.SetConsoleTitleW
    # set_console.argtypes = [ctypes.c_wchar_p]
    # set_console('My Process')

    app = create_default_app(app_name='yus')

    # 1. 创建并显示 Splash Screen
    splash_pix = QPixmap(img.I_NDW)  # 替换为你的图片路径
    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()  # 确保立即显示

    main_window = create_main_window()
    main_window.hide()

    # 2. 在后台执行初始化
    init_thread = InitThread()
    init_thread.finished.connect(lambda: show_in_center(main_window))
    init_thread.finished.connect(splash.close)
    init_thread.start()

    main_window.setWindowIcon(load_icon(img.I_AIRPLANE, colored=False))
    main_window.setWindowTitle('YUS_DEMO')
    main_window.resize(1000, 600)

    sys.exit(app.exec())
