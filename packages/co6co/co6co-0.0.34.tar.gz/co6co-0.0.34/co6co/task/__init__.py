import threading
from queue import Queue
import time
from typing import Generator, Callable, Any


class ThreadTask:
    """
    任务类
    多线程执行任务
    """

    def __init__(self, handlerTask: Callable[[Any], None], generTaskParam: Generator[Any, None, None], *arg, oneWorkerEndBck: Callable[[], None] = None, taskEndBck: Callable[[bool], None] = None, **kwargs):
        """ 
        :param handlerTask: 处理任务的函数
        :param generTaskParam: 生成任务的函数
        :param oneWorkerEnd: 一个工作线程结束时的回调函数
        :param taskEnd: 任务结束时的回调函数, 会传入一个bool值, True表示任务正常结束, False表示任务提前结束
        """
        self.task_queue = Queue()
        self.working = False
        self.handler = handlerTask
        self.generator = generTaskParam
        self.oneWorkerEndBck = oneWorkerEndBck
        self.taskEndBck = taskEndBck
        self.arg = arg
        self.kwargs = kwargs

    def _worker(self):
        """
        # 定义线程函数，从队列中取出任务并处理
        """
        while True:
            # 会阻塞
            task = self. task_queue.get()  # 从队列中获取任务
            if task is None:  # 如果任务为None，表示终止信号
                break
            try:
                self.handler(task, *self.arg, **self.kwargs)
            except Exception as e:
                print(f"任务执行出错: {e}")
            self.task_queue.task_done()  # 标记任务已完成
        if self.oneWorkerEndBck:
            self.oneWorkerEndBck()

    def start(self, max_threads: int = 4):
        """
        开始执行任务 
        join 到 主线程 主线程不退出
        :param max_threads: 最大线程数 
        """
        self.working = True
        taskEndFlag = True  # 任务正常结束标志
        # 创建指定数量的线程
        threads = []
        for _ in range(max_threads):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            threads.append(thread)
        # 使用生成器生成任务，并将其放入队列

        for task in self.generator:
            if not self.working:
                print("任务提前结束")
                taskEndFlag = False
                break
            # 等待队列中有空闲位置（即有线程完成任务）
            while self.task_queue.qsize() >= max_threads:
                time.sleep(0.1)  # 短暂等待，避免高CPU占用
            self.task_queue.put(task)

        # 等待所有任务完成
        self.task_queue.join()

        # 发送终止信号给所有线程
        for _ in range(max_threads):
            self.task_queue.put(None)

        # 等待所有线程结束
        for thread in threads:
            thread.join()
        self.working = True
        if self.taskEndBck:
            self.taskEndBck(taskEndFlag)

    def stop(self):
        self.working = False
