# -*- mes.py: python ; coding: utf-8 -*-
# 性能度量包
import time
import timeit
import cProfile
import pstats
from functools import wraps
from contextlib import contextmanager
from typing import Callable, Any, Optional


class CodeTimer:
    """
    一个用于测量代码执行时间的工具类，支持上下文管理器和装饰器两种使用方式
    """

    def __init__(self, name: str = None, print_report: bool = True):
        """
        初始化计时器

        :param name: 计时器名称，用于标识不同的计时段
        :param print_report: 是否在结束时自动打印报告
        """
        self.name = name or "Unnamed"
        self.print_report = print_report
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0

    def __enter__(self):
        """
        上下文管理器入口，开始计时
        """
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，结束计时并计算耗时
        """
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time

        if self.print_report:
            print(f"{self.name} executed in {self.elapsed_time:.6f} seconds")

    def __call__(self, func):
        """
        使实例可作为装饰器使用
        """

        @wraps(func)
        def wrapped(*args, **kwargs):
            with self.__class__(name=func.__name__, print_report=self.print_report):
                return func(*args, **kwargs)

        return wrapped


def time_it(func: Callable = None, *, number: int = 1, repeat: int = 1) -> Any:
    """
    使用timeit模块测量函数执行时间的装饰器

    :param func: 被装饰的函数
    :param number: 每次测量中执行函数的次数
    :param repeat: 重复测量的次数
    :return: 函数执行结果和计时结果的元组 (result, timings)
    """
    if func is None:
        return lambda f: time_it(f, number=number, repeat=repeat)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 执行函数并获取结果
        result = func(*args, **kwargs)

        # 测量执行时间
        timer = timeit.Timer(lambda: func(*args, **kwargs))
        timings = timer.repeat(repeat=repeat, number=number)

        # 打印报告
        min_time = min(timings) / number
        avg_time = sum(timings) / len(timings) / number
        max_time = max(timings) / number

        print(f"\n--- {func.__name__} 执行时间报告 ---")
        print(f"执行次数: {number} 次/测量, 重复测量: {repeat} 次")
        print(f"最短单次执行时间: {min_time:.6f} 秒")
        print(f"平均单次执行时间: {avg_time:.6f} 秒")
        print(f"最长单次执行时间: {max_time:.6f} 秒")
        print(f"总执行时间: {sum(timings):.6f} 秒")

        return result, timings

    return wrapper


@contextmanager
def profile_code(sort_by: str = 'cumulative', limit: int = 10):
    """
    使用cProfile分析代码性能的上下文管理器

    :param sort_by: 排序依据，可选 'cumulative', 'time', 'calls' 等
    :param limit: 显示的行数限制
    """
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats(sort_by)
        print("\n--- 性能分析报告 ---")
        stats.print_stats(limit)


def measure_performance(func: Callable = None, *,
                        enable_timeit: bool = True,
                        enable_profile: bool = False,
                        timeit_kwargs: Optional[dict] = None,
                        profile_kwargs: Optional[dict] = None):
    """
    综合性能测量装饰器，可以同时使用多种测量方法

    :param func: 被装饰的函数
    :param enable_timeit: 是否启用timeit测量
    :param enable_profile: 是否启用cProfile分析
    :param timeit_kwargs: 传递给time_it装饰器的参数
    :param profile_kwargs: 传递给profile_code的参数
    """
    if func is None:
        return lambda f: measure_performance(
            f,
            enable_timeit=enable_timeit,
            enable_profile=enable_profile,
            timeit_kwargs=timeit_kwargs,
            profile_kwargs=profile_kwargs
        )

    timeit_kwargs = timeit_kwargs or {}
    profile_kwargs = profile_kwargs or {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 如果有性能分析，先处理
        if enable_profile:
            with profile_code(**profile_kwargs):
                if enable_timeit:
                    decorated_func = time_it(func, **timeit_kwargs)
                    return decorated_func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
        else:
            if enable_timeit:
                decorated_func = time_it(func, **timeit_kwargs)
                return decorated_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

    return wrapper


# 示例用法
if __name__ == "__main__":
    # 示例1: 使用CodeTimer类作为上下文管理器
    with CodeTimer("示例代码块1"):
        # 这里放你要测试的代码
        sum(range(1000000))


    # 示例2: 使用CodeTimer类作为装饰器
    @CodeTimer("计算平方和")
    def calculate_square_sum(n):
        return sum(i * i for i in range(n))


    calculate_square_sum(1000000)


    # 示例3: 使用time_it装饰器
    @time_it(number=10, repeat=3)
    def example_function(n):
        return sum(range(n))


    result, timings = example_function(1000000)
    print(f"计算结果: {result}")

    # 示例4: 使用profile_code上下文管理器
    with profile_code(sort_by='time', limit=5):
        sum(i * i for i in range(1000000))


    # 示例5: 使用综合性能测量装饰器
    @measure_performance(
        enable_timeit=True,
        enable_profile=True,
        timeit_kwargs={'number': 10, 'repeat': 3},
        profile_kwargs={'sort_by': 'time', 'limit': 5}
    )
    def performance_example(n):
        return sum(i * i * i for i in range(n))


    performance_example(10000)
