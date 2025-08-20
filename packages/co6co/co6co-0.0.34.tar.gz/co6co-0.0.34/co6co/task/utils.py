import time
from functools import wraps
import random

def clock(func):
    """
    装饰器函数，用于计算函数的执行时间
    :param func: 被装饰的函数
    :return: 包装后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer(f"{func.__name__}(arg->{args}kwargs:{kwargs})"):
            result = func(*args, **kwargs)  # 调用原始函数并获取返回值
            return result
    return wrapper


def exponential_backoff(retry_count: int, base_delay=1, max_delay=30, showMess: bool = True):
    """
    指数退避算法，等待时间 = base_delay * (2^retry_count)

    参数:
    - retry_count: 当前重试次数 (从0开始)
    - base_delay: 基础等待时间 (秒)
    - max_delay: 最大等待时间 (秒)
    """
    # 计算指数退避时间
    delay = base_delay * (2 ** retry_count)
    # 添加随机抖动，避免多个客户端同时重试
    jitter = random.uniform(0, 1)
    delay = min(delay + jitter, max_delay)
    if showMess:
        print(f"第 {retry_count+1} 次重试，等待 {delay:.2f} 秒...")
    time.sleep(delay)


def linear_backoff(retry_count: int, base_delay: int = 1, max_delay=10, showMess: bool = True):
    """
    线性退避算法，等待时间 = base_delay * retry_count

    参数:
    - retry_count: 当前重试次数 (从0开始)
    - base_delay: 基础等待时间 (秒)
    - max_delay: 最大等待时间 (秒)
    """
    delay = min(base_delay * (retry_count + 1), max_delay)
    if showMess:
        print(f"第 {retry_count+1} 次重试，等待 {delay} 秒...")
    time.sleep(delay)


class Timer:
    """
    # 示例用法 1 手动启动和停止
    timer = Timer("手动计时")
    timer.start()
    for i in range(1000000):
        pass
    timer.stop()

    # 示例用法 2 使用 with 语句自动管理计时
    with Timer("自动计时"):
        for i in range(1000000):
            pass
    """

    def __init__(self, activity_name="任务", ndigits: int = 4, showMsg: bool = True):
        """
        初始化计时器类
        :param activity_name: 计时器描述名称，默认为 "任务"
        """
        self.activity_name = activity_name
        self.start_time = None
        self.end_time = None
        self.ndigits = ndigits
        self.show = showMsg

    def start(self):
        """
        开始计时
        """
        self.start_time = time.time()
        if self.show:
            print(f"{self.activity_name} 开始...")

    @property
    def elapsed(self):
        """
        经过了多少秒
        :return: 经过的秒数
        """
        start_time = self.start_time or time.time()
        end_time = self.end_time or time.time()
        elapsed_time = end_time - start_time
        return round(elapsed_time, self.ndigits)

    def stop(self):
        """
        停止计时并打印耗时
        """
        if self.start_time is None:
            raise ValueError("计时器未开始，请先调用 start() 方法！")
        self.end_time = time.time()
        if self.show:
            print(f"{self.activity_name} 结束，耗时：{self.elapsed} 秒")

    def __enter__(self):
        """
        支持 with 语句的进入方法
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持 with 语句的退出方法
        """
        self.stop()
