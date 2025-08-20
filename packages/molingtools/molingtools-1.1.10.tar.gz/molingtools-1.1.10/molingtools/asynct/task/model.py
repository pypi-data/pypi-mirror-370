import asyncio
import time
from typing import Any, AsyncIterator, Iterator
from warnings import warn
from pydantic import BaseModel
from tqdm import tqdm
    

class Dataer(BaseModel):
    data:Any
    is_complete: bool = False
    result: Any = None
    error: str|None = None
    is_deid: bool = False

class Dataers(BaseModel):
    dataers: list[Dataer]

    def get_first(self, timeout: float=None)-> tuple[Any, str|None]:
        der = self.dataers[0]
        while not der.is_complete:
            time.sleep(0.1)
            if timeout is not None: 
                timeout -= 0.1
                if timeout < 0:
                    self.kill()
                    raise TimeoutError
        return der.result, der.error
    
    async def aget_first(self, timeout: float=None)-> tuple[Any, str|None]:
        der = self.dataers[0]
        while not der.is_complete:
            await asyncio.sleep(0.1)
            if timeout is not None: 
                timeout -= 0.1
                if timeout < 0:
                    self.kill()
                    raise TimeoutError
        return der.result, der.error
    
    def it_result_error(self, is_tqdm=False, timeout: float=None)-> Iterator[tuple[Any, str|None]]:
        jder = tqdm(total=len(self.dataers)) if is_tqdm else None
        for der in self.dataers:
            while not der.is_complete:
                time.sleep(0.1)
                if timeout is not None: 
                    timeout -= 0.1
                    if timeout < 0:
                        self.kill()
                        raise TimeoutError
            if jder: jder.update(1)
            yield der.result, der.error
        if jder: jder.close()
    
    async def ait_result_error(self, is_tqdm=False, timeout: float=None)-> AsyncIterator[tuple[Any, str|None]]:
        jder = tqdm(total=len(self.dataers)) if is_tqdm else None
        for der in self.dataers:
            while not der.is_complete:
                await asyncio.sleep(0.1)
                if timeout is not None: 
                    timeout -= 0.1
                    if timeout < 0:
                        self.kill()
                        raise TimeoutError
            if jder: jder.update(1)
            yield der.result, der.error
        if jder: jder.close()
            
    @property
    def is_complete(self):
        return all([der.is_complete for der in self.dataers])
    
    def kill(self):
        for der in self.dataers:
            der.is_deid=True

class PDataer(Dataer):
    id: str
        
class PDataers(Dataers):
    dataers: list[PDataer]
    
    def kill(self):
        warn('进程任务不支持kill, 调用无效')
