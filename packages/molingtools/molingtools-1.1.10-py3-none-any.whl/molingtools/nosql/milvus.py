import asyncio
import hashlib
from threading import Thread, Lock
import time
from typing import Callable, Awaitable
from pydantic import BaseModel
try:
    from pymilvus import MilvusClient, AsyncMilvusClient
    from sentence_transformers import SentenceTransformer
    from torch import Tensor
    from openai import OpenAI, AsyncOpenAI
except:
    raise ModuleNotFoundError('pip install pymilvus sentence-transformers openai')


def getMD5(bt: bytes)->str:
    md5 = hashlib.md5()
    md5.update(bt)
    return md5.hexdigest()

class Milvuser:
    def __init__(self, url:str, get_model:Callable, default_col:str, default_vector_key:str, 
                 user: str = "", password: str = "", db_name: str = ""):
        self.client:MilvusClient=None
        self._lock = Lock()
        self.url = url
        self.get_model = get_model
        self.default_col = default_col
        self.default_vector_key=default_vector_key
        self._user = user
        self._pwd = password
        self._db_name = db_name
        self.model = None
        self._getvcs:Callable[[list], list] = lambda ls: [self.model(data) for data in ls]
        self._func:Callable[[list[dict]], list[str]] = lambda dts: [data[self.default_vector_key] for data in dts]
    
    def init_model(self):
        self.model = self.model or self.get_model()
        
    def set_getData_func(self, func:Callable[[list[dict]], list[str]]):
        self._func = func
        
    def set_getvectors_func(self, func:Callable[[list], list]):
        self._getvcs = func
        
    def getClient(self)->AsyncMilvusClient:
        client = AsyncMilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    def getClient(self)->MilvusClient:
        client = MilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
            
    def client_auto_reset(self, s=600):
        def temp():
            while True:
                time.sleep(s)
                with self._lock:
                    self.client.close()
                    self.client = self.getClient()
        Thread(target=temp, daemon=True).start()
        
    def create_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.client = self.client or self.getClient()
        if self.client.has_collection(col or self.default_col): return None
        return self.client.create_collection(
                                collection_name=col or self.default_col,
                                primary_field_name=primary_field_name,
                                dimension=dimension,  # 维度
                                id_type = id_type,
                                max_length=max_length,
                                **kwargs
                            )
            
    def drop_collection(self, col:str=None, **kwargs):
        self.client = self.client or self.getClient()
        if not self.client.has_collection(col or self.default_col): return None
        return self.client.create_collection(
                                collection_name=col or self.default_col,
                                **kwargs
                            )

    def update_insert(self, *datas:dict|BaseModel, col:str=None)->dict:
        datas=list(datas)
        for i in range(len(datas)):
            if isinstance(datas[i], BaseModel):
                datas[i] = datas[i].model_dump(exclude_none=True)
        vector_datas = self._func(datas)
        self.init_model()
        vcs = self._getvcs(vector_datas)
        rs = [{**data, 'vector': vector} for data, vector in zip(datas, vcs)]
        self.client = self.client or self.getClient()
        return self.client.insert(col or self.default_col, rs)
    
    def search(self, *query:str|Tensor, min_similarity:float=0.5, kn:int=3, col:str=None, output_fields:list[str]=None,
               filter:str='', filter_params:dict=None, **kwargs)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比  
        返回字段包含id、distance、output_fields中的字段  
        is null语法在milvus lite中不支持  
        """
        if isinstance(query[0], str):
            self.init_model()
            vc = self._getvcs(query)
        else:
            vc = list(query)
        self.client = self.client or self.getClient()
        res = self.client.search(col or self.default_col, vc, limit=kn, 
                                output_fields=output_fields,
                                filter=filter,
                                filter_params=filter_params or {},
                                # 相似度取值范围
                                search_params={"params": {
                                                    "radius": min_similarity,
                                                # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                    }
                                                },
                                **kwargs)
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(query)>1 else datas[0]
    
    def query(self, limit:int=10, col:str=None, ids:list=None, output_fields:list=None,
              filter:str='', filter_params:dict=None, **kwargs)-> list[dict]:
        self.client = self.client or self.getClient()
        res = self.client.query(col or self.default_col, filter=filter, filter_params=filter_params or {}, 
                                limit=limit, ids=ids, output_fields=output_fields, **kwargs)
        return list(res)
    
    def delete(self, filter:str, filter_params:dict=None, ids:list=None, col:str = None)-> list[dict]:
        self.client = self.client or self.getClient()
        res = self.client.delete(col or self.default_col, filter=filter, filter_params=filter_params or {}, ids=ids)
        return res
    
class AMilvuser:
    def __init__(self, url:str, get_model:Callable, default_col:str, default_vector_key:str, 
                 user: str = "", password: str = "", db_name: str = ""):
        self.client:AsyncMilvusClient=None
        self.url = url
        self.get_model = get_model
        self.default_col = default_col
        self.default_vector_key=default_vector_key
        self._user = user
        self._pwd = password
        self._db_name = db_name
        self.model = None
        self._getvcs:Callable[[list], Awaitable[list]] = lambda ls: asyncio.to_thread(lambda :[self.model(data) for data in ls])
        self._func:Callable[[list[dict]], list[str]] = lambda dts: [data[self.default_vector_key] for data in dts]
    
    def init_model(self):
        self.model = self.model or self.get_model()
        
    def set_getData_func(self, func:Callable[[list[dict]], list[str]]):
        self._func = func
        
    def set_getvectors_func(self, func:Callable[[list], Awaitable[list]]):
        self._getvcs = func
        
    def getClient(self)->AsyncMilvusClient:
        client = AsyncMilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    async def client_reset(self):
        if self.client: await self.client.close()
        self.client = self.getClient()
            
    async def client_auto_reset(self, s=600):
        while True:
            await asyncio.sleep(s)
            await self.client.close()
            self.client = self.getClient()

    async def create_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.client = self.client or self.getClient()
        if await self.client.has_collection(col or self.default_col): return None
        return await self.client.create_collection(
                                    collection_name=col or self.default_col,
                                    primary_field_name=primary_field_name,
                                    dimension=dimension,  # 维度
                                    id_type = id_type,
                                    max_length=max_length,
                                    **kwargs
                                )
    
    async def drop_collection(self, col:str=None, **kwargs):
        self.client = self.client or self.getClient()
        return await self.client.drop_collection(
                                    collection_name=col or self.default_col,
                                    **kwargs
                                )        
        
    async def update_insert(self, *datas:dict|BaseModel, col:str=None)->dict:
        datas=list(datas)
        for i in range(len(datas)):
            if isinstance(datas[i], BaseModel):
                datas[i] = datas[i].model_dump(exclude_none=True)
        vector_datas = self._func(datas)
        self.init_model()
        vcs = await self._getvcs(vector_datas)
        rs = [{**data, 'vector': vector} for data, vector in zip(datas, vcs)]
        self.client = self.client or self.getClient()
        return await self.client.insert(col or self.default_col, rs)
    
    async def search(self, *query:str|Tensor, min_similarity:float=0.5, kn:int=3, col:str=None, output_fields:list[str]=None, 
                      filter:str='', filter_params:dict=None, **kwargs)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比  
        返回字段包含id、distance、output_fields中的字段
        """
        if isinstance(query[0], str):
            self.init_model()
            vc = await self._getvcs(query)
        else:
            vc = list(query)
        self.client = self.client or self.getClient()
        res = await self.client.search(col or self.default_col, vc, limit=kn, 
                                        output_fields=output_fields,
                                        filter=filter,
                                        filter_params=filter_params or {},
                                        # 相似度取值范围
                                        search_params={"params": {
                                                            "radius": min_similarity,
                                                        # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                            }
                                                        },
                                        **kwargs)
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(query)>1 else datas[0]    

    async def query(self, limit:int=10, col:str=None, ids:list=None, output_fields:list=None,
                     filter:str='', filter_params:dict=None, **kwargs)-> list[dict]:
        self.client = self.client or self.getClient()
        res = await self.client.query(col or self.default_col, filter=filter, filter_params=filter_params or {},
                                       limit=limit, ids=ids, output_fields=output_fields, **kwargs)
        return list(res)

    async def delete(self, filter:str, filter_params:dict=None, ids:list=None, col:str = None)-> list[dict]:
        self.client = self.client or self.getClient()
        res = await self.client.delete(col or self.default_col, filter=filter, filter_params=filter_params or {}, ids=ids)
        return res
    
    
class STMilvuser(Milvuser):
    """使用SentenceTransformer加载模型
    """
    def __init__(self, url:str, model_name_or_path:str, default_col:str, default_vector_key:str, 
                 user: str = "", password: str = "", db_name: str = "", 
                 device:str='cpu'):
        super().__init__(url, get_model=lambda: SentenceTransformer(model_name_or_path, device=device), 
                         default_col=default_col, default_vector_key=default_vector_key, 
                        user=user, password=password, db_name=db_name)
        self.set_getvectors_func(lambda ls: self.model.encode(ls))
   
class ASTMilvuser(AMilvuser):
    """使用SentenceTransformer加载模型
    """
    def __init__(self, url:str, model_name_or_path:str, default_col:str, default_vector_key:str, 
                 user: str = "", password: str = "", db_name: str = "", 
                 device:str='cpu'):
        super().__init__(url, get_model=lambda: SentenceTransformer(model_name_or_path, device=device), 
                         default_col=default_col, default_vector_key=default_vector_key, 
                        user=user, password=password, db_name=db_name)
        self.set_getvectors_func(lambda ls: asyncio.to_thread(lambda :self.model.encode(ls)))
       
class OpenaiMilvuser(Milvuser):
    """使用openai接口加载模型
    """
    def _getvectors_func(self, ls):
        datas = self.model.embeddings.create(input=ls, model=self.embeddings_model).data
        return [data.embedding for data in datas]
        
    def __init__(self, url:str, openai_url:str, embeddings_model:str, default_col:str, default_vector_key:str,
                 api_key:str='EMPTY', user: str = "", password: str = "", db_name: str = ""):
        super().__init__(url, get_model=lambda: OpenAI(base_url=openai_url,api_key=api_key), 
                         default_col=default_col, default_vector_key=default_vector_key, 
                        user=user, password=password, db_name=db_name)
        self.embeddings_model=embeddings_model
        self.set_getvectors_func(self._getvectors_func)

class AOpenaiMilvuser(AMilvuser):
    """使用openai接口加载模型
    """
    async def _getvectors_func(self, ls):
        datas = (await self.model.embeddings.create(input=ls, model=self.embeddings_model)).data
        return [data.embedding for data in datas]
        
    def __init__(self, url:str, openai_url:str, embeddings_model:str, default_col:str, default_vector_key:str,
                 api_key:str='EMPTY', user: str = "", password: str = "", db_name: str = ""):
        super().__init__(url, get_model=lambda: AsyncOpenAI(base_url=openai_url,api_key=api_key), 
                         default_col=default_col, default_vector_key=default_vector_key, 
                        user=user, password=password, db_name=db_name)
        self.embeddings_model=embeddings_model
        self.set_getvectors_func(self._getvectors_func)