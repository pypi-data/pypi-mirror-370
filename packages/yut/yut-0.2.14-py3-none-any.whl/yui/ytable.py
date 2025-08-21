# ytable.py - 通用表格查询控件
import datetime
from typing import Callable

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (QTableView, QWidget, QHBoxLayout, QLabel, QSplitter, QFrame, QToolButton,
                               QStyledItemDelegate, QHeaderView, QLineEdit, QMenu, QTreeView, QAbstractItemView,
                               QToolBar, QApplication)

from . import create_layout_widget, change_font, load_icon, create_button, create_toolbar, create_menu_button, \
    create_tool_button, pop_info, img, create_action, create_layout
from .wdg import TabSetting, show_widget
from .yfield import YEditorDelegate, FACTORY, YDisplayDelegate
from .yform import YQueryForm
from .ymodel import ColumnSpec
from .ymodel import PandasModel
from .ystat import YStatWidget
from yut import get_attr, format_obj, set_attr, Obj, call_exp


def create_column_delegate(view: QTableView | QTreeView, col_spec: ColumnSpec, for_edit=False,
                           **kwargs) -> QStyledItemDelegate:
    kwargs.update(col_spec.__dict__)
    if for_edit:
        return YEditorDelegate(view, col_spec, **kwargs)
    else:
        return YDisplayDelegate(view, col_spec, **kwargs)


class Ct(Obj):
    DEFAULT_WIDTH = 150
    DEFAULT_HEIGHT = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def width(self):
        return get_attr(self, 'w', self.DEFAULT_WIDTH)

    def height(self):
        return get_attr(self, 'h', self.DEFAULT_HEIGHT)

    def alignment(self):
        al_h, al_v = Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignVCenter
        align_flag: str = get_attr(self, 'a', '')
        for f, v in {'<': Qt.AlignmentFlag.AlignLeft,
                     '|': Qt.AlignmentFlag.AlignCenter,
                     '+': Qt.AlignmentFlag.AlignCenter,
                     '>': Qt.AlignmentFlag.AlignRight, }.items():
            if f in align_flag:
                al_h = v
        for f, v in {'^': Qt.AlignmentFlag.AlignTop,
                     '-': Qt.AlignmentFlag.AlignVCenter,
                     '+': Qt.AlignmentFlag.AlignVCenter,
                     '_': Qt.AlignmentFlag.AlignBottom,
                     }.items():
            if f in align_flag:
                al_v = v
        return al_h | al_v


