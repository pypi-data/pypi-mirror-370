# ytree.py - 通用树形显示控件
from typing import Any

from PySide6.QtCore import Qt, QSize, Signal, QModelIndex
from PySide6.QtWidgets import (
    QTreeView, QAbstractItemView
)

from .ymodel import YTreeModel


class YTreeView(QTreeView):
    """
    支持YTreeModel的树形组件
    """
    itemChanged = Signal(QModelIndex, object)

    def __init__(self, parent=None,
                 model: YTreeModel = None,
                 hidden_columns=None,
                 show_grid=False,
                 ):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setIconSize(QSize(12, 12))
        self.setUniformRowHeights(True)
        self.hidden_columns = hidden_columns if hidden_columns is not None else []
        self._model = None
        if model:
            self.setup_with_model(model)
        self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        if show_grid:
            self.set_grid()

    def item_changed(self):
        index = self.currentIndex()
        if self._model:
            row_dat = self._model.data(index, Qt.ItemDataRole.UserRole)
            self.itemChanged.emit(index, row_dat)

    def setup_with_model(self, model: YTreeModel) -> None:
        self.setModel(model)
        col_index = 0
        for col in self._model.columns:
            if col in self.hidden_columns:
                continue
            self.setColumnWidth(col_index, 100)
            col_index = col_index + 1

    def setModel(self, model, /):
        self._model = model
        super().setModel(model)
        if model and model.rowCount() > 0:
            self.selectionModel().selectionChanged.connect(self.item_changed)

    def get_selected_data(self, role=Qt.ItemDataRole.UserRole) -> Any:
        indexes = self.selectedIndexes()
        return indexes[0].data(role) if indexes else None

    def set_columns_width(self, columns_width: list):
        if not columns_width:
            return
        d = columns_width if columns_width is dict else {i: c for i, c in enumerate(columns_width)}
        for c, w in d.items():
            c_idx = c if type(c) is int else self._model.columns.index(c)
            if 0 <= c_idx < len(self._model.columns):
                self.setColumnWidth(c_idx, w)

    def set_grid(self):
        self.setStyleSheet("""
            QTreeView {
                show-decoration-selected: 0;
                gridline-color: palette(Midlight);
            }
            QTreeView::item {
                border: 1px solid palette(Midlight);
                border-top-color: transparent;
                border-left-color: transparent;
                border-right-color: palette(Midlight);
                border-bottom-color: palette(Midlight);
            }
            QTreeView::item:selected {
                background-color: palette(Highlight);
                color: palette(HighlightedText);
            }
        """)

        """
        QHeaderView::section
        {
            background-color:  # f0f0f0;
            border: 1px solid  # c0c0c0;
        }
        """

    def expand_root(self):
        model = self.model()
        root_index = self.rootIndex()  # 获取根索引
        for i in range(model.rowCount(root_index)):
            child_index = model.index(i, 0, root_index)
            self.expand(child_index)  # 展开一级节点
