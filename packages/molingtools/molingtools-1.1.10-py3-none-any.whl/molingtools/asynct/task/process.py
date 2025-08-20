from uuid import uuid4
from .model import PDataer, PDataers
from multiprocessing import Process, Queue as PQueue, Value
from multiprocessing.sharedctypes import Synchronized
from threading import Thread
import time
import traceback
from typing import Any, Callable


class PTaskControl:
    def __init__(self, func:Callable[[Any], Any], get_model_func:Callable[..., Any]=None, interval: float = 0.05):
        """单入参函数, 带返回值  
        注意输入输出需要可序列化
        """
        self._func = func
        self._get_model_func=get_model_func
        self._queue = PQueue()
        self._out_queue = PQueue()
        self._task_num = Value('i', 0)
        self._start = Value('b', False)
        self._map:dict[str, PDataer] = {}
        self._interval = interval
    
    @staticmethod
    def _ceil(is_start:Synchronized, task_num:Synchronized, inq: PQueue, outq: PQueue, func, get_model_func, interval):
        task_num.value+=1
        model = get_model_func and get_model_func()
        while is_start.value:
            try:
                dataer:PDataer = inq.get_nowait()
            except KeyboardInterrupt:
                return
            except:
                time.sleep(interval)
                continue
            # if dataer.is_deid.value: continue
            result, error= None, None
            try:
                result = func(model, dataer.data) if model else func(dataer.data)
            except KeyboardInterrupt:
                return
            except:
                error = traceback.format_exc()
            outq.put((dataer.id, result, error))
        task_num.value -=1
        
    def _map_result(self):
        while self._start.value:
            try:
                tid, result, error = self._out_queue.get_nowait()
                der = self._map.pop(tid)
                der.result = result
                der.error = error
                der.is_complete = True
            except:
                time.sleep(self._interval)
    
    def run(self, num:int):
        if self._start.value: self.stop()
        self._start.value = True
        [Process(target=PTaskControl._ceil, args=(self._start,self._task_num,self._queue,self._out_queue,self._func,self._get_model_func,self._interval), daemon=True).start() for _ in range(num)]
        Thread(target=self._map_result, daemon=True).start()
        
    def add_data(self, *data)->PDataers:
        """加入不阻塞
        """
        if not self._start.value: raise RuntimeError('任务已停止')
        dataers = []
        uuid = str(uuid4())
        for i,d in enumerate(data):
            tid = f'{uuid}_{i}'
            dataer = PDataer(data=d, id=tid)
            self._queue.put(dataer)
            dataers.append(dataer)
            self._map[tid] = dataer
        return PDataers(dataers=dataers)
        
    def stop(self):
        self._start.value = False
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                continue
        while self._task_num.value>0:
            time.sleep(self._interval)


