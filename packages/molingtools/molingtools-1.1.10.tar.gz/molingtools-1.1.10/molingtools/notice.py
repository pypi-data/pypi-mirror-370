from smtplib import SMTP_SSL, SMTP
import time
import sys
import traceback
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import asyncio
import warnings


# 生成发信人配置
class Sender:
    def __init__(self, user: str, pwd: str, server_host: str='smtp.qq.com', if_ssl: bool=True, encoding='utf-8'):
        self.sender = user
        self.password = pwd
        self.if_ssl = if_ssl
        self.server_host = server_host
        self.encoding = encoding


# 自定义邮件通知
def emailSend(sender: Sender, title, context, mane_mails, path='', filename=None, ifhtml=False, iftz=False):
    for i in range(3):
        try:
            # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
            msg = MIMEMultipart()
            # 邮件头信息
            msg['From'] = Header(sender.sender)
            msg['To'] = Header(';'.join(mane_mails))
            msg['Subject'] = Header(title)
            if ifhtml:
                try:
                    astext = '\n'.join(
                        [f'<a href="{h}">{c}</a></p>' for c, h in context])
                    html = '<html><body>%s</body></html>' % astext
                    part1 = MIMEText(html, 'html', sender.encoding)
                except:
                    print('[内容格式错误]', '发送超链接需要输入内容为格式:[(内容,链接),(内容,链接)]')
                    return None
            else:
                # 自动转化数据情况
                if type(context) in [list, tuple]:
                    context = '\n'.join(map(str, context))
                # 对编码中的链接进行处理
                context = context.replace(
                    'https://', 'h_ttps://').replace('http://', 'h_ttp://')
                part1 = MIMEText(context, 'plain', sender.encoding)
            msg.attach(part1)

            if filename:
                # 附件传输
                if path != '':
                    path += '/'
                part2 = MIMEApplication(open(path + filename, 'rb').read())
                part2.add_header('Content-Disposition',
                                 'attachment', filename=filename)
                msg.attach(part2)

            if sender.if_ssl:
                server = SMTP_SSL(host=sender.server_host)
                server.connect(sender.server_host, 465)
                # 登录发信邮箱
                server.login(sender.sender, sender.password)
            else:
                # 连接邮箱，传入邮箱地址，和端口号，smtp的端口号是25
                server = SMTP(sender.server_host, port=25)
                # 登录发信邮箱
                server.login(sender.sender, sender.password)  # 发送者的邮箱账号，密码
            # 发送邮件
            note = server.sendmail(sender.sender, mane_mails, msg.as_string())
            # 关闭服务器
            server.quit()
            return note
        except:
            if iftz:
                traceback.print_exc()  # 直接打印出来
                print('发送失败等待重试...3s')
            time.sleep(3)
    print("\033[4;31m", '邮件发送失败！', "\033[0m")


# 报错通知装饰器
def raiseEmailFunc(sender: Sender, title, mane_mails):
    def temp1(func):
        def temp(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                emailSend(sender, title, traceback.format_exc(), mane_mails)
                raise e

        return temp

    return temp1


# 错误通知装饰器方法
def errorFunc(delay:float=3, tries:int=3, is_raise=True, err_details=False):
    def temp(func):
        def temp_ch(*args, **kwargs):
            err = None
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    err = e
                    print(f'错误{i+1}:\n{traceback.format_exc() if err_details else e}{f"\n{delay}s后重试..." if delay else ""}')
                    if delay>0: time.sleep(delay)
            if is_raise:
                raise err
            else:
                warnings.warn(f'错误已到最大限制, 默认返回None\n{err}')
                return None
        return temp_ch
    return temp

# 错误通知装饰器方法
def aerrorFunc(delay:float=3, tries:int=3, is_raise=True, err_details=False):
    def temp(afunc):
        async def temp_ch(*args, **kwargs):
            err = None
            for i in range(tries):
                try:
                    return await afunc(*args, **kwargs)
                except Exception as e:
                    err = e
                    print(f'错误{i+1}:\n{traceback.format_exc() if err_details else e}{f"\n{delay}s后重试..." if delay else ""}')
                    if delay>0: await asyncio.sleep(delay)
            if is_raise:
                raise err
            else:
                warnings.warn(f'错误已到最大限制, 默认返回None\n{err}')
                return None
        return temp_ch
    return temp

# print捕获者
class _Printer:
    def __init__(self, str_writedfunc=None, if_clear=True):
        self._if_clear = if_clear
        self.writedfunc = (
            lambda x: None) if str_writedfunc is None else str_writedfunc
        self.content = ""

    def write(self, txt):
        self.writedfunc(str(txt).strip())
        self.content += txt

    def flush(self):
        if self._if_clear: self.content = ""


# 修改系统print的输出
def setSysPrint(str_writedfunc=None, if_clear=True):
    sys.stdout = _Printer(str_writedfunc, if_clear)


def getSysPrint():
    return sys.stdout.content


def defSysPrint():
    sys.stdout = sys.__stdout__


# 自定义抛出
class ResultEx(Exception):
    def __init__(self, *args):
        self.args = args


# 获取颜色字体文本用于输出使用
def getColorStr(*txts, if_underline=False, color_index=31) -> str:
    return f'\033[{4 if if_underline else 0};{color_index}m{" ".join(map(str, txts))}\033[0m'
