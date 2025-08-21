# -*- yfield.py: python ; coding: utf-8 -*-
#####################################################
# 字段及其控制器
#####################################################
import datetime
import re
from abc import abstractmethod

import pandas as pd
from PySide6.QtCore import Qt, QDate, Signal, QObject, QTime, QDateTime, QRect
from PySide6.QtGui import QDoubleValidator, QColor, QPainter, QBrush, QPalette
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QLayout, \
    QSpinBox, QDateEdit, QLabel, QComboBox, QButtonGroup, QRadioButton, QCheckBox, QDateTimeEdit, \
    QStyledItemDelegate, QTableView, QSizePolicy, QTextEdit, QGroupBox, QVBoxLayout, QTreeView
from pandas import Timestamp

from yus import ColumnSpec, Op, UnitType, ChooseMode, DisplayAttitude
from yut import to_float, to_date, to_datetime, is_execute_able, format_date, has_attr, get_attr, \
    set_attr, format_datetime, o2d, is_collection, copy_obj, create_instance
from . import Stage, WorkMode, add_to_layout, img, current_theme, alignment_flag
from . import add_field, create_layout_widget, create_layout, clear_layout, set_label_color, load_icon, create_button
from .wdg import YearMonthSpin
from .ydict import DictFetcher


class YFieldWidget(QTextEdit):
    """
    数据字段只读显示组件
    """

    def __init__(self, parent, col_spec: ColumnSpec, value=None, bind_obj=None):
        super().__init__(parent=parent)
        self.factory = FACTORY
        self.col_spec = col_spec
        copy_obj(self, self.col_spec)
        self._value = value
        self._bind_obj = bind_obj
        self._text = str(self._value) if self._value else ''
        self._field_painter = self.factory.get_painter(self.col_spec)
        if self._bind_obj:
            self.bind(self._bind_obj)
        self.setup_ui()

    def setup_ui(self):
        self.setReadOnly(True)
        font = self.font()
        color = get_attr(self, 'color', None)
        if color:
            self.setTextColor(color)
        font_size = get_attr(self.col_spec, 'font_size', None)
        if font_size:
            font.setPointSize(font_size)
            self.setFont(font)
        font_bold = get_attr(self.col_spec, 'font_bold', None)
        if font_bold:
            font.setBold(font_bold)
            self.setFont(font)
        height = get_attr(self.col_spec, 'height', None)
        if self.col_spec.utype != UnitType.RICH_TEXT:
            self.setFixedHeight(self.fontMetrics().height() + 12)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        else:  # 长文本类型，尽可能大
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if height:
            self.setFixedHeight(height)  # self.fontMetrics().height())

    def field_alignment(self):
        spec = self.col_spec
        alignment = get_attr(spec, 'alignment')
        if alignment:  # 优先使用列规格中的对齐属性
            return alignment_flag(alignment)
        elif spec.utype in (UnitType.CURRENCY, UnitType.INT, UnitType.NUMBER):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        elif spec.utype in (UnitType.CHOOSE, UnitType.LOOKUP, UnitType.DATE):
            return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        elif spec.utype == UnitType.RICH_TEXT:
            return Qt.AlignmentFlag.AlignLeft
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

    def set_value(self, value):
        self._value = value
        self._text = self._field_painter.get_text(self._value, self._bind_obj)
        self.setUpdatesEnabled(False)
        self.setText(self._text)
        self.setUpdatesEnabled(True)

    def bind(self, obj):
        self._bind_obj = obj
        self.set_value(get_attr(self._bind_obj, self.col_spec.name))

    def add_to(self, layout):
        label = self.get_field_label() + ':'
        if isinstance(layout, QFormLayout):  # Form布局，label为widget部件，否则label为字符串
            add_field(layout, self, QLabel(label))
        else:
            add_field(layout, self, label)

    def get_field_label(self):
        # label 依次使用 title/comment/field属性
        label: str = get_attr(self, 'title', None)
        if label is None:
            label = get_attr(self, 'comment', None)
        if label is None:
            label = self.col_spec.name.upper()
        return label

    def setup_palette(self):
        spec = self.col_spec
        self.setAlignment(self.field_alignment())
        pl = self.palette()
        fp = self._field_painter
        if spec.is_link():  # 处理链接样式
            font = self.font()
            font.setUnderline(True)
            self.setFont(font)
            brush = self.palette().brush(QPalette.ColorRole.Link)
            pl.setColor(QPalette.ColorRole.Text, brush.color())
        elif hasattr(fp, 'get_color'):  # 调用fp的设置painter方法
            color = fp.get_color(self._value, self._text)
            if color:
                pl.setColor(QPalette.ColorRole.Text, color)
        self.setPalette(pl)

    def paintEvent(self, event):
        if self.col_spec.utype != UnitType.RICH_TEXT:  # 富文本不要调用setup_palette，否则会卡顿
            self.setup_palette()
        # 调用FieldPainter，自定义绘制
        if hasattr(self._field_painter, 'draw_field'):
            painter = QPainter(self.viewport())
            self._field_painter.draw_field(painter, self.rect(), self._value, self._text)
        else:
            super().paintEvent(event)


