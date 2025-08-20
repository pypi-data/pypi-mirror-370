from .__sqltool__.body import encrypt, decrypt
from .__sqltool__.action import Action
from .__sqltool__.alter import Alter
import importlib
try:
    import pymysql
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install pymysql')

class Mysql(Action, Alter):
    def __init__(self, dbname, user, pwd,
                 host='127.0.0.1', port: int = 3306,
                 charset='utf8mb4',
                 ifencryp=True, custom_db_func=None):
        def db_func():
            return pymysql.connect(host=host, port=port,
                               user=user, passwd=decrypt(user, pwd) if ifencryp else pwd,
                               database=dbname, charset=charset)

        class_map = {'varchar': 'varchar(255)',
                     'text': 'text',
                     'bool': 'blob',
                     'int': 'int',
                     'float': 'float'
                     }
        super().__init__(custom_db_func if custom_db_func else db_func,
                         placeholder='%s', class_map=class_map)
        self._normal = '`%s`'

    def run(self, sql):
        # 设置重连
        self._db.ping(reconnect=True)
        return Action.run(self, sql)

    def in_run(self, sql, *datas):
        # 设置重连
        self._db.ping(reconnect=True)
        return Action.in_run(self, sql, *datas)

    def commit(self):
        # 设置重连
        self._db.ping(reconnect=True)
        return Action.commit(self)

    def ifExist(self, table):
        b = self.run(f'show tables like "{table}"')
        return b and len(self._cursor.fetchall()) > 0


class MysqlPool:
    def __init__(self, dbname, user, pwd, pool_size=10,
                 host='127.0.0.1', port: int = 3306,
                 charset='utf8mb4',
                 ifencryp=True, **kwargs):
        # 动态加载模块
        # pip install mysql-connector-python
        try:
            module = importlib.import_module('mysql.connector')
        except:
            raise ImportError('需要安装: pip install mysql-connector-python')
        # 使用动态加载的模块
        self.pool = module.pooling.MySQLConnectionPool(pool_name="mysqlpool", pool_size=pool_size,
                                                       host=host, port=port,
                                                       user=user, password=decrypt(user, pwd) if ifencryp else pwd,
                                                       database=dbname, charset=charset, **kwargs)

    def get(self) -> Mysql:
        return Mysql(None, None, None, custom_db_func=self.pool.get_connection)

    def close(self):
        try:
            self.pool.close()
        except:
            pass
