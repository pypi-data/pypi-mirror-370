import asyncio
from threading import Thread
from time import sleep, ctime
from co6co.utils import log
from functools import partial
from typing import Callable, Awaitable, Any, TypeVar
from co6co.utils import isCallable
_T = TypeVar("_T")
# 2. 自定义事件循环设置


def create_event_loop():
    """创建并配置自定义事件循环"""
    # 创建新的事件循环
    custom_loop = asyncio.new_event_loop()
    # print(f"创建自定义事件循环: {custom_loop} (ID: {id(custom_loop)})")

    # 将自定义循环设置为当前线程的默认循环
    asyncio.set_event_loop(custom_loop)
    return custom_loop


class ThreadEvent:
    """
    线程 Event loop
    提供一个线程，执行任务
    Run Event Loop in different thread. 
    """
    @property
    def loop(self):
        return self._loop

    def __init__(self, threadName: str = None, quitBck: Callable[[], None] = None):
        self._loop = create_event_loop()
        self._loopStopBck = quitBck
        self.closed = False
        Thread(target=self._start_background, daemon=True, name=threadName) .start()

    def _start_background(self):
        self.loop.run_forever()
        if self._loopStopBck != None and isCallable(self._loopStopBck):
            self._loopStopBck()

    def runTask(self, tastFun: Callable[..., Awaitable[Any]], *args, **kwargs):
        task = asyncio.run_coroutine_threadsafe(tastFun(*args, **kwargs), loop=self.loop)
        return task.result()

    def run(self, fun: Callable[..., Any], bck: Callable[[asyncio.Handle], None] = None, *args, **kwargs):
        """
        执行普通方法

        :param fun: 普通方法
        :param bck: 回调方法,为取消任务提供handle
                                        handle.cancel() 
                                        handle.cancelled()#返回 True 表示回调已被取消
                                        handle.done()#返回 True 表示回调已执行或已取消
                                        handle.callback #获取原始回调函数
                                        handle.args #获取传递给回调的位置参数
        :param args: 普通方法参数
        :param kwargs: 普通方法参数
        :return: None
        """
        # fun,*args,**kwargs
        handle = self.loop.call_soon_threadsafe(partial(fun, *args, **kwargs))
        if bck and isCallable(bck):
            bck(handle)

    def _shutdown(self):
        # self._loop.close() -> self._loop.is_running=false
        if not self.closed and self._loop.is_running():
            self.closed = True
            self._loop.stop()

    def close(self):
        # 执行一个普通函数
        self._loop.call_soon_threadsafe(partial(self._shutdown))

    def __del__(self):
        #
        if self._loop.is_running():
            self._loop.close()


class EventLoop:
    """
    数据库操作 【对 ThreadEvent 简单封装】
    定义异步方法
    运行 result=run(异步方法,arg)

    """
    _eventLoop: ThreadEvent
    _closed: bool = None

    def __init__(self) -> None:
        self._eventLoop = ThreadEvent()
        self._closed = False

    def run(self, task, *args, **argkv):
        if self._closed:
            raise RuntimeError('ThreadEvent is closed')
        data = self._eventLoop.runTask(task, *args, **argkv)
        return data

    def close(self):
        self._eventLoop.close()
        self._closed = True

    def __del__(self) -> None:
        if not self._closed:
            self._eventLoop.close()


class Executing:
    """
    创建线程，以新的 look 执行一个 异步方法
    """
    _starting: bool = None

    @property
    def loop(self):
        return self._loop

    @property
    def runing(self):
        return self._starting

    def __init__(self, threadName: str, func: Callable[..., Awaitable[Any]], *args, **kvgs):
        '''
        threadName: 线程名
        func: 执行的方法 async   :Callable[[str], str]
        args:  func 参数
        kvgs: func 参数
        '''
        self._isCallClose = False
        self.threadName = threadName
        self.taskFunc = func
        self.args = args
        self.kvgs = kvgs
        Thread(target=self._start_background, daemon=True, name=threadName) .start()

    def _start_background(self):
        try:
            self._loop = create_event_loop()
            log.log("线程'{}->{}'运行...".format(self.threadName, id(self.loop)))
            self._starting = True
            self.loop.run_until_complete(self.taskFunc(*self.args, **self.kvgs))
        except Exception as e:
            log.warn("线程'{}->{}'执行出错:{}".format(self.threadName, id(self.loop), e))
        finally:
            log.log("线程'{}->{}'结束.".format(self.threadName, id(self.loop)))
            self._starting = False
            self.loop.close()


class TaskManage:
    _starting: bool = None

    @property
    def loop(self):
        return self._loop

    @property
    def runing(self):
        return self._starting

    def __init__(self, threadName: str = None):
        self._loop = asyncio.new_event_loop()
        self._loopClosed = False
        self.threadName = threadName
        Thread(target=self._start_background, daemon=True, name=threadName) .start()

    def _start_background(self):
        asyncio.set_event_loop(self.loop)
        log.log("线程'{}->{}'运行...".format(self.threadName, id(self.loop)))
        self._starting = True
        self._loop.run_forever()
        log.log("线程'{}->{}'结束.".format(self.threadName, id(self.loop)))
        self._starting = False

    def runTask(self, tastFun: Callable[..., Awaitable[Any]], callBck: Callable[[asyncio.Future[_T]], Any] = None, *args, **kwargs):
        """
        param tastFun: 异步方法
        param callBck: 回调方法 [执行结果]，默认None,将直接返回tastFun执行的结果
        param args: tastFun异步方法参数
        param kwargs: tastFun异步方法参数
        """
        # log.warn(f"ThreadEventLoop22:{id(self._loop)}")
        # run_coroutine_threadsafe 从非事件循环线程向事件循环线程提交协程任务
        task = asyncio.run_coroutine_threadsafe(tastFun(*args, **kwargs), loop=self._loop)
        # .result() 方法等待协程的结果，或者使用 .add_done_callback() 添加回调来处理结果。
        if callBck:
            task.add_done_callback(callBck)
        else:
            return task.result()

    def _stop(self):
        self._loop.stop()
        self._starting = False

    def stop(self):
        """
        runTask: 执行完后后才能调用，可再回调中调用
        调用完记得关闭
        """
        self._loop.call_soon_threadsafe(self._stop)

    def close(self):
        self._loop.call_soon_threadsafe(self._loop.close)
        self._loopClosed = True

    def __del__(self):
        if not self._loopClosed:
            self._loop.close()
