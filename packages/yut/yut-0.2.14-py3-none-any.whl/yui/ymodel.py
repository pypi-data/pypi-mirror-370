# -*- ymodel.py: python ; coding: utf-8 -*-
#####################################################
# MVC机制下的Model类
#####################################################
import os
from typing import Callable, Any, List, Optional

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QAbstractItemModel, QSize
from pandas import DataFrame

from . import TranslateDirection, filename_for_save, alignment_flag
from .yfield import FACTORY
from yus import ColumnSpec, Op
from yut import is_collection, format_obj, get_attr, set_attr, is_execute_able


class PandasModel(QAbstractTableModel):

    def __init__(self,
                 data: DataFrame,
                 spec: list[ColumnSpec],
                 display_columns: list[str] = None,
                 custom_style_handler: Callable = None,
                 for_edit=False):
        """
        Pandas DataFrame 模型
        :param data: Pandas DataFrame
        :param spec: 列规格列表
        :param display_columns: 显示列名称
        :param custom_style_handler: 单元格格式处理函数，签名：(role:ForegroundRole|BackgroundRole|FontRole, index, col_name, cell_data)->Any
        :param for_edit: 模型的数据是否可以修改
        """
        super().__init__()
        self._data = data
        self._spec = {get_attr(o, 'name'): ColumnSpec.from_obj(o) for o in spec} if spec else {}
        self._display_columns = display_columns if display_columns is not None else self._data.columns.tolist()
        self.for_edit = for_edit
        self._custom_style_handler = custom_style_handler
        self._sort_order = [False] * len(self._display_columns)
        self._current_row_number = 0 if self.rowCount() > 0 else -1
        self._field_painters = {name: FACTORY.get_painter(spec) for name, spec in self._spec.items()}
        self._merged_cells = {}
        self._merged_columns = []
        self._cache = {}

    def set_display_columns(self, display_columns: list[str] = None):
        self._display_columns = display_columns if display_columns is not None else self._data.columns.tolist()

    def set_custom_style_handler(self, style_handler):
        self._custom_style_handler = style_handler

    def custom_style_handler(self):
        return self._custom_style_handler

    def update_data(self, data):
        self._data = data
        self._current_row_number = 0 if self.rowCount() > 0 else -1
        self._cache.clear()

    def load(self, data, spec: list):
        self._data = data
        self._spec = {sp.name: sp for sp in spec}
        self._current_row_number = 0 if self.rowCount() > 0 else -1
        self._cache.clear()

    def data_frame(self):
        return self._data

    def column_spec(self, col: int | str) -> ColumnSpec:
        if isinstance(col, int):
            keys_list = list(self._spec.keys())
            index = col if col >= 0 else len(keys_list) + col  # 可以指定负数，从尾部取索引
            return self._spec.get(keys_list[index])
        else:
            return self._spec[col]

    def column_specs(self):
        return self._spec.values()

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return len(self._display_columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        # 使用缓存
        cache_key = (index.row(), index.column(), role)
        if cache_key in self._cache:
            return self._cache[cache_key]
        ret = self._real_data(index, role)
        self._cache[cache_key] = ret
        return ret

    def _real_data(self, index, role):
        col_name = self._display_columns[index.column()]
        spec = self.column_spec(col_name)
        field_painter = self._field_painters.get(col_name)
        row_dat = self.data_of_row(index.row())
        cell_data = row_dat[col_name]  # self._data.iloc[index.row()][col_name] #

        if role == Qt.ItemDataRole.EditRole:
            return cell_data

        if role == Qt.ItemDataRole.UserRole:  # 返回当前行对象
            col_name = self._display_columns[index.column()]
            row_dat['_value'] = row_dat[col_name]
            return row_dat

        if role == Qt.ItemDataRole.DisplayRole:
            if field_painter:
                return field_painter.get_text(cell_data, row_dat)
            else:
                return '' if pd.isna(cell_data) or cell_data is None else str(cell_data)

        if role == Qt.ItemDataRole.ToolTipRole:  # 使用ToolTipRole处理链接跳转信息
            if spec.is_link():
                return get_attr(spec, 'link_to')

        if self._custom_style_handler:  # 如果定义了格式处理函数，调用并优先使用。
            ret = self._custom_style_handler(role, index, col_name, cell_data)
            if ret is not None:
                return ret

        if role == Qt.ItemDataRole.TextAlignmentRole:
            alignment = get_attr(spec, 'alignment')
            if alignment:  # 优先使用列规格中的对齐属性
                return alignment_flag(alignment)
            elif field_painter:
                fp_align = get_attr(field_painter, 'alignment')
                if fp_align:
                    return fp_align() if is_execute_able(fp_align) else alignment_flag(fp_align)
            else:
                return Qt.AlignmentFlag.AlignCenter

        return None

    def data_of_row(self, row_num):
        return self._data.iloc[row_num].to_dict()

    def current_row_number(self):
        return self._current_row_number

    def data_of_current_row(self):
        if self._current_row_number >= 0:
            return self.data_of_row(self._current_row_number)
        else:
            return None

    def set_current_row_number(self, row_number):
        if 0 <= row_number < self.rowCount():
            self._current_row_number = row_number

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:  # 列标题
                col_name = self._display_columns[section]
                return self.column_spec(col_name).title
            else:  # 行标题
                # row_dat = self.data_of_row(section)
                # col = self._display_columns[0]
                return f"{section + 1:d}"
        else:
            return super().headerData(section, orientation, role)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            col_name = self._display_columns[index.column()]
            self._data.iat[index.row(), col_name] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
            return True
        return False

    def setForEdit(self, value):
        self.for_edit = value

    def isForEdit(self):
        return self.for_edit

    def flags(self, index):
        if self.isForEdit():
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def sort(self, column, order=...):
        self.layoutAboutToBeChanged.emit()
        order = self._sort_order[column]
        self._data = self._data.sort_values(by=self._display_columns[column], ascending=order)
        self._sort_order[column] = not self._sort_order[column]
        self._cache.clear()
        self.layoutChanged.emit()

    def updateMergedCells(self, columns_to_merge):
        self._merged_cells = {}
        self._merged_columns = columns_to_merge
        self._cache.clear()

        for col_name in columns_to_merge:
            if col_name not in self._display_columns:
                continue

            col_idx = self._display_columns.index(col_name)
            current_value = None
            start_row = 0

            for row in range(len(self._data)):
                value = self._data.iloc[row, self._data.columns.get_loc(col_name)]

                if value != current_value:
                    # 只有当有连续相同值时才合并
                    if current_value is not None and row > start_row:
                        span_rows = row - start_row
                        self._merged_cells[(start_row, col_idx)] = (span_rows, 1)
                    current_value = value
                    start_row = row

            # 处理最后一段
            if current_value is not None and len(self._data) > start_row:
                span_rows = len(self._data) - start_row
                if span_rows > 1:
                    self._merged_cells[(start_row, col_idx)] = (span_rows, 1)

    def span(self, index):
        return self._merged_cells.get((index.row(), index.column()), (1, 1))

    def summary(self, col_name):
        return 0.0 if self._data.empty else self._data[col_name].sum()

    def sort_order(self, column) -> bool:
        return self._sort_order[column]

    def export(self, filename=None, file_format='excel', select_file=False):
        ext, fn = {'excel': ('xlsx',
                             lambda f, columns, headers: self._data.to_excel(f, sheet_name='data',
                                                                             columns=columns,
                                                                             header=headers,
                                                                             engine='openpyxl')),
                   'csv': ('csv',
                           lambda f, columns, headers: self._data.to_csv(f, columns=columns, header=headers,
                                                                         encoding='utf-8')),
                   'html': ('html',
                            lambda f, columns, headers: self._data.to_html(f, columns=columns, header=headers, )),
                   'markdown': ('md',
                                lambda f, columns, headers:
                                self._data.to_markdown(f, columns=columns, header=headers, )),
                   }[file_format]
        if not filename or select_file:
            path = filename if filename else os.curdir
            filename = filename_for_save(path=path, caption=f'请选择待保存的{file_format}文件位置和文件名称',
                                         file_filter=f"*.{ext}")
        elif not filename.endswith(ext):
            filename = f"{filename}.{ext}"
        exp_columns = self._display_columns
        exp_headers = [self.column_spec(c).title for c in exp_columns]
        if filename:
            fn(filename, exp_columns, exp_headers)
            return filename
        else:
            return None


class YTreeItem:
    """Y系列树节点基类"""

    def __init__(self, data: List[Any], parent=None):
        self.item_data = data
        self.parent_item = parent
        self.child_items = []
        self.has_children = False

    def appendChild(self, item) -> None:
        self.child_items.append(item)
        item.parent_item = self
        self.has_children = True

    def child(self, row: int) -> Optional['YTreeItem']:
        return self.child_items[row] if 0 <= row < len(self.child_items) else None

    def childCount(self) -> int:
        return len(self.child_items)

    def row(self) -> int:
        return self.parent_item.child_items.index(self) if self.parent_item else 0

    def data(self, column: int) -> Any:
        return self.item_data[column] if 0 <= column < len(self.item_data) else None

    def parent(self) -> Optional['YTreeItem']:
        return self.parent_item


class YTreeModel(QAbstractItemModel):
    """
    Y系列通用树模型
    """

    def __init__(self,
                 data: pd.DataFrame,
                 spec: list[ColumnSpec],
                 id_extractor: Callable[[Any], str],
                 parent_id_extractor: Callable[[Any], str],
                 caption_exp=None,
                 display_columns: Optional[List[str]] = None,
                 icon_provider: Optional[Callable[[YTreeItem], Any]] = None,
                 parent=None):
        super().__init__(parent)
        self._data = data
        self._spec = {get_attr(o, 'name'): ColumnSpec.from_obj(o) for o in spec}
        self._field_painters = {name: FACTORY.get_painter(spec) for name, spec in self._spec.items()}
        self.id_extractor = id_extractor
        self.parent_id_extractor = parent_id_extractor
        self.icon_provider = icon_provider
        self.caption_exp = caption_exp

        self.columns = display_columns if display_columns else list(data.columns)
        self.records = self._data.to_dict('records')
        self.root_item = YTreeItem([""] * len(self.columns))
        self.nodes = {}
        self._setup_model_data()

    def column_spec(self, col: int | str) -> ColumnSpec:
        if isinstance(col, int):
            keys_list = list(self._spec.keys())
            index = col if col >= 0 else len(keys_list) + col  # 可以指定负数，从尾部取索引
            return self._spec.get(keys_list[index])
        else:
            return self._spec[col]

    def column_specs(self):
        return self._spec.values()

    def _setup_model_data(self) -> None:
        # sorted_data = self._data.to_dict('records')
        sorted_data = sorted(self.records, key=lambda x: len(str(self.id_extractor(x))))
        self.nodes[''] = self.root_item

        for item in sorted_data:
            item_id = str(self.id_extractor(item))
            item_data = [str(item.get(col, "")) for col in self.columns]
            new_node = YTreeItem(item_data)
            set_attr(new_node, 'record', item)

            parent_id = str(self.parent_id_extractor(item))
            parent_node = self.nodes.get(parent_id, self.root_item)

            parent_node.appendChild(new_node)
            self.nodes[item_id] = new_node

        self._mark_has_children()

    def _mark_has_children(self) -> None:
        def process_item(item: YTreeItem) -> None:
            for i in range(item.childCount()):
                child = item.child(i)
                if child.childCount() > 0:
                    child.has_children = True
                process_item(child)

        process_item(self.root_item)

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_item = self._get_item(parent)
        child_item = parent_item.child(row)
        return self.createIndex(row, column, child_item) if child_item else QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.parent()
        return QModelIndex() if parent_item == self.root_item else self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._get_item(parent).childCount()

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.columns) + 1  # 多一个空列，确保最右侧的列宽度准确

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        item = index.internalPointer()
        column = index.column()
        is_blank = column >= len(self.columns) or column < 0

        col_name = self.columns[column] if not is_blank else ''
        cell_data = item.data(column) if not is_blank else ''
        row_dat = {col: item.data(i) for i, col in enumerate(self.columns)} if not is_blank else {}
        field_painter = self._field_painters.get(col_name) if not is_blank else None

        if role == Qt.ItemDataRole.EditRole:
            return cell_data

        if role == Qt.ItemDataRole.DisplayRole:
            if field_painter:
                return field_painter.get_text(cell_data, row_dat)
            else:
                return None if pd.isna(cell_data) else str(cell_data)

        if role == Qt.ItemDataRole.UserRole:
            return row_dat

        if role == Qt.ItemDataRole.DecorationRole and column == 0 and self.icon_provider:
            return self.icon_provider(item)

        if role == Qt.ItemDataRole.TextAlignmentRole and not is_blank:
            spec = self.column_spec(col_name)
            alignment = get_attr(spec, 'alignment')
            if alignment:
                return alignment_flag(alignment)
            if field_painter:
                return field_painter.alignment()

        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(-1, 24)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            col = self.columns[section] if section < len(self.columns) else None
            return self.column_spec(col).title if col else None
        return None

    def _get_item(self, index: QModelIndex) -> YTreeItem:
        return index.internalPointer() if index.isValid() else self.root_item

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def data_frame(self):
        return self._data


