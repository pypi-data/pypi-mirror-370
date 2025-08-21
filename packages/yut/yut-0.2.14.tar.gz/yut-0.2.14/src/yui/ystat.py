# -*- ystat.py: python ; coding: utf-8 -*-
import sys
from decimal import Decimal
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QComboBox, QListWidget, QListWidgetItem, QTableWidgetItem,
    QAbstractItemView, QLabel, QSizePolicy, QMessageBox, QFormLayout, QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pandas import DataFrame

import yui
from yui import img, current_theme, create_layout, create_button, load_icon
from yui.wdg import YTitle, YWidgetPages, YLink, YSortableTable, YSortableItem
from yui.ymodel import PandasModel
from yus import UnitType

# 设置Matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# 枚举类型定义
class StatsType(Enum):
    SUM = "汇总"
    COUNT = "计数"
    MAX = "最大值"
    MIN = "最小值"
    MEAN = "平均值"
    MEDIAN = "中位数"

    def func_name(self):
        return {
            StatsType.SUM: "sum",
            StatsType.COUNT: "count",
            StatsType.MAX: "max",
            StatsType.MIN: "min",
            StatsType.MEAN: "mean",
            StatsType.MEDIAN: "median"
        }.get(self, "sum")


class ChartType(Enum):
    PIE = "饼图"
    BAR = "柱状图"
    LINE = "折线图"

    def icon_file(self):
        return {ChartType.PIE: img.P_CHART_PIE,
                ChartType.BAR: img.P_CHART_BAR,
                ChartType.LINE: img.P_CHART_LINE}.get(self)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()


