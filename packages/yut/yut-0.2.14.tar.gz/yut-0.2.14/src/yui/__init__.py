# -*- yui.py: python ; coding: utf-8 -*-
# 基于PySide开发的通用GUI工具
import sys
from enum import Enum

from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import (QIcon, QColor, QEnterEvent, QPalette, QPixmap, QAction)
from PySide6.QtWidgets import (QApplication, QToolBar, QWidget, QPushButton, QToolButton, QSizePolicy,
                               QLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout, QDateTimeEdit,
                               QCalendarWidget, QGroupBox, QFileDialog, QDateEdit, QMenu)
from PySide6.QtWidgets import (QMessageBox)

from yut import get_attr, is_execute_able, call_exp
from yut.win32 import set_process_user_model_id


class Theme(Enum):
    DARK = '深色'
    LIGHT = '浅色'

    def icon_color(self):
        return {self.DARK: QColor(100, 149, 237),
                self.LIGHT: QColor(80, 128, 218), }.get(self)

    def hover_color(self):
        return {self.DARK: QColor(80, 140, 242),
                self.LIGHT: QColor(80, 120, 226), }.get(self)

    def hi_light_color(self):
        return {self.DARK: QColor(212, 212, 212),
                self.LIGHT: QColor(212, 212, 30), }.get(self)

    def enforce_color(self):
        return {self.DARK: QColor(192, 168, 32),
                self.LIGHT: QColor(16, 12, 30), }.get(self)


class HoveredButton(QPushButton):
    entered = Signal()
    leaved = Signal()

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.entered.emit()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.leaved.emit()


class HoveredToolButton(QToolButton):
    entered = Signal()
    leaved = Signal()

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.entered.emit()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.leaved.emit()


current_theme = Theme.DARK


def set_current_theme(theme: Theme):
    global current_theme
    current_theme = theme


def create_default_app(argv=None, theme: Theme = Theme.DARK, app_name=None, icon_file=None) -> QApplication:
    import yui.images_rc as images
    import qtmodern.styles as style
    arv = argv if argv is not None else sys.argv
    app = QApplication(arv)
    if app_name:
        set_process_user_model_id(app_name)
        app.setApplicationDisplayName(app_name)
        app.setApplicationName(app_name)
    if icon_file:
        app.setWindowIcon(load_icon(icon_file, colored=False))
    set_current_theme(theme)
    if theme == Theme.DARK:
        style.dark(app)
    else:
        style.light(app)
    return app


def get_app() -> QApplication | None:
    return QApplication.instance()


def get_mainwindow() -> QWidget | None:
    app = get_app()
    if hasattr(app, 'main_window'):
        return app.main_window
    else:
        return app.activeWindow()


def get_active_window() -> QWidget | None:
    app = get_app()
    return app.activeWindow() if app else None


def colored_pixmap(file_name, colored=True):
    pix = QPixmap(file_name)
    if colored:
        mask = pix.createMaskFromColor(Qt.GlobalColor.transparent)
        color = current_theme.icon_color()  # QPalette().color(QPalette.Highlight)  # theme_icon_color
        pix.fill(color)
        pix.setMask(mask)
    return pix


def load_icon(file_name, colored=True):
    return QIcon(colored_pixmap(file_name, colored=colored))


def create_action(text, trigger, icon_file=None, parent=None, object_name=None) -> QAction:
    action = QAction(load_icon(icon_file), text, parent)
    action.triggered.connect(trigger)
    action.setObjectName(object_name)
    return action


def create_button(text='', trigger=None, icon=None, icon_file=None, flat=None, tip_text=None, parent=None,
                  object_name=None, icon_only=False,
                  icon_size: QSize | int = None, ):
    btn = QPushButton(text if not icon_only else '', parent=parent)
    btn.setObjectName(object_name)
    if icon:
        btn.setIcon(icon)
    else:
        if icon_file:
            btn.setIcon(load_icon(icon_file))
    if flat is not None:
        btn.setFlat(flat)
    if tip_text is not None:
        btn.setToolTip(tip_text)
    else:
        if text:
            btn.setToolTip(text)
    if trigger:
        btn.clicked.connect(trigger)
    if icon_size:
        size = icon_size if isinstance(icon_size, QSize) else QSize(icon_size, icon_size)
        btn.setIconSize(size)
        btn.setIconSize(QSize(icon_size, icon_size))
    return btn


