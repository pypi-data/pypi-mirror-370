# -*- coding: UTF-8 -*-
import json
from .__sqltool__.action import Action
try:
    from pandas import DataFrame
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install pandas==2.2.2')


def _make_func(data):
    if type(data) == str:
        data = data.replace("'", "\\'").strip()
    if type(data) in (tuple, list, dict):
        data = json.dumps(data, ensure_ascii=False)
    return data


# 用于操作的集成数据库类型
class SqlData:
    def __init__(self, data: list[dict] | DataFrame):
        df = data if type(data) == DataFrame else DataFrame(data=data)
        df.rename(columns={lie: lie.strip()
                  for lie in df.columns}, inplace=True)
        self._data = df.where(df.notnull(), None)
        try:
            self._data = self._data.map(_make_func)
        except:
            self._data = self._data.applymap(_make_func)

    def __bool__(self):
        return len(self._data) > 0

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data

    # 获取
    def getLies(self) -> list:
        return list(self._data.columns)

    def getDf(self) -> DataFrame:
        return self._data

    def getDts(self) -> list[dict]:
        return self._data.to_dict(orient='records')

    def getValues(self, lies: list = None) -> list[tuple]:
        if lies:
            return list(zip(*[self._data[lie].tolist() for lie in lies]))
        else:
            return self._data.to_records(index=False).tolist()

    def getAutoColMap(self, class_map: dict, **colmap) -> dict:
        dt = {}
        # 以首行数据为基准进行自动类型分配
        for lie, value in self._data.iloc[0].to_dict().items():
            if colmap.get(lie):
                dt[lie] = colmap[lie]
                continue
            if type(value) == str:
                if len(lie) < 255:
                    dt[lie] = class_map['varchar']
                else:
                    dt[lie] = class_map['text']
            elif type(value) == bool:
                dt[lie] = class_map['bool']
            elif type(value) == int:
                dt[lie] = class_map['int']
            elif type(value) == float:
                dt[lie] = class_map['float']
            else:
                dt[lie] = class_map['varchar']
        return dt

# 表格去重
def table_drop_duplicates(dts: list, *lies) -> DataFrame:
    df = DataFrame(data=dts)
    df.drop_duplicates(subset=lies, keep='first', inplace=True)
    return df


# 数据保存工具
class DataUpdateSave:
    def __init__(self, sqlt: Action, main_keys: list, iftz=True):
        self.sqlt = sqlt
        self.main_keys = main_keys
        self.iftz = iftz

    def getWhere(self, datadts):
        assert datadts
        wheres = []
        for dt in datadts:
            txt = "','".join([str(dt[k]) for k in self.main_keys])
            wheres.append(f"('{txt}')")
        # 删除主表主键数据
        where = f"({','.join(self.main_keys)}) in ({','.join(wheres)})"
        return where

    def getChildDts(self, datadts, chlie, if_pop=True) -> list:
        all_chls = []
        for dt in datadts:
            if if_pop:
                chls = dt.pop(chlie, [])
            else:
                chls = dt.get(chlie, [])
            # 自动转换
            if type(chls) == str:
                chls = json.loads(chls)
            for key in self.main_keys:
                for chdt in chls:
                    chdt[key] = dt[key]
            all_chls.extend(chls)
        return all_chls

    def updateMain(self, datadts: list, table, json_lies: list = (), colmap: dict = {}):
        if not datadts:
            if self.iftz:
                print('没有主数据')
            return False
        where = self.getWhere(datadts)
        if self.sqlt.ifExist(table):
            if self.iftz:
                print('删除主表主键')
            self.sqlt.delete(table, where)
        else:
            if self.iftz:
                print('暂无主表:', table)
        for lie in json_lies:
            colmap[lie] = 'text'
            for dt in datadts:
                dt[lie] = json.dumps(dt.get(lie, ''), ensure_ascii=False)
        # 插入数据
        sqldata = SqlData(datadts)
        self.sqlt.createTable(table, sqldata.getLies(),
                              colmap=colmap, key=self.main_keys)
        self.sqlt.insert(table, sqldata)
        if self.iftz:
            print(table, '主表数据量:', len(sqldata))

    def updateChild(self, datadts, child_table, chlie, if_pop=True, colmap=None):
        chdts = self.getChildDts(datadts, chlie, if_pop=if_pop)
        if chdts:
            where = self.getWhere(datadts)
            if self.sqlt.ifExist(child_table):
                if self.iftz:
                    print('删除子表主键')
                self.sqlt.delete(child_table, where)
            else:
                if self.iftz:
                    print('暂无子表:', child_table)
            # 插入数据
            sqldata = SqlData(datadts)
            self.sqlt.createTable(
                child_table, sqldata.getLies(), colmap=colmap)
            self.sqlt.insert(child_table, *chdts)
            if self.iftz:
                print(child_table, '子表数据量:', len(sqldata))
        else:
            if self.iftz:
                print('没有子表数据!')

    def commit(self):
        self.sqlt.commit()
        if self.iftz:
            print('提交成功!')