class YStatsChart(QWidget):
    def __init__(self, parent=None, chart_type_combo=None, fullscreen_btn=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = MplCanvas(self)

        # 创建工具栏布局
        toolbar_layout = QHBoxLayout()

        # 添加标准Matplotlib工具栏
        self.toolbar = NavigationToolbar(self.canvas, self)
        toolbar_layout.addWidget(self.toolbar)

        # 添加弹簧使控件靠右
        toolbar_layout.addStretch(1)

        # 添加自定义控件
        toolbar_layout.addWidget(YTitle.create_label("图表类型:", buddy=chart_type_combo))
        toolbar_layout.addWidget(fullscreen_btn)

        self.layout.addLayout(toolbar_layout)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def reset_axes(self):
        """重置坐标轴状态，确保切换图表类型时不会保留之前的设置"""
        self.canvas.axes.clear()
        self.canvas.axes.set_xlabel('')
        self.canvas.axes.set_ylabel('')
        self.canvas.axes.set_title('')
        self.canvas.axes.grid(False)
        self.canvas.axes.set_axis_on()  # 确保坐标轴显示
        self.canvas.axes.set_aspect('auto')  # 重置为自动比例
        self.canvas.axes.relim()  # 重新计算坐标轴范围
        self.canvas.axes.autoscale_view()  # 自动调整视图范围

    def plot_group_chart(self, chart_data):
        """
        绘制分组统计图表
        参数chart_data是一个字典，包含以下键：
        - chart_type: 图表类型 (ChartType 枚举)
        - labels: 分组标签列表
        - values: 值列表（单数值列）或值字典（多数值列）
        - group_field_cn: 分组字段中文名
        - value_fields_cn: 数值列中文名列表
        - stats_func: 统计方式中文名
        """
        # 重置坐标轴状态
        self.reset_axes()
        ax = self.canvas.axes

        chart_type = chart_data['chart_type']
        labels = chart_data['labels']
        values = chart_data['values']
        group_field_cn = chart_data['group_field_cn']
        value_fields_cn = chart_data.get('value_fields_cn', [])
        stats_func = chart_data['stats_func']

        if not labels:
            return

        if chart_type == ChartType.PIE:
            # 饼图只取第一个数值列或计数
            if isinstance(values, dict) and values:
                # 多数值列，取第一个
                field_cn = list(values.keys())[0]
                sizes = list(values.values())[0]
            elif isinstance(values, list):
                # 单数值列（计数）
                field_cn = '计数'
                sizes = values
            else:
                return

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title(f'{group_field_cn} - {field_cn} {stats_func}')

        elif chart_type in [ChartType.BAR, ChartType.LINE]:  # 柱图和折线图
            x = np.arange(len(labels))

            # 清除之前的图例
            if ax.legend_:
                ax.legend_.remove()

            # 单数值列
            if isinstance(values, list):
                if chart_type == ChartType.BAR:
                    # 创建柱状图
                    bars = ax.bar(x, values, width=0.8, label='计数')
                    # 为每个柱子添加数值标签
                    for bar in bars:
                        height = bar.get_height()
                        ax.annotate(f'{height:,.2f}',
                                    xy=(bar.get_x() + bar.get_width() / 2, height),
                                    xytext=(0, 3),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom')
                else:
                    # 创建折线图
                    line = ax.plot(x, values, marker='o', label='计数')
                    # 为每个点添加数值标签
                    for i, v in enumerate(values):
                        ax.annotate(f'{v:,.2f}', (x[i], v),
                                    textcoords="offset points",
                                    xytext=(0, 10), ha='center')
            # 多数值列
            elif isinstance(values, dict) and values:
                num_fields = len(values)
                width = 0.8 / num_fields if num_fields > 0 else 0.8

                for i, (field_cn, field_values) in enumerate(values.items()):
                    offset = width * i

                    if chart_type == ChartType.BAR:
                        # 创建柱状图
                        bars = ax.bar(x + offset, field_values, width, label=field_cn)
                        # 为每个柱子添加数值标签
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate(f'{height:,.2f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),  # 3 points vertical offset
                                        textcoords="offset points",
                                        ha='center', va='bottom')
                    else:
                        # 创建折线图
                        line = ax.plot(x + offset, field_values, marker='o', label=field_cn)
                        # 为每个点添加数值标签
                        for j, v in enumerate(field_values):
                            ax.annotate(f'{v:,.2f}', (x[j] + offset, v),
                                        textcoords="offset points",
                                        xytext=(0, 10), ha='center')

                # 设置X轴刻度位置
                ax.set_xticks(x + width * (num_fields - 1) / 2)
            else:
                return

            # 设置X轴标签
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')  # 旋转标签避免重叠
            ax.set_xlabel(group_field_cn)
            ax.set_ylabel('值')
            ax.set_title(f'{group_field_cn} - {stats_func}')

            # 添加图例
            ax.legend()

            # 设置网格线
            ax.grid(True, linestyle='--', alpha=0.7)

        self.canvas.draw()

    def plot_cross_chart(self, chart_data):
        """
        绘制交叉统计图表
        参数chart_data是一个字典，包含以下键：
        - chart_type: 图表类型 (ChartType 枚举)
        - row_labels: 行标签列表
        - col_labels: 列标签列表
        - values: 二维数组或字典（多行数据）
        - row_field_cn: 行字段中文名
        - col_field_cn: 列字段中文名
        - value_field_cn: 数值列中文名
        - stats_func: 统计方式中文名
        """
        # 重置坐标轴状态
        self.reset_axes()
        ax = self.canvas.axes

        chart_type = chart_data['chart_type']
        row_labels = chart_data['row_labels']
        col_labels = chart_data['col_labels']
        values = chart_data['values']
        row_field_cn = chart_data['row_field_cn']
        col_field_cn = chart_data['col_field_cn']
        value_field_cn = chart_data['value_field_cn']
        stats_func = chart_data['stats_func']

        if not row_labels or not col_labels:
            return

        x = np.arange(len(col_labels))
        width = 0.8 / len(row_labels) if len(row_labels) > 0 else 0.8

        # 清除之前的图例
        if ax.legend_:
            ax.legend_.remove()

        # 处理多行数据
        if isinstance(values, dict):
            # 字典形式：{行标签: [值列表]}
            for i, (row_label, row_values) in enumerate(values.items()):
                if len(row_values) != len(col_labels):
                    continue

                offset = width * i
                self._plot_chart_data(ax, chart_type, x, offset, width, row_label, row_values)
        elif isinstance(values, list) and values and isinstance(values[0], list):
            # 二维数组形式：[[行1值], [行2值], ...]
            for i, row_values in enumerate(values):
                if len(row_values) != len(col_labels):
                    continue

                offset = width * i
                row_label = row_labels[i] if i < len(row_labels) else f"行{i + 1}"
                self._plot_chart_data(ax, chart_type, x, offset, width, row_label, row_values)
        else:
            return

        if len(row_labels) > 0:
            ax.set_xticks(x + width * (len(row_labels) - 1) / 2)
        ax.set_xticklabels(col_labels, rotation=45, ha='right')  # 旋转标签避免重叠
        ax.set_xlabel(col_field_cn)
        ax.set_ylabel(f'{value_field_cn} {stats_func}')
        ax.set_title(f'{row_field_cn} x {col_field_cn}')
        ax.legend()

        # 设置网格线
        ax.grid(True, linestyle='--', alpha=0.7)

        self.canvas.draw()

    def _plot_chart_data(self, ax, chart_type, x, offset, width, label, values):
        """内部方法：根据图表类型绘制数据"""
        if chart_type == ChartType.BAR:
            bars = ax.bar(x + offset, values, width, label=label)
            # 为每个柱子添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:,.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
        else:
            line = ax.plot(x + offset, values, marker='o', label=label)
            # 为每个点添加数值标签
            for j, v in enumerate(values):
                ax.annotate(f'{v:,.2f}', (x[j] + offset, v),
                            textcoords="offset points",
                            xytext=(0, 10), ha='center')


class StatsCalculator:
    RowSumText = '<合计>'
    ColSumText = '<总计>'

    @staticmethod
    def group_stats(df: DataFrame, group_field: str, stats_type: StatsType, value_fields, value_columns=None, units=1):
        """
        执行分组统计
        参数:
            df: 原始DataFrame
            group_field: 分组字段名
            stats_type: 统计方式 (StatsType枚举)
            value_fields: 数值列列表
            value_columns: 数值列列表（可选）
            units: 金额单位（元、万元）
        返回:
            分组统计结果DataFrame（包含合计行）
        """
        # 自动检测数值列（如果未提供）
        if value_columns is None:
            value_columns = [
                col for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
            ]

        # 执行分组统计
        try:
            group_df = df.groupby(group_field)
        except KeyError as e:
            raise ValueError(f"分组字段错误: {e}")
        # 创建结果DataFrame - 始终包含计数列
        result_df = pd.DataFrame()
        result_df['计数'] = group_df.size()

        # 添加数值列统计
        for field in value_fields:
            if field in df.columns and field in value_columns:
                # 处理Decimal类型数据
                if pd.api.types.is_numeric_dtype(df[field]):
                    result_df[field] = group_df[field].agg(stats_type.func_name())
                else:
                    # 尝试转换为数值
                    try:
                        numeric_series = pd.to_numeric(df[field], errors='coerce')
                        result_df[field] = group_df[field].apply(
                            lambda x: numeric_series.loc[x.index].agg(stats_type.func_name()))
                    except:
                        result_df[field] = group_df[field].agg(stats_type.func_name())
            if units > 1:
                result_df[field] = result_df[field] / units

        # 重置索引，使分组字段成为普通列
        result_df = result_df.reset_index()

        # 添加合计行
        total_row = pd.Series(result_df.iloc[:, 1:].sum(numeric_only=True), name=StatsCalculator.ColSumText)
        # 设置分组字段列的值为"合计"
        total_row[group_field] = StatsCalculator.ColSumText  # '合计'
        total_row['计数'] = len(df)  # 计数列特殊处理

        # 重新排列列顺序
        columns = [group_field] + list(result_df.columns[1:])
        total_row = total_row.reindex(columns)

        # 添加合计行
        return pd.concat([result_df, total_row.to_frame().T], ignore_index=True)

    @staticmethod
    def cross_stats(df: DataFrame, row_field: str, col_field: str, value_field: str, stats_type: StatsType, units=1):
        """
        执行交叉统计
        参数:
            df: 原始DataFrame
            row_field: 行字段名
            col_field: 列字段名
            value_field: 数值列名
            stats_type: 统计方式 (StatsType枚举)
        返回:
            交叉统计结果DataFrame（包含行合计和列合计）
        """
        # 执行交叉统计
        try:
            pivot_df = pd.pivot_table(
                df,
                values=value_field,
                index=row_field,
                columns=col_field,
                aggfunc=stats_type.func_name(),
                fill_value=0
            )
            if units > 1:
                pivot_df = pivot_df.astype(dtype=float) / units
            # 解决FutureWarning问题
            pivot_df = pivot_df.infer_objects(copy=False)
        except KeyError as e:
            raise ValueError(f"交叉统计字段错误: {e}")

        # 添加行合计
        pivot_df[StatsCalculator.RowSumText] = pivot_df.sum(axis=1)

        # 添加列合计
        col_totals = pivot_df.sum(axis=0).to_frame().T
        col_totals.index = [StatsCalculator.ColSumText]
        return pd.concat([pivot_df, col_totals])


class GroupStatsWidget(QWidget):
    filteredData = Signal(object, str)  # 过滤后的数据mask,说明文字

    def __init__(self, parent=None, count_only=False):
        super().__init__(parent)
        self.df = None
        self.count_only = count_only
        self.cn_mapping = {}
        self.value_columns = []  # 外部传入的数值列
        self.chart_fullscreen = False
        self.result_df = None  # 存储当前统计结果

        # 当前统计参数
        self.current_params = {}

        # 创建主布局
        main_layout = create_layout(layout_flag='H')
        self.setLayout(main_layout)

        # 左侧控制面板
        left_box = create_layout(layout_flag='V')
        left_box.setSpacing(12)
        fbox: QFormLayout() = create_layout(layout_flag='F')
        fbox.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        fbox.setVerticalSpacing(6)
        fbox.setHorizontalSpacing(20)

        # 数值列
        self.value_list = QListWidget()
        self.value_list.setMaximumHeight(100)
        fbox.addRow(YTitle.create_label('数值列：'), self.value_list)
        self.units_10k = QCheckBox('启用（万元）转换')
        self.units_10k.setEnabled(not self.count_only)
        fbox.addRow(QLabel(''), self.units_10k)

        # 统计方式
        self.stats_combo = QComboBox()
        # 使用枚举值填充下拉框
        for stat in StatsType:
            self.stats_combo.addItem(load_icon(img.P_BULLET3), stat.value, stat)
        self.stats_combo.setCurrentText(StatsType.COUNT.value if self.count_only else StatsType.SUM.value)
        self.stats_combo.setEnabled(not self.count_only)
        fbox.addRow(YTitle.create_label('统计方式：'), self.stats_combo)

        # 分组字段
        self.group_combo = QComboBox()
        fbox.addRow(YTitle.create_label('分组字段：'), self.group_combo)

        # 统计按钮
        self.stats_btn = create_button("执行统计", self.perform_stats, icon_file=img.P_LIGHTNING, flat=False)
        self.stats_btn.setFixedSize(QSize(200, 30))

        # 结果表格
        self.result_table: YSortableTable = YSortableTable()
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.cellClicked.connect(self.handle_cell_click)

        left_box.addLayout(fbox, stretch=0)
        left_box.addWidget(self.stats_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        left_box.layout().addWidget(self.result_table, stretch=1)

        # 右侧图表及全屏按钮
        # 创建全屏按钮
        self.fullscreen_btn = create_button("", self.toggle_chart_fullscreen, icon_file=img.P_GRID, flat=True,
                                            tip_text='切换全屏图表')
        self.fullscreen_btn.setCheckable(True)

        # 右侧图表
        self.chart_combo = QComboBox()
        # 使用枚举值填充下拉框
        for chart in ChartType:
            self.chart_combo.addItem(yui.load_icon(chart.icon_file()), chart.value, chart)
        self.chart_combo.setCurrentText(ChartType.BAR.value)

        self.chart_widget = YStatsChart(
            chart_type_combo=self.chart_combo,
            fullscreen_btn=self.fullscreen_btn
        )

        # 图表类型改变时重新执行统计
        self.chart_combo.currentIndexChanged.connect(self.perform_stats)

        # 统计方式改变时更新数值列状态
        # self.stats_combo.currentIndexChanged.connect(self.update_value_list_state)

        # 添加到主布局
        self.left_widget = QWidget()
        self.left_widget.setLayout(left_box)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.chart_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 6)
        yui.add_to_layout(main_layout, splitter)

    def update_value_list_state(self):
        """根据统计方式更新数值列列表状态"""
        stats_type = self.stats_combo.currentData()
        # 如果是计数统计，禁用数值列列表；否则启用
        if stats_type == StatsType.COUNT:
            self.value_list.setEnabled(False)
        else:
            self.value_list.setEnabled(True)

    def set_data(self, df, cn_mapping, value_columns=None):
        self.df = df
        self.cn_mapping = cn_mapping

        # 设置数值列
        if value_columns is not None:
            self.value_columns = value_columns
        else:
            # 自动检测数值列
            self.value_columns = [
                col for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
            ]

        # 更新字段选择
        self.group_combo.clear()
        self.value_list.clear()

        # 添加所有列到分组字段下拉框
        for col, cn_name in cn_mapping.items():
            if col in df.columns:
                self.group_combo.addItem(yui.load_icon(img.P_LABEL), cn_name, col)

        # 添加数值列到数值列列表
        for i, col in enumerate(self.value_columns):
            cn_name = cn_mapping.get(col, col)
            item = QListWidgetItem(cn_name)
            item.setData(Qt.ItemDataRole.UserRole, col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if not self.count_only and i == 0:
                item.setCheckState(Qt.CheckState.Checked)  # 选中第一个
            else:
                item.setCheckState(Qt.CheckState.Unchecked)  # 不可省略，否则不显示复选框
            item.setIcon(yui.load_icon(img.P_LABEL))
            self.value_list.addItem(item)
        # 初始化数值列状态
        self.update_value_list_state()

    def toggle_chart_fullscreen(self, checked):
        self.chart_fullscreen = checked
        if checked:
            self.left_widget.hide()
            self.fullscreen_btn.setToolTip("退出全屏")
        else:
            self.left_widget.show()
            self.fullscreen_btn.setToolTip("切换全屏图表")

    def perform_stats(self):
        if self.df is None or self.df.empty:
            return

        # 获取选择的字段
        group_idx = self.group_combo.currentIndex()
        group_field = self.group_combo.itemData(group_idx)
        group_field_cn = self.group_combo.currentText()  # 获取中文名称

        # 获取统计方式
        stats_type = self.stats_combo.currentData()

        # 获取数值列
        value_fields = []
        value_fields_cn = []  # 数值列的中文名称
        units = 10000 if self.units_10k.isChecked() else 1

        for i in range(self.value_list.count()):
            item = self.value_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                value_fields.append(item.data(Qt.ItemDataRole.UserRole))
                value_fields_cn.append(item.text())  # 获取中文名称

        # 如果是计数统计则忽略数值列
        if stats_type == StatsType.COUNT and len(value_fields) > 0:
            yui.pop_info("计数统计不需要选择数值列，系统将忽略您的选择，直接分组计数。", title="提示")

        if stats_type == StatsType.COUNT and units > 1:
            yui.pop_info("计数统计不需要进行万元转换，系统将忽略此选项。", title="提示")
            units = 1

        try:
            # 使用统计计算器执行分组统计
            result_df = StatsCalculator.group_stats(
                self.df,
                group_field,
                stats_type,
                value_fields,
                self.value_columns,
                units=units,
            )
        except ValueError as e:
            QMessageBox.warning(self, "统计错误", str(e))
            return

        # 保存当前统计结果
        self.result_df = result_df

        # 更新表格
        self.update_result_table(result_df, group_field, value_fields)

        # 获取当前图表类型
        chart_type = self.chart_combo.currentData()

        # 准备图表数据
        chart_data = self.prepare_chart_data(
            result_df,
            group_field,
            group_field_cn,
            value_fields_cn,
            stats_type.value,
            chart_type
        )

        # 更新图表
        self.chart_widget.plot_group_chart(chart_data)

    def prepare_chart_data(self, result_df, group_field, group_field_cn, value_fields_cn, stats_func, chart_type):
        """准备图表数据，排除合计行"""
        # 排除合计行
        chart_df = result_df.iloc[:-1]

        # 获取分组标签
        labels = chart_df[group_field].astype(str).tolist()

        # 获取数值列
        if value_fields_cn:
            # 多数值列
            values = {}
            for field_cn in value_fields_cn:
                # 通过中文名找原始字段名
                for col, cn in self.cn_mapping.items():
                    if cn == field_cn and col in chart_df.columns:
                        values[field_cn] = chart_df[col].tolist()
                        break
        else:
            # 单数值列（计数）
            values = chart_df['计数'].tolist() if '计数' in chart_df.columns else []

        # 返回图表数据字典
        return {
            'chart_type': chart_type,
            'labels': labels,
            'values': values,
            'group_field_cn': group_field_cn,
            'value_fields_cn': value_fields_cn,
            'stats_func': stats_func
        }

    def update_result_table(self, result_df, group_field, value_fields):
        # 禁用排序以避免在填充数据时触发排序
        self.result_table.setSortingEnabled(False)

        self.result_table.clear()

        # 设置行列数
        n_rows, n_cols = result_df.shape
        self.result_table.setRowCount(n_rows)
        self.result_table.setColumnCount(n_cols)

        # 设置表头
        headers = []
        for col in result_df.columns:
            cn_name = self.cn_mapping.get(col, col)
            headers.append(cn_name)
        self.result_table.setHorizontalHeaderLabels(headers)

        # 填充数据
        for i in range(n_rows):
            for j in range(n_cols):
                is_sum, is_link = i == n_rows - 1, j == 1
                value = result_df.iloc[i, j]
                if pd.isna(value):
                    value = 0.0

                # 格式化数值
                if j > 1 and isinstance(value, (int, float, Decimal)):
                    text = f"{value:,.2f}" if value != 0 else "0.00"
                    item = YSortableItem(text)
                else:
                    item = YSortableItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, value)  # 用于排序

                # 标记合计行
                if is_sum:
                    item.setFont(YStatWidget.MARK_FONT)
                    item.setForeground(YStatWidget.MARK_COLOR)

                # 为计数列设置超链接样式（第1列）
                if is_link and not is_sum:  # 计数列
                    item.setForeground(YStatWidget.LINK_COLOR)
                    item.setFont(YStatWidget.LINK_FONT)

                if j > 0:  # 只要不是第一行，右对齐
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.result_table.setItem(i, j, item)

        # 调整列宽
        self.result_table.adjust_column_width()
        # 重新启用排序
        self.result_table.setSortingEnabled(True)

    def handle_cell_click(self, row, col):
        if self.result_df is None or col != 1:
            return

        group_field = self.group_combo.itemData(self.group_combo.currentIndex())
        group_text = self.group_combo.currentText()
        mask, filter_text = None, f"{group_text}*"

        if row != self.result_table.rowCount() - 1:  # 不是合计行
            group_value = self.result_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            mask = self.df[group_field] == group_value
            filter_text = f"{group_text}~{group_value}"

        self.filteredData.emit(mask, filter_text)


class CrossStatsWidget(QWidget):
    filteredData = Signal(object, str)  # 过滤后的数据mask,说明文字

    def __init__(self, parent=None, count_only=False):
        super().__init__(parent)
        self.df = None  # 执行统计时使用的df,通常是预处理之后的
        self.count_only = count_only
        self.cn_mapping = {}
        self.value_columns = []  # 外部传入的数值列
        self.chart_fullscreen = False
        self.result_df = None  # 存储当前统计结果

        # 当前统计参数
        self.current_params = {}

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建上下分割器
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # 上部控制面板
        self.top_widget = QWidget()
        top_layout = QVBoxLayout(self.top_widget)

        # 字段选择
        hbox = QHBoxLayout()
        hbox.setSpacing(16)

        # 数值列
        self.value_combo = QComboBox()
        hbox.addWidget(YTitle.create_label('数值列：', buddy=self.value_combo))
        self.units_10k = QCheckBox('启用（万元）转换')
        self.units_10k.setEnabled(not self.count_only)
        self.value_combo.setEnabled(not self.count_only)
        hbox.addWidget(self.units_10k)
        hbox.addSpacing(40)

        # 统计方式
        self.stats_combo = QComboBox()
        # 使用枚举值填充下拉框
        for stat in StatsType:
            self.stats_combo.addItem(load_icon(img.P_BULLET3), stat.value, stat)
        self.stats_combo.setCurrentText(StatsType.COUNT.value if self.count_only else StatsType.SUM.value)
        hbox.addWidget(YTitle.create_label('统计方式：', buddy=self.stats_combo))
        self.stats_combo.setEnabled(not self.count_only)
        hbox.addSpacing(40)

        # 行列字段
        self.row_combo = QComboBox()
        self.col_combo = QComboBox()
        hbox.addWidget(YTitle.create_label('行字段：', buddy=self.row_combo))
        hbox.addWidget(YTitle.create_label('列字段：', buddy=self.col_combo))
        hbox.addStretch(1)

        # 统计按钮
        self.stats_btn = create_button("执行统计", self.perform_stats, icon_file=img.P_LIGHTNING)
        hbox.addWidget(self.stats_btn)

        top_layout.addLayout(hbox)

        # 结果表格
        self.result_table = YSortableTable()
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.cellClicked.connect(self.handle_cell_click)
        top_layout.addWidget(self.result_table)

        # 全屏按钮
        self.fullscreen_btn = create_button("", self.toggle_chart_fullscreen, icon_file=img.P_GRID, flat=True,
                                            tip_text='切换全屏图表')
        self.fullscreen_btn.setCheckable(True)

        # 下部图表 - 传入图表类型下拉框和全屏按钮
        self.chart_combo = QComboBox()
        # 使用枚举值填充下拉框 - 只支持柱状图和折线图
        for chart in [ChartType.BAR, ChartType.LINE]:
            self.chart_combo.addItem(yui.load_icon(chart.icon_file()), chart.value, chart)
        self.chart_combo.setCurrentText(ChartType.BAR.value)

        self.chart_widget = YStatsChart(
            chart_type_combo=self.chart_combo,
            fullscreen_btn=self.fullscreen_btn
        )

        # 图表类型改变时重新执行统计
        self.chart_combo.currentIndexChanged.connect(self.perform_stats)

        # 添加到分割器
        self.splitter.addWidget(self.top_widget)
        self.splitter.addWidget(self.chart_widget)
        self.splitter.setSizes([400, 600])

        main_layout.addWidget(self.splitter)

        self.setLayout(main_layout)

    def set_data(self, df, cn_mapping, value_columns=None):
        self.df = df
        self.cn_mapping = cn_mapping

        # 设置数值列
        if value_columns is not None:
            self.value_columns = value_columns
        else:
            # 自动检测数值列
            self.value_columns = [
                col for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
            ]

        # 更新字段选择
        self.row_combo.clear()
        self.col_combo.clear()
        self.value_combo.clear()

        # 添加所有列到行字段和列字段下拉框
        for col, cn_name in cn_mapping.items():
            if col in df.columns:
                self.row_combo.addItem(yui.load_icon(img.P_LABEL), cn_name, col)
                self.col_combo.addItem(yui.load_icon(img.P_LABEL), cn_name, col)

        # 添加数值列到数值列下拉框
        for col in self.value_columns:
            cn_name = cn_mapping.get(col, col)
            self.value_combo.addItem(yui.load_icon(img.P_LABEL), cn_name, col)

    def toggle_chart_fullscreen(self, checked):
        self.chart_fullscreen = checked
        if checked:
            # 隐藏上部控制面板
            self.top_widget.hide()
            # 调整分割器使图表占据全部空间
            self.splitter.setSizes([0, 1000])
            self.fullscreen_btn.setToolTip("退出全屏")
        else:
            # 显示上部控制面板
            self.top_widget.show()
            # 恢复分割器比例
            self.splitter.setSizes([400, 600])
            self.fullscreen_btn.setToolTip("切换全屏图表")

    def perform_stats(self):
        if self.df is None or self.df.empty:
            return

        # 获取选择的字段
        row_idx = self.row_combo.currentIndex()
        row_field = self.row_combo.itemData(row_idx)  # 原始字段名
        row_field_cn = self.row_combo.currentText()  # 中文名称

        col_idx = self.col_combo.currentIndex()
        col_field = self.col_combo.itemData(col_idx)  # 原始字段名
        col_field_cn = self.col_combo.currentText()  # 中文名称

        value_idx = self.value_combo.currentIndex()
        value_field_cn = self.value_combo.currentText()  # 中文名称

        # 通过中文名称获取原始字段名
        value_field = None
        for col, cn in self.cn_mapping.items():
            if cn == value_field_cn:
                value_field = col
                break
        if value_field is None:
            value_field = value_field_cn  # 如果找不到匹配，使用中文名称

        units = 10000 if self.units_10k.isChecked() else 1

        # 获取统计方式
        stats_type = self.stats_combo.currentData()
        if stats_type == StatsType.COUNT and units > 1:
            yui.pop_info("计数统计不需要进行万元转换，系统将忽略此选项。", title="提示")
            units = 1

        try:
            # 使用统计计算器执行交叉统计
            result_df = StatsCalculator.cross_stats(
                self.df,
                row_field,
                col_field,
                value_field,
                stats_type,
                units=units
            )
        except ValueError as e:
            QMessageBox.warning(self, "统计错误", str(e))
            return

        # 保存当前统计结果
        self.result_df = result_df

        # 更新表格
        self.update_result_table(result_df, row_field, col_field, value_field)

        # 获取当前图表类型
        chart_type = self.chart_combo.currentData()

        # 准备图表数据
        chart_data = self.prepare_chart_data(
            result_df,
            row_field_cn,
            col_field_cn,
            value_field_cn,
            stats_type.value,
            chart_type
        )

        # 更新图表
        self.chart_widget.plot_cross_chart(chart_data)

    def prepare_chart_data(self, result_df, row_field_cn, col_field_cn, value_field_cn, stats_func, chart_type):
        """准备图表数据，排除合计行/列"""
        # 排除合计行和合计列
        chart_df = result_df.iloc[:-1, :-1]

        # 获取行标签和列标签
        row_labels = chart_df.index.tolist()
        col_labels = chart_df.columns.tolist()

        # 修复：确保行标签是字符串类型
        row_labels = [str(label) for label in row_labels]
        col_labels = [str(label) for label in col_labels]

        # 获取值数据
        values = {}
        for i, row_label in enumerate(row_labels):
            # 修复：使用原始索引值访问数据，而不是字符串标签
            original_row_label = chart_df.index[i]
            values[row_label] = chart_df.loc[original_row_label].tolist()

        # 返回图表数据字典
        return {
            'chart_type': chart_type,
            'row_labels': row_labels,
            'col_labels': col_labels,
            'values': values,
            'row_field_cn': row_field_cn,
            'col_field_cn': col_field_cn,
            'value_field_cn': value_field_cn,
            'stats_func': stats_func
        }

    def update_result_table(self, result_df, row_field, col_field, value_field):
        # 禁用排序以避免在填充数据时触发排序
        self.result_table.setSortingEnabled(False)

        self.result_table.clear()

        # 设置行列数
        n_rows, n_cols = result_df.shape
        self.result_table.setRowCount(n_rows)
        self.result_table.setColumnCount(n_cols + 1)  # 增加行标题列

        # 设置表头
        col_headers = [self.cn_mapping.get(row_field, row_field)]
        for col in result_df.columns:
            col_headers.append(str(col))
        self.result_table.setHorizontalHeaderLabels(col_headers)
        for i, col in enumerate(result_df.columns):
            text = col_headers[i]
            item = QTableWidgetItem(text)
            item.setData(Qt.ItemDataRole.ToolTipRole, col)
            self.result_table.setHorizontalHeaderItem(i, item)

        # 填充数据
        for i, (idx, row) in enumerate(result_df.iterrows()):
            # 行标题
            index_item = YSortableItem(str(idx))
            self.result_table.setItem(i, 0, index_item)

            # 数据列
            for j, col in enumerate(result_df.columns, 1):
                value = row[col]
                if pd.isna(value):
                    value = 0.0

                # 格式化数值
                if isinstance(value, (int, float, Decimal)):
                    text = f"{value:,.2f}" if value != 0 else "0.00"
                else:
                    text = str(value)

                item = YSortableItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item.setData(Qt.ItemDataRole.UserRole, value)  # 本单元格的值，用于排序
                item.setData(Qt.ItemDataRole.ToolTipRole, idx)  # 索引值，用于filter
                if text not in ('0.00', '0', ''):
                    item.setForeground(YStatWidget.LINK_COLOR)
                    item.setFont(YStatWidget.LINK_FONT)

                # 特殊标记合计行/列
                if i == n_rows - 1 or j == n_cols:  # 最后一行或最后一列
                    item.setForeground(YStatWidget.MARK_COLOR)
                    item.setFont(YStatWidget.MARK_FONT)

                self.result_table.setItem(i, j, item)

        # 调整列宽
        self.result_table.adjust_column_width()
        # 重新启用排序
        self.result_table.setSortingEnabled(True)

    def handle_cell_click(self, row, col):
        if self.result_df is None or col < 1:
            return

        df = self.df
        is_last_row, is_last_col = row == self.result_table.rowCount() - 1, col == self.result_table.columnCount() - 1

        # 获取行字段和列字段
        row_field = self.row_combo.itemData(self.row_combo.currentIndex())
        col_field = self.col_combo.itemData(self.col_combo.currentIndex())

        row_value = self.result_table.item(row, col).data(Qt.ItemDataRole.ToolTipRole)
        col_value = self.result_table.horizontalHeaderItem(col - 1).data(Qt.ItemDataRole.ToolTipRole)
        mask, filter_text = None, ''

        if not is_last_col and not is_last_row:  # 普通单元格
            mask = (df[row_field] == row_value) & (df[col_field] == col_value)
            filter_text = f"{row_value}x{col_value}"
        elif is_last_row and not is_last_col:  # 行合计
            mask = df[col_field] == col_value
            filter_text = f"{col_value}*"
        elif is_last_col and not is_last_row:  # 列合计
            mask = df[row_field] == row_value
            filter_text = f"{row_value}*"
        elif is_last_row and is_last_col:  # 总合计
            mask = None
            filter_text = "*"

        # print(f"位置(row,col):({row},{col})", f"{row_field}={row_value!r} && {col_field}={col_value!r}",
        #       filter_text, sep='\n')
        self.filteredData.emit(mask, filter_text)


class YStatWidget(QWidget):
    LINK_FONT = QFont()
    LINK_FONT.setUnderline(True)
    MARK_FONT = QFont()
    MARK_FONT.setUnderline(True)
    MARK_FONT.setBold(True)

    LINK_COLOR = current_theme.icon_color()
    HOVER_COLOR = current_theme.hover_color()
    MARK_COLOR = current_theme.enforce_color()

    filterModel = Signal(PandasModel, str)  # 过滤后的model，描述文字，通常是过滤条件说明

    def __init__(self, parent=None, count_only=False):
        super().__init__(parent)

        YStatWidget.LINK_COLOR = self.palette().link()
        YStatWidget.HOVER_COLOR = self.palette().highlightedText()
        YStatWidget.MARK_COLOR = self.palette().highlight()

        self.model = None
        self.df = None
        self.count_only = count_only
        self.group_tab = GroupStatsWidget(count_only=self.count_only)
        self.cross_tab = CrossStatsWidget(count_only=self.count_only)
        self.pages = YWidgetPages(YLink('分组统计', icon=img.P_SUM_1, target=self.group_tab),
                                  YLink('交叉统计', icon=img.P_TREE, target=self.cross_tab),
                                  parent=self,
                                  close_able=False,
                                  tab_alignment=Qt.AlignmentFlag.AlignLeft,
                                  show_single_tab=True,
                                  )
        self.setup_ui()

    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.pages)

    def set_data_frame(self, df, column_names, value_columns=None):
        self.df = df
        self.group_tab.set_data(df, column_names, value_columns)
        self.cross_tab.set_data(df, column_names, value_columns)
        self.group_tab.filteredData.connect(self.filter_data)
        self.cross_tab.filteredData.connect(self.filter_data)

    def filter_data(self, mask, filter_text):
        df = self.model.data_frame() if self.model else self.df
        column_spec = self.model.column_specs() if self.model else None
        if df is None:
            return
        filtered_df = df[mask] if mask is not None else df
        if not filtered_df.empty:
            self.filterModel.emit(PandasModel(filtered_df, column_spec), filter_text)

    def prepare_dataframe(self):
        # 处理Choose列，使用显示文字替换原始值
        df = self.model.data_frame().copy()
        column_specs = self.model.column_specs()
        choose_columns = [spec.name for spec in column_specs if spec.utype in (UnitType.CHOOSE, UnitType.LOOKUP)]
        for col in choose_columns:
            try:
                col_idx = self.model._display_columns.index(col)
                new_dat = [self.model.data(self.model.index(i, col_idx),
                                           Qt.ItemDataRole.DisplayRole) for i in range(self.model.rowCount())]
                df[col] = new_dat
            except ValueError:
                pass
        return df

    def set_model(self, model: PandasModel, value_columns=None):
        self.model = model
        df = self.prepare_dataframe()  # 预处理之后的df
        column_specs = self.model.column_specs()
        col_map = {sp.name: sp.comment for sp in column_specs}
        if not value_columns:
            value_columns = [sp.name for sp in column_specs if sp.utype in (UnitType.CURRENCY, UnitType.INT)]
        self.set_data_frame(df, column_names=col_map, value_columns=value_columns)


# 测试数据生成函数
def generate_test_data(n=30):
    np.random.seed(42)

    departments = ['技术部', '市场部', '财务部', '人事部', '行政部']
    positions = ['经理', '主管', '工程师', '专员', '助理']
    genders = ['男', '女']

    data = {
        'employee_id': [f'E{1000 + i}' for i in range(n)],
        'name': [f'员工{i}' for i in range(n)],
        'gender': np.random.choice(genders, n),
        'age': np.random.randint(22, 55, n),
        'department': np.random.choice(departments, n),
        'position': np.random.choice(positions, n),
        'income': np.random.uniform(5000, 20000, n).round(2),
        'expense': np.random.uniform(1000, 5000, n).round(2),
        'bonus': np.random.uniform(1000, 10000, n).round(2)
    }

    # 添加一些空值
    for i in range(3):
        idx = np.random.randint(n)
        data['income'][idx] = None
        idx = np.random.randint(n)
        data['expense'][idx] = np.nan
        idx = np.random.randint(n)
        data['bonus'][idx] = None

    df = pd.DataFrame(data)

    # 将部分数值列转换为Decimal类型
    for col in ['income', 'expense', 'bonus']:
        df[col] = df[col].apply(lambda x: Decimal(x) if not pd.isna(x) else x)

    return df


# 中英文列名对照
CN_MAPPING = {
    'employee_id': '工号',
    'name': '姓名',
    'gender': '性别',
    'age': '年龄',
    'department': '部门',
    'position': '职务',
    'income': '收入',
    'expense': '支出',
    'bonus': '奖金'
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataFrame统计分析工具")
        self.setGeometry(100, 100, 1200, 800)

        # 生成测试数据
        self.df = generate_test_data(50)

        # 指定数值列
        value_columns = ['income', 'expense', 'bonus']

        # 创建主部件
        self.stats_widget = YStatWidget(count_only=False)
        self.stats_widget.set_data_frame(self.df, CN_MAPPING, value_columns)
        self.stats_widget.filterModel.connect(lambda model, txt: print(txt, model.data_frame().to_string()))

        self.setCentralWidget(self.stats_widget)


if __name__ == "__main__":
    app = yui.create_default_app()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
