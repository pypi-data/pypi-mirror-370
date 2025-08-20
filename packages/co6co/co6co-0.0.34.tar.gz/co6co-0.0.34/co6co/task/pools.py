
from concurrent.futures import ThreadPoolExecutor
import netrc
import queue
import asyncio
import threading
from typing import Callable, Tuple, Any, List, TypeVar, Iterable, Awaitable

RT = TypeVar('RT')
T = TypeVar('T')


async def timeout_async(timeout, func, *args, **kwargs):
    """ 
    loop = asyncio.get_event_loop()
    cap = loop.run_until_complete(timeout_async(5, open_video))

    :param timeout: 超时时间（秒）
    :return: 打开结果
    """
    try:
        # 等待指定的超时时间
        cap = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        return cap
    except asyncio.TimeoutError:
        print("Timeout occurred while opening the video stream.")
        return False


def timeout(timeout, func, throw: bool = True,  *args, **kwargs) -> Tuple[bool, Any | None]:
    """
    此函数用于在指定时间内尝试打开视频流
    :param timeout: 超时时间（秒）
    :param func , *args, **kwargs
    :param throw: 是否抛出异常

    func 执行异常会抛出异常

    :return: 是否超时,返回值
    """
    result = []
    exception = []

    def wrapper():
        try:
            result.append(func(*args, **kwargs))
        except Exception as e:
            exception.append(e)
    # 创建并启动新线程来打开视频流
    thread = threading.Thread(target=wrapper)
    thread.start()
    # 等待指定的超时时间
    thread.join(timeout)
    if thread.is_alive():
        # //todo 这里不知要怎么停止线程，_stop 有锁时，会有断言错误，
        # 如果线程仍在运行，说明超时了
        lock = thread._tstate_lock
        if lock is None:
            thread._stop()
        else:
            # 让它自己完成后停止
            pass
        return True, None
    if throw and exception:
        raise exception[0]
    return False, result[0]


async def run_async_tasks(data: Iterable[T], taskHandler: Callable[[T], Awaitable[RT]]) -> List[RT]:
    """
    批量执行异步任务并返回结果 
    Args:
        data: 输入数据的可迭代对象
        task_handler: 异步处理函数，接收单个数据项并返回可等待对象

    Returns:
        按任务提交顺序排列的结果列表
    """
    tasks = [taskHandler(item) for item in data]

    if not tasks:
        return []  # 处理空输入的边界情况

    # 等待所有任务完成
    results: List[RT] = await asyncio.gather(*tasks)
    # 处理结果
    # for i, result in enumerate(results):
    #    print(f"{i}-<{result}")
    return results


class limitThreadPoolExecutor(ThreadPoolExecutor):
    """
    限制进程池队列长度（默认队列长度无限）
    warning: 使用该模型的 submit 方法，请不要使用带锁异步模型[比如 AsyncSession]，否则可能出现死锁情况
             如果有需要执行异步，可以 使用 async_task 方法或者 run_async_tasks 执行,锁可以使用asyncio.lock 锁

    防止内存爆满的问题
    //2025-08-07
    //todo 任务中存在 ping + db +event_loop 会卡死未找到原因！
    // 可下面类 ThreadPool 替代


    # .shutdown(wait=True)
    # True  =>会阻塞主线程，直到 task 任务完成
    # False =>线程池会立即关闭，不再接受新任务，并且不会等待已提交的任务完成
    # 当 cancel_futures 为 True 时，在调用 shutdown 方法关闭线程池时，会尝试取消所有尚未开始执行的任 
    """

    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        # 不甚至将时无限队列长度
        self._work_queue = queue.Queue(self._max_workers * 2)  # 设置队列大小

    def async_task(self, sync_task: Callable[..., RT],  *args, loop: asyncio.AbstractEventLoop = None):
        """
        使用 loop执行 
        @parm sync_task 执行同步方法  
        @... sync_task 需要的参数 
        async def update(session,name,ip)
            pass
        def checkAll(ip,name):
            bll=createDb()
            # update  
            result = bll.run(update, bll.session, name, ip)
            return result

        with ThreadPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_running_loop() 
            tasks = [] 
            # 创建多个任务
            for i in range(1, 10):
                ip = f"192.168.1.{i}"
                name = f"test{i}"  
                db_task=executor.async_task(checkAll,name, ip ) 
                tasks.append(db_task)

        # 等待所有数据库操作完成
        results = await asyncio.gather(*tasks)

        # 处理结果
        for i, (updated, result) in enumerate(results):
            log.succ(f"任务 {i+1}: {'更新' if updated else '插入'} 影响行数: {result}")
        """
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        # 将同步函数提交到线程池，由事件循环管理
        return loop.run_in_executor(self, sync_task, *args)


class ThreadPool:
    """
    线程池
    使用示例
    def task(num):
        print(f"任务 {num} 开始执行")
        time.sleep(1)
        print(f"任务 {num} 执行完毕")

    pool = ThreadPool(max_workers=3)
    for i in range(5):
        # n=i 来 "冻结" 当前的 i 值，而不是让 lambda 函数在执行时才去查找 i 变量（此时可能已被修改）
        pool.submit(lambda n=i: task(n)) 
    pool.join()
    """

    def __init__(self, max_workers: int = 4):
        if not max_workers or max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")
        self.max_workers = max_workers
        self.task_queue = queue.Queue(max_workers)
        self.workers: List[threading.Thread] = []
        self._create_workers()

    def _create_workers(self):
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            try:
                task()
            finally:
                self.task_queue.task_done()

    def submit(self, task):
        self.task_queue.put(task)

    def join(self):
        self.task_queue.join()
        # 发送终止信号
        for _ in range(self.max_workers):
            self.task_queue.put(None)
        for worker in self.workers:
            worker.join()
