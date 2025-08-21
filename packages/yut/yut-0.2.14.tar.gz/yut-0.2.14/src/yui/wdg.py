# -*- wdg.py: python ; coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Union, Any

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QObject, Signal, QEvent, QSize, Slot, QDate, QRectF
from PySide6.QtGui import QEnterEvent, QPalette, QAction, QFont, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QStackedWidget, QFrame, QVBoxLayout, QToolButton, QHBoxLayout, QGridLayout, \
    QTabWidget, QSizePolicy, QMenu, QSpacerItem, QPushButton, QLabel, QSpinBox, QLayout, QButtonGroup, QProgressBar, \
    QScrollArea, QApplication, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem

import yui
from yui import img, create_layout, create_layout_widget, create_button, change_font, create_menu_button, \
    create_date_edit, load_icon, create_widget, create_toolbar, create_tool_button, pop_question, colored_pixmap, \
    set_label_color, get_mainwindow
from yut import to_date, Obj, copy_obj, format_date, is_collection, get_attr, set_attr, to_float


class YTitle(QWidget):
    """
    通用标题组件，包含图标和文字

    参数:
        parent: 父组件
        icon_path: 图标路径
        text: 标题文本
        icon_size: 图标大小 (默认 24x24)
        font_size: 文本字体大小 (默认14，加粗)
        spacing: 图标和文本间距 (默认10)
    """

    def __init__(self, text, parent=None,
                 icon_path=img.P_4_DOTS,
                 icon_size=QSize(24, 24),
                 on_click=None,
                 click_param=None,
                 alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                 font_size=14,
                 font_bold=True,
                 spacing=4,
                 object_name=None):
        super().__init__(parent)

        self.on_click = on_click
        self.click_param = click_param
        self.setObjectName(object_name)

        # 初始化布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

        # 图标标签
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_icon(icon_path, icon_size)

        # 文本标签
        self.text_label = QLabel(self)
        self.text_label.setTextFormat(Qt.TextFormat.RichText)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.text_label.setOpenExternalLinks(False)  # 禁用自动打开
        self.text_label.linkActivated.connect(self.link_activated)
        self.set_text(text)

        # 设置字体
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(font_bold)
        self.set_font(font)

        # 添加组件到布局
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label, 1, alignment=alignment)
        self.layout.addStretch(0)

    def link_activated(self, link):
        if self.on_click:
            self.on_click(self, link)

    def set_icon(self, icon_path, size=None):
        if icon_path:
            pixmap = colored_pixmap(icon_path)
            if size:
                pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.clear()

    def set_text(self, text):
        href = self.click_param if self.click_param else '#'
        text = f"<a href='{href}' style='text-decoration: none; color:#c0c0c0'>{text}</a>" if self.on_click else text
        self.text_label.setText(text)

    def set_font(self, font):
        self.text_label.setFont(font)

    def set_icon_size(self, size):
        if self.icon_label.pixmap():
            pixmap = self.icon_label.pixmap()
            self.icon_label.setPixmap(pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation))

    def set_spacing(self, spacing):
        self.layout.setSpacing(spacing)

    def add_buddy(self, wdg: QWidget):
        index = self.layout.indexOf(self.text_label)
        if index < self.layout.count() - 1:
            self.layout.insertWidget(self.layout.count() - 1, wdg, stretch=1)
        else:
            self.layout.addWidget(wdg, stretch=1)
        self.layout.setStretch(index, 0)

    @staticmethod
    def create_label(text, icon_file=img.P_4_DOTS, buddy=None):
        ytl = YTitle(text, icon_path=icon_file, icon_size=QSize(12, 12), font_bold=False, font_size=9)
        if buddy is not None:
            ytl.add_buddy(buddy)
        return ytl


