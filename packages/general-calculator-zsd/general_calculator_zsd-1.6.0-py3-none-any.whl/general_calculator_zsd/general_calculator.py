# -*- coding: utf-8 -*-
# @Time : 2022/2/23 10:47
# @Author : Zhang Shaodong
# @Email : colin.zhang@smart.com
# @File : general_calculater_zsd.py
# @Info : 该脚本中包含通用的函数模块
import os
import time
import json
from fake_useragent import UserAgent
import requests
import pandas as pd
import urllib.request
import urllib.parse
import hashlib
import base64
import random
import pymysql
import datetime
import bs4
import re
import requests as req
import sys
from general_calculator_zsd.general_parameter import user_agent_list
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pickle
from textrank4zh import TextRank4Keyword
import cpca


# 文件读取
#########################################################################

# 功能：读取json文件变成字典格式
# 输入：json_file - json文件的路径 - str
# 输出：data_dict - json文件转化成的字典 - dict
def read_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as load_f:
        data_dict = json.load(load_f)
    return data_dict


# 时间处理的模块
#########################################################################

# 功能：获取当前时间，返回yyyymmss格式的时间字符串
# 输入：-
# 输出：time_out - yyyymmss格式的时间字符串 - str
def get_time_now():
    time_out = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    return time_out


# 功能：获取当前时间，返回 %Y-%m-%d %H:%M:%S 格式的时间字符串
# 输入：-
# 输出：datetime_out - %Y-%m-%d %H:%M:%S格式的时间字符串 - str
def get_datetime_now():
    datetime_out = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return datetime_out


# 功能：比较"yyyy-mm-dd"格式时间字符串的大小
# 输入：time1 - 时间1 - str，如'2022-01-01'
#      time2 - 时间2 - str，如'2022-01-01'
#      identifier - 比较符，可选5种：大于（>)、大于等于（>=）、等于（=）、小于等于（<=）、小于（<） - str
# 输出：True/False - 比较结果 - bool
def compare_time_v1(time1: str, time2: str, identifier: str):
    s_time = time.mktime(time.strptime(time1, '%Y-%m-%d'))
    e_time = time.mktime(time.strptime(time2, '%Y-%m-%d'))
    if identifier == '>':
        if int(s_time) - int(e_time) > 0:
            return True
        else:
            return False
    if identifier == '<':
        if int(s_time) - int(e_time) < 0:
            return True
        else:
            return False
    if identifier == '>=':
        if int(s_time) - int(e_time) >= 0:
            return True
        else:
            return False
    if identifier == '<=':
        if int(s_time) - int(e_time) <= 0:
            return True
        else:
            return False
    if identifier == '=':
        if int(s_time) - int(e_time) == 0:
            return True
        else:
            return False


# 功能：比较"yyyy-mm-dd hh:mm:ss"格式时间字符串的大小
# 输入：time1 - 时间1 - str，如'2022-01-01 00:00:00'
#      time2 - 时间2 - str，如'2022-01-01 00:00:00'
#      identifier - 比较符，可选5种：大于（>)、大于等于（>=）、等于（=）、小于等于（<=）、小于（<） - str
# 输出：True/False - 比较结果 - bool
def compare_time_v2(time1: str, time2: str, identifier: str):
    s_time = time.mktime(time.strptime(time1, '%Y-%m-%d %H:%M:%S'))
    e_time = time.mktime(time.strptime(time2, '%Y-%m-%d %H:%M:%S'))
    if identifier == '>':
        if int(s_time) - int(e_time) > 0:
            return True
        else:
            return False
    if identifier == '<':
        if int(s_time) - int(e_time) < 0:
            return True
        else:
            return False
    if identifier == '>=':
        if int(s_time) - int(e_time) >= 0:
            return True
        else:
            return False
    if identifier == '<=':
        if int(s_time) - int(e_time) <= 0:
            return True
        else:
            return False
    if identifier == '=':
        if int(s_time) - int(e_time) == 0:
            return True
        else:
            return False


# 功能：将自epoch以来经过的秒数字符串转化为"yyyy-mm-dd hh:mm:ss"格式
# 输入：stamp_string - 自epoch以来经过的秒数字符串 - str，如'1545925769'
# 输出：date_time - "yyyy-mm-dd hh:mm:ss"格式的时间字符串 - str
def stamp2date(stamp_string: str):
    time_array = time.localtime(int(stamp_string))
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return date_time


# 功能：随机sleep n - m 秒，k表示小数点后k位的时间
# 输入：m - 最短时间 - int
#      n - 最长时间 - int
#      k - 小数点后k位 - int
# 输出：True - 表示完成 - bool
def sleep_some_seconds(m: int, n: int, k: int):
    time.sleep(round(random.uniform(m, n), k))
    return True


# 功能：计算sec（秒数）与当前时间的时间间隔，并且输出指定格式的字符串形式
# 输入：sec - 最短时间 - int/str
#      date_format - 指定的输出格式 - str
# 输出：time_gap - 指定格式的时间间隔 - str
def change2date(sec, date_format: str):
    sec = int(sec)
    time_gap = time.time() - sec
    time_gap = time.strftime(date_format, time.localtime(time_gap))
    return time_gap


