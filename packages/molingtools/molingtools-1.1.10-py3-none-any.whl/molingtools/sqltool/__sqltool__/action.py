from .body import Body
import traceback


class Action(Body):
    def createTable(self, table, lies: list,
                    colmap: dict = None,
                    key: list|str = None,
                    suffix: str = None):
        colmap = colmap if colmap else {}
        assert lies, "数量有误！"
        if key:
            key = f" ,PRIMARY KEY({','.join(key if isinstance(key,list) else [key])})"
        else:
            key = ''
        # 默认类型为短字符串类型
        sql = '''
            Create Table If Not Exists {table}
            ({lies} {key}) {suffix}
        '''.format(table=table,
                   lies=",\n".join(f'{liestr} {colmap.get(lie, self.class_map["varchar"])}'
                                   for liestr, lie in zip(lies, lies)),
                   key=key,
                   suffix=suffix if suffix else '')
        return self.run(sql)

    # 删除表
    def deleteTable(self, table):
        # DROP TABLE table_name
        sql = f'DROP TABLE IF EXISTS {table}'
        return self.run(sql)

    def _auto_add_lie(self, lies, table, colclass):
        self.select('*', table, where='1=0')
        have_lies = self.getLies()
        not_liest = set(lies) - set(have_lies)
        for lie in not_liest:
            self.run(
                f'ALTER TABLE {table} ADD {lie} {colclass};')
            print(f'{table} 新增字段 {lie}')

    # 插入
    def insert(self, table: str, lies, datas: list[list|tuple],
               in_suffix='',
               auto_lie_class=None):
        assert datas, "插入数据不能为空！"
        # 插入语句
        sql = '''INSERT INTO {table}({liestr})
                VALUES ({cstr}) {in_suffix}
        '''.format(table=table, liestr=','.join(lies),
                   cstr=','.join([self.placeholder] * len(lies)), in_suffix=in_suffix)
        if auto_lie_class:
            try:
                return self.in_run(sql, *datas)
            except:
                self._auto_add_lie(lies, table, auto_lie_class)
                return self.in_run(sql, lies, *datas)
        else:
            return self.in_run(sql, *datas)

    # 插入
    def insert_dts(self, table: str, dts: list[dict],
                   in_suffix='',
                   auto_lie_class=None):
        lies = dts[0].keys()
        return self.insert(table, lies, [list(dt.values()) for dt in dts],
                           in_suffix=in_suffix, auto_lie_class=auto_lie_class)

    def create_insert(self, table, dts: list[dict],
                      colmap: dict = None,
                      key: list or str = None,  # type: ignore
                      suffix: str = None,
                      in_suffix='',
                      auto_lie_class=None):
        lies = dts[0].keys()
        self.createTable(table, lies, colmap, key=key, suffix=suffix)
        self.insert(table, lies, [list(dt.values()) for dt in dts],
                    in_suffix=in_suffix, auto_lie_class=auto_lie_class)

    # 修改
    def update(self, table, dt: dict, where: str):
        assert dt, "数据为空！"
        lies = dt.keys()
        setv = ','.join(
            f"{lie}={self.placeholder}" for lie in lies)
        sql = '''UPDATE {table}
                SET {setv}
                WHERE {where}
        '''.format(table=table, setv=setv, where=where)
        return self.in_run(sql, list(dt.values()))

    # 删除
    def delete(self, table, where: str):
        # 表名
        sql = '''DELETE FROM {table}
            WHERE {where}
        '''.format(table=table, where=where)
        return self.run(sql)

    def select_run(self, sql:str, data_class='dts') -> list:
        self.run(sql)
        # 获取数据
        return self.getResult(data_class=data_class)
        
    def select(self, lies:str|list[str], table, where=None, other='',data_class='dts') -> list:
        if isinstance(lies, str): lies = [lies]
        sql = '''select {lies}
                   from {table}
                   where {where}
                   {other}
           '''.format(lies=','.join(lies),
                      table=table,
                      where=where if where else '1=1',
                      other=other)
        self.run(sql)
        # 获取数据
        if len(lies)==1 and lies[0]!='*':
            return [d[0] for d in self.getResult(data_class='ls')]
        else:
            return self.getResult(data_class=data_class)

    # 判断是否可以查询到
    def ifGet(self, table, where=None, if_error=True):
        try:
            if len(self.select('1', table, where=where, other='limit 1')) > 0:
                return True
            else:
                return False
        except:
            if if_error:
                traceback.print_exc()
            return False

    # 获取数量
    def getNum(self, table, where=None):
        num = self.select('count(1)', table, where=where, data_class='ls')[0]
        return num