class YLink(Obj):
    def __init__(self, title, icon=None, target: Union[QWidget, Any] = None, tip_text=None, layout_flag='V', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.icon = icon if icon else img.P_4_DOTS
        self.target = target
        self.tip_text = tip_text
        self.layout_flag = layout_flag

    def create_target(self):
        widget = create_widget(self.target) if self.target else QLabel(self.title)
        if widget and self.icon:
            widget.setWindowIcon(load_icon(self.icon))
        return widget

    @staticmethod
    def instance(p):
        if isinstance(p, YLink):
            return p
        elif isinstance(p, str):
            return YLink(p)
        elif isinstance(p, dict):
            return YLink(**p)
        return None


class YTab(QWidget):
    CloseTab = Signal(QObject)
    SwitchTab = Signal(QObject)

    def __init__(self, parent, ref_widget, title='', icon=None, close_able=False, tip_text=None, object_name=None):
        super().__init__(parent=parent)
        self.title = title
        self.ref_widget = ref_widget
        self.icon = icon if icon else img.P_4_DOTS
        self.setObjectName(object_name)
        self.tip_text = tip_text
        self.close_able = close_able
        self.ui = QObject(parent=self)
        self._is_active = False
        self.setup_ui()

    def setup_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        self.ui.btn_title = create_button(text=self.title,
                                          trigger=self.switch_tab,
                                          tip_text=self.tip_text,
                                          flat=True,
                                          icon_file=self.icon)
        self.ui.btn_title.setCheckable(True)

        hbox = create_layout(layout_flag='H')
        hbox.addWidget(self.ui.btn_title)
        if self.close_able:
            self.ui.btn_close = create_button(text='',
                                              trigger=self.close_tab,
                                              icon_file=img.P_CLOSE,
                                              flat=True)
            hbox.addWidget(self.ui.btn_close)
            self.ui.btn_close.setVisible(False)

        focus_bar = QFrame(parent=self)
        focus_bar.setFixedHeight(2)
        self.ui.focus_bar = focus_bar
        vbox.addLayout(hbox)
        vbox.addWidget(self.ui.focus_bar)
        self.hi_light(False)

    def close_tab(self):
        self.CloseTab.emit(self.ref_widget)
        self.close()

    def switch_tab(self):
        self.SwitchTab.emit(self.ref_widget)

    def activate(self, is_activate):
        self._is_active = is_activate
        self.ui.btn_title.setChecked(self._is_active)
        self.hi_light(self._is_active)
        change_font(self.ui.btn_title, bold=self._is_active)

    def hi_light(self, light):
        if self.is_active():
            active_color = QPalette().color(QPalette.Dark).name()
            self.ui.focus_bar.setFixedHeight(2)
            self.ui.btn_title.setFlat(False)
            self.ui.btn_title.setStyleSheet(f"background-color:{active_color}")
        else:
            self.ui.focus_bar.setFixedHeight(1)
            self.ui.btn_title.setFlat(False)
        if light or self.is_active():
            focus_color = QPalette().color(QPalette.Highlight).name()
            self.ui.focus_bar.setStyleSheet(f"background-color:{focus_color}")
        else:
            self.ui.focus_bar.setStyleSheet("")
            self.ui.btn_title.setFlat(True)
            self.ui.btn_title.setStyleSheet("")
        if self.close_able:
            self.ui.btn_close.setVisible(light)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.hi_light(True)

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.hi_light(False)

    def is_active(self):
        return self._is_active


class YWidgetPages(QWidget):
    """
    用StackedWidget和ButtonGroup组合的多页面组件.
    """
    pageSwitched = Signal(QWidget, YTab)
    pageClosed = Signal(QWidget, YTab)

    def __init__(self,
                 *pages,
                 parent=None,
                 close_able=False,
                 show_single_tab=False,
                 tab_alignment=Qt.AlignmentFlag.AlignLeft,
                 object_name=None,
                 ):
        """
        初始化方法
        :param pages: 页签定义信息
        :param parent:
        :param on_switch:
        :param show_single_tab:
        :param tab_alignment:
        """
        super().__init__(parent=parent)
        self._pages = [YLink.instance(p) for p in pages]  # 页签定义,支持多种参数类型
        self._tabs = []  # 页签控件
        self.close_able = close_able
        self.show_single_tab = show_single_tab
        self.tab_alignment = tab_alignment
        self.setObjectName(object_name)

        self._stacked_widget = None  # 堆叠widget控件
        self._tab_bar = None  # Tab栏控件

        self.setup_ui()

    def setup_ui(self):
        self.setLayout(create_layout('V'))

        # 页签按钮栏
        self._tab_bar = self.create_tab_bar()  # Tab栏控件
        self.layout().addWidget(self._tab_bar)
        self._tab_bar.layout().setAlignment(self.tab_alignment | Qt.AlignmentFlag.AlignVCenter)

        # 页签窗体
        self._stacked_widget = QStackedWidget(parent=self.parent())  # 堆叠widget控件
        self._stacked_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._stacked_widget.layout().setSpacing(0)
        self.layout().addWidget(self._stacked_widget)

        # 创建各个页签以及切换按钮
        for pd in self._pages:
            self.add_page(pd)

        # 切换到第一个
        if self.page_count() > 0:
            self._tabs[0].activate(True)
            self._tabs[0].hi_light(False)

    def create_tab_bar(self):
        w = create_layout_widget(QWidget, parent=self, layout_flag='H')
        w.layout().setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
        w.layout().setSpacing(12)
        return w

    def close_page(self, page):
        for tab in self._tabs:
            tab.activate(False)
        if page is None:
            return
        cur_index = self._stacked_widget.indexOf(page)
        self._stacked_widget.removeWidget(page)
        page.close()
        closed_tab = self._tabs.pop(cur_index)
        cur_index = self._stacked_widget.currentIndex()
        if cur_index >= 0:
            self.switch_page(cur_index)
            tab = self._tabs[cur_index]
            tab.activate(True)
            tab.hi_light(False)
        self.pageClosed.emit(page, closed_tab)

    def switch_page(self, page):
        for tab in self._tabs:
            tab.activate(False)
            tab.hi_light(False)
        if isinstance(page, QWidget):
            self._stacked_widget.setCurrentWidget(page)
        else:
            self._stacked_widget.setCurrentIndex(page)
        cur_tab = self._tabs[self._stacked_widget.currentIndex()]
        cur_tab.activate(True)
        self.pageSwitched.emit(self._stacked_widget.currentWidget(), cur_tab)

    def page(self, index):
        return self._pages[index]

    def pages(self):
        return self._pages

    def widget(self, index):
        return self._stacked_widget.widget(index)

    def current_widget(self) -> QWidget:
        return self._stacked_widget.currentWidget()

    def current_index(self) -> int:
        return self._stacked_widget.currentIndex()

    def page_count(self):
        return self._stacked_widget.count()

    def add_page(self, pd, auto_switch=False) -> QWidget:
        pd = YLink.instance(pd)
        cur_index = self._stacked_widget.currentIndex()
        if cur_index < 0:
            cur_index = 0

        # 创建页签主体Widget
        w = pd.create_target()
        if w.layout() is None:
            w.setLayout(create_layout(layout_flag=pd.layout_flag))
        w.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        # 创建Tab
        tab = self.create_tab(pd, w)

        self._stacked_widget.addWidget(w)
        self._tabs.append(tab)
        self._tab_bar.layout().addWidget(tab)

        self.show_tab_bar()
        if auto_switch:
            self.switch_page(w)
        else:
            self.switch_page(cur_index)  # 不要影响当前页
        return w

    def create_tab(self, pd, page):
        tab = YTab(parent=self,
                   ref_widget=page,
                   title=pd.title,
                   icon=pd.icon,
                   tip_text=pd.tip_text,
                   close_able=self.close_able,
                   )
        tab.SwitchTab.connect(self.switch_page)
        tab.CloseTab.connect(self.close_page)
        return tab

    def show_tab_bar(self):
        self._tab_bar.setVisible(len(self._tabs) > 1 or self.show_single_tab)


class WidgetDragger(QWidget):
    doubleClicked = Signal()

    def __init__(self, window, parent=None):
        QWidget.__init__(self, parent)
        self._windowPos = None
        self._mousePos = None
        self._window = window
        self._mousePressed = False

    def mousePressEvent(self, event):
        self._mousePressed = True
        self._mousePos = event.globalPos()
        self._windowPos = self._window.pos()

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            self._window.move(self._windowPos +
                              (event.globalPos() - self._mousePos))

    def mouseReleaseEvent(self, event):
        self._mousePressed = False

    def mouseDoubleClickEvent(self, event):
        if self._window.windowState() == Qt.WindowState.WindowMaximized:
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self._window.resizeEvent(None)
        self.doubleClicked.emit()


class YWindow(QWidget):
    TITLE_HEIGHT = 22

    def __init__(self, parent=None, full_left=True, object_name=None):
        super().__init__(parent=parent)
        self.ui = QObject(parent=self)
        self.full_left = full_left
        self.setObjectName(object_name)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint)
        self.create_widgets()
        if self.full_left:
            self.full_left_layout()
        else:
            self.v_tile_layout()
        self.refresh_size_bar()

    def create_widgets(self):
        self.ui.top = WidgetDragger(self, parent=self)
        top_layout: QHBoxLayout = create_layout(layout_flag='H')
        top_layout.setSpacing(1)
        self.ui.top.setLayout(top_layout)
        self.ui.title_bar = QWidget(parent=self)
        self.ui.size_bar = self.create_size_bar()
        top_layout.addWidget(self.ui.title_bar, 1)
        top_layout.addWidget(self.ui.size_bar, alignment=Qt.AlignmentFlag.AlignRight)

        self.ui.header = QWidget(parent=self)
        self.ui.header.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.ui.header.setVisible(False)
        self.ui.left = QWidget(parent=self)
        self.ui.left.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.ui.left.setVisible(False)
        self.ui.content = QWidget(parent=self)
        self.ui.content.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.ui.bottom = QWidget(parent=self)
        self.ui.bottom.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.ui.bottom.setVisible(False)

    def full_left_layout(self):
        grid: QGridLayout = create_layout(layout_flag='G2')
        grid.setSpacing(0)
        # +----+------------------------------+
        # |    |  top (title_bar | size_bar)  |
        # |  l +------------------------------+
        # |  e |  header                      |
        # |  f +------------------------------+
        # |  t |  content                     |
        # -----+------------------------------+
        # |        b o t t o m                |
        # +-----------------------------------+
        grid.addWidget(self.ui.left, 0, 0, 3, 1)
        grid.addWidget(self.ui.top, 0, 1, 1, 1)
        grid.addWidget(self.ui.header, 1, 1, 1, 1)
        grid.addWidget(self.ui.content, 2, 1, 1, 1)
        grid.addWidget(self.ui.bottom, 3, 0, 1, 2)
        self.setLayout(grid)

    def v_tile_layout(self):
        """
        垂直平铺布局
        :return:
        """
        grid: QGridLayout = create_layout(layout_flag='G2')
        grid.setSpacing(0)
        # +----+------------------------------+
        # |     top (title_bar | size_bar)    |
        # +-----------------------------------+
        # |     header                        |
        # +------+----------------------------+
        # | left |     c o n t e n t          |
        # +------+----------------------------+
        # |        b o t t o m                |
        # +-----------------------------------+
        grid.addWidget(self.ui.top, 0, 0, 1, 2)
        grid.addWidget(self.ui.header, 1, 0, 1, 2)
        grid.addWidget(self.ui.left, 2, 0, 1, 1)
        grid.addWidget(self.ui.content, 2, 1, 1, 1)
        grid.addWidget(self.ui.bottom, 3, 0, 1, 2)
        self.setLayout(grid)

    def closeEvent(self, event):
        if pop_question('您确定要退出吗?'):
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_size_bar()

    def create_size_bar(self):
        buttons = {
            'min': create_tool_button(trigger=self.showMinimized,
                                      icon=load_icon(img.P_MIN, colored=False),
                                      tip_text='最小化',
                                      ),
            'max': create_tool_button(trigger=self.show_max_or_normal,
                                      icon=load_icon(img.P_MAX, colored=False),
                                      ),
            'close': create_tool_button(trigger=self.close,
                                        icon=load_icon(img.P_CLOSE, colored=False),
                                        tip_text='关闭',
                                        ),
        }
        bar = create_toolbar(buttons=buttons.values(), icon_size=self.TITLE_HEIGHT)
        bar.layout().setContentsMargins(0, 0, 0, 0)
        copy_obj(bar, buttons)
        return bar

    def refresh_size_bar(self):
        btn: QToolButton = getattr(self.ui.size_bar, 'max')
        is_max = self.windowState() == Qt.WindowState.WindowMaximized
        if is_max:
            btn.trigger = self.showNormal
            btn.setIcon(load_icon(img.P_SHOW_NORMAL, colored=False))
            btn.setToolTip('还原')
        else:
            btn.trigger = self.showMaximized
            btn.setIcon(load_icon(img.P_MAX, colored=False))
            btn.setToolTip('最大化')

    def show_max_or_normal(self):
        btn: QToolButton = getattr(self.ui.size_bar, 'max')
        is_max = get_attr(btn, '_is_max', self.windowState() == Qt.WindowState.WindowMaximized)
        if is_max:
            self.showNormal()
        else:
            self.showMaximized()
        set_attr(btn, '_is_max', not is_max)

    def title_bar(self) -> QWidget:
        return self.ui.title_bar

    def content(self) -> QWidget:
        return self.ui.content

    def left_widget(self) -> QWidget:
        return self.ui.left

    def header_widget(self) -> QWidget:
        return self.ui.header

    def bottom_widget(self) -> QWidget:
        return self.ui.bottom