class YDisplayDelegate(QStyledItemDelegate):
    """
    只读显示列代理控制器。
    """
    MARGIN_LEFT = 4
    MARGIN_RIGHT = 4

    def __init__(self, view: QTableView | QTreeView, col_spec: ColumnSpec, **kwargs):
        super().__init__(parent=view)
        self.factory = FACTORY
        self.view = view
        self.col_spec = col_spec
        self.name = col_spec.name
        self.label = col_spec.title
        self.utype = self.factory.deduce_unit_type(col_spec=col_spec)  # UnitType(col_spec.unit_type())
        self.comment = col_spec.comment
        self.fv_kwargs = kwargs
        self._field_painter = self.factory.get_painter(self.col_spec, **self.fv_kwargs)

    def createEditor(self, parent, option, index):
        return QLineEdit(parent=parent)  # 也要返回一个QLineEdit，用于选中显示文字，复制粘贴

    def setEditorData(self, editor, index):
        model = index.model()
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setText(self._field_painter.get_text(value, model.data_of_row(index.row())))

    def setModelData(self, editor, model, index):
        pass  # 只读，不修改

    def setup_painter(self, painter, value, text):
        if hasattr(self._field_painter, 'setup_painter'):  # 调用fp的设置painter方法
            self._field_painter.setup_painter(painter, value, text)

    def setup_link_painter(self, painter):
        font = painter.font()
        font.setUnderline(True)
        painter.setFont(font)
        brush = self.view.palette().brush(QPalette.ColorRole.Link)
        painter.setFont(font)
        painter.setPen(brush.color())

    def paint(self, painter, option, index):
        model = index.model()
        fp = self._field_painter
        if model is None or not index.isValid():
            return
        value = model.data(index, Qt.ItemDataRole.EditRole)
        text = model.data(index, Qt.ItemDataRole.DisplayRole)
        link_to = model.data(index, Qt.ItemDataRole.ToolTipRole)
        painter.save()
        self.initStyleOption(option, index)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 设置painter
        if link_to:  # 处理链接样式
            self.setup_link_painter(painter)
        self.setup_painter(painter, value, text)
        # 调用FieldPainter，自定义绘制
        if hasattr(fp, 'draw_field'):
            fp.draw_field(painter, option.rect, value, text)
        elif text:  # 显示文本,None或空时不显示
            rect: QRect = option.rect.adjusted(self.MARGIN_LEFT, 0, 0 - self.MARGIN_RIGHT, 0)
            alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
            font = model.data(index, Qt.ItemDataRole.FontRole)
            fr_color = model.data(index, Qt.ItemDataRole.ForegroundRole)
            bg_color = model.data(index, Qt.ItemDataRole.BackgroundRole)
            if font:
                painter.setFont(font)
            if fr_color:
                painter.setPen(fr_color)
            if bg_color:
                painter.setBackground(bg_color)
            painter.drawText(rect, alignment, text)
        painter.restore()


class YEditorDelegate(YDisplayDelegate):
    """
    可编辑列代理控制器。
    """

    def createEditor(self, parent, option, index):
        field_editor = self.factory.get_editor(parent=parent,
                                               col_spec=self.col_spec,
                                               stage=Stage.IN_TABLE,
                                               **self.fv_kwargs)
        return field_editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        # print(f'[YField] - YEditorDelegate.setEditorData: {index.row(), index.column()} -> ', '%r' % value,
        #       f", editor = {editor}")
        if value is pd.NaT:
            value = None
        if value is not None:
            editor.set_value(value)

    def setModelData(self, editor, model, index):
        value = editor.get_value()
        # old_value = model.data(index, Qt.ItemDataRole.EditRole)
        # print('[YField] - YEditorDelegate.setModelData: %r' % value, f' -> {index.row(), index.column()}',
        #       ', old value = %r' % old_value)
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def paint(self, painter, option, index):
        if not self.view.indexWidget(index):  # 仅在没有活动的编辑器时调用父类的paint方法绘制默认文本显示内容。
            super().paint(painter, option, index)


