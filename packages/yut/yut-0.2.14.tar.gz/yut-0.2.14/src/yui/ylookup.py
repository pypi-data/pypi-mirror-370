# -*- ylookup.py: python ; coding: utf-8 -*-
#####################################################
# 数据检索/选择部件
#####################################################
from abc import abstractmethod

from PySide6.QtCore import Qt, QObject, QSize
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGroupBox, \
    QStackedWidget, QFrame, QListWidget, QTableWidget, QTreeWidget, QListView, QTableWidgetItem, QHeaderView, \
    QAbstractItemView, QTableView, QListWidgetItem, QTreeView, QTreeWidgetItem

from .ymodel import translate_olist
from yut import format_obj, copy_obj, get_attr, Obj
from . import LookupViewType, load_icon, create_tool_button, create_button, create_toolbar, change_font, \
    TranslateDirection, img


class YViewBuilder(QObject):
    def __init__(self, headers: dict, loader=None, translator=None, item_icon_file=None, leaf_icon_file=None):
        super().__init__()
        self._headers = headers
        self.loader = loader
        self.translator = translator
        self.item_icon = load_icon(item_icon_file) if item_icon_file else load_icon(img.P_LABEL)
        self.leaf_icon = load_icon(leaf_icon_file) if leaf_icon_file else load_icon(img.P_BULLET3)

    def create_view(self, view_type: LookupViewType, parent: QWidget, multi_selection, accept):
        if view_type == LookupViewType.List:
            view = QListWidget(parent=parent)
            view.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection if multi_selection else QAbstractItemView.SelectionMode.SingleSelection)
            if accept:
                view.doubleClicked.connect(accept)  # 双击视同点击【确定】按钮
        elif view_type == LookupViewType.Table:
            view = QTableWidget(parent=parent)
            view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # 行选择
            view.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection if multi_selection else QAbstractItemView.SelectionMode.SingleSelection)
            view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # 没有EditTrigger时只读
            if accept:
                view.doubleClicked.connect(accept)  # 双击视同点击【确定】按钮
            # view.setStyleSheet('gridline-color:palette(Midlight)')
        elif view_type == LookupViewType.Tree:
            view = QTreeWidget(parent=parent)
            view.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection if multi_selection else QAbstractItemView.SelectionMode.SingleSelection)
            view.setUniformRowHeights(True)
        else:
            view = None
        if view and multi_selection:
            view.setToolTip('按住Ctrl键点击鼠标可以多选, 按住Shift键点击鼠标可连选')
        return view

    def set_view_headers(self, view):
        if isinstance(view, QListView):  # ListView只有一列，不设置表头
            return
        if isinstance(view, QTableView):
            view.setColumnCount(len(self._headers.keys()))
            # 设置表头
            view.setHorizontalHeaderLabels(self._headers.keys())
            view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
            view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            # view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            return
        if isinstance(view, QTreeView):
            labels = []
            labels.extend(self._headers.keys())
            # labels.append('')
            view.setHeaderLabels(labels)
            view.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
            return

    def load_view(self, view, query_condition):
        def set_item(item, obj, exp, col_index=0):
            item.setData(Qt.ItemDataRole.UserRole, obj)
            item.setData(Qt.ItemDataRole.DisplayRole, format_obj(obj, exp))
            if col_index == 0:
                item.setIcon(self.item_icon)
            return item

        view.clear()
        if self.loader is None:
            return
        olist = self.loader(query_condition)
        if isinstance(view, QListView):
            exp = list(self._headers.values())[0]
            for rec in olist:
                view.addItem(set_item(QListWidgetItem(), rec, exp, 0))
        if isinstance(view, QTableView):
            self.set_view_headers(view)
            view.setRowCount(len(olist))
            for i, rec in enumerate(olist):
                for j, exp in enumerate(self._headers.values()):
                    view.setItem(i, j, set_item(QTableWidgetItem(), rec, exp, j))
            view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            view.horizontalHeader().setStretchLastSection(True)
            view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        if isinstance(view, QTreeView):
            self.set_view_headers(view)
            self.add_tree(view, parent_item=None, olist=olist)
            view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        return olist

    def add_tree(self, view, parent_item, olist):
        for obj in olist:
            o_sons = self.loader(obj)  # 直接下级节点
            item = QTreeWidgetItem(parent_item) if parent_item else QTreeWidgetItem(view)
            # 设置各列显示
            for col, exp in enumerate(self._headers.values()):
                item.setData(col, Qt.ItemDataRole.DisplayRole, format_obj(obj, exp))
            # 绑定数据对象到0列
            item.setData(0, Qt.ItemDataRole.UserRole, obj)
            item.setSizeHint(0, QSize(200, 28))
            # 根据是否有子节点设置item
            if o_sons:  # 有子节点
                item.setIcon(0, self.item_icon)
                # 将下级节点递归加入到tree中
                self.add_tree(view, item, o_sons)
            else:
                item.setIcon(0, self.leaf_icon)
            item.setExpanded(item.parent() is None)  # 仅展开根节点

    def get_selected(self, view):
        if isinstance(view, QTableView):
            selected_rows = {idx.row() for idx in view.selectedIndexes()}
            return [view.item(r, 0).data(Qt.ItemDataRole.UserRole) for r in selected_rows]
        if isinstance(view, QListView):
            return [item.data(Qt.ItemDataRole.UserRole) for item in view.selectedItems()]
        if isinstance(view, QTreeView):
            return [item.data(0, Qt.ItemDataRole.UserRole) for item in view.selectedItems()]