def create_tool_button(text='',
                       trigger=None,
                       icon=None,
                       icon_file=None,
                       tip_text=None,
                       parent=None,
                       icon_size: QSize | int = None,
                       button_style=Qt.ToolButtonStyle.ToolButtonIconOnly,
                       flat=False,
                       object_name=None,
                       ) -> QToolButton:
    btn = QToolButton(parent=parent)
    btn.setToolButtonStyle(button_style)
    btn.setObjectName(object_name)
    if text:
        btn.setText(text)
    if icon:
        btn.setIcon(icon)
    else:
        if icon_file:
            btn.setIcon(load_icon(icon_file))
    if tip_text is not None:
        btn.setToolTip(tip_text)
    else:
        if text:
            btn.setToolTip(text)
    if trigger:
        btn.clicked.connect(trigger)
    if icon_size:
        size = icon_size if isinstance(icon_size, QSize) else QSize(icon_size, icon_size)
        btn.setIconSize(size)
    if flat:
        btn.setStyleSheet("border - style: flat; background: transparent;")
    # btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    return btn


def create_menu_button(menu: QMenu,
                       title=None,
                       icon_file=None,
                       icon=None,
                       hovered=False,
                       icon_size: QSize | int = None,
                       tool_button=False,
                       indicator=False,
                       object_name=None) -> HoveredButton | HoveredToolButton | QToolButton | QPushButton:
    if icon_size is not None:
        size = icon_size if isinstance(icon_size, QSize) else QSize(icon_size, icon_size)
    else:
        size = QSize(14, 14)

    if hovered:
        if tool_button:
            btn = HoveredToolButton()
            btn.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
            btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        else:
            btn = HoveredButton()
            btn.setFlat(True)
        btn.entered.connect(btn.click)
    else:
        if tool_button:
            btn = QToolButton()
            btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        else:
            btn = QPushButton()
            btn.setFlat(True)

    btn.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

    if not indicator:  # 去掉menu指引箭头
        if isinstance(btn, QToolButton):
            btn.setStyleSheet('QToolButton::menu-indicator {image: none;}')
        if isinstance(btn, QPushButton):
            btn.setStyleSheet('QPushButton::menu-indicator {image: none;}')

    btn.setMenu(menu)
    btn.setIconSize(size)
    btn.setObjectName(object_name)

    if title:
        btn.setText(title)
        btn.setToolTip(title)

    if icon:
        btn.setIcon(icon)
    elif icon_file:
        btn.setIcon(load_icon(icon_file))

    return btn


def create_toolbar(buttons=None, actions=None, icon_size=12, parent=None, object_name=None) -> QToolBar:
    tbar = QToolBar(parent=parent)
    tbar.setIconSize(QSize(icon_size, icon_size))
    tbar.setObjectName(object_name)
    if actions:
        tbar.addActions(actions)
    if buttons:
        if actions:
            tbar.addSeparator()
        for btn in buttons:
            tbar.addWidget(btn)
    return tbar


def pop_info(*args, title=None, sep=' '):
    text = sep.join([str(a) for a in args])
    if not title:
        title = '提示信息'
    QMessageBox.information(get_mainwindow(), title, text)


