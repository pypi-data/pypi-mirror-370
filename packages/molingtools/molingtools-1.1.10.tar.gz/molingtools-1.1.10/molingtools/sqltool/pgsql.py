from .__sqltool__.action import Action
from .__sqltool__.body import encrypt, decrypt
from .__sqltool__.alter import Alter
try:
    from psycopg2 import connect as pgt_connect
    from psycopg2 import pool
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install psycopg2-binary')
    

class Pgsql(Action, Alter):
    def __init__(self, dbname, user, pwd,
                 host='127.0.0.1', port: int = 5432,
                 charset='UTF8',
                 ifencryp=True, custom_db_func = None):
        
        def db_func():
            db = pgt_connect(host=host, port=port,
                            user=user, password=decrypt(user, pwd) if ifencryp else pwd,
                            database=dbname)
            db.set_client_encoding(charset)
            return db
        
        class_map = {'varchar': 'varchar(255)',
                     'text': 'text',
                     'bool': 'bool',
                     'int': 'int8',
                     'float': 'float8'
                     }
        super().__init__(custom_db_func if custom_db_func else db_func, placeholder='%s', class_map=class_map)

    # 创建物化视图
    def createMaterializedView(self, view_name, run_sql):
        self.run(f'create materialized view "{view_name}" as {run_sql}')

    # 创建唯一约束
    pass

    # 刷新物化视图
    def refreshMaterializedView(self, view_name, if_lock=True):
        # 使用CONCURRENTLY的物化索引必须具有 unique 约束,否则会报错
        self.run(f'REFRESH MATERIALIZED VIEW {"" if if_lock else "CONCURRENTLY"} "{view_name}"')

    # 删除物化视图
    def deleteMaterializedView(self, view_name):
        self.run(f'drop materialized view if exists {view_name}')

    def createTable(self, table, lies: list,
                    colmap: dict = None,
                    key: list|str = None,
                    suffix: str = None,
                    parentable_valuetxt: tuple = None):
        if parentable_valuetxt:
            parent_table, valuetxt = parentable_valuetxt
            return self.createTable_child(table, parent_table, valuetxt)
        else:
            return Action.createTable(self, table, lies, suffix=suffix, colmap=colmap, key=key)

    def createTable_copy(self, table, copy_table):
        # 子表与父表结构保持一致
        sql = f'CREATE TABLE If Not Exists {table} (LIKE {copy_table} including all)'
        return self.run(sql)

    def createTable_parent(self, table, lies: list, key_lie: str, columnclassdict: dict = None, colmap: dict = None,
                           key=None, map_class='list', **kwargs):  # range
        # 分区父表
        return Action.createTable(self, table, lies, suffix=f"PARTITION BY {map_class} (\"{key_lie}\")",
                                  colmap=colmap, key=key, **kwargs)

    def createTable_child(self, table, parent_table, valuetxt):
        # 分区子表
        sql = f'CREATE TABLE If Not Exists {table} PARTITION of {parent_table} FOR values {valuetxt}'  # in ('123') from ('123') to ('125')
        return self.run(sql)

    # 解除子表分区关系
    def detachPartition(self, parentable, childtable):
        sql = f"ALTER TABLE {parentable} detach PARTITION {childtable}"
        return self.run(sql)

    # 绑定子表分区关系
    def attachPartition(self, parentable, childtable, valuetxt):
        sql = f"ALTER TABLE {parentable} attach PARTITION {childtable} FOR VALUES {valuetxt}"
        return self.run(sql)

    # 判断表是否存在
    def ifExist(self, table):
        return Action.ifExist(self, table, def_schema='public')

class PgsqlPool:
    def __init__(self, dbname, user, pwd, minconn=1, maxconn=10,
                 host='127.0.0.1', port: int = 5432,
                 charset='UTF8',
                 ifencryp=True, **kwargs):
        self._charset = charset
        self.pool = pool.SimpleConnectionPool(minconn, maxconn,
                                            host=host, port=port,
                                            user=user, password=decrypt(user, pwd) if ifencryp else pwd,
                                            database=dbname, **kwargs)
    
    def get(self) -> Pgsql:
        pgt = Pgsql(None, None, None, custom_db_func=self.pool.getconn)
        pgt._db.set_client_encoding(self._charset)
        pgt.close = lambda :self.pool.putconn(pgt._db)
        return pgt

    def close(self):
        try:
            self.pool.close()
        except:
            pass