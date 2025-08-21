# -*- asynx.py: python ; coding: utf-8 -*-
# 异步处理和多线程相关的工具类
"""
提供了两种异步函数的使用方式：

# 1.使用AsyncFunc类将普通函数封装为异步函数的对象，然后再调用
def div(a, b):
    t = QThread.currentThread()
    for i in range(5):
        print(f'[{t}]div #{i}')
        time.sleep(1)
    return a / b


def sample_1():
    AsyncFunc(div, on_result=lambda r: print('div result is', r)).call(100, 20)


def sample_2():
    def handle_result(r):
        print('handle result:', r)

    def handle_error(e):
        print('handle error:', e)

    af = AsyncFunc(div)
    af.onResult.connect(handle_result)
    af.onException.connect(handle_error)
    af.call(1000, 20)
    af.call(100, 0)


# 2.使用async_func装饰器

@async_func(on_result=lambda r: print('函数返回的结果:', r),
            on_exception=lambda e: print('函数执行时发生异常:', e))
def divide(a, b):
    t = QThread.currentThread()
    for i in range(5):
        print(f'[{t}]divide #{i}')
        time.sleep(1)
    return a / b


@async_func
def safe_div(a, b):
    t = QThread.currentThread()
    for i in range(5):
        print(f'[{t}]safe_div #{i}')
        time.sleep(1)
    if b == 0:
        return 0
    return a / b


def sample_3():
    divide(20000, 3.5)
    divide(20, 0)


def sample_4():
    safe_div(10000, 2.5)
    safe_div(20, 0)


无论如何使用，都需要启动Qt的事件循环
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)  # 创建Qt应用
sample_1()
sample_2()
sample_3()
sample_4()
sys.exit(app.exec())  # 启动事件循环

"""
import functools
import time
import weakref
from typing import Callable, Any

from PySide6.QtCore import QThread, Signal, QObject, QRunnable, QThreadPool

from yut import get_attr


class RunnableFunc(QRunnable):
    class _Signals(QObject):
        # QRunnable不是QObject的子类，不能connect定义信号,故将信号封装到单独的QObject类中
        onResult = Signal(object)
        onException = Signal(Exception)

    signals = _Signals()
    _thread_pool = QThreadPool()

    def __init__(self, func, on_result=None, on_exception=None):
        super().__init__()
        self.setAutoDelete(True)
        self.func = func
        self.func = func
        self.args = ()
        self.kwargs = {}
        # 存储回调函数的弱引用
        self._result_callbacks = weakref.WeakSet()
        self._exception_callbacks = weakref.WeakSet()
        # 初始连接
        self.connect_signals(on_result, on_exception)

    def connect_signals(self, on_result=None, on_exception=None):
        """动态连接结果信号"""
        if on_result and on_result not in self._result_callbacks:
            self.signals.onResult.connect(on_result)
            self._result_callbacks.add(on_result)
        if on_exception and on_exception not in self._exception_callbacks:
            self.signals.onException.connect(on_exception)
            self._result_callbacks.add(on_exception)

    def call(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._thread_pool.start(self)

    def run(self):
        func, args, kwargs = self.func, self.args, self.kwargs
        try:
            ret = func(*args, **kwargs)
            self.signals.onResult.emit(ret)
        except Exception as e:
            self.signals.onException.emit(e)


def runnable(func=None, on_result=None, on_exception=None):
    """RunnableFunc的装饰器"""

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            r = RunnableFunc(f)
            # 支持装饰器参数和动态连接
            r.connect_signals(on_result, on_exception)
            r.call(*args, **kwargs)
            return r

        return wrapper

    return decorator(func) if callable(func) else decorator


class LongRunningThread(QThread):
    """
    长时间执行的线程
    """
    ThreadPool = []

    def __init__(self, interval_seconds: int = 5, min_seconds=-1, max_seconds=-1, max_times=-1,
                 on_work: Callable[[Any], bool] = None):
        super().__init__()
        self.interval_seconds, self.min_seconds, self.max_seconds = interval_seconds, min_seconds, max_seconds
        self.max_times = max_times
        self._on_work = on_work

        self.running = True
        self.count = 0
        self.running_seconds = 0
        self.start_time = time.time()
        # 保存线程对象，设置自动清理
        LongRunningThread.ThreadPool.append(self)
        self.finished.connect(self.deleteLater)

    def set_on_work(self, on_work: Callable[[object], bool]):
        self._on_work = on_work

    def save_time(self):
        self.running_seconds = time.time() - self.start_time

    def run(self):
        # 记录启动时间、初始启动状态等
        self.reset_time()
        while self.running or self.running_seconds < self.min_seconds:
            self.running = self._check_running()
            if self.running:
                context = {attr: get_attr(self, attr) for attr in ('count', 'running_seconds')}
                self.running = self.work(context)
                self.count += 1
            self.save_time()
            if self.running_seconds < self.min_seconds:  # 无论是否继续执行，时间不够的都要补足
                time.sleep(self.min_seconds - self.running_seconds)
            self.save_time()
            for i in range(self.interval_seconds):  # 1秒1秒检查，给外部stop机会
                if not self.running:
                    return
                time.sleep(1)
                self.save_time()

    def work(self, context) -> bool:
        if self._on_work:
            return self._on_work(context)
        return True

    def _check_running(self):
        if self.count >= self.max_times > 0:
            return False
        if self.running_seconds >= self.max_seconds > 0:
            return False
        return self.running

    def reset_time(self):
        self.running, self.start_time = True, time.time()
        self.save_time()

    def reset_count(self):
        self.count = 0

    def stop(self):
        self.running = False
        try:
            self.wait()
        except:
            pass
        try:
            LongRunningThread.ThreadPool.remove(self)
        except:
            pass
