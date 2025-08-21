# -*- yform.py: python ; coding: utf-8 -*-
#####################################################
# 表单式输入组件库
#####################################################
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout, QGroupBox

from .wdg import (TabSetting, TabInfo, YStackedPages, YTitle)
from .yfield import FACTORY, YFieldWidget, YFdCriteria
from .ymodel import PandasModel
from yut import format_obj
from . import EditMode, Stage, create_button, create_toolbar
from . import create_layout


############################################################
# 单笔数据录入/显示表单
############################################################
class YForm(QWidget):
    def __init__(self,
                 model: PandasModel = None,
                 column_specs=None,
                 title='标题未命名',
                 parent=None,
                 caption=None,
                 read_only=False,
                 edit_mode: EditMode = EditMode.MODIFY,
                 page_def: TabSetting = None,
                 layout_flag='V',
                 ):
        super().__init__(parent=parent)
        self.column_specs = column_specs
        self.caption = caption
        self.edit_mode = edit_mode
        self.read_only = read_only
        self.field_editors = []
        self.model = model
        self._data = {}
        if self.model:
            self.column_specs = model.column_specs()
            self._data = self.model.data_of_current_row()

        if not page_def:
            page_def = TabSetting(TabInfo('详细内容', layout_flag='F'))

        self.title = format_obj(self._data, title) if title else ''

        self.pages_widget = YStackedPages(page_def, parent=self)

        self.label_title = self.create_label_title()
        self.label_caption = self.create_label_caption()
        self.setWindowTitle(self.title)
        self.setLayout(create_layout(layout_flag))
        self.setup_ui()

    def refresh_display(self):
        # set caption
        if self.caption:
            self.label_caption.set_text(format_obj(self._data, self.caption))

    def setup_ui(self):
        m_layout = self.layout()
        # m_layout.setContentsMargins(12, 20, 12, 20)
        # 标题
        m_layout.addWidget(self.label_title)

        # 顶部标题和工具栏
        m_layout.addLayout(self.create_top_bar())

        # 页签组件
        m_layout.addWidget(self.pages_widget)

        # 更新绑定数据
        self.refresh_display()

    def clean(self):
        self.field_editors.clear()
        self.model = None

    def create_top_bar(self):
        tbox = create_layout('H')
        tbox.setContentsMargins(0, 8, 0, 16)
        tbox.addWidget(self.label_caption)
        tbox.addStretch(0)
        if not self.read_only:
            tbox.addWidget(self.create_toolbar())
        return tbox

    def add_editors(self, editors, page_index=None, stretch=True):
        layout = self.pages_widget.page_layout(page_index)
        for fd in editors:
            fd.bind(self._data)
            fd.add_to(layout)
        if hasattr(layout, "addStretch") and stretch:
            layout.addStretch(0)

    def add_fields(self, field_names: list, page_index=None, stretch=True):
        if self.read_only:  # 只读显示，使用只读部件
            items = [YFieldWidget(parent=self, col_spec=self.model.column_spec(fd)) for fd in field_names]
        else:
            items = [FACTORY.get_editor(self, self.model.column_spec(fd),
                                        stage=Stage.IN_FORM,
                                        read_only=False, )
                     for fd in field_names]
        self.add_editors(items, page_index, stretch)
        self.field_editors.extend(items)

    def build_default_fields(self):
        """
        按照默认内容添加字段控件。不分页签，将全部默认field加入其中
        :return:
        """
        self.add_fields([cp.name for cp in self.column_specs])

    def update_data(self):
        self.update_data_to(self.model.current_row_number())

    def update_data_to(self, row):
        self.model.set_current_row_number(row)
        self._data = self.model.data_of_current_row()
        for item in self.field_editors:
            item.bind(self._data)
        self.refresh_display()

    def data(self):
        for item in self.field_editors:
            item.assign_to(self._data)
        return self._data

    def create_label_title(self):
        return YTitle(self.title, parent=self, font_size=12, font_bold=True, icon_path=None)

    def create_label_caption(self):
        return YTitle(self.caption, parent=self, font_size=10, font_bold=True)

    def create_toolbar(self):
        buttons = [
            create_button('刷新',
                          trigger=self.load_data,
                          flat=True,
                          icon_file='refresh.png'),
            create_button('保存',
                          trigger=self.save_data,
                          tip_text='保存当前数据',
                          flat=True,
                          icon_file='save.png'),
        ]
        if self.edit_mode == EditMode.MODIFY:  # 修改模式，增加删除按钮
            buttons.append(create_button('删除',
                                         trigger=self.remove_data,
                                         tip_text='删除当前数据',
                                         flat=True,
                                         icon_file='cancel.png'))
        tbar = create_toolbar(buttons)
        return tbar

    def load_data(self):
        print(f'<YForm.load_data>  ...')

    def save_data(self):
        print(f'<YForm.save_data> saving ui data  ...', self._data)

    def remove_data(self):
        print(f'<YForm.remove_data> removing data  ...')


################################################################
# 查询条件表单
################################################################
class YQueryForm(QGroupBox):
    def __init__(self, parent=None, layout_flag='V', page_def: TabSetting = None, auto_from=None):
        super().__init__(parent)
        # 不要显示groupbox的顶部标题
        self.setObjectName('_query_form')
        self.setTitle("")
        self.setStyleSheet("#_query_form { margin-top: 0px; }")  # 减少顶部边距
        self.layout_flag = layout_flag
        if not page_def:
            page_def = TabSetting(TabInfo('查询条件', layout_flag=self.layout_flag))
        self.widget = YStackedPages(page_def, parent=self)
        self.items = []
        self.auto_from = auto_from
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.widget)

    def add_criteria(self, items: list[YFdCriteria], page_index=None):
        layout: QLayout = self.widget.page_layout(page_index)
        for item in items:
            if self.auto_from:
                item.assign_from(self.auto_from)
            item.add_to(layout)
            self.items.append(item)
        if hasattr(layout, 'addStretch'):
            layout.addStretch(0)

    def assign_from(self, value):
        for item in self.items:
            item.assign_from(value)

    def assign_to(self, value):
        for item in self.items:
            item.assign_to(value)
        return value

    def values(self):
        return self.assign_to(dict())
