from datetime import datetime
from threading import Thread, Lock
import traceback
from tqdm import tqdm
try:
    from pymongo import MongoClient
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install pymongo')


WAIT = 'wait'
RUNNING = 'running'
SUCCESS = 'success'
ERROR = 'error'


class MGSaver:
    def __init__(self, mongodb_connect: str, dbname='savedata', batch_size=1000):
        self.getmg_func = lambda: MongoClient(mongodb_connect)
        self.dbname = dbname
        self._client = self.getmg_func()
        self._lock = Lock()
        self.batch_size = batch_size

    # 保存任务输入参数
    def keys_save(self, keyname, keys: list=None, lies=None, if_replace_index=False):
        self._keyname = keyname
        self._kcet = self._client[self.dbname][keyname]
        if not keys: return
        lies = lies if lies else keys[0].keys()
        if if_replace_index:
            try:
                self._kcet.drop_index(self._keyname)
            except:
                pass
        self._kcet.create_index(
            {lie: 1 for lie in lies}, unique=True, name=self._keyname)
        for dt in keys:
            try:
                dt['_complete'] = WAIT
                self._kcet.insert_one(dt)
            except:
                pass

    # 将结果表作为下个任务的参数表,包含全部数据
    def set_alldata_keytable(self, keyname):
        self._keyname = keyname
        self._kcet = self._client[self.dbname][keyname]
        self._kcet.update_many({'_complete': {'$ne': SUCCESS}}, {
                               '$set': {'_complete': WAIT}})

    # 获取匹配包含值的数据
    def getMongoContainDatadts(self, keyname, mark_lie:str, *values:str, lies:list = None, is_case_insensitive=True)->list:
        return self.getMongoDatadts(keyname, { '$or': [{mark_lie: {"$regex": value, '$options': 'i' if is_case_insensitive else None}}
                                                       for value in values]}, lies)
    
    def getMongoDatadts(self, keyname, query: dict, lies:list = None)->list:
        kcet = self._client[self.dbname][keyname]
        fields={'_id': 0}
        if lies: fields.update({lie: 1 for lie in lies})
        return list(kcet.find(query, fields))
        
    def _run(self):
        client = self.getmg_func()
        kcet = client[self.dbname][self._keyname]
        dcet = client[self.dbname][self._dataname]

        while True:
            try:
                # 取出数据
                with self._lock:
                    kdt = kcet.find_one_and_update({'_complete': WAIT},
                                                   {'$set': {'_complete': RUNNING, '_sd': datetime.now()}})
                if kdt is None: break
                taskid = kdt.pop('_id')
                # 移除框架自带的字段
                [kdt.pop(k) for k in list(kdt.keys()) if k.startswith('_')]
                dts = self._task_func(**kdt)
                if dts: dcet.insert_many([{'_key': taskid, **dt} for dt in dts])
                # 更新完成状态
                status = {'_complete': SUCCESS, '_ed': datetime.now()}
            except:
                err = traceback.format_exc()
                # 更新错误状态
                status = {'_complete': ERROR,
                          '_ed': datetime.now(), '_err': err}
            kcet.update_one({'_id': taskid}, {'$set': status})
            self._pbar.update()

        client.close()

    def task_run(self, dataname, kwargs_func_dts, threadnum=5, max_retry_num: int = 3):
        if max_retry_num <= 0: raise ValueError('重试次数已达上限!')
        self._dataname = dataname
        self._task_func = kwargs_func_dts
        task_num = self._kcet.count_documents({})

        # 初始化开始状态
        self._kcet.update_many({'_complete': {'$ne': SUCCESS, '$exists': True}}, {
                               '$set': {'_complete': WAIT}})
        self._pbar = tqdm(total=task_num, desc=f"task-{self._keyname}", unit="item")
        self._pbar.update(self._kcet.count_documents({'_complete': SUCCESS}))
        # 开始多线程任务
        ts = [Thread(target=self._run) for _ in range(threadnum)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self._pbar.close()
        # 监测任务完成情况
        incomplete_num = self._kcet.count_documents({'_complete': {'$ne': SUCCESS, '$exists': True}})
        if incomplete_num:
            print('未完成任务数量:', incomplete_num)
            self.task_run(dataname, kwargs_func_dts, threadnum=threadnum, max_retry_num=max_retry_num-1)
        else:
            print(f'任务-{self._keyname} 全部完成')

    def get_linkDataIt(self, keyname, dataname, is_keyname_startswith=True):
        with self.getmg_func() as client:
            dcet = client[self.dbname][dataname]
            desc = f'获取连接数据'
            data_num = dcet.count_documents({})
            if data_num == 0: 
                print('数据表为空!')
                return
            pbar = tqdm(total=data_num, desc=desc)
            dts = []
            for dt in dcet.aggregate([{'$lookup': {'from': keyname, 'localField': '_key', 'foreignField': '_id', 'as': '_keys'}}]):
                [dt.pop(k) for k in list(dt.keys())
                if k.startswith('_') and k != '_keys']
                keydt = dt.pop('_keys')[0]
                for k in list(keydt.keys()):
                    if k.startswith('_'):
                        keydt.pop(k)
                    else:
                        keydt[f'{keyname}_{k}' if is_keyname_startswith else k] = keydt.pop(k)
                dts.append({**keydt, **dt})
                if len(dts) >= self.batch_size:
                    pbar.update(self.batch_size)
                    yield dts
                    dts.clear()
            if len(dts):
                pbar.update(len(dts))
                yield dts
            pbar.close()
            
    def get_dataIt(self, dataname, query:dict = None, conf:dict = None):
        query = query or {}
        conf = conf or {}
        with self.getmg_func() as client:
            dcet = client[self.dbname][dataname]
            desc = f'获取集合数据'
            data_num = dcet.count_documents(query)
            if data_num == 0: 
                print('数据表为空!')
                return
            pbar = tqdm(total=data_num, desc=desc)
            dts = []
            for dt in dcet.find(query, {'_id': 0, '_key': 0, '_complete': 0, '_sd': 0, '_ed': 0, '_err':0, **conf}):
                dts.append(dt)
                if len(dts) >= self.batch_size:
                    pbar.update(self.batch_size)
                    yield dts
                    dts.clear()
            if len(dts):
                pbar.update(len(dts))
                yield dts
            pbar.close()
            
    # 保存合并连接数据
    def save_linkData(self, keyname, dataname, linkname:str, is_keyname_startswith=True):
        with self.getmg_func() as client:
            lcet = client[self.dbname][linkname]
            lcet.drop()
            print(f'重新生成连接表-{linkname}')
            for dts in self.get_linkDataIt(keyname, dataname, is_keyname_startswith=is_keyname_startswith):
                lcet.insert_many(dts)