def add_qc_value(o, attr, op: Op, value):
    v = (op.value, value)
    if isinstance(o, dict):
        o[attr] = v
    else:
        setattr(o, attr, v)
    return o


def translate_olist(direction: TranslateDirection, lookup, v_from, olist):
    """
    翻译对象属性
    :param direction: 翻译的方向: 正向 lookup[0] -> lookup[1]; 反向 lookup[1] -> lookup[0]
    :param lookup: 属性映射表['{CODE}','{CODE} - {NAME}']
    :param v_from: 待转换的属性值，可以是集合，如['0001','0002','0003']
    :param olist: 对象集合
    :return: 翻译后的结果值
    例如，有码表集合[
    Record(Code=100,Name='001',Text='Text1'),
    Record(Code=102,Name='002',Text='Text2'),
    Record(Code=103,Name='003',Text='Text3'),
    ]
    可以执行
        texts=translate_olist(TranslateDirection.TO_TEXT,['{Code}','{Code} - {Text}'],[100,102])
        返回['100 - Text1','102 - Text2']
    """
    v_to = []
    v_src = []
    lookup_from, lookup_to = (lookup[0], lookup[1]) if direction == TranslateDirection.TO_TEXT else (
        lookup[1], lookup[0])
    v_src.extend(v_from) if is_collection(v_from) else v_src.append(v_from)
    for vf in v_src:
        for o in olist:
            o_from = format_obj(o, lookup_from)
            if vf is not None and o_from.strip() == vf.strip():
                v_to.append(format_obj(o, lookup_to))
                break
    return ','.join(v_to)


def col_spec(column_specs: list, col_key, **kwargs):
    """
    依据列规格列表中的现有对象生成新的的列规格
    :param column_specs: 列规格列表
    :param col_key: 列名/列标识
    :param kwargs: 补充或替代的规格属性
    :return:
    """
    cp = [c for c in column_specs if col_key == c['name']]
    if len(cp) == 1:
        d = dict(cp[0])
        d.update(kwargs)
        return ColumnSpec(**d)
    else:
        return None