class YLookupDialog(QDialog):
    def __init__(self, view_type: LookupViewType = LookupViewType.Table, view_builder: YViewBuilder = None, parent=None,
                 title='选择列表', multi_selection=False):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.view_type = view_type
        self.title = title
        self.view_builder = view_builder
        self.multi_selection = multi_selection
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_content())
        self.label_title = self.create_label_title()
        self.label_caption = self.create_label_caption()
        self.olist = []
        self.setWindowTitle('数据查找对话框')
        self.setWindowIcon(load_icon(img.P_LOOKUP))
        self.setStyleSheet('background-color:#202020')
        self.setMinimumWidth(1024)
        self.setMinimumHeight(760)
        if self.view_type == LookupViewType.Table:  # 创建查询条件widget和展开按钮
            self.qc_widget = self.create_qc()
            self.qc_btn = create_tool_button(
                trigger=lambda: self.show_qc(not self.qc_widget.isVisible()),
                icon_file=img.P_VV_DOWN, )
        else:
            self.qc_widget = None
            self.qc_btn = None
        self.view_widget = self.view_builder.create_view(self.view_type, parent=self,
                                                         multi_selection=self.multi_selection, accept=self.accept)
        self.setup_ui()
        self.do_query()

    def create_content(self):
        content = QFrame(parent=self)
        content.setLayout(QVBoxLayout())
        content.setFrameShape(QFrame.Shape.StyledPanel)
        return content

    def setup_ui(self):

        # 工具栏
        tbox = QHBoxLayout()
        tbox.setContentsMargins(0, 8, 0, 16)
        # -- 查询条件展示/关闭按钮
        if self.view_type in [LookupViewType.Table]:
            tbox.addWidget(self.qc_btn)
        tbox.addWidget(self.label_caption)
        tbox.addStretch(0)
        tbox.addWidget(self.create_toolbar())

        hbox = QHBoxLayout()
        if self.view_type in [LookupViewType.Table]:
            hbox.addWidget(self.qc_widget)  # 查询条件
        hbox.addWidget(self.view_widget)  # 列表

        self.pages.currentWidget().layout().addLayout(tbox)
        self.pages.currentWidget().layout().addLayout(hbox)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.pages)
        # 设置列表内容显示
        self.setup_view()

    def setup_view(self):
        if self.view_builder is None:
            return
        self.view_builder.set_view_headers(self.view_widget)

    def create_qc(self):
        w = QWidget()
        w.setLayout(QVBoxLayout())
        # 查询工具条
        tbar = create_toolbar([create_button('重置',
                                             trigger=self.reset_qc,
                                             flat=True,
                                             icon_file=img.P_LOOP),
                               create_button('查询',
                                             trigger=self.do_query,
                                             flat=True,
                                             icon_file=img.P_LIGHTNING),
                               ])
        w.layout().addWidget(tbar)
        # 查询条件内容
        w.layout().addWidget(QGroupBox("查询条件"))
        # 默认不显示
        w.setVisible(False)
        return w

    def create_toolbar(self):
        buttons = [
            create_button('取消',
                          trigger=self.reject,
                          flat=True,
                          icon_file=img.P_CANCEL),
            create_button('确定',
                          trigger=self.accept,
                          tip_text='确定当前选择内容',
                          flat=True,
                          icon_file=img.P_CHECK),
        ]
        tbar = create_toolbar(buttons)
        return tbar

    def create_label_title(self):
        lb = QLabel(self.title)
        change_font(lb, bold=True, size=10)
        return lb

    def create_label_caption(self):
        tle = self.title
        if self.multi_selection:
            tle = tle + '[多选]'
        lb = QLabel(tle)
        change_font(lb, bold=True, size=12)
        return lb

    def do_query(self):
        print('<YLookupDialog> do query ...')
        if self.view_builder:
            qc = Obj()
            self.olist = self.view_builder.load_view(self.view_widget, qc)
        self.show_qc(False)

    def get_olist(self):
        return self.olist

    def reset_qc(self):
        print('reset query condition ...')

    def show_qc(self, visible: bool):
        if self.qc_widget:
            self.qc_widget.setVisible(visible)
            self.qc_btn.setChecked(self.qc_widget.isVisible())

    def selected(self):
        selection = self.view_builder.get_selected(self.view_widget)
        if self.multi_selection:
            return selection
        else:
            if len(selection) > 0:
                return selection[0]
            else:
                return None

    def is_multi_selection(self):
        return self.multi_selection

    def showEvent(self, event):
        super().showEvent(event)
        if self.view_widget:
            self.view_widget.clearSelection()


