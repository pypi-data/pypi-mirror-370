import asyncio
from threading import Thread, Lock
import time
from typing import Generator,AsyncGenerator
from pydantic import BaseModel
try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
    from pymongo import MongoClient
except:
    raise ModuleNotFoundError('pip install pymongo motor')


class Mongoer:
    def __init__(self, url:str, default_db:str, default_col:str):
        self.url = url
        self.client=None
        self.aclient=None
        self._lock = Lock()
        self.default_db=default_db
        self.default_col=default_col
    
    def _getAClient(self):
        client = AsyncIOMotorClient(self.url)
        client.get_io_loop = asyncio.get_running_loop
        return client
    
    def _getClient(self):
        client = MongoClient(self.url)
        return client
        
    def getConnect(self, db: str=None, col:str=None):
        if self.client is None: 
            with self._lock:
                self.client=self._getClient()
        return self.client[db or self.default_db][col or self.default_col]
    
    def getAConnect(self, db: str=None, col:str=None)->AsyncIOMotorCollection:
        if self.aclient is None: self.aclient=self._getAClient()
        return self.aclient[db or self.default_db][col or self.default_col]
    
    async def aclient_reset(self):
        if self.aclient: self.aclient.close()
        self.aclient = self._getAClient()
        
    def client_auto_reset(self, s=600):
        def temp():
            while True:
                time.sleep(s)
                with self._lock:
                    self.client.close()
                    self.client = self._getClient()
        Thread(target=temp, daemon=True).start()
            
    async def aclient_auto_reset(self, s=600):
        while True:
            await asyncio.sleep(s)
            self.aclient.close()
            self.aclient = self._getAClient()
        
    def find(self, query: dict, db:str=None, col:str=None, cig:dict=None, default_id:int=0)->dict|None:
        if default_id==0: cig = {'_id':0, **cig} if cig else {'_id':0}
        result = self.getConnect(db,col).find_one(query or {}, cig or {})
        return result
    
    async def afind(self, query: dict, db:str=None, col:str=None, cig:dict=None, default_id:int=0)->dict|None:
        if default_id==0: cig = {'_id':0, **cig} if cig else {'_id':0}
        result = await self.getAConnect(db,col).find_one(query or {}, cig or {})
        return result

    def find_all(self, query: dict=None, db:str=None, col:str=None, cig=None,
                 sort_key_or_list: str|list[str]=None, sort_direction=1,
                 skip:int=None, limit:int=None)->Generator[dict, None, None]:
        cursor  = self.getConnect(db,col).find(query,  {'_id':0, **cig} if cig else {'_id':0})
        if sort_key_or_list: cursor=cursor.sort(sort_key_or_list, sort_direction)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        for dt in cursor:
            yield dt
        
    async def afind_all(self, query: dict=None, db:str=None, col:str=None, cig=None,
                        sort_key_or_list: str|list[str]=None, sort_direction=1,
                        skip:int=None, limit:int=None)->AsyncGenerator[dict, None]:
        cursor  = self.getAConnect(db,col).find(query,  {'_id':0, **cig} if cig else {'_id':0})
        if sort_key_or_list: cursor=cursor.sort(sort_key_or_list, sort_direction)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        async for dt in cursor:
            yield dt
    
    def find_onekey_all(self, key:str, query: dict=None, db:str=None, col:str=None)->list:
        cursor  = self.getConnect(db,col).find(query, {'_id':0, key:1})
        return [dt[key] for dt in cursor]
    
    async def afind_onekey_all(self, key:str, query: dict=None, db:str=None, col:str=None)->list:
        cursor  = self.getAConnect(db,col).find(query, {'_id':0, key:1})
        return [dt[key] async for dt in cursor]

    def find_onecol(self, key:str, query: dict=None, db:str=None, col:str=None, default=None):
        dt  = (self.getConnect(db,col).find_one(query, {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    async def afind_onecol(self, key:str, query: dict, db:str=None, col:str=None, default=None):
        dt  = (await self.getAConnect(db,col).find_one(query, {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    def count(self, query: dict=None, db:str=None, col:str=None,)->int:
        return self.getConnect(db,col).count_documents(query)

    async def acount(self, query: dict=None, db:str=None, col:str=None,)->int:
        return await self.getAConnect(db,col).count_documents(query)

    def update_one(self, query: dict, data: BaseModel|dict, db:str=None, col:str=None, upsert=True)->dict:
        return self.getConnect(db,col).update_one(query, {'$set': data.model_dump() if isinstance(data,BaseModel) else data}, upsert=upsert).raw_result
    
    async def aupdate_one(self, query: dict, data: BaseModel|dict, db:str=None, col:str=None, upsert=True)->dict:
        return (await self.getAConnect(db,col).update_one(query, {'$set': data.model_dump() if isinstance(data,BaseModel) else data}, upsert=upsert)).raw_result

    def update(self, query: dict, dt: dict, db:str=None, col:str=None)->dict:
        return self.getConnect(db,col).update_many(query, {'$set': dt}).raw_result
    
    async def aupdate(self, query: dict, dt:dict, db:str=None, col:str=None)->dict:
        return (await self.getAConnect(db,col).update_many(query, {'$set': dt})).raw_result

    def pop(self, query: dict,db:str=None, col:str=None)->dict|None:
        try:
            dt = self.getConnect(db,col).find_one_and_delete(query) or {}
            dt.pop('_id', None)
            return dt
        except asyncio.exceptions.CancelledError as e:
            raise e
        except Exception as e:
            return None
        
    async def apop(self, query: dict,db:str=None, col:str=None)->dict|None:
        try:
            dt = (await self.getAConnect(db,col).find_one_and_delete(query)) or {}
            dt.pop('_id', None)
            return dt
        except asyncio.exceptions.CancelledError as e:
            raise e
        except Exception as e:
            return None

    def insert(self, data: BaseModel|dict, db:str=None, col:str=None, **kwargs):
        return self.getConnect(db,col).insert_one(data.model_dump( **kwargs) if isinstance(data, BaseModel) else data)
    
    async def ainsert(self, data: BaseModel|dict, db:str=None, col:str=None, **kwargs):
        return await self.getAConnect(db,col).insert_one(data.model_dump( **kwargs) if isinstance(data, BaseModel) else data)

    def insert_many(self, datas: list[BaseModel|dict], db:str=None, col:str=None, **kwargs):
        if not datas: return None
        datas = [(data.model_dump(**kwargs) if isinstance(data, BaseModel) else data) for data in datas]
        return self.getConnect(db,col).insert_many(datas)
    
    async def ainsert_many(self, datas: list[BaseModel|dict], db:str=None, col:str=None, **kwargs):
        if not datas: return None
        datas = [(data.model_dump(**kwargs) if isinstance(data, BaseModel) else data) for data in datas]
        return await self.getAConnect(db,col).insert_many(datas)

    def delete(self, query: dict, db:str=None, col:str=None)->dict:
        return self.getConnect(db,col).delete_many(query).raw_result
    
    async def adelete(self, query: dict, db:str=None, col:str=None)->dict:
        return (await self.getAConnect(db,col).delete_many(query)).raw_result