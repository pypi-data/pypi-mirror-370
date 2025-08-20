from asyncio import Queue as AQueue
import asyncio
from threading import Thread
from typing import Any, Callable
from .model import Dataers, Dataer
import traceback


class ATaskControl:
    def __init__(self, afunc:Callable[[Any], Any], get_model_afunc:Callable[..., Any]=None, interval: float = 0.05):
        """单入参函数, 带返回值  
        """
        self._afunc = afunc
        self._get_model_afunc=get_model_afunc
        self._queue = AQueue()
        self._task_num = 0
        self._start = False
        self._interval = interval
    
    async def _ceil(self):
        self._task_num += 1
        model = self._get_model_afunc and await self._get_model_afunc()
        while self._start:
            try:
                dataer:Dataer = self._queue.get_nowait()
            except:
                await asyncio.sleep(self._interval)
                continue
            if dataer.is_deid: continue
            try:
                dataer.result = (await self._afunc(model, dataer.data)) if model else (await self._afunc(dataer.data))
            except:
                dataer.error = traceback.format_exc()
            finally:
                dataer.is_complete=True
        self._task_num -=1
    
    def _run(self, num):
        async def t():
            await asyncio.gather(*[self._ceil() for _ in range(num)])
        asyncio.run(t())
    
    async def run(self, num:int):
        if self._start: await self.stop()
        self._start = True
        Thread(target=self._run, args=(num,), daemon=True).start()
    
    def add_data(self, *data)->Dataers:
        """加入不阻塞
        """
        if not self._start: raise RuntimeError('任务已停止')
        dataers = []
        for d in data:
            dataer = Dataer(data=d)
            self._queue.put(dataer)
            dataers.append(dataer)
        return Dataers(dataers=dataers)
    
    async def stop(self):
        self._start = False
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                continue
        while self._task_num>0:
            await asyncio.sleep(self._interval)