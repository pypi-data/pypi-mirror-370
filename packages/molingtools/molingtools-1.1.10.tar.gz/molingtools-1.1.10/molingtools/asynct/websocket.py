from asyncio import Queue, Task
import asyncio
from typing import Callable
try:
    import websockets
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install websockets')


class WBSer:
    def __init__(self, ping_interval:float=5, recv_ping='ping', send_ping='ping'):
        self.ws = None
        self.inq = Queue()
        self.outq = Queue()
        self.afuncs = []
        self.tasks:list[Task] = []
        self.is_start = False
        self.ping_interval = ping_interval
        self.recv_ping = recv_ping
        self.send_ping = send_ping
    
    async def afunc_recv(self):
        while self.is_start:
            frame = await self.ws.recv()
            if frame!=self.recv_ping: await self.inq.put(frame)
    
    async def afunc_send(self):
        while self.is_start:
            await self.ws.send(await self.outq.get())
    
    # 心跳
    async def afunc_ping(self):
        while self.is_start:
            await asyncio.sleep(self.ping_interval)
            await self.ws.send(self.send_ping)
        
    def add_other_atask(self, *afuncs:Callable[['WBSer'], None]):
        for afunc in afuncs:
            self.afuncs.append(afunc)
            if self.is_start: self.tasks.append(asyncio.create_task(afunc(self)))
    
    async def start(self, ws_url:str):
        if self.is_start: await self.close()
        self.ws = await websockets.connect(ws_url)
        self.is_start = True
        self.tasks.append(asyncio.create_task(self.afunc_recv()))
        self.tasks.append(asyncio.create_task(self.afunc_send()))
        self.tasks.append(asyncio.create_task(self.afunc_ping()))
        self.tasks.extend([asyncio.create_task(func(self)) for func in self.afuncs])
        
    async def close(self):
        self.is_start=False
        try:
            await self.ws.close()
            [task.cancel() for task in self.tasks]
        except:
            pass
        self.tasks.clear()
        