class YTableView(QTableView):
    onLinkTo = Signal(str, str, QModelIndex)  # tag,column_name,index

    def __init__(self, model: PandasModel, parent=None,
                 display_columns: list[str] | tuple[str] | dict[str:Ct] = None,
                 hidden_columns: set[str] | list[str] | tuple[str] = None,
                 sortable=True):
        """
        表格View，如果未指定display_columns,按照model中的column_specs确定显示列的次序，并使用默认的size和alignment
        如果指定了display_columns，则按照display_columns显示。无论是否指定了display_columns，只要在hidden_columns中，则将对应列隐藏。
        :param model: 模型
        :param parent:
        :param display_columns:显示列，列名:CellStyle字典
        :param hidden_columns:隐藏列
        """
        super().__init__(parent=parent)
        self.setStyleSheet('gridline-color:palette(Midlight)')

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        if hidden_columns is None:
            hidden_columns = {}

        self._column_names = [cs.name for cs in model.column_specs() if cs.name not in hidden_columns]  # keys
        self.merged_columns = []
        cell_styles = {}

        if display_columns is not None:
            col_names = display_columns.keys() if isinstance(display_columns, dict) else display_columns
            cell_styles = display_columns if isinstance(display_columns, dict) else {}
            self._column_names = [cn for cn in col_names if cn not in hidden_columns]

        self.setModel(model)

        col_index = 0
        for col in self._column_names:
            if col in hidden_columns:
                continue
            col_spec = model.column_spec(col)
            delegate = create_column_delegate(self, col_spec, for_edit=model.isForEdit())
            if delegate:
                self.setItemDelegateForColumn(col_index, delegate)
            style = cell_styles.get(col)
            if style is None:  # 按照默认
                self.setColumnWidth(col_index, 100)
            else:
                self.setColumnWidth(col_index, style.width())
            col_index = col_index + 1

        # 鼠标单击即可唤起editor
        if model.isForEdit():
            self.setEditTriggers(QTableView.EditTrigger.CurrentChanged | QTableView.EditTrigger.SelectedClicked)
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        else:
            self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
            self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setMouseTracking(True)
        self.clicked.connect(self.on_cell_clicked)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # 设置点击表头排序
        if sortable:
            self.horizontalHeader().setSectionsClickable(True)
            self.horizontalHeader().setSortIndicatorShown(True)
            self.horizontalHeader().setSortIndicatorClearable(True)
            self.horizontalHeader().sectionClicked.connect(self.header_clicked)
        # self.hot_button = self.create_hot_button()
        # self.add_hot_button(self.hot_button)
        # self.resizeEvent = self.on_table_resize

    def setModel(self, model, /):
        model.set_display_columns(self._column_names)
        super().setModel(model)
        self.model().updateMergedCells(self.merged_columns)
        self._updateAllSpans()

    def setMergedColumns(self, columns):
        self.merged_columns = columns
        self.model().updateMergedCells(columns)
        self._updateAllSpans()

    def _updateAllSpans(self):
        model = self.model()
        if not model or not hasattr(model, 'span'):
            return
        # 先重置所有合并
        self.clearSpans()
        # 应用新的合并
        for (row, col), (row_span, col_span) in model._merged_cells.items():
            if row_span != 1 or col_span != 1:
                self.setSpan(row, col, row_span, col_span)

    def column_names(self):
        return self._column_names

    @staticmethod
    def cell_link_exp(index):
        link_to = index.data(Qt.ItemDataRole.ToolTipRole)  # 使用ToolTipRole传递link_to
        row_dat = index.data(Qt.ItemDataRole.UserRole)
        return format_obj(row_dat, link_to, use_repr=True) if link_to else None

    def on_cell_clicked(self, index: QModelIndex):
        if not index.isValid():
            return
        # 支持两种link_to机制，1.通过信号，2.link_to表达式
        link_to = index.data(Qt.ItemDataRole.ToolTipRole)  # 使用ToolTipRole传递link_to
        column_name = self.column_names()[index.column()]
        self.onLinkTo.emit(link_to, column_name, index)

        link_to_exp = self.cell_link_exp(index)
        if link_to_exp:
            call_exp(link_to_exp)

    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            link_to_exp = self.cell_link_exp(index)
            if link_to_exp:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                self.setToolTip(link_to_exp)
                return
        self.unsetCursor()
        self.setToolTip('')

    def set_columns_width(self, columns_width):
        if not columns_width:
            return
        d = columns_width if columns_width is dict else {i: c for i, c in enumerate(columns_width)}
        for c, w in d.items():
            c_idx = c if type(c) is int else self.column_names().index(c)
            if 0 <= c_idx < len(self.column_names()):
                self.setColumnWidth(c_idx, w)

    def header_clicked(self, col_index):
        order = self.model().sort_order(col_index)
        order = Qt.SortOrder.AscendingOrder if order else Qt.SortOrder.DescendingOrder
        self.sortByColumn(col_index, order)
        self.horizontalHeader().setSortIndicator(col_index, order)

    def export_data(self, file_format='excel'):
        fname = self.model.export(
            filename="%s_%s" % (self.windowTitle(),
                                datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')),
            file_format=file_format, select_file=True)
        if fname:
            pop_info('文件导出成功', fname)


def deduce_utype(spec):
    # 推断 unit_type
    for s in spec:
        FACTORY.deduce_unit_type(s)
    return spec


class YTableWidget(QWidget):
    onQuery = Signal(dict)
    onLinkTo = Signal(str, str, QModelIndex)  # tag,column_name,index

    def __init__(self, title,
                 parent=None,
                 model: PandasModel = None,
                 display_columns: list[str] | tuple[str] | dict[str:Ct] = None,
                 hidden_columns: set[str] | list[str] | tuple[str] = None,
                 merged_columns: set[str] | list[str] | tuple[str] = None,
                 fn_query: Callable = None,
                 fn_get_query_condition: Callable = None,
                 query_condition=None,
                 query_specs=None,
                 editable=False,
                 sortable=True,
                 summary: list = None,
                 query_form_layout=None,
                 query_form_orientation=Qt.Orientation.Vertical,
                 left_bar_visible=True,
                 right_bar_visible=True,
                 status_bar_visible=True,
                 title_alignment=Qt.AlignmentFlag.AlignLeft,
                 stat_count_only=False,
                 ):
        """

        :param title:
        :param parent:
        :param model: PandasModel模型
        :param display_columns: 显示列，默认全显示
        :param hidden_columns: 隐藏列
        :param fn_query: 查询函数，签名： fn_query(qc)->PandasModel
        :param query_condition: 查询参数的值，会被传递给 fn_query
        :param query_specs: 查询参数的规格，用于显示查询条件
        :param editable:
        :param summary:
        :param query_form_layout:
        :param query_form_orientation:
        """
        super().__init__(parent=parent)
        self.title = title
        self.fn_query = fn_query
        self.fn_get_query_condition = fn_get_query_condition
        self.qc = query_condition if query_condition else {}
        if self.fn_get_query_condition:
            self.qc = self.fn_get_query_condition(self.qc)
        self.query_spec = query_specs
        self._editable = editable
        self._sortable = sortable
        self._query_form_orientation = query_form_orientation
        self._query_form_layout = query_form_layout
        self.summary = summary
        self.display_columns = display_columns
        self.hidden_columns = hidden_columns
        self.merged_columns = merged_columns
        self.title_alignment = title_alignment
        self.stat_count_only = stat_count_only
        self.model = model
        if model is None:
            self.set_model(self.query_model())

        self.m_layout = create_layout(layout_flag='V')
        self.label_title = self.create_label_title()
        self.caption = f"{title}"
        self.label_caption = self.create_label_caption()
        self.splitter = QSplitter(self._query_form_orientation, parent=self)
        self.query_form = self.create_query_widget()

        self.view = YTableView(self.model, display_columns=display_columns, hidden_columns=hidden_columns,
                               sortable=self._sortable)
        if merged_columns:
            self.view.setMergedColumns(merged_columns)

        self._status_bar = self.create_status_bar()
        self.setup_ui()

        self.view.onLinkTo.connect(self.onLinkTo)
        self.set_left_bar_visible(left_bar_visible)
        self.set_right_bar_visible(right_bar_visible)
        self.set_status_bar_visible(status_bar_visible)

    def setup_ui(self):
        self.setLayout(self.m_layout)

        # 标题
        if self.title is not None:
            self.m_layout.addWidget(self.label_title, alignment=self.title_alignment)

        # 工具栏
        tbox = create_layout(layout_flag='H')
        tbox.setObjectName("toolbar_box")

        tbox.addWidget(self.create_toolbar_left())
        tbox.addStretch(0)
        tbox.addWidget(self.create_toolbar_right())
        self.m_layout.addLayout(tbox)

        # 主区域
        # 查询条件，表格
        if not self.query_form:  # 无查询条件
            self.m_layout.addWidget(self.view, 1)
        else:
            if self._query_form_orientation == Qt.Orientation.Horizontal:  # 水平
                self.splitter.addWidget(self.query_form)
                self.splitter.addWidget(self.view)
                self.splitter.setStretchFactor(0, 2)  # 条件栏分割因子
                self.splitter.setStretchFactor(1, 5)  # 列表栏分割因子
                self.m_layout.addWidget(self.splitter, 1)
            else:  # 垂直布局
                self.m_layout.addWidget(self.query_form)
                self.m_layout.addWidget(self.view, 1)

        # 状态栏
        self.m_layout.addWidget(self._status_bar)
        self.refresh_status()

    def create_query_widget(self):
        if not self.query_spec:
            return None
        if self._query_form_layout:  # 明确指定了布局
            layout_flag = self._query_form_layout
        else:
            layout_flag = 'F' if self._query_form_orientation == Qt.Orientation.Horizontal else 'G4'
        q_spec = self.query_spec if isinstance(self.query_spec, dict) else {'查询条件': self.query_spec}
        # print('create_query_widget... query_form_layout=', layout_flag)
        w = YQueryForm(parent=self, page_def=TabSetting(*q_spec.keys()), layout_flag=layout_flag, auto_from=self.qc)
        for page_index, items in enumerate(q_spec.values()):
            w.add_criteria(items, page_index)

        w.layout().setContentsMargins(8, 0, 8, 0)

        if self._query_form_orientation == Qt.Orientation.Horizontal:
            w.layout().addStretch(0)
            w.layout().setSpacing(12)
        return w

    def create_label_title(self):
        lb = QLabel(self.title)
        change_font(lb, bold=True, size=10)
        lb.setObjectName('label_title')
        return lb

    def create_label_caption(self):
        lb = QLabel(self.caption)
        change_font(lb, bold=True, size=12)
        lb.setObjectName('label_caption')
        return lb

    def create_status_bar(self):
        w = create_layout_widget(QFrame, parent=self, layout_flag='H')
        w.layout().addWidget(QLabel(''))
        w.setObjectName('status_bar')
        return w

    def create_toolbar_right(self):
        more_menu = QMenu('...', self)

        action = create_action('自动列宽', self.resize_header, icon_file=img.P_FIT_WIDTH, parent=self, )
        action.setShortcut("Ctrl+W")
        more_menu.addAction(action)

        action = create_action('行选/格选', self.toggle_selection_behavior, icon_file=img.P_ARROW_CURSOR, parent=self, )
        action.setShortcut("Ctrl+R")
        more_menu.addAction(action)

        action = create_action('复制所选', self.copy_selected_cells, icon_file=img.P_SHOW_NORMAL, parent=self, )
        action.setShortcut("Ctrl+C")
        more_menu.addAction(action)

        more_menu.addSeparator()

        more_menu.addActions([
            create_action('导出 Excel', lambda: self.export_data('excel'), icon_file=img.P_GRID_1, parent=self, ),
            create_action('导出 Html', lambda: self.export_data('html'), icon_file=img.P_HTML, parent=self, ),
            create_action('导出 CSV', lambda: self.export_data('csv'), icon_file=img.P_TODO, parent=self, ),
            create_action('导出 Markdown', lambda: self.export_data('markdown'), icon_file=img.P_DOC, parent=self, ),
        ])
        buttons = [
            create_tool_button('刷新',
                               trigger=self.load_data,
                               flat=True,
                               parent=self,
                               icon_file=img.P_REFRESH,
                               object_name='btn_refresh', ),
            create_tool_button('统计',
                               trigger=self.stat_model,
                               parent=self,
                               flat=True,
                               icon_file=img.P_CHART_LINEBAR,
                               object_name='btn_stat'),
            create_menu_button(more_menu,
                               title='更多...',
                               icon_file=img.P_3DOTS_V,
                               tool_button=True,
                               hovered=False),
        ]
        tbar = create_toolbar(buttons, parent=self, icon_size=16, object_name='toolbar_right')
        tbar.layout().setSpacing(2)
        return tbar

    def create_toolbar_left(self):
        buttons = [
            create_tool_button(parent=self,
                               trigger=self.toggle_query,
                               text='查询条件',
                               icon=load_icon(img.P_3DOTS_V),
                               object_name='toggle_query_btn'),
        ]
        tbar = create_toolbar(buttons, icon_size=20, parent=self, object_name='toolbar_left')
        return tbar

    def is_editable(self):
        return self._editable

    def resize_header(self):
        header = self.view.horizontalHeader()
        model = self.view.model()
        fm = self.view.fontMetrics()

        for col in range(model.columnCount()):
            max_width = 0
            # 检查表头宽度
            header_text = model.headerData(col, Qt.Orientation.Horizontal)
            header_width = fm.boundingRect(header_text).width() + 20  # 加边距
            max_width = max(max_width, header_width)

            # 只检查可见行（大幅减少计算量）
            for row in range(self.view.verticalHeader().count()):
                if not self.view.isRowHidden(row):
                    index = model.index(row, col)
                    text = model.data(index, Qt.ItemDataRole.DisplayRole) or ""
                    text_width = fm.boundingRect(text).width() + 20  # 加边距
                    if text_width > max_width:
                        max_width = text_width

            header.resizeSection(col, min(max_width, 500))  # 限制最大宽度

    def copy_selected_cells(self):
        selected_indexes = self.view.selectedIndexes()
        if len(selected_indexes) < 1:
            return
        clipboard_data = ''
        prev_row = -1
        for index in selected_indexes:
            row, column = index.row(), index.column()
            if row != prev_row and prev_row != -1:
                clipboard_data = clipboard_data.rstrip('\t') + '\n'
            clipboard_data += f"{index.data(Qt.ItemDataRole.DisplayRole)}\t"
            prev_row = row
        # 将所选数据复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data.rstrip('\t'))

    def toggle_selection_behavior(self):
        if QAbstractItemView.SelectionBehavior.SelectItems == self.view.selectionBehavior():
            self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        else:
            self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

    def set_query_form_visible(self, visible=True):
        if self.query_form is None:
            return
        self.query_form.setVisible(visible)
        icon_file = img.P_3DOTS_V if self.query_form.isVisible() else img.P_3DOTS_H
        tooltip = '隐藏查询条件' if self.query_form.isVisible() else '显示查询条件'
        btn = self.findChild(QToolButton, 'toggle_query_btn')
        if btn:
            btn.setIcon(load_icon(icon_file))
            btn.setToolTip(tooltip)

    def toggle_query(self):
        if not self.query_form:  # 没有查询条件表单，直接返回
            return
        self.set_query_form_visible(not self.query_form.isVisible())

    def query_model(self):
        if self.fn_query:
            m = self.fn_query(self.qc)
            return m
        return None

    def set_model(self, value):
        if get_attr(self, 'model'):
            self.model.beginResetModel()
        self.model = value
        if self.model is None:
            return
        self.model.setForEdit(self._editable)
        if get_attr(self, 'view'):
            self.view.setModel(self.model)
        self.model.endResetModel()

    def stat_model(self):
        def create_stat_widget():
            stats_widget = YStatWidget(count_only=self.stat_count_only)
            if self.title:
                stats_widget.setWindowTitle(f"{self.title}-统计")
            else:
                stats_widget.setWindowTitle(f"统计")
            stats_widget.filterModel.connect(show_filter_model)
            stats_widget.set_model(self.model, value_columns=self.summary)
            return stats_widget

        def show_filter_model(model, text):
            new_wdg = YTableWidget(f"{self.title}({text})",
                                   model=model,
                                   display_columns=self.display_columns,
                                   hidden_columns=self.hidden_columns,
                                   summary=self.summary,
                                   merged_columns=self.merged_columns,
                                   left_bar_visible=False,
                                   stat_count_only=self.stat_count_only,
                                   )
            new_wdg.setWindowTitle(self.title if self.title else f'{text}统计详情')
            columns_width = [self.view.columnWidth(i) for i in range(self.view.horizontalHeader().count())]
            new_wdg.set_columns_width(columns_width)
            show_widget(new_wdg)

        if self.model is None:
            return
        show_widget(create_stat_widget())

    def load_data(self):
        if self.query_form:
            self.query_form.assign_to(self.qc)
        if self.fn_get_query_condition:
            self.qc = self.fn_get_query_condition(self.qc)
        self.set_model(self.query_model())
        set_attr(self, 'stat_widget', None)
        self.refresh_status()
        self.onQuery.emit(self.qc)

    def export_data(self, file_format='excel'):
        fname = self.model.export(
            filename="%s_%s" % (self.title, datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')),
            file_format=file_format, select_file=True)
        if fname:
            pop_info('文件导出成功', fname)

    def status_message(self, text):
        status_bar = self._status_bar
        if not hasattr(status_bar, '_message'):
            status_bar._message = create_button(text=text, icon=load_icon(img.P_BULLET3), flat=True)
            self._status_bar.layout().addWidget(status_bar._message)
        status_bar._message.setText(text)

    def status_sum(self, sum_dict):
        status_bar = self._status_bar
        if not hasattr(status_bar, '_sum'):
            status_bar._sum = dict()
            for col_name, value in sum_dict.items():
                label = self.model.column_spec(col_name).title
                span = create_layout(layout_flag='H')
                span.setContentsMargins(2, 2, 2, 2)
                lb = create_button(text=f"{label}合计:", icon=load_icon(img.P_SUM), flat=True)
                txt = QLineEdit(f"{value:,.2f}")
                txt.setAlignment(Qt.AlignmentFlag.AlignRight)
                txt.setReadOnly(True)
                txt.setObjectName(f"{col_name}_sum")
                span.addWidget(lb)
                span.addWidget(txt)
                status_bar.layout().addStretch(0)
                status_bar.layout().addLayout(span)
                status_bar._sum[col_name] = txt
        else:
            for col_name, value in sum_dict.items():
                status_bar._sum[col_name].setText(f"{value:,.2f}")

    def set_buttons_styles(self):
        btn_style = Qt.ToolButtonStyle.ToolButtonIconOnly if self.width() < 600 else Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        for obj_name in ('btn_refresh', 'btn_stat'):
            self.findChild(QToolButton, obj_name).setToolButtonStyle(btn_style)

    def refresh_status(self):
        if self.model is None:
            return
        self.status_message(f"共 {self.model.rowCount()} 条记录")
        if self.summary:  # 指定了合计栏
            self.status_sum({sc: self.model.summary(sc) for sc in self.summary})
        else:
            self._status_bar.layout().addStretch(0)  # 占位，否则无合计时消息栏位置靠右
        self.set_buttons_styles()

    def toolbar_left(self):
        return self.findChild(QToolBar, 'toolbar_left')

    def toolbar_right(self):
        return self.findChild(QToolBar, 'toolbar_right')

    def toolbar_box(self):
        return self.findChild(QHBoxLayout, 'toolbar_box')

    def status_bar(self):
        return self.findChild(QFrame, 'status_bar')

    def set_left_bar_visible(self, value: bool):
        self.toolbar_left().setVisible(value)

    def set_right_bar_visible(self, value: bool):
        self.toolbar_right().setVisible(value)

    def set_status_bar_visible(self, value: bool):
        self.status_bar().setVisible(value)

    def set_columns_width(self, columns_width):
        self.view.set_columns_width(columns_width)