#############################################################
# 字段编辑组件
#############################################################
class YFieldEditor(QWidget):
    """
    各种数据字段的录入/展示控制器
    适应一个model属性绑定多个element的场景。on_change -> 当前改动的内容传播到model，并更新所有element的显示内容
    需要创建一个信号，各Element值更改后发射此信号，form得到属性值后循环调用全部element的set_value
    """
    valueChanged = Signal(str)  # field

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        # 从初始化参数中解析属性
        copy_obj(self, kwargs)
        self.stage = get_attr(self, 'stage', Stage.IN_FORM)
        self.field: str = get_attr(self, 'field', None)
        if self.field is None:
            self.field = get_attr(self, 'name', None)
        # label 依次使用 label/comment/field属性
        self.label: str = get_attr(self, 'label', None)
        if self.label is None:
            self.label = get_attr(self, 'comment', None)
        if self.label is None:
            self.label = self.field.upper()
        self.desc = get_attr(self, 'desc')
        self.mandatory = get_attr(self, 'mandatory', False)
        self.read_only = get_attr(self, 'read_only', False)
        self.work_mode = get_attr(self, 'work_mode', WorkMode.EDIT)
        if self.label.startswith('*'):
            self.mandatory = True
            self.label = self.label[1:]
        # 准备内部属性
        self._binds = []
        self._label_widget = None
        # 初始化UI
        self.setLayout(create_layout('H'))
        self.layout().setContentsMargins(2, 0, 2, 0)
        # 设置初始值
        v = get_attr(self, 'value')
        if v is not None:
            self.set_value(v)

    def editor(self):
        # return self.findChild(QWidget, 'editor')
        return get_attr(self, '_editor')

    def tag_editor(self, editor: QWidget):
        # editor.setObjectName('editor')
        set_attr(self, '_editor', editor)

    def label_widget(self):
        if self._label_widget is None:
            self._label_widget = self.create_label_widget()
            self._label_widget.field_view = self
        return self._label_widget

    def bind(self, o, attr=None, only_has_attr=False):
        o_attr = attr if attr else self.field
        self._binds.append([o, o_attr, only_has_attr])
        if has_attr(o, o_attr):
            self.set_value(get_attr(o, o_attr))

    def unbind(self, o):
        for i in range(len(self._binds)):
            if o in self._binds[i]:
                self._binds.pop(i)

    def on_change(self):
        # 更新绑定对象的值
        v = self.get_value()
        for o, attr, only_has_attr in self._binds:
            if not only_has_attr or has_attr(o, attr):
                set_attr(o, attr, v)
        self.valueChanged.emit(self.field)

    def add_to(self, layout: QLayout, index: int = -1):
        """
        将控件加入到指定的布局中
        :param layout: 待加入的布局对象
        :return:
        """
        if isinstance(layout, QFormLayout):  # Form布局，label为widget部件，否则label为字符串
            add_field(layout, self, self.label_widget(), index)
        else:
            add_field(layout, self, f'* {self.label}' if self.mandatory else f'{self.label}', index)

    def create_label_widget(self) -> QWidget:
        w_label = create_layout_widget(QWidget, parent=self.parentWidget())
        if self.mandatory:
            mark = QLabel('*')
            set_label_color(mark, fore_color=current_theme.icon_color())
            w_label.layout().addWidget(mark, 0)
        w_label.layout().addWidget(QLabel(f"{self.label}:" if self.label else ""), 1)
        return w_label

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def get_value(self):
        return None


