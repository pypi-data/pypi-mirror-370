import os
import sqlite3
from .__sqltool__.action import Action
from .__sqltool__.body import encrypt, decrypt
from .__sqltool__.alter import Alter


class Sqlite(Action, Alter):
    def __init__(self, dbfilepath, if_new=True, ifencryp=False):
        
        # 打开数据库连接
        def db_func():
            if not if_new and not os.path.exists(dbfilepath):
                raise ValueError(f'没有 {dbfilepath} 文件!')
            db = sqlite3.connect(dbfilepath)
            return db
    
        class_map = {'varchar': 'text',
                     'text': 'text',
                     'bool': 'integer',
                     'int': 'integer',
                     'float': 'real'
                     }
        super().__init__(db_func, placeholder='?', class_map=class_map)

    # 判断表是否存在
    def ifExist(self, table):
        b = self.run(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table}'")
        return b and len(self._cursor.fetchall()) > 0