class YLookup(QObject):
    def __init__(self, **kwargs):
        super().__init__()
        copy_obj(self, kwargs)
        self.multi_value = get_attr(self, 'multi_value', False)
        self._dialog = None
        self.dialog_field_value = ''
        self.dialog_field_text = ''

    def get_dialog(self) -> YLookupDialog:
        if self._dialog is None:
            self._dialog = self.create_dialog()
        return self._dialog

    def execute_lookup(self):
        lookup_value, lookup_text = None, None
        dialog = self.get_dialog()
        value_exp, text_exp = self.dialog_lookup_field()
        ret = dialog.exec()
        if ret > 0:
            selected = dialog.selected()
            if dialog.is_multi_selection():  # 多选
                lookup_value = [format_obj(r, value_exp) for r in selected]
                lookup_text = ','.join([format_obj(r, text_exp) for r in selected])
            else:
                lookup_value = format_obj(selected, value_exp)
                lookup_text = format_obj(selected, text_exp)
        return ret, lookup_value, lookup_text

    @abstractmethod
    def create_dialog(self) -> YLookupDialog:
        return None

    @abstractmethod
    def dialog_lookup_field(self):
        return self.dialog_field_value, self.dialog_field_text

    def to_text(self, value):
        # 列表方式选择可以直接从Dialog中取olist，如果是树形选择，dialog的olist仅包含顶层节点，必须在字类中覆盖本方法另行实现
        olist = self.get_dialog().get_olist()
        return translate_olist(TranslateDirection.TO_TEXT, self.dialog_lookup_field(), value, olist)

    def to_value(self, text):
        # 列表方式选择可以直接从Dialog中取olist，如果是树形选择，dialog的olist仅包含顶层节点，必须在字类中覆盖本方法另行实现
        olist = self.get_dialog().get_olist()
        return translate_olist(TranslateDirection.TO_VALUE, self.dialog_lookup_field(), text, olist)