class YFdText(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.none_text = ''
        editor = QLineEdit(parent=self)
        editor.setReadOnly(self.read_only)
        # editor.setEnabled(not self.read_only)
        editor.setPlaceholderText(self.desc)
        editor.editingFinished.connect(self.on_change)
        self.layout().addWidget(editor)
        self.tag_editor(editor)

    def set_value(self, value):
        self.editor().setText(self.none_text if value is None else f'{value}')

    def get_value(self):
        return self.editor().text().strip()


class YFdRichText(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.none_text = ''
        self.text_format = get_attr(self, 'text_format', 'plain')

        editor = QTextEdit(parent=self)
        editor.setReadOnly(self.read_only)
        editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # editor.setEnabled(not self.read_only)
        editor.setPlaceholderText(self.desc)
        # editor.setStyleSheet("background-color: gray;")
        self.layout().addWidget(editor)
        self.tag_editor(editor)

    def set_value(self, value):
        self.editor().setHtml(self.none_text if value is None else f'{value}')

    def get_value(self):
        editor: QTextEdit = self.editor()
        if self.text_format == 'plain':
            return editor.toPlainText()
        elif self.text_format == 'markdown':
            return editor.toMarkdown()
        else:
            return editor.toHtml()


class YFdNumber(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.none_text = ''
        self._value = 0.00
        self.decimals = get_attr(self, 'decimals', 2)
        editor = NumberEdit(parent=self)
        editor.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        editor.setValidator(QDoubleValidator(decimals=self.decimals, parent=self))
        editor.setReadOnly(self.read_only)
        # editor.setEnabled(not self.read_only)
        editor.editingFinished.connect(self.edit_finished)
        self.layout().addWidget(editor)
        self.tag_editor(editor)
        self._disp_value()

    def set_value(self, value):
        self._value = to_float(value) if value is not None else 0.0
        self._disp_value()

    def get_value(self):
        self._value = to_float(self.editor().text())
        return self._value

    def edit_finished(self):
        self.get_value()  # 为了更新self._value
        self._disp_value()
        self.on_change()

    def _disp_value(self):
        self.editor().setText(f'{self._value:.2f}')


class YFdInt(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.min_value = get_attr(self, 'min_value', None)
        self.max_value = get_attr(self, 'max_value', None)
        editor = QSpinBox(parent=parent)
        editor.setRange(0, 2147483647)
        if self.min_value is not None:
            editor.setMinimum(self.min_value)
        if self.max_value is not None:
            editor.setMaximum(self.max_value)
        editor.setReadOnly(self.read_only)
        editor.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        # editor.setEnabled(not self.read_only)
        editor.setValue(0)
        editor.editingFinished.connect(self.on_change)
        self.layout().addWidget(editor)
        self.tag_editor(editor)

    def set_value(self, value):
        editor = self.editor()
        if value:
            editor.setValue(editor.valueFromText(f'{value}'))  # 整形、字符型、浮点型都可兼容

    def get_value(self):
        return self.editor().value()


class YFdSwitch(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.disp_text = get_attr(self, 'disp_text', ['[NO]', '[YES]'])
        editor = QCheckBox(parent=parent)
        editor.setEnabled(not self.read_only)
        editor.setText(self.disp_text[1])
        editor.setChecked(False)
        self.layout().addWidget(editor)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.tag_editor(editor)

    def set_value(self, value):
        value = to_float(value)
        editor = self.editor()
        editor.setChecked(value > 0.01)

    def get_value(self):
        return 1 if self.editor().isChecked() else 0


# 金额部件
class YFdCurrency(YFdNumber):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.decimals = 2

    def _disp_value(self):
        if self.stage in (Stage.IN_FORM, Stage.IN_QUERY):
            self.editor().setText(f'{self._value:,.2f}')  # 在Form/Query中，千分位
        else:
            self.editor().setText(f'{self._value:.2f}')  # 在表格中编辑，编辑组件不做千分位，外部的表格会通过get_text()千分位


class YFdYear(YFdInt):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.min_value = get_attr(self, 'min_value', 2000)
        self.max_value = get_attr(self, 'max_value', 2999)
        self.editor().setRange(2000, 2099)
        self.editor().valueChanged.connect(self.on_change)
        self.set_value(datetime.date.today().year)


class YFdYearMonth(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        editor = YearMonthSpin(datetime.date.today().year, datetime.date.today().month)
        editor.valueChanged.connect(self.on_change)
        self.tag_editor(editor)

    def set_value(self, value):
        if value is not None:
            self.editor().set_monthcode(value)

    def get_value(self):
        return self.editor().month_code()


class YFdDateTime(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.display_format = get_attr(self, 'display_format', 'yyyy-MM-dd HH:mm:ss.zzz (dddd)')
        self.calendar_popup = get_attr(self, 'calendar_popup', True)
        editor = QDateTimeEdit(QDateTime.currentDateTime(), parent=parent)
        editor.setDisplayFormat(self.display_format)
        editor.setReadOnly(self.read_only)
        # editor.setEnabled(not self.read_only)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setMaximumDate(QDate(2999, 12, 31))
        editor.setMinimumDate(QDate(1900, 1, 1))
        editor.setCalendarPopup(self.calendar_popup)
        editor.editingFinished.connect(self.on_change)
        self.layout().addWidget(editor)
        self.layout().addStretch(0)
        self.tag_editor(editor)

    def set_value(self, value):
        if value is None:
            return
        dt = to_datetime(value)
        self.editor.setDate(QDate(dt.year, dt.month, dt.day))
        self.editor.setTime(QTime(dt.hour, dt.minute, dt.second, dt.microsecond))

    def get_value(self):
        d = self.editor.dateTime()
        return format_datetime(d.toPython()) if d else None


class YFdDate(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        editor = QDateEdit(parent=parent)
        editor.setReadOnly(self.read_only)
        # editor.setEnabled(not self.read_only)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setMaximumDate(QDate(2999, 12, 31))
        editor.setMinimumDate(QDate(1900, 1, 1))
        editor.setCalendarPopup(True)
        today = datetime.date.today()
        editor.setDate(QDate(today.year, today.month, today.day))
        editor.editingFinished.connect(self.on_change)
        self.layout().addWidget(editor)
        self.layout().addStretch(0)
        self.tag_editor(editor)

    def set_value(self, value):
        if value is None:
            return
        date = to_date(value)
        self.editor().setDate(QDate(date.year, date.month, date.day))

    def get_value(self):
        d = self.editor().date()
        return format_date(d.toPython()) if d else None


class YFdChoose(YFieldEditor):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.code_dict = DictFetcher.instance().get_dict(self)
        if self.code_dict is None:
            self.code_dict = {}
        self.query_op = get_attr(self, 'op', Op.IN)
        self.mode = get_attr(self, 'mode', ChooseMode.LIST)
        self.format = get_attr(self, 'format', '[{code}] - {name}')
        # 如果是查询场景，mode自动设置为checkbox,布局根据可选项数量确定为'V'或'G2'
        if self.stage == Stage.IN_QUERY and self.query_op != Op.EQU:
            self.mode = ChooseMode.CHECK
            self.layout_flag = get_attr(self, 'layout_flag', 'V') if len(self.code_dict.keys()) < 6 else 'G2'
        else:
            self.layout_flag = get_attr(self, 'layout_flag', 'H')
        # 设置UI
        editor = self.create_editor(parent)
        self.layout().addWidget(editor)
        self.tag_editor(editor)

    def create_editor(self, parent) -> None | QWidget | QComboBox:
        if ChooseMode.LIST == self.mode:  # 使用 ComboBox
            editor = QComboBox(parent=parent)
            editor.setEditable(False)
            for code, name in self.code_dict.items():
                editor.addItem(load_icon(img.P_LABEL), eval(f'f"{self.format}"'), code)
            editor.currentIndexChanged.connect(self.on_change)
            editor.setEnabled(not self.read_only)
            return editor

        elif ChooseMode.RADIO == self.mode:  # 使用ButtonGroup -> RadioButton
            editor = create_layout_widget(QWidget, parent=parent, layout_flag=self.layout_flag)
            editor.button_group = QButtonGroup(parent=parent)
            for code, name in self.code_dict.items():
                btn = QRadioButton(eval(f'f"{self.format}"'))
                btn.data = code
                add_to_layout(editor.layout(), btn)
                editor.button_group.addButton(btn)
            editor.setEnabled(not self.read_only)
            editor.button_group.buttonClicked.connect(self.on_change)
            return editor

        elif ChooseMode.CHECK == self.mode:  # 使用GroupBox -> CheckBox
            editor = create_layout_widget(QWidget, parent=parent, layout_flag=self.layout_flag)
            for code, name in self.code_dict.items():
                btn = QCheckBox(eval(f'f"{self.format}"'))
                btn.data = code
                add_to_layout(editor.layout(), btn)
                btn.stateChanged.connect(self.on_change)
            editor.setEnabled(not self.read_only)
            return editor
        else:
            return None

    def set_value(self, value):
        if value is None:
            return
        editor = self.editor()
        if ChooseMode.LIST == self.mode:  # 使用 ComboBox
            for index in range(editor.count()):
                if str(value) == str(editor.itemData(index, Qt.ItemDataRole.UserRole)):
                    editor.setCurrentIndex(index)
        elif ChooseMode.RADIO == self.mode:  # 使用ButtonGroup -> RadioButton
            for btn in editor.button_group.buttons():
                btn.setChecked(str(value) == str(btn.data))
        elif ChooseMode.CHECK == self.mode:  # 使用GroupBox -> CheckBox
            for btn in editor.children():
                if hasattr(btn, 'data'):
                    btn.setChecked(str(btn.data) in [str(v) for v in value])

    def get_value(self):
        editor = self.editor()
        if ChooseMode.LIST == self.mode:  # 使用 ComboBox
            return editor.currentData(Qt.ItemDataRole.UserRole)
        elif ChooseMode.RADIO == self.mode:  # 使用ButtonGroup -> RadioButton
            choose = editor.button_group.checkedButton()
            if choose:
                return choose.data
        elif ChooseMode.CHECK == self.mode:  # 使用GroupBox -> CheckBox
            values = []
            grp = editor
            if hasattr(grp, 'check_all'):
                if grp.check_all.isChecked():
                    return None
            for chd in grp.children():
                if hasattr(chd, 'data'):
                    if chd.isChecked():
                        values.append(chd.data)
            return values
        return None


class YFdLookup(YFieldEditor):
    """
    弹框查选组件。
    组件由文本框+点选按钮构成。点选按钮可唤出弹框，并从候选列表中选取记录。候选列表支持查询，支持多选。
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.lookup_key = get_attr(self, 'lookup_key')
        self.lookup = FACTORY.get_lookup(**kwargs) if self.lookup_key else None
        self.lookup_value = None
        self.lookup_display = ''
        editor = QLineEdit(self.lookup_display, parent=parent)
        self.lookup_btn = create_button('',
                                        trigger=self.on_select,
                                        flat=False,
                                        tip_text='从弹出窗口选择',
                                        icon_file=img.P_3DOTS_H)
        self.lookup_btn.setEnabled(not self.read_only)
        self.layout().addWidget(editor)
        self.layout().addWidget(self.lookup_btn)
        self.tag_editor(editor)

    def on_select(self):
        # btn = self.sender()
        if self.lookup is None:
            return
        flag, value, text = self.lookup.execute_lookup()
        if flag > 0:  # 用户执行了选择
            self.lookup_value = value
            self.lookup_display = text
            self.editor().setText(self.lookup_display)

    def set_value(self, value):
        self.lookup_value = value
        self.lookup_display = f'{value}' if value is not None else ''
        if self.lookup:
            self.lookup_display = self.lookup.to_text(value)
        self.editor().setText(self.lookup_display)

    def get_value(self):
        return self.lookup_value


class NumberEdit(QLineEdit):
    def __init__(self, parent=None):
        super(NumberEdit, self).__init__(parent=parent)

    def focusInEvent(self, e):
        if hasattr(self, 'amount'):  # 不显示千分位
            self.setText(f"{self.amount:.2f}")
        self.selectAll()


#############################################################
# 字段显示组件
#############################################################

class YFieldPainter(QObject):
    def __init__(self, **kwargs):
        super().__init__(parent=None)
        copy_obj(self, kwargs)

    def setup_painter(self, painter, value, text):
        pass

    @abstractmethod
    def get_text(self, value, record):
        return f"{value}"

    @staticmethod
    def get_attitude_color(attitude: DisplayAttitude):
        return {
            DisplayAttitude.POSITIVE: QColor(0x00, 0xD0, 0xA0),
            DisplayAttitude.WEAK_POSITIVE: QColor(0x60, 0xD0, 0xD0),
            DisplayAttitude.NEUTRAL: QColor(Qt.GlobalColor.lightGray),
            DisplayAttitude.WEAK_NEGATIVE: QColor(0xD0, 0xA0, 0x60),
            DisplayAttitude.NEGATIVE: QColor(0xD0, 0x60, 0x60),
            DisplayAttitude.INACTIVE: QColor(Qt.GlobalColor.darkGray),
        }.get(attitude)

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class YFpText(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        color_match: dict = get_attr(self, 'color_match', None)
        display = get_attr(self, 'display', None)
        self._color_match = color_match
        self._display = display

    def get_color(self, value, text):
        if not self._color_match:
            return None
        # 根据显示文本设置颜色
        for pattern, color in self._color_match.items():
            if re.match(pattern, text):
                return QColor(color)
        return None

    def get_text(self, value, record):
        if value is None:
            return ''
        if self._display is None:
            return super().get_text(value, record)
        if is_execute_able(self._display):
            return self._display(value, record)
        l_ctx = o2d(record)
        l_ctx['value'] = value  # 将value也加入上下文，方便直接使用
        return eval(f'f"{self._display}"', __locals=l_ctx)

    def setup_painter(self, painter, value, text):
        color = self.get_color(value, text)
        if color:
            painter.setPen(QColor(color))


class YFpInt(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.leading_zero = get_attr(self, 'leading_zero', 0)
        self.format = get_attr(self, 'format', '%d')
        self.zero = get_attr(self, 'zero', '0')

    def get_text(self, value, record):
        fmt = f"%0{self.leading_zero}d" if self.leading_zero else self.format
        v = None if pd.isna(value) else int(value)
        txt = fmt % v if v is not None else None
        if txt == '0':
            return get_attr(self, 'zero', txt)
        return txt

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class YFpSwitch(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.disp_text = get_attr(self, 'disp_text', ['[NO]', '[YES]'])
        self.attitude_color = get_attr(self, 'attitude_color')

    def setup_painter(self, painter, value, text):
        color = self.get_color(value, text)
        if color:
            painter.setPen(color)

    def get_color(self, value, text):
        if not self.attitude_color:
            return None
        # 根据值设置颜色，开关值为ON时显示 WEAK_POSITIVE 颜色
        att = DisplayAttitude.INACTIVE
        if text == self.disp_text[1]:
            att = DisplayAttitude.WEAK_POSITIVE
        return self.get_attitude_color(att)

    def get_text(self, value, record):
        if value is None:
            return self.disp_text[0]
        value = str(value).strip().upper()
        p = r"(1.*)|(T.*)|(Y.*)"
        if re.match(p, value):
            return self.disp_text[1]
        else:
            return self.disp_text[0]

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


class YFpCurrency(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attitude_color = get_attr(self, 'attitude_color')
        self.units = get_attr(self, 'units')
        self.zero = get_attr(self, 'zero', '0.00')
        if not self.units:
            self.units = 1

    def setup_painter(self, painter, value, text):
        color = self.get_color(value, text)
        if color:
            painter.setPen(color)

    def get_color(self, value, text):
        if not self.attitude_color:
            return None
        # 根据值设置颜色
        att = DisplayAttitude.INACTIVE
        if value > 0.001:
            att = DisplayAttitude.POSITIVE
        if value < -0.001:
            att = DisplayAttitude.NEGATIVE
        return self.get_attitude_color(att)

    def get_text(self, value, record):
        if value is None:
            return None
        v = to_float(value, none_value=0)
        if -0.0001 < v < 0.0001:  # 视为0
            return self.zero
        else:
            return f"{v / self.units:,.2f}"

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class YFpPercent(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._color = current_theme.hover_color()
        self._max = 100.0
        self.zero = get_attr(self, 'zero', '0.0%')

    def draw_field(self, painter, rect, value, text):
        left_margin, right_margin = 4, 4
        full_width = rect.width() - left_margin - right_margin
        full_height = rect.height()
        top_margin, bottom_margin = full_height * 0.15, full_height * 0.15
        value = to_float(value)
        # 根据比率计算右边界
        right_margin = (self._max - value) / self._max * full_width + right_margin
        if right_margin > full_width:
            right_margin = full_width
        # 绘制百分比bar
        painter.setPen(self._color)
        brush = QBrush(self._color, Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        rect_bar = rect.adjusted(left_margin, top_margin, 0 - right_margin, 0 - bottom_margin)
        painter.drawRoundedRect(rect_bar, left_margin, top_margin)
        # 文字
        font = painter.font()
        font.setUnderline(True)  # 添加下划线
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.lightGray)
        painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter, text)

    def get_text(self, value, record):
        if value is None:
            return None
        value = to_float(value)
        if -0.0001 < value < 0.0001:  # 视为0
            return self.zero
        else:
            return f"{value:,.1f}%"

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class YFpDateTime(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_text(self, value, record):
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, Timestamp):
            value = value.to_pydatetime()
        return f"{value}"

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


class YFpDate(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_text(self, value, record):
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, Timestamp):
            value = value.to_pydatetime()
        return format_date(value)

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


class YFpYearMonth(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_text(self, value, record):
        return f'{value[:4]}年{value[4:]}月' if value else None

    @staticmethod
    def alignment():
        return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


class YFpChoose(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code_dict = DictFetcher.instance().get_dict(self)
        self.attitude = get_attr(self, 'attitude')
        self.format = get_attr(self, 'format', '[{code}] - {name}')

    def get_color(self, value, text):
        if not self.attitude or pd.isna(value):
            return None
        for att, v in self.attitude.items():
            if value in v:
                return self.get_attitude_color(att)
        return None

    def setup_painter(self, painter, value, text):
        color = self.get_color(value, text)
        if color:
            painter.setPen(color)

    def get_text(self, value, record):
        ret = []
        values = value if is_collection(value) else [value]
        if self.code_dict:
            for code, name in self.code_dict.items():
                if str(code) in [str(v) for v in values]:  # 值和字典码均转换为字符串再做比较，防止值为数值但码表中的类型为字符时无法匹配
                    ret.append(eval(f'f"{self.format}"'))
        else:
            ret.extend([str(v) for v in values])
        return ', '.join(ret) if ret else None


class YFpLookup(YFieldPainter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lookup_key = get_attr(self, 'lookup_key')
        self.lookup = FACTORY.get_lookup(**kwargs) if self.lookup_key else None

    def get_text(self, value, record):
        return self.lookup.to_text(value) if self.lookup else f"{value}"


#############################################################
# 数据字段准则控件
#############################################################
class YFdCriteria(QWidget):
    """
    数据字段的查询条件显示组件
    """

    def __init__(self,
                 column_spec,
                 parent=None,
                 editor_cls=None,
                 op: Op = None,
                 value=None,
                 layout_flag='H',
                 check_able=True,
                 auto_from=None,
                 ):
        super().__init__(parent=parent)
        self.column_spec = column_spec
        self.editor_cls = editor_cls if editor_cls else FACTORY.get_editor_class(self.column_spec)
        self.field = column_spec.name
        self.label = self.column_spec.title if self.column_spec.title else self.column_spec.comment
        if self.label is None:
            self.label = self.field.upper()
        self.check_able = check_able
        if self.label.startswith('*'):
            self.label = self.label[1:]
        self.layout_flag = layout_flag
        self.op = op if op else self.get_default_op()
        self._editors = []
        self._checked = False
        self.setup_ui()
        if auto_from:
            self.assign_from(auto_from)
        if value:
            self.set_value(value)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def get_default_op(self):
        return {
            YFdText: Op.LIKE_IN,
            YFdNumber: Op.BETWEEN,
            YFdInt: Op.BETWEEN,
            YFdYear: Op.BETWEEN,
            YFdCurrency: Op.BETWEEN,
            YFdDate: Op.BETWEEN,
            YFdDateTime: Op.BETWEEN,
            YFdYearMonth: Op.BETWEEN,
            YFdChoose: Op.IN,
            YFdLookup: Op.IN,
        }[self.editor_cls]

    def add_to(self, layout: QLayout, index=-1):
        """
        将控件加入到指定的布局中
        :param index:
        :param layout: 待加入的布局对象
        :return:
        """
        label_text = f"{self.label} ({self.op.text()}):" if self.label else ""
        if isinstance(layout, QFormLayout):  # Form布局，label为checkbox
            w = QCheckBox(label_text, parent=self.parent())
            w.setChecked(self._checked)
            w.clicked.connect(self.on_check)
            layout.addRow(w, self)
        else:
            w = self
            if label_text:
                if self.check_able:  # 创建组合框
                    w = QGroupBox(self.parent())
                    w.setTitle(label_text)
                    w.setLayout(QVBoxLayout())
                    w.setCheckable(True)
                    w.setChecked(self._checked)
                    w.clicked.connect(self.on_check)
                    w.layout().setContentsMargins(0, 0, 0, 0)
                    w.layout().addWidget(self)
                else:  # 水平标题+组件
                    w = create_layout_widget(parent=self.parent(), layout_flag='H')
                    w.layout().addWidget(QLabel(label_text))
                    w.layout().addWidget(self)
            add_to_layout(layout, w, index)

    def setup_ui(self):
        def create_editor():
            editor = FACTORY.get_editor(self, self.column_spec,
                                        Stage.IN_QUERY,
                                        op=self.op,
                                        **self.column_spec.__dict__)
            self.layout().addWidget(editor)
            return editor

        def clear_editors(layout):
            clear_layout(layout)
            self._editors.clear()

        if self.layout():
            clear_editors(self.layout())
        self.setLayout(create_layout(self.layout_flag))
        self._editors.append(create_editor())
        if self.is_editor_pair():
            self.layout().addWidget(QLabel('~', alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))
            self._editors.append(create_editor())

    def get_value(self):
        values = [ed.get_value() for ed in self._editors]
        value = values[0] if len(values) < 2 else values
        return value

    def assign_to(self, qc):
        if self._checked and qc:
            set_attr(qc, self.field, (self.op.value, self.get_value()))
        else:
            set_attr(qc, self.field, None)

    def assign_from(self, obj):
        if obj:
            o_value = get_attr(obj, self.field)
            if o_value is None:
                return
            if not is_collection(o_value):
                raise Exception('查询条件值不符合要求，应为集合类型，且对应两个元素： (Op,Value)')
            new_op = Op(o_value[0])
            if new_op != self.op:  # 重置界面
                self.op = new_op
                self.setup_ui()
            self.set_value(o_value[1])

    def is_checked(self):
        return self._checked

    def on_check(self):
        sender = self.sender()
        self._checked = sender.isChecked()

    def is_editor_pair(self):
        return self.op == Op.BETWEEN

    def set_value(self, value):
        values = value if self.is_editor_pair() else [value]
        for i, edt in enumerate(self._editors):
            edt.set_value(values[i])
            if values[i] is not None:  # 如果存在有效值，自动设置条件生效标记
                self._checked = True


#####################################################################
# 字段相关组件工厂
#####################################################################
class YFdFactory:
    # 保存Lookup工具的静态字典
    _LOOKUPS = {}

    editor_map = {
        UnitType.TEXT: YFdText,
        UnitType.INT: YFdInt,
        UnitType.SWITCH: YFdSwitch,
        UnitType.NUMBER: YFdNumber,
        UnitType.CURRENCY: YFdCurrency,
        UnitType.DATE: YFdDate,
        UnitType.YEAR: YFdYear,
        UnitType.YEAR_MONTH: YFdYearMonth,
        UnitType.TIME: YFdDateTime,
        UnitType.CHOOSE: YFdChoose,
        UnitType.LOOKUP: YFdLookup,
        UnitType.PERCENT: YFdNumber,
        UnitType.RICH_TEXT: YFdRichText,
    }

    painter_map = {
        UnitType.TEXT: YFpText,
        UnitType.INT: YFpInt,
        UnitType.SWITCH: YFpSwitch,
        UnitType.NUMBER: YFpText,
        UnitType.CURRENCY: YFpCurrency,
        UnitType.DATE: YFpDate,
        UnitType.TIME: YFpDateTime,
        UnitType.YEAR: YFpText,
        UnitType.YEAR_MONTH: YFpYearMonth,
        UnitType.CHOOSE: YFpChoose,
        UnitType.LOOKUP: YFpLookup,
        UnitType.PERCENT: YFpPercent,
        UnitType.RICH_TEXT: YFpText,
    }

    @staticmethod
    def deduce_unit_type(col_spec) -> UnitType:
        # 简单使用col_spec确定的utype
        utype = get_attr(col_spec, 'utype')
        if utype:  # 指定了明确的utype，直接返回
            set_attr(col_spec, 'utype', utype)
            return utype
        # 没有明确指定utype,根据类型推断
        utype = UnitType.TEXT  # 默认TEXT
        dtype = get_attr(col_spec, 'dtype')
        if dtype:
            for p, u_type in {
                r'(NUMERIC)|(DECIMAL)': UnitType.CURRENCY,
                r'(INT.*)': UnitType.INT,
                r'(DATETIME.*)': UnitType.DATE,  # DATETIME类型默认还是用DATE
                r'(DATE *)': UnitType.DATE,
                r'(.*LOB.*)|(TEXT)': UnitType.RICH_TEXT,
            }.items():
                if re.match(p, dtype.upper()):
                    utype = u_type
        set_attr(col_spec, 'utype', utype)
        return utype

    @staticmethod
    def unite_dict(*ods) -> dict:
        d = dict()
        for o in ods:
            copy_obj(d, o)
        return d

    def get_editor_class(self, col_spec: ColumnSpec):
        utype = self.deduce_unit_type(col_spec)
        return self.editor_map[utype]

    def get_editor(self, parent, col_spec: ColumnSpec, stage: Stage = Stage.IN_TABLE, **kwargs):
        cls = self.get_editor_class(col_spec=col_spec)
        if cls is None:
            raise Exception(f'无法创建FieldEditor-找不到对应的 YFieldEditor Class,col_spec={col_spec}')
        return cls(parent=parent, stage=stage, **self.unite_dict(col_spec, kwargs))

    def get_painter(self, col_spec: ColumnSpec, **kwargs):
        utype = self.deduce_unit_type(col_spec)
        cls = self.painter_map[utype]
        if cls is None:
            raise Exception(f'无法创建FieldPainter-找不到对应的 YFieldPainter Class,col_spec={col_spec}')
        return cls(**self.unite_dict(col_spec, kwargs))

    @staticmethod
    def get_lookup(**kwargs):
        def split_r(s):
            dot_index = s.rfind('.')
            if dot_index != -1:
                return s[:dot_index], s[dot_index + 1:]
            else:  # 如果没有找到'.'，则返回整个字符串作为第一部分，第二部分为空字符串
                return s, ""

        lookup_key = get_attr(kwargs, 'lookup_key')
        if not lookup_key:
            raise Exception('实例化YLookup失败', '缺少lookup_key属性')
        lk = YFdFactory._LOOKUPS.get(lookup_key)
        if lk is None:
            mod, cls = split_r(lookup_key)
            # print(f'[YField] - YFdFactory.get_lookup: Creating instance of YLookup ... mod={mod},cls={cls}')
            if not mod or not cls:
                raise Exception("实例化YLookup失败",
                                f"无效的lookup key: '{lookup_key}' , 正确的格式应该为'.'连接的模块名和YLookup的子类名。")
            lk = create_instance(mod, cls, **kwargs)
            YFdFactory._LOOKUPS[lookup_key] = lk
        return lk


# 字段工具工厂
FACTORY = YFdFactory()
