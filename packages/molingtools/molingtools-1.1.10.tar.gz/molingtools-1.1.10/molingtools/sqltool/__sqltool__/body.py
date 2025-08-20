from base64 import b64encode, b64decode
import re
try:
    from pyDes import PAD_PKCS5, CBC, des
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install pyDes')
    
__Des_Key0 = '%s&@W2*<FRW2'  # '%s+23das&@W2*<FRW2'
__Des_IV = b'\x52\x63\x78\x61\xBC\x48\x6A\x07'


def encrypt(user, passwd):
    k = des((__Des_Key0 % user)[:8], CBC, __Des_IV, padmode=PAD_PKCS5)
    return b64encode(k.encrypt(passwd)).decode('utf-8')


def decrypt(user, passwd_enc):
    k = des((__Des_Key0 % user)[:8], CBC, __Des_IV, padmode=PAD_PKCS5)
    return k.decrypt(b64decode(passwd_enc)).decode('utf-8')


class Body:
    def __init__(self, db_func, placeholder, class_map: dict):
        self._db_func = db_func
        self._db = db_func()
        self._cursor = self._db.cursor()
        self._normal = '"%s"'
        self.placeholder = placeholder
        self.class_map = class_map

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self._db.commit()

    def close(self):
        try:
            self._cursor.close()
            self._db.close()
        except:
            # traceback.print_exc()
            pass

    # 刷新连接
    def refresh(self):
        self.close()
        self._db = self._db_func()
        self._cursor = self._db.cursor()

    # 事务回滚
    def rollback(self):
        self._db.rollback()

    # 使用sql操作
    def run(self, sql):
        # print(sql)
        return self._cursor.execute(sql)

    def getLies(self) -> list:
        return [lc[0] for lc in self._cursor.description] \
            if self._cursor.description else []

    # 获取结果
    def getResult(self, data_class='dts') -> list:
        # 处理返回格式
        if data_class == 'ls':
            results = self._cursor.fetchall()
        else:
            lies = self.getLies()
            results = [dict(zip(lies, row)) for row in self._cursor.fetchall()]
        return results

    # 判断表是否存在
    def ifExist(self, table, def_schema):
        ls = table.split('.')
        if len(ls) == 1:
            schema = def_schema
        else:
            schema, table = ls
        self.run(f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}' and table_schema='{schema}'")
        return len(self._cursor.fetchall()) > 0

    def in_run(self, sql, *datas):
        try:
            self._cursor.executemany(sql, datas)
        except Exception as e:
            self.rollback()
            raise e

    def getField(self, field:str|list[str]) -> str|list[str]:
        """对字段进行有效设置
        """
        if isinstance(field, str):
            fs = field.lower().split('.')
            return '.'.join(self._normal.format(f) for f in fs)
        else:
            return [self._normal.format(f.lower()) for f in field]
