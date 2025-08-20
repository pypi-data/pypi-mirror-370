import calendar
import re
import time
from datetime import datetime, timedelta, date
try:
    from dateutil.relativedelta import relativedelta
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install python-dateutil')


_default_gs = "%Y-%m-%d %H:%M:%S"

def setDefaultGs(gs="%Y-%m-%d %H:%M:%S"):
    global _default_gs
    _default_gs = gs
    
class TimeTool:
    def __init__(self, date_obj: datetime|str|int|float, gs=None):
        if isinstance(date_obj, TimeTool): date_obj = str(date_obj)
        if type(date_obj) is str:
            cdate = re.match(r'[0-9.]+', date_obj)
            # 对时间戳字符串的识别
            if cdate and len(cdate.group(0)) in (10, 13, 14):
                date_obj = (float(cdate.group(0)) / 1000) if len(cdate.group(0)) == 13 else float(cdate.group(0))
            else:
                ts = re.findall(r'\d{2}', date_obj)
                assert len(ts) > 3, f'{date_obj} 格式有误'
                year = ts.pop(0) + ts.pop(0)
                month = ts.pop(0)
                day = ts.pop(0)
                h = ts.pop(0) if len(ts) > 0 else '00'
                m = ts.pop(0) if len(ts) > 0 else '00'
                s = ts.pop(0) if len(ts) > 0 else '00'
                date_obj = datetime.strptime(f'{year}-{month}-{day} {h}:{m}:{s}', "%Y-%m-%d %H:%M:%S")
        if type(date_obj) in (int, float):
            date_obj = datetime.fromtimestamp(date_obj)
            # date = time.strftime(gs, timeArray)
        self.date = date_obj
        self.gs = gs or _default_gs

    def _getMonDay(self, if_first):
        first_day, last_day = calendar.monthrange(self.date.year, self.date.mon)
        temp = TimeTool(date(year=self.date.year, month=self.date.mon, day=first_day if if_first else last_day),
                        self.gs)
        return temp

    def getMonFirstDay(self):
        return self._getMonDay(True)

    def getMonLastDay(self):
        return self._getMonDay(False)

    def next(self, dn, hn=0, mn=0, sn=0, monn=0, if_replace=False):
        temp = self.date + timedelta(days=dn, hours=hn, minutes=mn, seconds=sn)
        temp += relativedelta(months=monn)
        if if_replace:
            self.date = temp
            t = self
        else:
            t = TimeTool(temp, gs=self.gs)
        return t

    def to_txt(self, gs=None) -> str:
        return self.date.strftime(gs if gs else self.gs)

    def to_datetime(self) -> datetime:
        return datetime.strptime(self.to_txt(), self.gs)

    def to_stamp(self) -> int:
        # 转换为时间戳
        return round(time.mktime(self.date.timetuple()))

    def isoweekday(self) -> int:
        return self.date.isoweekday()

    def __str__(self):
        return self.to_txt()

    def _other_class(self, other)->str:
        if not isinstance(other, TimeTool): other = TimeTool(other,gs=self.gs) 
        return other.to_txt()

    # 重载大于等于
    def __ge__(self, other) -> bool:
        return self.to_txt() >= self._other_class(other)

    # 重载大于
    def __gt__(self, other) -> bool:
        return self.to_txt() > self._other_class(other)

    # 重载小于
    def __lt__(self, other) -> bool:
        return self.to_txt() < self._other_class(other)

    # 重载小于等于
    def __le__(self, other) -> bool:
        return self.to_txt() <= self._other_class(other)


def getNowTime(next_day=0, gs=None) -> TimeTool:
    t = TimeTool(datetime.now(), gs=gs)
    t.next(next_day, if_replace=True)
    return t


# 运行时间显示装饰器
def runTimeFunc(func):
    def temp(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print('方法', func.__name__, '运行时间：', round(time.time() - start, 6), '秒')
        return result

    return temp


# 获取时间区间
def getTimeSection(date: TimeTool|str|int|datetime, forward: int, backward: int,re_gs='%Y-%m-%d') -> list[TimeTool]:
    t = TimeTool(date, re_gs)
    results = list()
    for i in range(-forward, backward + 1):
        t = t.next(i)
        results.append(t)
    return results


# 获取时间区间
def getDatels(start_date: TimeTool|str|int|datetime, end_date: TimeTool|str|int|datetime,
              gs='%Y-%m-%d', interval_day=1, interval_hour=0) -> list[TimeTool]:
    ds = list()
    st = TimeTool(start_date, gs)
    et = TimeTool(end_date, gs)
    while st <= et:
        ds.append(st)
        st = st.next(interval_day, hn=interval_hour)
    # 包含最后一天
    return ds


# 输出等待
def printWait(sleeptime):
    for i in range(sleeptime):
        print('\r剩余时间：%s 秒     ' % (sleeptime - i), end='')
        time.sleep(1)


# 计算年龄 周岁
def calculate_age(year, mon, day):
    today = date.today()
    return today.year - int(year) - ((today.month, today.day) < (int(mon), int(day)))


# 休息输出通知函数
def sleePrintTime(sleeptime: int, qz_txt='剩余时间'):
    for i in range(sleeptime):
        print(f'\r{qz_txt}：{sleeptime - i} 秒     ', end='')
        time.sleep(1)


# 获取某月最后一天
def getLastDay(year, mon, gs='%Y-%m-%d') -> TimeTool:
    firstDayWeekDay, monthRange = calendar.monthrange(year, mon)
    der = TimeTool(date(year=year, month=mon, day=monthRange), gs)
    return der


# 秒数转时长
def secondToTime(s0: int, ifre_str=True) -> tuple[int, int, int]|str:
    m, s = divmod(s0, 60)
    h, m = divmod(m, 60)
    if ifre_str:
        return "%02d时%02d分%02d秒" % (h, m, s)
    else:
        return h, m, s
