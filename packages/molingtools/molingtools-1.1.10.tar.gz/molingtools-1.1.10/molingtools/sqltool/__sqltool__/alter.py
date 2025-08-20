from .body import Body


class Alter(Body):
    # 删除列
    def deleteColumn(self, table, liename):
        # ALTER TABLE tablename  DROP i;
        sql = '''ALTER TABLE {table}  DROP {lie}
        '''.format(table, lie=liename)
        return self.run(sql)

    # 修改列属性
    def setColumn(self, table, liename, newname, dataclass):
        sql = '''ALTER TABLE {table} 
                CHANGE {liename} {newname} {dataclass}
        '''.format(table=table,
                   liename=liename, newname=newname,
                   dataclass=dataclass)
        return self.run(sql)

    # 新增列
    def addColumn(self, table, liename, dataclass, other=""):
        # ALTER TABLE `tcl科技 (深证:000100)` add `昨日收盘` VARCHAR(255) AFTER `今日收盘`
        sql = '''ALTER TABLE {table}
                ADD {liename} {dataclass} 
                {other}
        '''.format(table=table,
                   liename=liename, dataclass=dataclass,
                   other=other)
        return self.run(sql)

    # 添加索引
    def addIndex(self, table, *index_lies, index_name=None):
        index_lie = ','.join(index_lies)
        if not index_name:
            index_name = "_".join([table] + list(index_lies))
        self.run(f'create index {index_name} on {table}({index_lie});')

    # # 删除索引
    # def delIndex(self, table, index_name):
    #     self.run(f'DROP INDEX {self.getField(index_name)}')