def pop_question(*args, title=None, sep=' '):
    text = sep.join([str(a) for a in args])
    if not title:
        title = '请确认信息'
    return QMessageBox.question(get_mainwindow(), title, text,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Ok


def pop_warning(*args, title=None, sep=' '):
    text = sep.join([str(a) for a in args])
    if not title:
        title = '提示信息'
    QMessageBox.warning(get_mainwindow(), title, text)


def load_style_sheet(fname):
    style = ''
    for line in open(fname, encoding='utf-8').readlines():
        style += line
    get_app().setStyleSheet(style)


def contrast_color(color):
    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
    # luminance = (color.red() + color.green() + color.blue()) / (3 * 255)
    if luminance > 0.5:
        contrast = QColor('#000000')
    else:
        contrast = QColor('#FFFFFF')
    return contrast


def change_font(w, bold=None, size=None, italic=None, underline=None, strike=None):
    font = w.font()
    if bold is not None:
        font.setBold(bold)
    if underline is not None:
        font.setUnderline(underline)
    if italic is not None:
        font.setItalic(italic)
    if strike is not None:
        font.setStrike(strike)
    if size:
        font.setPointSize(size)
    w.setFont(font)
    return w


def change_item_display(item, bold=None, italic=None, underline=None, strike=None, size=None, color=None,
                        background=None):
    font = item.font()
    if bold is not None:
        font.setBold(bold)
    if size:
        font.setPointSize(size)
    if underline is not None:
        font.setUnderline(underline)
    if italic is not None:
        font.setItalic(italic)
    if strike is not None:
        font.setStrike(strike)
    item.setFont(font)

    if color:
        item.setForeground(color)
    if background:
        item.setBackground(background)
    return item


def set_label_color(lb, bk_color=None, fore_color=None):
    pe = QPalette()
    if bk_color:
        lb.setAutoFillBackground(True)
        pe.setColor(QPalette.ColorRole.Window, bk_color)
    if fore_color:
        pe.setColor(QPalette.ColorRole.WindowText, fore_color)
    lb.setPalette(pe)
    return lb


def set_widget_color(wdg, bk_color=None, fore_color=None):
    palette = wdg.palette()
    if bk_color:
        palette.setColor(QPalette.ColorRole.Window, bk_color)
    if fore_color:
        palette.setColor(QPalette.ColorRole.Text, fore_color)
    wdg.setPalette(palette)


def create_layout(layout_flag='H', parent=None,
                  object_name=None) -> QHBoxLayout | QVBoxLayout | QGridLayout | QFormLayout:
    """
    依据标记创建布局对象
    :param object_name:
    :param parent:
    :param layout_flag:
        'H' - HBox ;
        'V' - VBox ;
        'F' - FormLayout ;
        'G##' - GridLayout 紧跟在G后面的是Grid布局的列数目，如'G3'表示创建表格布局，每行3列，会将列数加到布局回想的column_num属性中
    :return: QLayout 对象，如果是GridLayout，增加column_num属性，保存打算布置的列数
    """
    if layout_flag == 'V':
        lyt = QVBoxLayout()
        lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lyt.setSpacing(4)
    elif layout_flag.startswith('G'):
        lyt = QGridLayout()
        if len(layout_flag) > 1:
            lyt.column_num = int(layout_flag[1:])
        lyt.setHorizontalSpacing(4)
        lyt.setVerticalSpacing(4)
    elif layout_flag == 'F':
        lyt = QFormLayout()
        lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        lyt.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
        lyt.setFormAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lyt.setHorizontalSpacing(16)
        lyt.setVerticalSpacing(16)
    else:
        lyt = QHBoxLayout()
        lyt.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lyt.setSpacing(4)
    lyt.setContentsMargins(0, 0, 0, 0)
    lyt.setParent(parent)
    lyt.setObjectName(object_name)
    return lyt


def create_widget(target=QWidget, parent=None, object_name=None) -> QWidget:
    """
    创建QWidget
    :param object_name:
    :param target: 可以是QWidget实例/QWidget class及其子类/函数/表达式，默认为QWidget class
    :param parent:
    :return:
    """
    import inspect
    widget = None
    if isinstance(target, QWidget):
        widget = target
    elif inspect.isclass(target):
        widget = target(parent=parent)
    elif is_execute_able(target):
        widget = target()
    elif isinstance(target, str):
        widget = call_exp(target)
    if parent and widget:
        widget.setParent(parent)
    widget.setObjectName(object_name)
    return widget


def create_layout_widget(target=QWidget, parent=None, layout_flag='H', object_name=None, window_title=None) -> QWidget:
    """
    创建带布局的widget,并将布局设置为widget的主布局
    :param target: Widget类，默认使用QWidget
    :param layout_flag:
        'H' - HBox ;
        'V' - VBox ;
        'F' - FormLayout ;
        'G##' - GridLayout 紧跟在G后面的是Grid布局的列数目，如'G3'表示创建表格布局，每行3列，会将列数加到布局回想的column_num属性中
    :param parent: 创建widget时使用的父对象
    :param object_name: 对象名,setObjectName
    :param window_title: 窗口标题，setWindowTitle
    :return: QWidget
    """
    widget = create_widget(target, parent=parent)
    widget.setLayout(create_layout(layout_flag))
    widget.setObjectName(object_name)
    if window_title:
        widget.setWindowTitle(window_title)
    return widget


def set_layout_spacing(lyt, h_spacing=0, v_spacing=0):
    if isinstance(lyt, QHBoxLayout):
        lyt.setSpacing(h_spacing)
    elif isinstance(lyt, QVBoxLayout):
        lyt.setSpacing(v_spacing)
    elif isinstance(lyt, QGridLayout):
        lyt.setHorizontalSpacing(h_spacing)
        lyt.setVerticalSpacing(v_spacing)
    elif isinstance(lyt, QFormLayout):
        lyt.setHorizontalSpacing(h_spacing)
        lyt.setVerticalSpacing(v_spacing)


def clear_layout(layout: QLayout):
    for i in range(layout.count() - 1, -1, -1):
        item = layout.itemAt(i)
        if item.widget():
            item.widget().deleteLater()
        layout.removeItem(item)


def show_in_center(widget):
    screen_rect = get_app().primaryScreen().geometry()
    widget.setGeometry(screen_rect.width() // 2 - widget.width() // 2,
                       screen_rect.height() // 2 - widget.height() // 2,
                       widget.width(),
                       widget.height())
    widget.show()


def create_date_edit(date, parent=None, object_name=None) -> QDateEdit:
    edt = QDateTimeEdit(date, parent=parent)
    edt.setObjectName(object_name)
    edt.setCalendarPopup(True)
    edt.setDisplayFormat('yyyy-MM-dd')
    edt.setMinimumWidth(100)
    w = QCalendarWidget(edt)
    w.setGridVisible(True)
    w.setAutoFillBackground(True)
    w.setObjectName('dateEditCalendar')
    w.setMinimumWidth(200)
    w.setMaximumHeight(300)
    edt._cal_widget = w
    edt.setCalendarWidget(edt._cal_widget)
    return edt


def filename_for_save(path='.', caption=None, file_filter='*.*'):
    caption = caption if not caption else '请选择待保存的文件位置'
    dlg = QFileDialog(parent=None, caption=caption)
    files = dlg.getSaveFileName(parent=None, caption=caption, dir=path, filter=file_filter)
    if files[0]:
        return files[0]
    else:
        return None


def add_to_layout(layout: QLayout, widget: QWidget | QLayout, index=-1):
    if index < 0:
        attr = 'addWidget' if isinstance(widget, QWidget) else 'addLayout'
    else:
        attr = 'insertWidget' if isinstance(widget, QWidget) else 'insertLayout'
    fn_add = get_attr(layout, attr)
    if isinstance(layout, QGridLayout):  # Grid布局
        n_count = layout.count()
        if hasattr(layout, 'column_num'):
            column_num = get_attr(layout, 'column_num', 2)
            fn_add(widget, n_count / column_num, n_count % column_num)
    else:  # HBox | VBox |GroupBox
        if index < 0:
            fn_add(widget)
        else:
            fn_add(index, widget)


def add_field(layout: QLayout, field: QWidget, label=None, index=-1):
    """
    在布局中添加部件。如果是FormLayout，要求label为QWidget使用addRow
    :param index: -1 - add; >=0 - insert
    :param layout:
    :param field:
    :param label:
    :return:
    """
    if isinstance(layout, QFormLayout):  # Form布局
        layout.addRow(label, field)
    else:
        w = field
        if label is not None:  # 创建组合框，否则直接在layout中增加
            g_box = QGroupBox(field.parent())
            g_box.setLayout(QVBoxLayout())
            g_box.layout().setContentsMargins(0, 0, 0, 0)
            g_box.layout().addWidget(field)
            g_box.setTitle(label)
            w = g_box
        add_to_layout(layout, w, index)


class WorkMode(Enum):
    """
    单元的工作模式，显示/编辑
    """
    DISPLAY = 0  # 显示模式
    EDIT = 1  # 编辑模式
    WATCH = 2  # 监视模式 - 只读显示，但该字段在其它地方改变之后需要更新


class EditMode(Enum):
    """
    表单/列表的编辑模式，新增/修改
    """
    NEW = 0  # 新增
    MODIFY = 1  # 修改


class Stage(Enum):
    """
    单元的使用场景
    """
    IN_FORM = 0  # 表单式
    IN_TABLE = 1  # 列表式
    IN_QUERY = 2  # 查询条件


class TranslateDirection(Enum):
    TO_TEXT = 0  # 值 -> 显示文字
    TO_VALUE = 1  # 显示文字 -> 值


class LookupViewType(Enum):
    """
    LookupView类型
    """
    List = 0  # 列表： 无表头，无查询条件，可以筛选
    Table = 1  # 表格： 有表头，可以多列，可以带查询条件以及点击排序
    Tree = 2  # 树：有表头，可以多列，树形展开，无查询条件录入框


def alignment_flag(tag):
    """
    :param tag:
    '>' - 右对齐
    '|' - 水平居中
    '<' - 左对齐
    '^' - 顶对齐
    '-' - 垂直居中
    '_' - 底对齐
    :return:
    """
    horizontal_alignment, vertical_alignment = Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignVCenter
    for ch, h_flag in {'>': Qt.AlignmentFlag.AlignRight,
                       '<': Qt.AlignmentFlag.AlignLeft,
                       '|': Qt.AlignmentFlag.AlignCenter
                       }.items():
        if ch in tag:
            horizontal_alignment = h_flag
    for ch, v_flag in {'^': Qt.AlignmentFlag.AlignTop,
                       '_': Qt.AlignmentFlag.AlignBottom,
                       '-': Qt.AlignmentFlag.AlignVCenter
                       }.items():
        if ch in tag:
            vertical_alignment = v_flag
    return horizontal_alignment | vertical_alignment
