from .model import Dataer, Dataers
from threading import Thread
from queue import Queue as TQueue
import time
import traceback
from typing import Any, Callable

    
class TaskControl:
    def __init__(self, func:Callable[[Any], Any], get_model_func:Callable[..., Any]=None, interval: float = 0.05):
        """单入参函数, 带返回值
        """
        self._func = func
        self._get_model_func=get_model_func
        self._queue = TQueue()
        self._task_num = 0
        self._start = False
        self._interval = interval
    
    def _ceil(self):
        self._task_num += 1
        model = self._get_model_func and self._get_model_func()
        while self._start:
            try:
                dataer:Dataer = self._queue.get_nowait()
            except KeyboardInterrupt:
                return
            except:
                time.sleep(self._interval)
                continue
            if dataer.is_deid: continue
            try:
                dataer.result = self._func(model, dataer.data) if model else self._func(dataer.data)
            except KeyboardInterrupt:
                return
            except:
                dataer.error = traceback.format_exc()
            dataer.is_complete=True
        self._task_num -=1
    
    def run(self, num:int):
        if self._start: self.stop()
        self._start = True
        [Thread(target=self._ceil, daemon=True).start() for _ in range(num)]
    
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
        
    def stop(self):
        self._start = False
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                continue
        while self._task_num>0:
            time.sleep(self._interval)
