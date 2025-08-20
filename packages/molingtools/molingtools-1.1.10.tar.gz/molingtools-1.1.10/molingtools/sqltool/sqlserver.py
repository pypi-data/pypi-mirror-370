# from pymssql import connect as sst_connect
from .__sqltool__.action import Action
from .__sqltool__.body import encrypt, decrypt
from .__sqltool__.alter import Alter
try:
    import pyodbc
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install pyodbc')


class Sqlserver(Action, Alter):
    def __init__(self, dbname, user, pwd,
                 host='127.0.0.1', port: int = 1433,
                 charset='UTF8',  # cp936
                 ifencryp=True, custom_db_func = None):
        
        def db_func():
            db = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={dbname};UID={user};PWD={decrypt(user, pwd) if ifencryp else pwd}')  # DRIVER={SQL Server};
            # db = sst_connect(host=self.host, port=self.port,
            #                      user=self.user, password=self.passwd,
            #                      database=self.dbname, charset=self.charset)
            return db
        
        class_map = {'varchar': 'nvarchar(255)',
                     'text': 'ntext',
                     'bool': 'bit',
                     'int': 'int',
                     'float': 'float'
                     }
        super().__init__(custom_db_func if custom_db_func else db_func, placeholder='?', class_map=class_map)
        self._normal = '[%s]'

    def deleteTable(self, table):
        # DROP TABLE table_name
        sql = '''
            If Exists (select * from sysobjects where id = object_id('{table}') and OBJECTPROPERTY(id, 'IsUserTable') = 1)
                DROP TABLE {table} 
        '''.format(table=table)
        return self.run(sql)

    # 判断表是否存在
    def ifExist(self, table):
        return Action.ifExist(self, table, def_schema='dbo')