class YNavPanel(QWidget):
    toLink = Signal(YLink)

    def __init__(self, parent=None, icon_size=20, icon_spacing=20, show_group=True, object_name=None):
        super().__init__(parent=parent)
        self.ui = QObject(parent=self)
        self.icon_size = icon_size
        self.icon_spacing = icon_spacing
        self.show_group = show_group
        self._links = {}
        self.setObjectName(object_name)
        self.setup_ui()

    def setup_ui(self):
        self.ui.group_menu = QMenu()
        self.ui.tabs = QTabWidget(parent=self)
        self.ui.tabs.setStyleSheet("pane{border:none;}")
        self.ui.tabs.tabBar().setVisible(False)
        self.ui.tabs.setToolTipDuration(0)
        self.setLayout(create_layout(layout_flag='V'))
        self.layout().addWidget(self.ui.tabs)

    def _add_group(self, group, tab_index):
        group.target = tab_index
        self.ui.group_menu.addAction(QAction(text=group.title, parent=self,
                                             triggered=lambda: self.switch_group(tab_index),
                                             icon=load_icon(group.icon),
                                             statusTip=group.tip_text))

    def add_links(self, group: YLink, items: list[YLink], logo=None):
        widget = create_layout_widget(layout_flag='V')
        widget.layout().setContentsMargins(0, 0, 0, 0)
        # widget.setAutoFillBackground(True)
        self._links[group] = items
        # 导航组切换按钮
        group_btn = create_menu_button(self.ui.group_menu,
                                       title=group.title,
                                       icon_file=group.icon,
                                       hovered=True,
                                       # tool_button=True,
                                       ) if self.show_group else None

        # 导航项->QAction
        actions = []
        for link in items:
            action = QAction(text=link.title,
                             triggered=self.to_link,
                             parent=self,
                             icon=load_icon(link.icon),
                             )
            action.setToolTip(link.tip_text)
            setattr(action, '_link', link)
            actions.append(action)

        # 导航工具条
        tbar = create_toolbar(actions=actions)
        tbar.setOrientation(Qt.Orientation.Vertical)
        tbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tbar.setIconSize(QSize(self.icon_size, self.icon_size))
        tbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tbar.setStyleSheet(f'spacing:{self.icon_spacing}px;')
        tbar.setToolTip(group.tip_text)

        # 添加到widget
        if logo:
            widget.layout().addWidget(logo)
        if group_btn:
            widget.layout().addWidget(group_btn)
            widget.layout().addItem(
                QSpacerItem(2, self.icon_spacing, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        widget.layout().addWidget(tbar)

        # 添加到tab中
        index = self.ui.tabs.addTab(widget, load_icon(group.icon), group.title)
        # 添加导航组
        self._add_group(group, index)

    def to_link(self):
        link = getattr(self.sender(), '_link')
        self.toLink.emit(link)

    def switch_group(self, index):
        grp_lst = list(self._links.keys())
        if not grp_lst:
            return
        group = grp_lst[index]
        tab_index = group.target
        self.ui.tabs.setCurrentIndex(tab_index)

    def showEvent(self, event):
        super().showEvent(event)
        self.switch_group(0)


class YLogo(QWidget):
    def __init__(self, img_file, logo_width=32, logo_height=32, parent=None, on_click=None, object_name=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        vbox = QVBoxLayout(self)
        btn = QPushButton(parent=self)
        btn.setIcon(load_icon(img_file, colored=False))
        btn.setIconSize(QSize(logo_width, logo_height))
        btn.setFlat(True)
        if on_click:
            btn.clicked.connect(on_click)
        vbox.addWidget(btn)


class YearMonthSpin(QWidget):
    valueChanged = Signal(str, int, int)
    yearChanged = Signal(int)
    monthChanged = Signal(int)

    def __init__(self, cur_year=None, cur_month=None, parent=None, object_name=None):
        super().__init__(parent=parent)
        self.setObjectName(object_name)
        if cur_year is None:
            cur_year = datetime.today().year
        if cur_month is None:
            cur_month = datetime.today().month
        self.setLayout(QHBoxLayout(self))
        self.create_spnboxs()
        self._spn_year.setValue(cur_year)
        self._spn_month.setValue(cur_month)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def create_spnboxs(self):
        self._spn_year = QSpinBox(self)
        self._spn_month = QSpinBox(self)
        self._spn_year.setRange(2000, 2099)
        self._spn_year.setSingleStep(1)
        self._spn_year.setSuffix(' 年 ')
        self._spn_month.setRange(1, 12)
        self._spn_month.setSuffix(' 月 ')
        self._spn_month.setSingleStep(1)
        self._spn_month.setWrapping(True)
        # self._spn_month.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.layout().addWidget(self._spn_year)
        self.layout().addWidget(self._spn_month)
        self._spn_year.valueChanged.connect(self.onYearChanged)
        self._spn_month.valueChanged.connect(self.onMonthChanged)

    def enclose_box(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return hbox

    def month_code(self):
        return '%4d%02d' % (self.value())

    def value(self):
        return self.year(), self.month()

    def year(self):
        return self._spn_year.value()

    def month(self):
        return self._spn_month.value()

    def set_monthcode(self, mth_code):
        if mth_code:
            self.set_value(int(mth_code[:4]), int(mth_code[-2:]))

    def set_value(self, y, m):
        self._spn_year.setValue(y)
        self._spn_month.setValue(m)

    def start_date(self):
        y = self.year()
        m = self.month()
        return to_date('%4d-%02d-01' % (y, m))

    def end_date(self):
        y = self.year()
        m = self.month()
        if m >= 12:
            y += 1
            m = 1
        else:
            m += 1
        d = to_date('%4d-%02d-01' % (y, m))
        return d - timedelta(days=1)

    @Slot()
    def onYearChanged(self):
        self.yearChanged.emit(self.year())
        self.valueChanged.emit(self.month_code(), self.year(), self.month())

    @Slot()
    def onMonthChanged(self):
        self.monthChanged.emit(self.month())
        self.valueChanged.emit(self.month_code(), self.year(), self.month())


class YearSpin(QWidget):
    def __init__(self, parent=None, label='年度', value=None, on_change=None, label_left=True, object_name=None):
        super().__init__(parent=parent)
        self.setObjectName(object_name)
        self._label_left = label_left
        self._label = QLabel(label)
        self._spn_year = QSpinBox()
        self._spn_year.setRange(1900, 2999)
        self.set_on_change(on_change)
        if value is None:
            self._spn_year.setValue(datetime.today().year)
        else:
            self._spn_year.setValue(value)

        self.setup_ui()

    def set_on_change(self, on_change):
        if on_change:
            self._spn_year.valueChanged.connect(on_change)

    def setup_ui(self):
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        if self._label_left:
            hbox.addWidget(self._label)
            hbox.addSpacing(2)
            hbox.addWidget(self._spn_year)
        else:
            hbox.addWidget(self._spn_year)
            hbox.addSpacing(2)
            hbox.addWidget(self._label)
        hbox.addStretch()

    def value(self):
        return self._spn_year.value()


class YearSelector(QWidget):
    valueChanged = Signal(int)

    def __init__(self, parent=None, value=None, on_change=None, object_name=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        if value is None:
            value = datetime.now().year
        self._value = value

        self._label = QLabel()
        self._label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        change_font(self._label, bold=True, size=12)

        btn_pre = create_button('', trigger=lambda: self.changeValue(self._value - 1), icon_file=img.P_LEFT)
        btn_next = create_button('', trigger=lambda: self.changeValue(self._value + 1), icon_file=img.P_RIGHT)
        btn_pre.setFlat(True)
        btn_next.setFlat(True)
        btn_pre.setIconSize(QSize(16, 16))
        btn_next.setIconSize(QSize(16, 16))

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        layout.addWidget(btn_pre)
        layout.addWidget(self._label)
        layout.addWidget(btn_next)

        self.setValue(value)
        self.set_on_change(on_change)

    def value(self):
        return self._value

    def changeValue(self, v):
        self.setValue(v)
        self.valueChanged.emit(v)

    def setValue(self, y):
        self._value = y
        self._label.setText('%4d 年' % self._value)

    def set_on_change(self, on_change):
        if on_change:
            self.valueChanged.connect(on_change)


class PeriodSelector(QWidget):
    valueChanged = Signal(object)

    def __init__(self, parent=None, cur_year=None, cur_month=None, ui_mode=0, show_switcher=True, object_name=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        # False-by 年月； True- by 日期段
        self._ui_mode = ui_mode
        self._start_date = self._end_date = datetime.today()
        if cur_year is None:
            cur_year = datetime.today().year
        if cur_month is None:
            cur_month = datetime.today().month
        self._cur_year = cur_year
        self._cur_month = cur_month
        self._set_value_by_period()

        self._w_by_date = self._widget_by_date()
        self._w_by_ym = self._widget_by_ym()

        self._menu = QMenu(self)
        self.tab = QStackedWidget(self)
        self.tab.setMaximumHeight(60)
        self.tab.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.tab.addWidget(self._w_by_ym)
        self.tab.addWidget(self._w_by_date)
        self.tab.setCurrentIndex(self._ui_mode)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tab)
        if show_switcher:
            layout.addSpacing(80)
            layout.addWidget(self.create_mode_switcher())

    # 两个日期选择时间段
    def _widget_by_date(self):
        w = QWidget()
        self.edt_sdate = create_date_edit(self._start_date)
        self.edt_edate = create_date_edit(self._end_date)
        change_font(self.edt_sdate, size=12)
        change_font(self.edt_edate, size=12)

        layout = QHBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        layout.addWidget(QLabel('从'))
        layout.addWidget(self.edt_sdate)
        layout.addWidget(QLabel('至'))
        layout.addWidget(self.edt_edate)

        btn_apply = create_button(trigger=self._apply_date_edit,
                                  icon_file=img.P_REFRESH,
                                  flat=True,
                                  tip_text='确定日期范围')
        layout.addWidget(btn_apply)

        return w

    # 年/月方式
    def _widget_by_ym(self):
        w = QWidget()
        self._label = QLabel()
        self._label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        btn_rev_fst = create_button(trigger=lambda: self._apply_ym(y=-1),
                                    icon_file=img.P_LEFT2,
                                    flat=True,
                                    tip_text='前一年')
        btn_rev = create_button(trigger=lambda: self._apply_ym(m=-1),
                                icon_file=img.P_LEFT,
                                flat=True,
                                tip_text='前一月')
        btn_fwd = create_button(trigger=lambda: self._apply_ym(m=1),
                                icon_file=img.P_RIGHT,
                                flat=True,
                                tip_text='后一月')
        btn_fwd_fst = create_button(trigger=lambda: self._apply_ym(y=1),
                                    icon_file=img.P_RIGHT2,
                                    flat=True,
                                    tip_text='后一年')

        btn_fwd.setIconSize(QSize(16, 16))
        btn_fwd_fst.setIconSize(QSize(16, 16))

        layout = QHBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        layout.addWidget(btn_rev_fst)
        layout.addWidget(btn_rev)
        layout.addWidget(self._label)
        layout.addWidget(btn_fwd)
        layout.addWidget(btn_fwd_fst)

        btn_apply = create_button(trigger=self._apply_ym,
                                  icon_file=img.P_REFRESH,
                                  flat=True,
                                  tip_text='刷新')
        layout.setSpacing(40)
        layout.addWidget(btn_apply)

        self._refresh()
        return w

    def create_mode_switcher(self):
        self._menu.addActions([
            yui.create_action('年/月选择', icon_file=img.P_INDEX, trigger=lambda: self.switch_to(0), parent=self, ),
            yui.create_action('日期段选择', icon_file=img.P_CALENDAR, trigger=lambda: self.switch_to(1), parent=self, ),
        ])
        self._menu.addSeparator()
        self._menu.addActions([
            yui.create_action('自年初起', icon_file=img.P_LOOP, trigger=lambda: self.switch_to(2), parent=self),
            yui.create_action('上年同期', icon_file=img.P_LAST, trigger=lambda: self.switch_to(3), parent=self),
            yui.create_action('下年同期', icon_file=img.P_NEXT, trigger=lambda: self.switch_to(4), parent=self),
        ])

        btn = create_menu_button(self._menu, icon_file=img.P_3DOTS_V, hovered=True)
        return btn

    def switch_to(self, mode):
        if mode in (0, 1):
            self._ui_mode = mode
            self.tab.setCurrentIndex(self._ui_mode)
            return
        self.tab.setCurrentIndex(1)
        if mode == 2:  # 自年初起
            self.edt_sdate.setDate(QDate(self._start_date.year, 1, 1))
        elif mode == 3:  # 上年同期
            self.edt_sdate.setDate(QDate(self._start_date.year - 1, self._start_date.month, self._start_date.day))
            self.edt_edate.setDate(QDate(self._end_date.year - 1, self._end_date.month, self._end_date.day))
        elif mode == 4:  # 下年同期
            self.edt_sdate.setDate(QDate(self._start_date.year + 1, self._start_date.month, self._start_date.day))
            self.edt_edate.setDate(QDate(self._end_date.year + 1, self._end_date.month, self._end_date.day))
        self._apply_date_edit()

    def set_date_pair(self, start_date, end_date):
        self.switch_to(1)  # 按照日期段方式设置，强制切换为日期段选择
        self._start_date, self._end_date = to_date(start_date), to_date(end_date)
        self.edt_sdate.setDate(QDate(self._start_date.year, self._start_date.month, self._start_date.day))
        self.edt_edate.setDate(QDate(self._end_date.year, self._end_date.month, self._end_date.day))

    def value(self) -> (object, object):
        return self._start_date, self._end_date

    def str_value(self) -> (str, str):
        return format_date(self._start_date), format_date(self._end_date)

    def _apply_date_edit(self):
        self._start_date = self.edt_sdate.date().toPython()
        self._end_date = self.edt_edate.date().toPython()
        self.valueChanged.emit(self)

    def _apply_ym(self, y=0, m=0):
        ny = self._cur_year + y
        nm = self._cur_month + m
        if nm > 12:
            nm = 1
            ny += 1
        if nm < 1:
            nm = 12
            ny -= 1
        self._cur_year = ny
        self._cur_month = nm
        self._set_value_by_period()
        self._refresh()
        self.valueChanged.emit(self)

    def _refresh(self):
        change_font(self._label, size=12, bold=True)
        self._label.setText(' %4d 年 %2d 月' % (self._cur_year, self._cur_month))

    def _set_value_by_period(self):
        self._start_date = to_date('%4d-%02d-01' % (self._cur_year, self._cur_month))
        y = self._cur_year
        m = self._cur_month
        if m >= 12:
            y += 1
            m = 1
        else:
            m += 1
        d = to_date('%4d-%02d-01' % (y, m))
        self._end_date = d - timedelta(days=1)

    def month_code(self):
        return '%4d%2d' % (self._cur_year, self._cur_month)

    def set_month_code(self, mth_code):
        if mth_code:
            (self._cur_year, self._cur_month) = (int(mth_code[:4]), int(mth_code[-2:]))
            self._set_value_by_period()
        self._refresh()

    def year(self):
        return self._cur_year

    def month(self):
        return self._cur_month

    def start_date(self):
        return self._start_date

    def end_date(self):
        return self._end_date

    def enclose_box(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return hbox


class TabInfo:
    def __init__(self, title, icon=None, w_class=None, layout_flag=None):
        self.title = title
        self.icon = icon if icon else img.P_4_DOTS
        self.w_class = w_class if w_class else QWidget
        self.layout_flag = layout_flag if layout_flag else 'V'


class TabSetting:
    """
    描述多页签信息
    """

    def __init__(self, *args, stretch=True):
        """
        多页签信息。
        :param stretch: 切换按钮栏是否在右部留白。False - 不留白，按钮会均匀分布占满顶部栏位; True - 右部留白
        :param args: 可以是字符串列表或字典列表。
        如果是字典或TabInfo的列表，每个元素对应一个页签的描述，分别为:
            'title':    标题
            'icon':     图标文件名，默认为 'bullet3.png'
            'w_class':  页Widget类，默认为QWidget
            'layout_flag': 页布局标记，默认为'V'
        如果是字符串列表，创建的页签使用列表元素作为标题，其它属性为默认值。
        """
        self._data = []
        self.stretch = stretch
        for arg in args:
            if is_collection(arg):
                self._data.extend(arg)
            else:
                if type(arg) is str:  # 只使用标题
                    self._data.append(TabInfo(arg))
                else:
                    r = TabInfo('')
                    copy_obj(r, arg)
                    self._data.append(r)

    def count(self):
        return len(self._data)

    def items(self):
        return self._data

    def index_of(self, index):
        tab_index = 0
        if isinstance(index, int):
            if index < 0 or index > len(self._data) - 1:
                raise IndexError(f'子页面数量：{len(self._data)}', index)
            tab_index = index
        else:
            str_index = str(index).strip()
            for index, text in enumerate([t.title for t in self._data]):
                if str_index == text.strip():
                    tab_index = index
        return tab_index

    def item(self, index):
        return self._data[self.index_of(index)]


class YStackedPages(QWidget):
    WIDGET_TAG = '_widget'
    LAYOUT_TAG = '_m_layout'

    """
    用StackedWidget和ButtonGroup组合的多页面组件.
    """

    def __init__(self, page_def: TabSetting = None, parent=None, on_switch=None, object_name=None):
        """
        初始化方法
        :param page_def: 页签定义信息
        :param parent:
        :param on_switch:
        """
        super().__init__(parent=parent)
        self._button_group = QButtonGroup(parent=self)
        self._pages = QStackedWidget(parent=self)
        self._tab_bar = self.create_tab_bar()
        self._on_switch = on_switch
        self._page_def = page_def
        self.setObjectName(object_name)

        self.setLayout(create_layout('V'))
        # 页签按钮栏
        self.layout().addWidget(self._tab_bar)
        # 页签窗体
        self.layout().addWidget(self._pages)

        # 创建各个页签以及切换按钮
        for pd in self._page_def.items():
            self.add_page(pd)

        if self._page_def.stretch:
            self._tab_bar.layout().addStretch(0)  # 右部留白

    def create_tab_bar(self):
        w = create_layout_widget(QWidget, parent=self, layout_flag='H')
        # w.layout().setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
        w.layout().setSpacing(12)
        w.layout().setContentsMargins(0, 8, 0, 8)
        return w

    def switch_widget(self):
        btn = self.sender()
        widget = get_attr(btn, self.WIDGET_TAG)
        self._pages.setCurrentWidget(widget)
        if self._on_switch:
            self._on_switch(self._pages, widget)

    def page(self, idx):
        buttons = self._button_group.buttons()
        widget_index = self._page_def.index_of(idx)
        return get_attr(buttons[widget_index], self.WIDGET_TAG)

    def pages(self):
        return self._pages

    def page_layout(self, idx) -> QLayout:
        return get_attr(self.page(idx), self.LAYOUT_TAG)

    def add_page(self, pd):
        cur_index = self._pages.currentIndex()
        if cur_index < 0:
            cur_index = 0

        # 创建页签Widget
        w = create_layout_widget(pd.w_class, layout_flag='V')
        layout = create_layout(layout_flag=pd.layout_flag)
        set_attr(w, self.LAYOUT_TAG, layout)
        w.layout().addLayout(layout)
        w.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self._pages.addWidget(w)

        # 创建切换按钮
        button = create_button(text=pd.title,
                               trigger=self.switch_widget,
                               flat=True,
                               icon_file=pd.icon)
        button.setCheckable(True)
        set_attr(button, self.WIDGET_TAG, w)  # 将表单对象保存到按钮对象的属性中供切换按钮时获取
        self._button_group.addButton(button)
        self._button_group.setExclusive(True)
        self._tab_bar.layout().addWidget(button)
        self._pages.setCurrentIndex(cur_index)  # 不要影响当前页
        self.show_buttons()

    def show_buttons(self):
        self._tab_bar.setVisible(len(self._button_group.buttons()) > 1)


class YPercentCircle(QWidget):
    def __init__(self, parent=None, object_name=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.value = 0
        self.width = 100
        self.height = 100
        self.progress_width = 10
        self.progress_rounded_cap = True
        self.progress_color = QColor(0, 137, 255)
        self.max_value = 100
        self.font_family = "Arial"
        self.font_size = 16
        self.suffix = "%"
        self.text_color = QColor(192, 192, 192)
        self.enable_bg = True
        self.bg_color = QColor(220, 220, 220)
        """
        通过修改以下属性来自定义组件外观：
        progress.progress_width = 15  # 圆环宽度
        progress.progress_color = QColor(255, 0, 127)  # 粉红色进度条
        progress.bg_color = QColor(240, 240, 240)  # 浅灰色背景
        progress.text_color = QColor(70, 70, 70)  # 深灰色文字
        progress.font_size = 16  # 更大的字体
        progress.suffix = "％"  # 使用全角百分号
        """
        # 设置默认大小
        self.setMinimumSize(self.width, self.height)

    def set_value(self, value):
        self.value = value
        self.update()  # 触发重绘

    def paintEvent(self, event):
        # 设置长宽
        width = self.width - self.progress_width
        height = self.height - self.progress_width
        margin = self.progress_width / 2
        value = self.value * 360 / self.max_value

        # 绘制器
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 创建矩形区域
        rect = QRectF(margin, margin, width, height)

        # 绘制背景圆环
        if self.enable_bg:
            pen = QPen()
            pen.setColor(self.bg_color)
            pen.setWidth(self.progress_width)
            if self.progress_rounded_cap:
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            paint.setPen(pen)
            paint.drawArc(rect, 0, 360 * 16)

        # 绘制进度圆环
        pen = QPen()
        pen.setColor(self.progress_color)
        pen.setWidth(self.progress_width)
        if self.progress_rounded_cap:
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        paint.setPen(pen)
        paint.drawArc(rect, 90 * 16, -value * 16)

        # 绘制文本
        font = QFont(self.font_family, self.font_size)
        font.setBold(True)
        paint.setFont(font)
        paint.setPen(QColor(self.text_color))
        paint.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self.value}{self.suffix}")

        paint.end()


class YPercentBar(QWidget):
    def __init__(self, parent=None, value=0.0, orientation=Qt.Orientation.Vertical, object_name=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.value = value
        self.orientation = orientation
        self.setObjectName(object_name)
        self.setup_ui()
        self.set_orientation(self.orientation)
        self.set_value(self.value)

    def setup_ui(self):
        self.setLayout(create_layout(layout_flag='V'))
        pbar = QProgressBar(parent=self, minimum=0, maximum=100)
        pbar.setObjectName('pbar')
        pbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(pbar)

    def set_value(self, value):
        self.value = value
        pbar: QProgressBar = self.findChild(QProgressBar, 'pbar')
        pbar.setValue(self.value)

    def set_orientation(self, value):
        self.orientation = value
        pbar: QProgressBar = self.findChild(QProgressBar, 'pbar')
        pbar.setOrientation(self.orientation)


class YCard(QFrame):
    def __init__(self, title_text,
                 items: list[object],
                 parent=None,
                 grid_col_num=3,
                 title_icon=None,
                 title_alignment=Qt.AlignmentFlag.AlignCenter,
                 caption_alignment=Qt.AlignmentFlag.AlignLeft,
                 value_alignment=Qt.AlignmentFlag.AlignRight,
                 comment_alignment=Qt.AlignmentFlag.AlignLeft,
                 bg_color=None,
                 on_title_clicked=None,
                 tag=None,
                 object_name=None,
                 ):
        super().__init__(parent=parent)
        self.title_text = title_text
        self.title_icon = title_icon
        self.title_alignment = title_alignment
        self.caption_alignment = caption_alignment
        self.value_alignment = value_alignment
        self.comment_alignment = comment_alignment
        self.setObjectName(object_name)
        self.items = items
        self.on_title_clicked = on_title_clicked
        self.tag = tag
        self.grid_col_num = grid_col_num
        self.background_color = bg_color
        self.ui = Obj()
        self.setup_ui()

    @staticmethod
    def format_value(v) -> str:
        if v is None:
            return ''
        if isinstance(v, str):
            return v
        if isinstance(v, Decimal) or isinstance(v, float):
            return f"{to_float(v):,.2f}"
        return str(v)

    def setup_ui(self):
        self.setMinimumSize(QSize(100, 50))
        gbox = QGridLayout()
        gbox.setHorizontalSpacing(16)
        gbox.setVerticalSpacing(8)
        self.setLayout(gbox)
        self.ui.title = YTitle(self.title_text,
                               parent=self,
                               icon_path=self.title_icon,
                               alignment=self.title_alignment,
                               icon_size=QSize(20, 20),
                               font_size=12,
                               on_click=self.on_title_clicked,
                               click_param=self.tag,
                               )
        gbox.addWidget(self.ui.title, 0, 0, 1, self.grid_col_num)
        row = 1
        for i, item in enumerate(self.items):
            caption = get_attr(item, 'caption', '')
            value = get_attr(item, 'value', '')
            comment = get_attr(item, 'comment', '')

            lb_caption = QLabel(f"{caption}", alignment=self.caption_alignment)
            lb_value = QLabel(self.format_value(value), alignment=self.value_alignment)
            lb_comment = QLabel(f"{comment}", alignment=self.comment_alignment)

            color = get_attr(item, 'color')
            if color:
                set_label_color(lb_value, fore_color=color)
            color = get_attr(item, 'caption_color')
            if color:
                set_label_color(lb_caption, fore_color=color)
            color = get_attr(item, 'comment_color')
            if color:
                set_label_color(lb_comment, fore_color=color)

            font_size = get_attr(item, 'font_size')
            if font_size:
                change_font(lb_value, size=font_size)

            gbox.addWidget(lb_caption, row + i, 0)
            gbox.addWidget(lb_value, row + i, 1)
            gbox.addWidget(lb_comment, row + i, 2)
            set_attr(self.ui, f'lb_value_{i}', lb_value)
        self.set_background_color(self.background_color)

    def update_items(self, items):
        self.items = items
        for i, item in enumerate(self.items):
            value = get_attr(item, 'value', '')
            lb: QLabel = get_attr(self.ui, f'lb_value_{i}')
            if lb:
                lb.setText(self.format_value(value))

    def set_background_color(self, bg_color):
        self.background_color = bg_color
        if self.background_color:
            self.setStyleSheet(f"background-color:{self.background_color};border-radius: 12px;")


class YSlideBoard(QWidget):
    def __init__(self, parent=None, object_name=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self._widget_width = 200
        self._button_size = QSize(40, 100)
        self._spacing = 10

        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 左按钮
        self.left_button = QPushButton("◀")
        self.left_button.setFlat(True)
        self.left_button.setFixedSize(self._button_size)
        self.left_button.setVisible(False)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # 容器widget
        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(self._spacing)

        self.scroll_area.setLayout(QHBoxLayout())
        self.scroll_area.setWidget(self.container)

        # 右按钮
        self.right_button = QPushButton("▶")
        self.right_button.setFlat(True)
        self.right_button.setFixedSize(self._button_size)
        self.right_button.setVisible(False)

        self.main_layout.addWidget(self.left_button)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.right_button)

    def _setup_connections(self):
        self.left_button.clicked.connect(self._slide_left)
        self.right_button.clicked.connect(self._slide_right)

    def set_button_size(self, size: QSize):
        self._button_size = size
        self.left_button.setFixedSize(size)
        self.right_button.setFixedSize(size)

    def set_widget_width(self, width: int):
        self._widget_width = width
        for i in range(self.container_layout.count()):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setFixedWidth(width)
        self._update_container_size()
        self._check_buttons_needed()  # 新增：立即检查按钮是否需要显示

    def set_spacing(self, spacing: int):
        self._spacing = spacing
        self.container_layout.setSpacing(spacing)
        self._update_container_size()
        self._check_buttons_needed()  # 新增：立即检查按钮是否需要显示

    def add_widget(self, widget: QWidget):
        widget.setFixedWidth(self._widget_width)
        widget.setMinimumHeight(150)
        self.container_layout.addWidget(widget)
        self._update_container_size()
        self._check_buttons_needed()  # 新增：立即检查按钮是否需要显示

    def _update_container_size(self):
        count = self.container_layout.count()
        total_width = count * (self._widget_width + self._spacing) - self._spacing
        self.container.setFixedSize(total_width, self.height())

    def _check_buttons_needed(self):
        """新增方法：检查是否需要显示滑动按钮"""
        if not self.isVisible():
            return

        # 强制更新布局，确保获取正确的尺寸
        self.updateGeometry()
        QApplication.processEvents()

        container_width = self.container.width()
        viewport_width = self.scroll_area.viewport().width()

        # 如果内容宽度大于可视区域宽度，则需要显示按钮
        needs_buttons = container_width > viewport_width

        self.right_button.setVisible(needs_buttons)
        self.left_button.setVisible(needs_buttons and
                                    self.scroll_area.horizontalScrollBar().value() > 0)

    def _slide_left(self):
        scroll_bar = self.scroll_area.horizontalScrollBar()
        current = scroll_bar.value()
        step = self._widget_width + self._spacing
        scroll_bar.setValue(max(0, current - step))
        self._update_button_visibility()

    def _slide_right(self):
        scroll_bar = self.scroll_area.horizontalScrollBar()
        current = scroll_bar.value()
        step = self._widget_width + self._spacing
        max_val = scroll_bar.maximum()
        scroll_bar.setValue(min(max_val, current + step))
        self._update_button_visibility()

    def _update_button_visibility(self):
        scroll_bar = self.scroll_area.horizontalScrollBar()
        current_scroll = scroll_bar.value()
        max_scroll = scroll_bar.maximum()

        self.left_button.setVisible(current_scroll > 0)
        self.right_button.setVisible(current_scroll < max_scroll)

    def showEvent(self, event):
        """重写showEvent以确保窗口显示时正确计算按钮可见性"""
        super().showEvent(event)
        self._check_buttons_needed()

    def resizeEvent(self, event):
        self._update_container_size()
        self._check_buttons_needed()
        super().resizeEvent(event)


class YSortableItem(QTableWidgetItem):
    DR_AttrName = 'DATA_ROLE_OF_SORT'

    def set_data_role_of_sort(self, data_role: Qt.ItemDataRole):
        set_attr(self, YSortableItem.DR_AttrName, data_role)

    def data_role_of_sort(self):
        return get_attr(self, YSortableItem.DR_AttrName, Qt.ItemDataRole.UserRole)

    def __lt__(self, other):
        # 比较原始数值,用于排序
        role = self.data_role_of_sort()
        d1, d2 = self.data(role), other.data(role)
        if d1 is None:
            return True
        if d2 is None:
            return False
        return d1 < d2


class YSortableTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('gridline-color:palette(Midlight)')
        self.setMouseTracking(True)
        self.original_style = None
        self.current_cell = (-1, -1)
        self.sort_orders = {}
        self.setSortingEnabled(True)  # 启用表头排序
        self.horizontalHeader().clicked.connect(self.header_clicked)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)  # 改为单元格选择

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item:
            row, col = item.row(), item.column()
            self.highlight_cell(row, col)
        super().mouseMoveEvent(event)

    def header_clicked(self, col_index):
        order = self.sort_orders.get(col_index, Qt.SortOrder.DescendingOrder)
        order = Qt.SortOrder.DescendingOrder if order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.DescendingOrder
        self.sortByColumn(col_index, order)
        self.horizontalHeader().setSortIndicator(col_index, order)
        self.sort_orders[col_index] = order

    def highlight_cell(self, row, col):
        # 恢复之前高亮的单元格
        if self.current_cell != (-1, -1):
            prev_item = self.item(*self.current_cell)
            if prev_item and self.original_style:
                prev_item.setForeground(self.original_style)

        # 高亮当前单元格
        item = self.item(row, col)
        if item:
            self.original_style = item.foreground()
            item.setForeground(yui.current_theme.hover_color())
            self.current_cell = (row, col)

    def adjust_column_width(self):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)


def show_widget(target: QWidget | YLink):
    m_win = get_mainwindow()
    fn_show_widget = get_attr(m_win, "show_widget")
    if isinstance(target, YLink) and fn_show_widget is not None:
        fn_show_widget(target)
    elif isinstance(target, QWidget):
        if fn_show_widget is not None:
            fn_show_widget(YLink(target.windowTitle(), icon=img.P_DOC, target=target))
        else:
            set_attr(m_win, '_target_widget_', target)
            target.show()


def switch_to_widget(widget: QWidget):
    m_win = get_mainwindow()
    fn = get_attr(m_win, "switch_to_widget")
    if fn:
        fn(widget)


class Redirector(QObject):
    displayText = Signal(str)
    reset = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def write(self, text):
        self.displayText.emit(str(text))

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def start_fn(self, func, *args, **kwargs):
        """
        执行函数，并重定向输出
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        saved_streams = sys.stdin, sys.stdout  # 保存标准输入输出对象，以便恢复
        sys.stdout = self
        sys.stderr = sys.stdout
        self.reset.emit()
        result = func(*args, **kwargs)
        sys.stdin, sys.stdout = saved_streams
        return result