# 功能：将n天前/n小时前/n周前转化为%Y-%m-%d %H:%M:%S的字符串格式
# 输入：before - 时间表达形式 - str
# 输出：datetime_str - 格式化的时间字符串 - str
def before2datetime(before: str):
    before_str = re.findall(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", before)
    if before_str != []:
        datetime_str = before_str[0]
    else:
        if '前天' in before:
            sec = 2 * 86400
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '周前' in before:
            a = re.findall('(.*?)天前', before)
            sec = int(a[0]) * 7 * 86400
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '天前' in before:
            a = re.findall('(.*?)天前', before)
            sec = int(a[0]) * 86400
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '小时前' in before:
            a = re.findall('(.*?)小时前', before)
            sec = int(a[0]) * 3600
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '分钟前' in before:
            a = re.findall('(.*?)分钟前', before)
            sec = int(a[0]) * 60
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '秒钟前' in before:
            a = re.findall('(.*?)秒钟前', before)
            sec = int(a[0])
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        elif '刚刚' in before:
            sec = 0
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
        else:
            print('意外的时间表达方式！！！！！！return当前时间')
            sec = 0
            datetime_str = change2date(sec, date_format='%Y-%m-%d %H:%M:%S')
    return datetime_str


# 功能：将yyyymmdd-yyyymmdd格式的字符串拆分，并转化为前后两个时间的起始及结束datetime
# 输入：text - 两个时间的表达形式，yyyymmdd-yyyymmdd - str
# 输出：True/False - 若输入不符合格式要求，则直接返回False - bool
#      start_dt - 起始的dateframe字符串
#      end_dt - 结束的dateframe字符串
def split_yyyymmdd(text: str):
    date_list = text.split('-')
    start_text = date_list[0]
    end_text = date_list[1]
    if len(date_list) != 2 or len(start_text) != 8 or len(end_text) != 8 or int(start_text) > int(end_text):
        return False, '', ''
    else:
        start_dt = start_text[:4] + '-' + start_text[4:6] + '-' + start_text[6:8] + ' 00:00:00'
        end_dt = end_text[:4] + '-' + end_text[4:6] + '-' + end_text[6:8] + ' 23:59:59'
        return True, start_dt, end_dt


# 功能：根据当前时间，反馈现在是周几
# 输入：-
# 输出：weekday - 周几 - str
def get_day_of_week():
    day_of_week = datetime.datetime.now().weekday() + 1
    if day_of_week == 1:
        weekday = '周一'
    elif day_of_week == 2:
        weekday = '周二'
    elif day_of_week == 3:
        weekday = '周三'
    elif day_of_week == 4:
        weekday = '周四'
    elif day_of_week == 5:
        weekday = '周五'
    elif day_of_week == 6:
        weekday = '周六'
    else:
        weekday = '周日'
    return weekday


# 功能：根据输入的date格式，得到n_day前的date格式日期
# 输入：date_start - 起始的日期 - datetime.date
#      n_day - n天前 - int
# 输出：date_before - n_day天之前的date - datetime.date
def get_date_before(date_start, n_day):
    days = datetime.timedelta(days=n_day)
    date_before = date_start - days
    return date_before


# 爬虫代理的模块
#########################################################################

# 功能：根据task和creator，找到task对应平台的最新cookie和useragent，最终输出一个header
# 输入：task - 任务名，包括autohome/weibo/bilibili等 - str
#      creator - 任务创建人，与cookie记录相一致 - str
#      db_config - 数据库config信息 - dict
#      connect - 数据库名 - str
# 输出：header - 生成的header - dict
def get_fake_header(task: str, creator: str, db_config: dict, connect: str):
    cursor, conn = get_cursor_times(db_config[connect], 10)
    sql = f'''
        SELECT cookie
        FROM log_cookies_info a
        where cookie_datetime = (select max(cookie_datetime) from log_cookies_info where task_name = '{task}' and cookie_owner = '{creator}' and LENGTH(cookie) > 100) 
        and task_name = '{task}' and cookie_owner = '{creator}'
        '''
    cursor.execute(sql)
    results = cursor.fetchall()
    cookie = results[0][0]
    header = {}
    # ua_object = UserAgent(path='user_agent_fix.json')
    # ua_object = UserAgent()
    # user_agent = ua_object.random
    header['User-Agent'] = random.choice(user_agent_list)
    header['Cookie'] = cookie
    return header


# 功能：解析代理proxy的信息
# 输入：proxy_info - 代理信息 - dict
# 输出：proxy_out - 代理地址字典 - dict
def get_proxy(proxy_info: dict):
    proxy = 'http://{}:{}@{}:{}'.format(proxy_info['key'], proxy_info['passwd'], proxy_info['host'], proxy_info['port'])
    # return {"http": proxy, "https": proxy}
    proxy_out = {"http": proxy}
    return proxy_out


# 动态隧道转发。返回response
def get_resp_by_proxy(url, timeout, headers, proxies, params=None, verify=True, try_cnt=20):
    try:
        resp = req.get(url, timeout=timeout, headers=headers, proxies=proxies, params=params, verify=verify)
    except:
        print(url)
        try_cnt -= 1
        print(f'ip代理失败，开启第{try_cnt}次调用！')
        sleep_some_seconds(1, 2, 1)
        if try_cnt > 0:
            resp = get_resp_by_proxy(url, timeout, headers, proxies, params=params, verify=verify, try_cnt=try_cnt)
        else:
            return None
    return resp


# 以登录方式获取第一个cookie
def get_first_cookie(task, driver_path, cur_path, db_config, connect, owner_name):
    if task == 'weibo':
        url = "https://weibo.com/"
    elif task == 'autohome':
        url = "https://www.autohome.com.cn/"
    elif task == 'bilibili':
        url = "https://www.bilibili.com/"
    else:
        print('error')
        sys.exit('任务启动错误，退出程序！！！！！')
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('--ignore-ssl-errors')
    option.add_argument('log-level=3')
    # 这行的意思是忽略日志
    option.add_experimental_option('excludeSwitches', ['enable-logging'])

    # 实例化浏览器对象
    driver = webdriver.Chrome(options=option, executable_path=driver_path)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                           {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
    driver.maximize_window()
    driver.implicitly_wait(6)

    driver.get(url)
    time.sleep(2)
    print('浏览器已经打开！！！！！')
    input_word = input('是否已经登录？？？')
    # while 1:
    cookies_str = ''
    pickle.dump(driver.get_cookies(), open(f"{cur_path}\\cookie_{task}.pk1", 'wb'))
    cookies_list = pickle.load(open(f"{cur_path}\\cookie_{task}.pk1", 'rb'))
    for cookie in cookies_list:
        cookies_str += (cookie['name'] + '=' + cookie['value'] + ';')
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        driver.add_cookie(cookie)
    dt_now = get_datetime_now()
    # with open(f'{cur_path}\\cookie_{task}.txt', 'a', encoding='utf-8') as f:
    #     f.write(dt_now + ' ' + cookies_str+'\n')
    #     f.close()
    # try:
    #     print('当前浏览器处于长期打开状态！！！！')
    #     time.sleep(3600)
    #     driver.refresh()  # 刷新方法 refresh
    #     print('test pass: refresh successful')
    # except Exception as e:
    #     print("Exception found", format(e))
    # 写入数据库
    json_data = {'cookie_datetime': dt_now, 'task_name': task, 'cookie_owner': owner_name, 'cookie': cookies_str}
    insert_json_sql(json_data, connect, 'log_cookies_info', db_config)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()
    print(dt_now + ': 首个cookie获取成功！！！')
    return cookies_str, driver


# 刷新指定浏览器
def driver_refresh(driver, second, task, db_config, connect, owner_name, cur_path=''):
    while 1:
        try:
            print('当前浏览器处于长期打开状态！！！！')
            driver.refresh()  # 刷新方法 refresh
            time.sleep(10)
            print('浏览器刷新成功，现在开始保存新的cookie...')
            cookies_str = ''
            pickle.dump(driver.get_cookies(), open(f"{cur_path}\\cookie_{task}.pk1", 'wb'))
            cookies_list = pickle.load(open(f"{cur_path}\\cookie_{task}.pk1", 'rb'))
            for cookie in cookies_list:
                cookies_str += (cookie['name'] + '=' + cookie['value'] + ';')
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                driver.add_cookie(cookie)
            dt_now = get_datetime_now()
            # with open(f'{cur_path}\\cookie_{task}.txt', 'a', encoding='utf-8') as f:
            #     f.write(dt_now + ' ' + cookies_str + '\n')
            #     f.close()
            # print(dt_now+': cookie保存成功！')
            # 写入数据库
            json_data = {'cookie_datetime': dt_now, 'task_name': task, 'cookie_owner': owner_name,
                         'cookie': cookies_str}
            insert_json_sql(json_data, connect, 'log_cookies_info', db_config)
            time.sleep(second)
        except Exception as e:
            print("Exception found", format(e))
    # ActionChains(driver).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()


# 针对字体设计的get_resp
def get_resp_for_font(url, timeout, proxies):
    try:
        ttf = req.get(url, timeout=timeout, stream=True, proxies=proxies)
    except:
        ttf = req.get(url, timeout=timeout, stream=True)
    return ttf


# --------------------------------------------------------------------------
# 4. API调用模块

# 调用讯飞关键词提取API，从content文本中提取关键词
def get_keywords_by_xunfei(content):
    try:
        # 调用讯飞平台关键词提取API服务：
        content = content.strip()
        # 接口地址
        url = "http://ltpapi.xfyun.cn/v1/ke"
        # 开放平台应用ID
        x_appid = "d98c93ce"
        # 开放平台应用接口秘钥
        api_key = "9ed34088080000bf82286f25f6702a36"
        body = urllib.parse.urlencode({'text': content}).encode('utf-8')
        param = {"type": "dependent"}
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
        x_time = str(int(time.time()))
        x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
        x_header = {'X-Appid': x_appid,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read()
        return result.decode('utf-8')
    except:
        return {"code": "1", "data": {"ke": []}}


# --------------------------------------------------------------------------
# 5. 其他模块

# 判断一个字符串里面是否全是中文
# 是，返回True；
# 否，返回False。
def is_chi_word(word):
    flag = True
    for w in word:
        if not '\u4e00' <= w <= '\u9fff':
            flag = False
            break
    return flag


# 解析bs的内容
def bs_resolve(resp):
    try:
        bs = bs4.BeautifulSoup(str(resp.content, "utf-8"), "html.parser")
    except:
        bs = bs4.BeautifulSoup(str(resp.content, "gbk"), "html.parser")
    resp.close()
    return bs


# --------------------------------------------------------------------------
# 6. 数据库相关

# 尝试多次连接数据库
def get_cursor_times(config, times):
    cnt_conn = 0
    while cnt_conn < times:
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            break
        except:
            print('数据库连接失败，正在重新连接，总共10次重新连接的机会...')
            sleep_some_seconds(20, 21, 1)
            cnt_conn += 1

    return cursor, conn


# 将json格式的数据插入insert_db的insert_tbl中
# 输入样例
# insert_db = 'BA_USING'
# insert_tbl = 'autohome_policy_post'
# db_config = {"BA_USING": {'host': '10.26.241.164', 'port': 3306, 'user': 'BA_USING', 'password': 'BA_USING@2022',
#                           'database': "BA_USING"}}
def insert_json_sql(json_data, insert_db, insert_tbl, db_config):
    # 连接数据库
    insert_cursor, insert_conn = get_cursor_times(db_config[insert_db], 10)
    keys = ', '.join(json_data.keys())
    values = ', '.join(['(%s)'] * len(json_data))
    sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
    DUPLICATE KEY UPDATE""".format(table=insert_tbl,
                                   keys=keys,
                                   values=values)
    update = ','.join([" {key} = %s".format(key=key) for key in json_data])
    sql += update
    insert_cursor.execute(sql, list(json_data.values()) * 2)
    insert_conn.commit()


# 读取数据库db中指定table中的指定列，返回df
def read_db2df(db, tbl, cols, db_config, condition):
    # conn = pymysql.connect(host=db_config[db]['host'], port=db_config[db]['port'],
    #                        user=db_config[db]['user'], password=db_config[db]['password'],
    #                        db=db_config[db]['database'])
    # cursor = conn.cursor()
    # 连接导入数据库
    cursor, conn = get_cursor_times(db_config[db], 10)

    if len(cols) > 0:
        col_sql = ','.join(cols)
    else:
        col_sql = '*'
    sql = 'select ' + col_sql + ' from ' + tbl + ' tbl ' + condition
    cursor.execute(sql)
    results = cursor.fetchall()  # 用于返回多条数据
    df = pd.DataFrame(list(results))
    if len(df) == 0:
        cursor.close()
        return df
    else:
        col_name = []
        for head in cursor.description:
            col_name.append(head[0])
        cursor.close()
        df.columns = col_name
    return df


# class get_mysql(config):
#     # 这里可以通过配置文件或者传参的方式来封装，但是我们用配置文件比较好管理
#     def __init__(self, config):
#
#         self.mysql = pymysql.connect(host=config['host'], user=config['user'], password=config['password'], port=config['port'])
#         self.cursor = self.mysql.cursor()
#
#     # 返回单条数据
#     def fetch_one(self, sql):
#         self.cursor.execute (sql)
#         return self.cursor.fetchone()
#
#     # 返回多条数据
#     def fetch_chall(self, sql):
#         self.cursor.execute(sql)
#         return self.cursor.fetchall()
#
#     def fetch_code(self):
#         self.cursor.close()

def record_message2txt(path, message):
    with open(path, "a") as f:
        f.write(get_time_now() + ' --- MSG: ' + message + '\n')
    print(message)


prov2goodprov_dict = {
    None: None,
    '地区未知': None,
    '其他': None,
    '其它': None,
    '': None,
    '安徽': '安徽省',
    '安徽省': '安徽省',
    '澳门': '澳门特别行政区',
    '澳门省': '澳门特别行政区',
    '澳门特别行政区': '澳门特别行政区',
    '中国澳门': '澳门特别行政区',
    '北京': '北京',
    '北京市': '北京',
    '北京城区': '北京',
    '福建': '福建省',
    '福建省': '福建省',
    '甘肃': '甘肃省',
    '甘肃省': '甘肃省',
    '广东': '广东省',
    '广东省': '广东省',
    '广西': '广西壮族自治区',
    '广西壮族自治区': '广西壮族自治区',
    '贵州': '贵州省',
    '贵州省': '贵州省',
    '海南': '海南省',
    '海南省': '海南省',
    '河北': '河北省',
    '河北省': '河北省',
    '河南': '河南省',
    '河南省': '河南省',
    '黑龙江': '黑龙江省',
    '黑龙江省': '黑龙江省',
    '湖北': '湖北省',
    '湖北省': '湖北省',
    '湖南': '湖南省',
    '湖南省': '湖南省',
    '吉林': '吉林省',
    '吉林省': '吉林省',
    '江苏': '江苏省',
    '江苏省': '江苏省',
    '江西': '江西省',
    '江西省': '江西省',
    '辽宁': '辽宁省',
    '辽宁省': '辽宁省',
    '内蒙古': '内蒙古自治区',
    '内蒙古自治区': '内蒙古自治区',
    '宁夏': '宁夏回族自治区',
    '宁夏回族自治区': '宁夏回族自治区',
    '青海': '青海省',
    '青海省': '青海省',
    '山东': '山东省',
    '山东省': '山东省',
    '山西': '山西省',
    '山西省': '山西省',
    '陕西': '陕西省',
    '陕西省': '陕西省',
    '上海': '上海',
    '上海市': '上海',
    '上海城区': '上海',
    '四川': '四川省',
    '四川省': '四川省',
    '台湾': '台湾省',
    '台湾省': '台湾省',
    '中国台湾': '台湾省',
    '天津': '天津',
    '天津市': '天津',
    '天津城区': '天津',
    '西藏': '西藏自治区',
    '西藏自治区': '西藏自治区',
    '香港': '香港特别行政区',
    '香港省': '香港特别行政区',
    '香港特别行政区': '香港特别行政区',
    '中国香港': '香港特别行政区',
    '新疆': '新疆维吾尔自治区',
    '新疆维吾尔自治区': '新疆维吾尔自治区',
    '新疆维吾尔族自治区': '新疆维吾尔自治区',
    '云南': '云南省',
    '云南省': '云南省',
    '浙江': '浙江省',
    '浙江省': '浙江省',
    '重庆': '重庆',
    '重庆市': '重庆',
    '重庆城区': '重庆'
}

city2goodcity_dict = {
    None: None,
    '其它': None,
    '其他': None,
    '': None,
    '阿坝': '阿坝藏族羌族自治州',
    '阿坝藏族羌族自治州': '阿坝藏族羌族自治州',
    '阿坝州': '阿坝藏族羌族自治州',
    '阿克苏': '阿克苏地区',
    '阿拉尔': '阿拉尔市',
    '阿拉善盟': '阿拉善盟',
    '阿勒泰': '阿勒泰地区',
    '阿里': '阿里地区',
    '安康': '安康市',
    '安庆': '安庆市',
    '安顺': '安顺市',
    '安阳': '安阳市',
    '鞍山': '鞍山市',
    '澳门': '澳门特别行政区',
    '澳门特别行政区': '澳门特别行政区',
    '大堂区': '澳门特别行政区',
    '花地玛堂区': '澳门特别行政区',
    '圣安多尼堂区': '澳门特别行政区',
    '花王堂区': '澳门特别行政区',
    '望德堂区': '澳门特别行政区',
    '风顺堂区': '澳门特别行政区',
    '嘉模堂区': '澳门特别行政区',
    '圣方济各堂区': '澳门特别行政区',
    '路氹城': '澳门特别行政区',
    '路凼填海区': '澳门特别行政区',
    '巴彦淖尔': '巴彦淖尔市',
    '巴音郭楞': '巴音郭楞蒙古自治州',
    '巴音郭楞蒙古自治州': '巴音郭楞蒙古自治州',
    '巴音郭楞州': '巴音郭楞蒙古自治州',
    '巴中': '巴中市',
    '白城': '白城市',
    '白沙': '白沙黎族自治县',
    '白沙县': '白沙黎族自治县',
    '白沙黎族自治县': '白沙黎族自治县',
    '白山': '白山市',
    '白银': '白银市',
    '百色': '百色市',
    '蚌埠': '蚌埠市',
    '包头': '包头市',
    '宝鸡': '宝鸡市',
    '保定': '保定市',
    '雄安新区': '保定市',
    '保山': '保山市',
    '保亭': '保亭黎族苗族自治县',
    '保亭县': '保亭黎族苗族自治县',
    '保亭黎族苗族自治县': '保亭黎族苗族自治县',
    '北海': '北海市',
    '北京': '北京市',
    '北京城区': '北京市',
    '北京市': '北京市',
    '北屯': '北屯市',
    '本溪': '本溪市',
    '毕节': '毕节市',
    '滨州': '滨州市',
    '亳州': '亳州市',
    '博尔塔拉': '博尔塔拉蒙古自治州',
    '博尔塔拉蒙古自治州': '博尔塔拉蒙古自治州',
    '博乐': '博尔塔拉蒙古自治州',
    '博尔塔拉蒙古州': '博尔塔拉蒙古自治州',
    '沧州': '沧州市',
    '昌都': '昌都市',
    '昌吉': '昌吉回族自治州',
    '昌吉回族自治州': '昌吉回族自治州',
    '昌吉州': '昌吉回族自治州',
    '昌江': '昌江黎族自治县',
    '昌江县': '昌江黎族自治县',
    '昌江黎族自治县': '昌江黎族自治县',
    '常德': '常德市',
    '常州': '常州市',
    '朝阳': '朝阳市',
    '潮州': '潮州市',
    '郴州': '郴州市',
    '成都': '成都市',
    '承德': '承德市',
    '澄迈县': '澄迈县',
    '池州': '池州市',
    '赤峰': '赤峰市',
    '崇左': '崇左市',
    '滁州': '滁州市',
    '楚雄': '楚雄彝族自治州',
    '楚雄州': '楚雄彝族自治州',
    '楚雄彝族自治州': '楚雄彝族自治州',
    '达州': '达州市',
    '大理': '大理白族自治州',
    '大理州': '大理白族自治州',
    '大理白族自治州': '大理白族自治州',
    '大连': '大连市',
    '大庆': '大庆市',
    '大同': '大同市',
    '大兴安岭': '大兴安岭地区',
    '大兴安岭地区': '大兴安岭地区',
    '丹东': '丹东市',
    '儋州': '儋州市',
    '德宏': '德宏傣族景颇族自治州',
    '德宏州': '德宏傣族景颇族自治州',
    '德宏傣族景颇族自治州': '德宏傣族景颇族自治州',
    '德阳': '德阳市',
    '绵竹': '德阳市',
    '德州': '德州市',
    '迪庆': '迪庆藏族自治州',
    '迪庆州': '迪庆藏族自治州',
    '迪庆藏族自治州': '迪庆藏族自治州',
    '定安县': '定安县',
    '定西': '定西市',
    '东方': '东方市',
    '东莞': '东莞市',
    '东营': '东营市',
    '鄂尔多斯': '鄂尔多斯市',
    '鄂州': '鄂州市',
    '恩施': '恩施土家族苗族自治州',
    '恩施土家族苗族自治州': '恩施土家族苗族自治州',
    '恩施州': '恩施土家族苗族自治州',
    '防城港': '防城港市',
    '佛山': '佛山市',
    '福州': '福州市',
    '抚顺': '抚顺市',
    '抚州': '抚州市',
    '阜新': '阜新市',
    '阜阳': '阜阳市',
    '甘南': '甘南藏族自治州',
    '甘南藏族自治州': '甘南藏族自治州',
    '甘南州': '甘南藏族自治州',
    '甘孜': '甘孜藏族自治州',
    '甘孜藏族自治州': '甘孜藏族自治州',
    '甘孜州': '甘孜藏族自治州',
    '赣州': '赣州市',
    '固原': '固原市',
    '广安': '广安市',
    '广元': '广元市',
    '广州': '广州市',
    '贵港': '贵港市',
    '贵阳': '贵阳市',
    '桂林': '桂林市',
    '果洛': '果洛藏族自治州',
    '果洛藏族自治州': '果洛藏族自治州',
    '果洛州': '果洛藏族自治州',
    '哈尔滨': '哈尔滨市',
    '哈密': '哈密市',
    '哈密地区': '哈密市',
    '海北': '海北藏族自治州',
    '海北藏族自治州': '海北藏族自治州',
    '海北州': '海北藏族自治州',
    '海东': '海东市',
    '海口': '海口市',
    '海南': '海南藏族自治州',
    '海南藏族自治州': '海南藏族自治州',
    '海南州': '海南藏族自治州',
    '海外': '海外',
    '海西': '海西蒙古族藏族自治州',
    '海西蒙古族藏族自治州': '海西蒙古族藏族自治州',
    '海西州': '海西蒙古族藏族自治州',
    '邯郸': '邯郸市',
    '汉中': '汉中市',
    '杭州': '杭州市',
    '合肥': '合肥市',
    '巢湖': '合肥市',
    '和田': '和田地区',
    '河池': '河池市',
    '河源': '河源市',
    '菏泽': '菏泽市',
    '贺州': '贺州市',
    '鹤壁': '鹤壁市',
    '鹤岗': '鹤岗市',
    '黑河': '黑河市',
    '衡水': '衡水市',
    '衡阳': '衡阳市',
    '红河': '红河哈尼族彝族自治州',
    '红河州': '红河哈尼族彝族自治州',
    '红河哈尼族彝族自治州': '红河哈尼族彝族自治州',
    '呼和浩特': '呼和浩特市',
    '呼伦贝尔': '呼伦贝尔市',
    '胡杨河': '胡杨河市',
    '葫芦岛': '葫芦岛市',
    '湖州': '湖州市',
    '怀化': '怀化市',
    '淮安': '淮安市',
    '淮北': '淮北市',
    '淮南': '淮南市',
    '黄冈': '黄冈市',
    '黄南': '黄南藏族自治州',
    '黄南藏族自治州': '黄南藏族自治州',
    '黄南州': '黄南藏族自治州',
    '黄山': '黄山市',
    '黄石': '黄石市',
    '惠州': '惠州市',
    '鸡西': '鸡西市',
    '吉安': '吉安市',
    '吉林': '吉林市',
    '济南': '济南市',
    '莱芜': '济南市',
    '济宁': '济宁市',
    '济源': '济源市',
    '佳木斯': '佳木斯市',
    '嘉兴': '嘉兴市',
    '嘉峪关': '嘉峪关市',
    '江门': '江门市',
    '焦作': '焦作市',
    '揭阳': '揭阳市',
    '金昌': '金昌市',
    '金华': '金华市',
    '东阳': '金华市',
    '义乌': '金华市',
    '锦州': '锦州市',
    '晋城': '晋城市',
    '晋中': '晋中市',
    '荆门': '荆门市',
    '荆州': '荆州市',
    '景德镇': '景德镇市',
    '九江': '九江市',
    '酒泉': '酒泉市',
    '喀什': '喀什地区',
    '开封': '开封市',
    '可克达拉': '可克达拉市',
    '克拉玛依': '克拉玛依市',
    '克孜勒苏': '克孜勒苏柯尔克孜自治州',
    '克孜勒苏柯尔克孜自治州': '克孜勒苏柯尔克孜自治州',
    '克州': '克孜勒苏柯尔克孜自治州',
    '昆明': '昆明市',
    '昆玉': '昆玉市',
    '拉萨': '拉萨市',
    '来宾': '来宾市',
    '兰州': '兰州市',
    '廊坊': '廊坊市',
    '乐东': '乐东黎族自治县',
    '乐东县': '乐东黎族自治县',
    '乐东黎族自治县': '乐东黎族自治县',
    '乐山': '乐山市',
    '丽江': '丽江市',
    '丽水': '丽水市',
    '连云港': '连云港市',
    '凉山': '凉山彝族自治州',
    '凉山彝族自治州': '凉山彝族自治州',
    '凉山州': '凉山彝族自治州',
    '辽阳': '辽阳市',
    '辽源': '辽源市',
    '聊城': '聊城市',
    '林芝': '林芝市',
    '临沧': '临沧市',
    '临汾': '临汾市',
    '临高县': '临高县',
    '临夏': '临夏回族自治州',
    '临夏回族自治州': '临夏回族自治州',
    '临夏州': '临夏回族自治州',
    '临沂': '临沂市',
    '陵水': '陵水黎族自治县',
    '陵水县': '陵水黎族自治县',
    '陵水黎族自治县': '陵水黎族自治县',
    '柳州': '柳州市',
    '六安': '六安市',
    '六盘水': '六盘水市',
    '龙岩': '龙岩市',
    '陇南': '陇南市',
    '娄底': '娄底市',
    '泸州': '泸州市',
    '洛阳': '洛阳市',
    '漯河': '漯河市',
    '吕梁': '吕梁市',
    '马鞍山': '马鞍山市',
    '茂名': '茂名市',
    '眉山': '眉山市',
    '梅州': '梅州市',
    '绵阳': '绵阳市',
    '牡丹江': '牡丹江市',
    '那曲': '那曲市',
    '南昌': '南昌市',
    '南充': '南充市',
    '南京': '南京市',
    '南宁': '南宁市',
    '南平': '南平市',
    '南通': '南通市',
    '南阳': '南阳市',
    '内江': '内江市',
    '宁波': '宁波市',
    '宁德': '宁德市',
    '怒江': '怒江傈僳族自治州',
    '怒江傈僳族自治州': '怒江傈僳族自治州',
    '怒江州': '怒江傈僳族自治州',
    '攀枝花': '攀枝花市',
    '盘锦': '盘锦市',
    '平顶山': '平顶山市',
    '汝州': '平顶山市',
    '平凉': '平凉市',
    '萍乡': '萍乡市',
    '莆田': '莆田市',
    '濮阳': '濮阳市',
    '普洱': '普洱市',
    '七台河': '七台河市',
    '齐齐哈尔': '齐齐哈尔市',
    '潜江': '潜江市',
    '黔东南': '黔东南苗族侗族自治州',
    '黔东南州': '黔东南苗族侗族自治州',
    '黔东南苗族侗族自治州': '黔东南苗族侗族自治州',
    '黔南': '黔南布依族苗族自治州',
    '黔南布依族苗族自治州': '黔南布依族苗族自治州',
    '黔南州': '黔南布依族苗族自治州',
    '黔西南': '黔西南布依族苗族自治州',
    '黔西南州': '黔西南布依族苗族自治州',
    '黔西南布依族苗族自治州': '黔西南布依族苗族自治州',
    '钦州': '钦州市',
    '秦皇岛': '秦皇岛市',
    '青岛': '青岛市',
    '清远': '清远市',
    '庆阳': '庆阳市',
    '琼海': '琼海市',
    '琼中': '琼中黎族苗族自治县',
    '琼中县': '琼中黎族苗族自治县',
    '琼中黎族苗族自治县': '琼中黎族苗族自治县',
    '曲靖': '曲靖市',
    '衢州': '衢州市',
    '泉州': '泉州市',
    '日喀则': '日喀则市',
    '日照': '日照市',
    '三门峡': '三门峡市',
    '三明': '三明市',
    '三沙': '三沙市',
    '三亚': '三亚市',
    '厦门': '厦门市',
    '山南': '山南市',
    '汕头': '汕头市',
    '汕尾': '汕尾市',
    '商洛': '商洛市',
    '商丘': '商丘市',
    '上海': '上海市',
    '上海城区': '上海市',
    '上海市': '上海市',
    '闵行区': '上海市',
    '上饶': '上饶市',
    '韶关': '韶关市',
    '邵阳': '邵阳市',
    '绍兴': '绍兴市',
    '深圳': '深圳市',
    '神农架林区': '神农架林区',
    '神农架': '神农架林区',
    '沈阳': '沈阳市',
    '十堰': '十堰市',
    '石河子': '石河子市',
    '石家庄': '石家庄市',
    '石嘴山': '石嘴山市',
    '双河': '双河市',
    '双鸭山': '双鸭山市',
    '朔州': '朔州市',
    '四平': '四平市',
    '松原': '松原市',
    '苏州': '苏州市',
    '张家港': '苏州市',
    '宿迁': '宿迁市',
    '宿州': '宿州市',
    '绥化': '绥化市',
    '随州': '随州市',
    '遂宁': '遂宁市',
    '塔城': '塔城地区',
    '台湾省': '台湾省',
    '台北': '台湾省',
    '台湾': '台湾省',
    '台州': '台州市',
    '太原': '太原市',
    '泰安': '泰安市',
    '泰州': '泰州市',
    '唐山': '唐山市',
    '天津': '天津市',
    '天津城区': '天津市',
    '天津市': '天津市',
    '天门': '天门市',
    '天水': '天水市',
    '铁岭': '铁岭市',
    '铁门关': '铁门关市',
    '通化': '通化市',
    '通辽': '通辽市',
    '铜川': '铜川市',
    '铜陵': '铜陵市',
    '铜仁': '铜仁市',
    '图木舒克': '图木舒克市',
    '吐鲁番': '吐鲁番市',
    '屯昌县': '屯昌县',
    '万宁': '万宁市',
    '威海': '威海市',
    '潍坊': '潍坊市',
    '渭南': '渭南市',
    '温州': '温州市',
    '乐清': '温州市',
    '文昌': '文昌市',
    '文山': '文山壮族苗族自治州',
    '文山州': '文山壮族苗族自治州',
    '文山壮族苗族自治州': '文山壮族苗族自治州',
    '乌海': '乌海市',
    '乌兰察布': '乌兰察布市',
    '乌鲁木齐': '乌鲁木齐市',
    '无锡': '无锡市',
    '宜兴': '无锡市',
    '芜湖': '芜湖市',
    '吴忠': '吴忠市',
    '梧州': '梧州市',
    '五家渠': '五家渠市',
    '五指山': '五指山市',
    '武汉': '武汉市',
    '武威': '武威市',
    '西安': '西安市',
    '西宁': '西宁市',
    '西双版纳': '西双版纳傣族自治州',
    '西双版纳州': '西双版纳傣族自治州',
    '西双版纳傣族自治州': '西双版纳傣族自治州',
    '锡林郭勒盟': '锡林郭勒盟',
    '锡林浩特': '锡林郭勒盟',
    '仙桃': '仙桃市',
    '咸宁': '咸宁市',
    '咸阳': '咸阳市',
    '香港': '香港特别行政区',
    '香港特别行政区': '香港特别行政区',
    '中西区': '香港特别行政区',
    '湾仔区': '香港特别行政区',
    '九龙城区': '香港特别行政区',
    '北区': '香港特别行政区',
    '元朗区': '香港特别行政区',
    '东区': '香港特别行政区',
    '南区': '香港特别行政区',
    '油尖旺区': '香港特别行政区',
    '观塘区': '香港特别行政区',
    '黄大仙区': '香港特别行政区',
    '深水埗区': '香港特别行政区',
    '大埔区': '香港特别行政区',
    '沙田区': '香港特别行政区',
    '西贡区': '香港特别行政区',
    '屯门区': '香港特别行政区',
    '荃湾区': '香港特别行政区',
    '葵青区': '香港特别行政区',
    '离岛区': '香港特别行政区',
    '港岛': '香港特别行政区',
    '九龙': '香港特别行政区',
    '新界': '香港特别行政区',
    '新界东': '香港特别行政区',
    '新界西': '香港特别行政区',
    '湘潭': '湘潭市',
    '湘西': '湘西土家族苗族自治州',
    '湘西土家族苗族自治州': '湘西土家族苗族自治州',
    '湘西州': '湘西土家族苗族自治州',
    '吉首': '湘西土家族苗族自治州',
    '襄阳': '襄阳市',
    '孝感': '孝感市',
    '忻州': '忻州市',
    '新乡': '新乡市',
    '新星': '新星市',
    '新余': '新余市',
    '信阳': '信阳市',
    '邢台': '邢台市',
    '兴安盟': '兴安盟',
    '徐州': '徐州市',
    '许昌': '许昌市',
    '宣城': '宣城市',
    '雅安': '雅安市',
    '烟台': '烟台市',
    '延安': '延安市',
    '延边': '延边朝鲜族自治州',
    '延边朝鲜族自治州': '延边朝鲜族自治州',
    '延边州': '延边朝鲜族自治州',
    '盐城': '盐城市',
    '扬州': '扬州市',
    '阳江': '阳江市',
    '阳泉': '阳泉市',
    '伊春': '伊春市',
    '伊犁': '伊犁哈萨克自治州',
    '伊犁哈萨克自治州': '伊犁哈萨克自治州',
    '伊犁州': '伊犁哈萨克自治州',
    '宜宾': '宜宾市',
    '宜昌': '宜昌市',
    '宜春': '宜春市',
    '益阳': '益阳市',
    '银川': '银川市',
    '鹰潭': '鹰潭市',
    '营口': '营口市',
    '永州': '永州市',
    '榆林': '榆林市',
    '玉林': '玉林市',
    '玉树': '玉树藏族自治州',
    '玉树藏族自治州': '玉树藏族自治州',
    '玉树州': '玉树藏族自治州',
    '玉溪': '玉溪市',
    '岳阳': '岳阳市',
    '云浮': '云浮市',
    '运城': '运城市',
    '枣庄': '枣庄市',
    '湛江': '湛江市',
    '张家界': '张家界市',
    '张家口': '张家口市',
    '张掖': '张掖市',
    '漳州': '漳州市',
    '长春': '长春市',
    '长沙': '长沙市',
    '长治': '长治市',
    '昭通': '昭通市',
    '肇庆': '肇庆市',
    '镇江': '镇江市',
    '郑州': '郑州市',
    '中山': '中山市',
    '中卫': '中卫市',
    '重庆': '重庆市',
    '渝北区': '重庆市',
    '重庆城区': '重庆市',
    '重庆郊县': '重庆市',
    '重庆市': '重庆市',
    '舟山': '舟山市',
    '周口': '周口市',
    '珠海': '珠海市',
    '株洲': '株洲市',
    '驻马店': '驻马店市',
    '资阳': '资阳市',
    '淄博': '淄博市',
    '自贡': '自贡市',
    '遵义': '遵义市',
    '高雄': '高雄市',
    '基隆': '基隆市',
    '台中': '台中市',
    '台南': '台南市',
    '新竹': '新竹市',
    '嘉义': '嘉义市',
    '新北': '新北市',
    '桃园': '桃园市',
    '宜兰': '宜兰市',
    '苗栗': '苗栗市',
    '彰化': '彰化市',
    '南投': '南投市',
    '云林': '云林市',
    '屏东': '屏东市',
    '台东': '台东市',
    '花莲': '花莲市',
    '澎湖': '澎湖市',
    '金门': '金门市',
    '连江': '连江市'
}

# 城市向省份映射表，注意，城市名需要使用标准城市名
city_province_map = {
    None: None,
    '': None,
    '北京市': '北京',
    '上海市': '上海',
    '天津市': '天津',
    '重庆市': '重庆',
    '哈尔滨市': '黑龙江省',
    '齐齐哈尔市': '黑龙江省',
    '牡丹江市': '黑龙江省',
    '大庆市': '黑龙江省',
    '佳木斯市': '黑龙江省',
    '伊春市': '黑龙江省',
    '双鸭山市': '黑龙江省',
    '七台河市': '黑龙江省',
    '鹤岗市': '黑龙江省',
    '黑河市': '黑龙江省',
    '绥化市': '黑龙江省',
    '大兴安岭地区': '黑龙江省',
    '长春市': '吉林省',
    '吉林市': '吉林省',
    '四平市': '吉林省',
    '辽源市': '吉林省',
    '通化市': '吉林省',
    '白山市': '吉林省',
    '松原市': '吉林省',
    '白城市': '吉林省',
    '延边朝鲜族自治州': '吉林省',
    '沈阳市': '辽宁省',
    '大连市': '辽宁省',
    '鞍山市': '辽宁省',
    '抚顺市': '辽宁省',
    '本溪市': '辽宁省',
    '丹东市': '辽宁省',
    '锦州市': '辽宁省',
    '营口市': '辽宁省',
    '阜新市': '辽宁省',
    '辽阳市': '辽宁省',
    '盘锦市': '辽宁省',
    '铁岭市': '辽宁省',
    '朝阳市': '辽宁省',
    '葫芦岛市': '辽宁省',
    '呼和浩特市': '内蒙古自治区',
    '包头市': '内蒙古自治区',
    '鄂尔多斯市': '内蒙古自治区',
    '乌兰察布市': '内蒙古自治区',
    '巴彦淖尔市': '内蒙古自治区',
    '乌海市': '内蒙古自治区',
    '赤峰市': '内蒙古自治区',
    '通辽市': '通辽市',
    '呼伦贝尔市': '内蒙古自治区',
    '兴安盟': '内蒙古自治区',
    '锡林郭勒盟': '内蒙古自治区',
    '阿拉善盟': '内蒙古自治区',
    '石家庄市': '河北省',
    '唐山市': '河北省',
    '保定市': '河北省',
    '承德市': '河北省',
    '沧州市': '河北省',
    '邯郸市': '河北省',
    '衡水市': '河北省',
    '廊坊市': '河北省',
    '秦皇岛市': '河北省',
    '邢台市': '河北省',
    '张家口市': '河北省',
    '太原市': '山西省',
    '大同市': '山西省',
    '阳泉市': '山西省',
    '长治市': '山西省',
    '晋城市': '山西省',
    '朔州市': '山西省',
    '晋中市': '山西省',
    '运城市': '山西省',
    '忻州市': '山西省',
    '临汾市': '山西省',
    '吕梁市': '山西省',
    '济南市': '山东省',
    '青岛市': '山东省',
    '淄博市': '山东省',
    '枣庄市': '山东省',
    '东营市': '山东省',
    '烟台市': '山东省',
    '潍坊市': '山东省',
    '济宁市': '山东省',
    '泰安市': '山东省',
    '威海市': '山东省',
    '日照市': '山东省',
    '临沂市': '山东省',
    '德州市': '山东省',
    '聊城市': '山东省',
    '滨州市': '山东省',
    '菏泽市': '山东省',
    '郑州市': '河南省',
    '洛阳市': '河南省',
    '开封市': '河南省',
    '平顶山市': '河南省',
    '安阳市': '河南省',
    '鹤壁市': '河南省',
    '新乡市': '河南省',
    '焦作市': '河南省',
    '濮阳市': '河南省',
    '许昌市': '河南省',
    '漯河市': '河南省',
    '三门峡市': '河南省',
    '南阳市': '河南省',
    '商丘市': '河南省',
    '信阳市': '河南省',
    '周口市': '河南省',
    '驻马店市': '河南省',
    '济源市': '河南省',
    '南京市': '江苏省',
    '苏州市': '江苏省',
    '无锡市': '江苏省',
    '常州市': '江苏省',
    '徐州市': '江苏省',
    '南通市': '江苏省',
    '连云港市': '江苏省',
    '淮安市': '江苏省',
    '盐城市': '江苏省',
    '扬州市': '江苏省',
    '镇江市': '江苏省',
    '泰州市': '江苏省',
    '宿迁市': '江苏省',
    '杭州市': '浙江省',
    '宁波市': '浙江省',
    '温州市': '浙江省',
    '嘉兴市': '浙江省',
    '湖州市': '浙江省',
    '绍兴市': '浙江省',
    '金华市': '浙江省',
    '衢州市': '浙江省',
    '舟山市': '浙江省',
    '台州市': '浙江省',
    '丽水市': '浙江省',
    '合肥市': '安徽省',
    '芜湖市': '安徽省',
    '蚌埠市': '安徽省',
    '淮南市': '安徽省',
    '马鞍山市': '安徽省',
    '淮北市': '安徽省',
    '铜陵市': '安徽省',
    '安庆市': '安徽省',
    '黄山市': '安徽省',
    '滁州市': '安徽省',
    '阜阳市': '安徽省',
    '宿州市': '安徽省',
    '六安市': '安徽省',
    '亳州市': '安徽省',
    '池州市': '安徽省',
    '宣城市': '安徽省',
    '福州市': '福建省',
    '厦门市': '福建省',
    '泉州市': '福建省',
    '漳州市': '福建省',
    '莆田市': '福建省',
    '三明市': '福建省',
    '南平市': '福建省',
    '龙岩市': '福建省',
    '宁德市': '福建省',
    '南昌市': '江西省',
    '九江市': '江西省',
    '景德镇市': '江西省',
    '萍乡市': '江西省',
    '新余市': '江西省',
    '鹰潭市': '江西省',
    '赣州市': '江西省',
    '吉安市': '江西省',
    '宜春市': '江西省',
    '抚州市': '江西省',
    '上饶市': '江西省',
    '武汉市': '湖北省',
    '宜昌市': '湖北省',
    '襄阳市': '湖北省',
    '黄石市': '湖北省',
    '十堰市': '湖北省',
    '荆州市': '湖北省',
    '荆门市': '湖北省',
    '鄂州市': '湖北省',
    '孝感市': '湖北省',
    '黄冈市': '湖北省',
    '咸宁市': '湖北省',
    '随州市': '湖北省',
    '恩施土家族苗族自治州': '湖北省',
    '仙桃市': '湖北省',
    '潜江市': '湖北省',
    '天门市': '湖北省',
    '神农架林区': '湖北省',
    '长沙市': '湖南省',
    '株洲市': '湖南省',
    '湘潭市': '湖南省',
    '衡阳市': '湖南省',
    '邵阳市': '湖南省',
    '岳阳市': '湖南省',
    '常德市': '湖南省',
    '张家界市': '湖南省',
    '益阳市': '湖南省',
    '郴州市': '湖南省',
    '永州市': '湖南省',
    '怀化市': '湖南省',
    '娄底市': '湖南省',
    '湘西土家族苗族自治州': '湖南省',
    '广州市': '广东省',
    '深圳市': '广东省',
    '珠海市': '广东省',
    '汕头市': '广东省',
    '佛山市': '广东省',
    '韶关市': '广东省',
    '湛江市': '广东省',
    '肇庆市': '广东省',
    '江门市': '广东省',
    '茂名市': '广东省',
    '惠州市': '广东省',
    '梅州市': '广东省',
    '汕尾市': '广东省',
    '河源市': '广东省',
    '阳江市': '广东省',
    '清远市': '广东省',
    '东莞市': '广东省',
    '中山市': '广东省',
    '潮州市': '广东省',
    '揭阳市': '广东省',
    '云浮市': '广东省',
    '南宁市': '广西壮族自治区',
    '柳州市': '广西壮族自治区',
    '桂林市': '广西壮族自治区',
    '梧州市': '广西壮族自治区',
    '北海市': '广西壮族自治区',
    '防城港市': '广西壮族自治区',
    '钦州市': '广西壮族自治区',
    '贵港市': '广西壮族自治区',
    '玉林市': '广西壮族自治区',
    '百色市': '广西壮族自治区',
    '贺州市': '广西壮族自治区',
    '河池市': '广西壮族自治区',
    '来宾市': '广西壮族自治区',
    '崇左市': '广西壮族自治区',
    '海口市': '海南省',
    '三亚市': '海南省',
    '三沙市': '海南省',
    '儋州市': '海南省',
    '成都市': '四川省',
    '绵阳市': '四川省',
    '自贡市': '四川省',
    '攀枝花市': '四川省',
    '泸州市': '四川省',
    '德阳市': '四川省',
    '广元市': '四川省',
    '遂宁市': '四川省',
    '内江市': '四川省',
    '乐山市': '四川省',
    '南充市': '四川省',
    '眉山市': '四川省',
    '宜宾市': '四川省',
    '广安市': '四川省',
    '达州市': '四川省',
    '雅安市': '四川省',
    '巴中市': '四川省',
    '资阳市': '四川省',
    '阿坝藏族羌族自治州': '四川省',
    '甘孜藏族自治州': '四川省',
    '凉山彝族自治州': '四川省',
    '贵阳市': '贵州省',
    '遵义市': '贵州省',
    '六盘水市': '贵州省',
    '安顺市': '贵州省',
    '毕节市': '贵州省',
    '铜仁市': '贵州省',
    '黔西南布依族苗族自治州': '贵州省',
    '黔东南苗族侗族自治州': '贵州省',
    '黔南布依族苗族自治州': '贵州省',
    '昆明市': '云南省',
    '曲靖市': '云南省',
    '玉溪市': '云南省',
    '保山市': '云南省',
    '昭通市': '云南省',
    '丽江市': '云南省',
    '普洱市': '云南省',
    '临沧市': '云南省',
    '楚雄彝族自治州': '云南省',
    '红河哈尼族彝族自治州': '云南省',
    '文山壮族苗族自治州': '云南省',
    '西双版纳傣族自治州': '云南省',
    '大理白族自治州': '云南省',
    '德宏傣族景颇族自治州': '云南省',
    '怒江傈僳族自治州': '云南省',
    '迪庆藏族自治州': '云南省',
    '拉萨市': '西藏自治区',
    '日喀则市': '西藏自治区',
    '昌都市': '西藏自治区',
    '林芝市': '西藏自治区',
    '山南市': '西藏自治区',
    '那曲市': '西藏自治区',
    '阿里地区': '西藏自治区',
    '西安市': '陕西省',
    '宝鸡市': '陕西省',
    '咸阳市': '陕西省',
    '铜川市': '陕西省',
    '渭南市': '陕西省',
    '延安市': '陕西省',
    '汉中市': '陕西省',
    '榆林市': '陕西省',
    '安康市': '陕西省',
    '商洛市': '陕西省',
    '兰州市': '甘肃省',
    '嘉峪关市': '甘肃省',
    '金昌市': '甘肃省',
    '白银市': '甘肃省',
    '天水市': '甘肃省',
    '武威市': '甘肃省',
    '张掖市': '甘肃省',
    '平凉市': '甘肃省',
    '酒泉市': '甘肃省',
    '庆阳市': '甘肃省',
    '定西市': '甘肃省',
    '陇南市': '甘肃省',
    '临夏回族自治州': '甘肃省',
    '甘南藏族自治州': '甘肃省',
    '西宁市': '青海省',
    '海东市': '青海省',
    '海北藏族自治州': '青海省',
    '黄南藏族自治州': '青海省',
    '海南藏族自治州': '青海省',
    '果洛藏族自治州': '青海省',
    '玉树藏族自治州': '青海省',
    '海西蒙古族藏族自治州': '青海省',
    '银川市': '宁夏回族自治区',
    '石嘴山市': '宁夏回族自治区',
    '吴忠市': '宁夏回族自治区',
    '固原市': '宁夏回族自治区',
    '中卫市': '宁夏回族自治区',
    '乌鲁木齐市': '新疆维吾尔自治区',
    '克拉玛依市': '新疆维吾尔自治区',
    '吐鲁番市': '新疆维吾尔自治区',
    '哈密市': '新疆维吾尔自治区',
    '昌吉回族自治州': '新疆维吾尔自治区',
    '博尔塔拉蒙古自治州': '新疆维吾尔自治区',
    '巴音郭楞蒙古自治州': '新疆维吾尔自治区',
    '阿克苏地区': '新疆维吾尔自治区',
    '克孜勒苏柯尔克孜自治州': '新疆维吾尔自治区',
    '喀什地区': '新疆维吾尔自治区',
    '和田地区': '新疆维吾尔自治区',
    '伊犁哈萨克自治州': '新疆维吾尔自治区',
    '塔城地区': '新疆维吾尔自治区',
    '阿勒泰地区': '新疆维吾尔自治区',
    '石河子市': '新疆维吾尔自治区',
    '阿拉尔市': '新疆维吾尔自治区',
    '图木舒克市': '新疆维吾尔自治区',
    '五家渠市': '新疆维吾尔自治区',
    '北屯市': '新疆维吾尔自治区',
    '铁门关市': '新疆维吾尔自治区',
    '双河市': '新疆维吾尔自治区',
    '可克达拉市': '新疆维吾尔自治区',
    '昆玉市': '新疆维吾尔自治区',
    '香港特别行政区': '香港特别行政区',
    '澳门特别行政区': '澳门特别行政区',
    '台湾省': '台湾省',
    '高雄市': '台湾省',
    '基隆市': '台湾省',
    '台中市': '台湾省',
    '台南市': '台湾省',
    '新竹市': '台湾省',
    '嘉义市': '台湾省',
    '新北市': '台湾省',
    '桃园市': '台湾省',
    '宜兰市': '台湾省',
    '苗栗市': '台湾省',
    '彰化市': '台湾省',
    '南投市': '台湾省',
    '云林市': '台湾省',
    '屏东市': '台湾省',
    '台东市': '台湾省',
    '花莲市': '台湾省',
    '澎湖市': '台湾省',
    '金门市': '台湾省',
    '连江市': '台湾省'
}

# 根据标准的城市名获取省份名
def get_province_from_city(city):
    # 获取城市对应的省份，如果城市不在映射中，返回 None
    province_name = city_province_map.get(city)
    return province_name


def word2none(word):
    print(f'可能存在其他省份/城市：{word}')
    word = None
    return word


def word2oversea(word):
    print(f'可能存在其他省份/城市：{word}')
    word = '海外'
    return word


# 修正汽车之家和微博的用户所在省名，以及汽车之家主贴和评论的ip省名
def fix_province_name(name):
    try:
        final_name = prov2goodprov_dict[name]
    except:
        final_name = word2none(name)
    return final_name


# 修正城市名
def fix_city_name4none(name):
    if name in city2goodcity_dict.keys():
        final_name = city2goodcity_dict[name]
    elif name in city2goodcity_dict.values():
        final_name = name
    else:
        final_name = word2none(name)
    return final_name


# 修正b站的省名
def fix_province_name4oversea(name):
    try:
        final_name = prov2goodprov_dict[name]
    except:
        final_name = word2oversea(name)
    return final_name


# 修正微博cmt的省名 + b站cmt的省名 + 汽车之家论坛post与cmt
def fix_province_name4none(name):
    try:
        prov_name = prov2goodprov_dict[name]
        if prov_name is not None:
            country_name = '中国'
        else:
            country_name = None
    except:
        prov_name = word2none(name)
        country_name = name
    return prov_name, country_name


# 根据输入的文本，找出其中的国家、省份及城市
# def find_country_and_province(text):
#     if text is None:
#         return None, None, None
#     # 数据处理，将繁体统一为简体
#
#     elif text.lower() in ['', '其他', '其它', '地区未知', 'other']:
#         country = province = None
#     else:
#         # 判断是否是英文，如果是英文，则默认是只去匹配国家；如果匹配的是中国，则再匹配一轮省份
#         if text.replace(' ', '').encode('utf-8').isalpha():
#         location_df = cpca.transform([text], index=0)
#         province = location_df.loc[0, '省']
#         if province is None:
#             country = '海外'

def create_task_id(task_owner, db_config, platform, log_table):
    task_owner_str = '|'.join(task_owner)
    db = 'BA_USING'
    cursor, conn = get_cursor_times(db_config[db], 10)
    sql = f'select max(task_id) as max_id from {log_table}'
    cursor.execute(sql)
    results = cursor.fetchall()  # 用于返回多条数据
    df = pd.DataFrame(list(results))
    cursor.close()
    if len(df) == 0:
        max_id = 1
    else:
        for row in results:
            max_id = row[0] + 1
            break
    start_dt = get_datetime_now()
    task_status = 'processing'
    task_dict = {'task_id': max_id, 'task_owner': task_owner_str, 'task_platform': platform, 'start_datetime': start_dt,
                 'end_datetime': None, 'task_status': task_status}
    insert_json_sql(task_dict, db, log_table, db_config)  # 默认都会根据主键对数据进行更新
    return task_dict


def sort_keyword2dict(df_input, col):
    dict_out = {}
    for idx, row in df_input.iterrows():
        keyword_dict = {}
        series_id = str(row['series_id'])
        brand_id = row['brand_id']
        keyword_list_str = str(row[col])
        keyword_list = keyword_list_str.split('、')
        for keyword in keyword_list:
            keyword_dict[keyword] = {"brand": int(brand_id), "series": int(series_id)}
        dict_out[series_id] = {"brand_id": int(brand_id), "keyword": keyword_dict}
    return dict_out


def sort_userid2dict(df_input, col_acount, col_word):
    dict_out = {}
    account_id_list = list(set(df_input[col_acount].tolist()))
    for account_id in account_id_list:
        dict_out[str(account_id)] = {}
        dict_out[str(account_id)]["valid_flag"] = 1
        df_account = df_input[df_input[col_acount] == account_id]
        dict_out[str(account_id)]["car_list"] = {}
        for idx, row in df_account.iterrows():
            brand_id = row["brand_id"]
            series_id = row["series_id"]
            series_keyword = row[col_word].split('、')
            dict_out[str(account_id)]["car_list"][str(series_id)] = {"series_keyword": series_keyword}
        dict_out[str(account_id)]["brand_id"] = brand_id
    return dict_out


sp_list = {'车险销售': ['车险', '汽车保险'], '车品销售': ['车品', '内饰', '汽车用品', '车辆用品'],
           '车膜销售': ['车膜', '贴膜', '车衣'],
           '轮毂销售': ['轮毂'], '二手车车商': ['二手车']}


def speacial_identify_summmary(text):
    if (type(text) is not str) or text == '':
        return None, None
    for i in list(sp_list.keys()):
        for keyword in sp_list[i]:
            if keyword in text:
                return keyword, i
            else:
                continue
    return None, None


emo_neg = 0.3
emo_pos = 0.7


def find_emotion_by_api(TEXT):
    # 接口地址
    url = "http://ltpapi.xfyun.cn/v2/sa"
    # 开放平台应用ID
    x_appid = "d98c93ce"
    # 开放平台应用接口秘钥
    api_key = "9ed34088080000bf82286f25f6702a36"
    # # 开放平台应用ID
    # x_appid = "f74adea1"
    # # 开放平台应用接口秘钥
    # api_key = "6bfb1da8c4ad2b0cbf28a0c829228db7"
    body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    # print(result.decode('utf-8'))
    return result.decode('utf-8')


def cut_sentences(content):
    # 结束符号，包含中文和英文的
    end_flag = ['?', '!', '.', '？', '！', '。', '…']
    try:
        content_len = len(content)
    except:
        return []
    sentences = []
    tmp_char = ''
    for idx, char in enumerate(content):
        # 拼接字符
        tmp_char += char
        # 判断是否已经到了最后一位
        if (idx + 1) == content_len:
            sentences.append(tmp_char)
            break
        # 判断此字符是否为结束符号
        if char in end_flag:
            # 再判断下一个字符是否为结束符号，如果不是结束符号，则切分句子
            next_idx = idx + 1
            if not content[next_idx] in end_flag:
                sentences.append(tmp_char)
                tmp_char = ''
    return sentences


def calculate_emotion_score(text):
    if text.replace(' ', '') == '' or (text.__contains__('互赞|回赞|已赞|求赞') and len(text) <= 15):
        final_sen = 0.50
    else:
        try:
            res = find_emotion_by_api(text)
            res = json.loads(res)
            if res['code'] != "0":
                text_list = cut_sentences(text)
                text_num = len(text_list)
                sentiments = 0
                for text in text_list:
                    time.sleep(0.5)
                    res = find_emotion_by_api(text)
                    res = json.loads(res)
                    if res['code'] == '10106':
                        text_num = text_num - 1
                        continue
                    try:
                        sentiment = res['data']['score']
                    except:
                        text_num = text_num - 1
                        sentiment = 0
                        continue
                    sentiments = sentiments + sentiment
                try:
                    final_sen = sentiments / text_num
                except Exception as e:
                    final_sen = 0.5
            else:
                final_sen = res['data']['score']
        except Exception as e:
            print(e)
            final_sen = 0.5
    if final_sen < emo_neg:
        emo_pn = -1
    elif final_sen > emo_pos:
        emo_pn = 1
    else:
        emo_pn = 0
    return final_sen, emo_pn


emo_pos_paddle = 0.8
emo_neg_paddle = 0.2


def calculate_emotion_score_by_paddle(text, model):
    if text.replace(' ', '') == '' or (text.__contains__('互赞|回赞|已赞|求赞') and len(text) <= 15):
        final_sen_neg = final_sen_pos = 0.50
    else:
        try:
            text_list = [text]
            text_dict = {'text': text_list}
            results = model.sentiment_classify(data=text_dict)
            result = results[0]
            final_sen_neg = result['negative_probs']
            final_sen_pos = result['positive_probs']
        except Exception as e:
            final_sen_neg = final_sen_pos = 0.5
    final_sen = final_sen_pos
    if final_sen < emo_neg_paddle:
        emo_pn = -1
    elif final_sen > emo_pos_paddle:
        emo_pn = 1
    else:
        emo_pn = 0
    return final_sen, emo_pn


def keywords_extraction(text, keyword_cnt):
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=text, lower=True)
    keywords = tr4w.get_keywords(num=keyword_cnt, word_min_len=1)
    return keywords


# 字体处理的模块
#########################################################################

# 功能：比较两个列表的坐标信息是否相同，位置是否接近。汽车之家专用。
def cor_compare(l1, l2):
    if len(l1) != len(l2):
        return False
    else:
        mark = True
        # 一个字的所有坐标中，有一个与base存在大于40的差异，就退出比较
        for idx in range(len(l1)):
            if abs(l1[idx][0] - l2[idx][0]) < 40 and abs(l1[idx][1] - l2[idx][1]) < 40:
                pass
            else:
                mark = False
                break
        return mark


# 功能：根据font基准寻找新的word_list。汽车之家专用。
def find_new_word_list(font_base, word_list_base, font_new):
    # 手动确定一组编码和字符的对应关系
    uni_list = font_base['cmap'].tables[0].ttFont.getGlyphOrder()[1:]

    # 获取38个字符的（x,y）信息
    cor_base_all = []
    for uni in uni_list:
        p1 = []  # 保存一个字符的(x,y)信息
        p = font_base['glyf'][uni].coordinates  # 获取对象的x,y信息，返回的是一个GlyphCoordinates对象，可以当作列表操作，每个元素是（x,y）元组
        for f in p:  # 把GlyphCoordinates对象改成一个列表
            p1.append(f)
        cor_base_all.append(p1)

    uni_list_new = font_new.getGlyphOrder()[1:]
    cor_list_new = []
    ss = []
    for i in uni_list_new:
        pp1 = []
        p = font_new['glyf'][i].coordinates
        for f in p:
            pp1.append(f)
        cor_list_new.append(pp1)

    word_list_new = []
    for cor_new in cor_list_new:
        idx_new = 0
        for cor_base in cor_base_all:
            idx_new += 1
            if cor_compare(cor_base, cor_new):
                word_list_new.append(word_list_base[idx_new - 1])

    return word_list_new