from threading import Thread, get_ident
import traceback
import os
import logging
import time
import asyncio
import warnings
from typing import Any
from queue import Queue
from pydantic import BaseModel


# 便捷获取log对象
def getLogger(name, level=logging.INFO, log_path=None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.FileHandler(log_path) if log_path else logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class CeilResult(BaseModel):
    index: int
    result: Any = None
    wait_time: float|None = None
    run_time: float|None = None
    err: str|None = None
    args: tuple|None = None
    kwargs: dict|None = None

class WorkPool:
    def __init__(self, logger: logging.Logger = None) -> None:
        self.logger = logger if logger else getLogger(f'pid-{get_ident()}')
        self.task_queue = Queue()
        self._alive = False
    
    def getTaskNum(self) -> int:
        return self.task_queue.qsize()
    
    def is_alive(self) -> bool:
        return self._alive
    
    def stop(self):
        self._alive = False
    
    def start(self, *, getGood = None, getResult, good_num: int = 3,
              is_put_args=False, is_put_kwargs=False) -> list:
        assert not self._alive, '任务已启动!'
        self.logger.info(f'PID-{os.getpid()} worker num: {good_num}')
        self._alive = True
        
        def _worker():
            gooder = getGood() if getGood else None
            while self._alive:
                que, index, put_time, args, kwargs = self.task_queue.get()
                sd = time.time()
                resulter = CeilResult(index=index, wait_time=sd-put_time)
                try:
                    resulter.result = getResult(gooder, *args, **kwargs) if gooder else getResult(*args, **kwargs)
                except:
                    resulter.err = traceback.format_exc()

                self.logger.info(f'pid-{get_ident()} args:{args}, kwargs:{kwargs}, is_err:{bool(resulter.err)}')
                if is_put_args: resulter.args = args
                if is_put_kwargs: resulter.kwargs = kwargs
                resulter.run_time = time.time() - sd
                que.put(resulter)

        ts = [Thread(target=_worker, daemon=True) for _ in range(good_num)]
        [t.start() for t in ts]
        return ts

    def kargs_in_task_put(self, *vs, kwargs:dict = None) -> Queue: 
        return self.all_in_task_puts([[vs, kwargs or {}]])
    
    def arg_in_task_puts(self, vs: list) -> Queue: 
        return self.all_in_task_puts([[(v,), {}] for v in vs])

    def kargs_in_task_puts(self, kargs: list[list[tuple, dict]]) -> Queue:
        return self.all_in_task_puts([[args, kws] for args, kws in kargs])

    def all_in_task_puts(self, args_and_kwargs: list) -> Queue:
        if len(args_and_kwargs)<=0: 
            warnings.warn("task_put参数数量小于1!")
            return None
        result_queue = Queue(maxsize=len(args_and_kwargs))
        [self.task_queue.put((result_queue, i, time.time(), *args_kwargs)) for i, args_kwargs in enumerate(args_and_kwargs)]
        return result_queue

    @staticmethod
    def getResult(result_queue: Queue, timeout = None) -> CeilResult:
        if result_queue is None: 
            warnings.warn("等待队列为None!")
            return CeilResult(index=0)
        return result_queue.get(timeout=timeout)
    
    @staticmethod
    def getResults(result_queue: Queue, is_sorded=True, timeout = None) -> list[CeilResult]:
        if result_queue is None: 
            warnings.warn("等待队列为None!")
            return []
        sd=time.time()
        results = []
        while len(results)<result_queue.maxsize:
            if timeout is not None:
                timeout-=time.time()-sd
                if timeout<0: raise TimeoutError(f'process:{len(results)}/{result_queue.maxsize}  timeout:{timeout}s')
            results.append(result_queue.get(timeout=timeout))
        return sorted(results, key=lambda x:x.index) if is_sorded else results
    
    @staticmethod
    async def async_getResult(result_queue: Queue, timeout = None) -> CeilResult:
        return await asyncio.to_thread(WorkPool.getResult, result_queue=result_queue, timeout=timeout)

    @staticmethod
    async def async_getResults(result_queue: Queue, is_sorded=True, timeout = None) -> list[CeilResult]:
        return await asyncio.to_thread(WorkPool.getResults, result_queue=result_queue, is_sorded=is_sorded, timeout=timeout)

