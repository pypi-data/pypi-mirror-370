# coding:utf-8
# V1.5.5
import sys
import pymysql
import pandas as pd
import numpy as np
from tqdm import tqdm
import jieba
import time
import datetime
import re
import warnings
import random
from bs4 import BeautifulSoup
import general_calculator_zsd.general_calculator as gc
import universal_function_zsd.universal_function as uf
global true, false, null
false = False
true = True
null = ''
warnings.filterwarnings("ignore")
# 如果数据库改了，就要修改这里
ip_database = {"localhost": "wom_db_local", "BA_USING": "BA_USING", "BI_READ": "bi"}  # 需修改本地数据库名
dic_connet = {"localhost": {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'zwp650811', 'database': ip_database["localhost"]},
              "BA_USING": {'host': '10.26.241.164', 'port': 3306, 'user': 'BA_USING', 'password': 'BA_USING@2022', 'database': ip_database["BA_USING"]},
              "BI_READ": {'host': '10.26.241.164', 'port': 3306, 'user': 'BI_READ', 'password': 'Bireader@1027', 'database': ip_database["BI_READ"]}}
insert_ip = 'BA_USING'
insert_map_detail = {
    # 'weibo_auth_post': ['etl_post', 'id', 100, 'BA_USING'],
    'weibo_search_post': ['etl_post', 'id', 100, 'BA_USING'],
    'weibo_user_info': ['etl_user', 'user_id', 100, 'BA_USING'],
    'weibo_comment': ['etl_comment', 'comment_id', 100, 'BA_USING'],
    'autohome_wenzhang_post': ['etl_post', 'wenzhang_id', 200, 'BA_USING'],
    'autohome_luntan_post': ['etl_post', 'tiezi_id', 200, 'BA_USING'],
    'autohome_koubei_post': ['etl_post', 'post_id', 200, 'BA_USING'],
    'autohome_wenzhang_comment': ['etl_comment', 'comment_id', 200, 'BA_USING'],
    'autohome_luntan_comment': ['etl_comment', 'comment_id', 200, 'BA_USING'],
    'autohome_koubei_comment': ['etl_comment', 'comment_id', 200, 'BA_USING'],
    'autohome_user_info': ['etl_user', 'user_id', 200, 'BA_USING'],
    'bilibili_video_post': ['etl_post', 'video_id', 300, 'BA_USING'],
    'bilibili_video_comment': ['etl_comment', 'comment_id',300, 'BA_USING'],
    'bilibili_video_danmu': ['etl_comment','danmu_comment_id', 300, 'BA_USING'],
    'bilibili_user_info': ['etl_user', 'user_id', 300, 'BA_USING'],
    'xiaohongshu_search_post': ['etl_post', 'note_id', 400, 'BA_USING'],
    'xiaohongshu_comment': ['etl_comment', 'comment_id', 400, 'BA_USING'],
    'xiaohongshu_user_info': ['etl_user', 'user_id', 400, 'BA_USING'],
    'dongchedi_community_post': ['etl_post', 'post_id', 600, 'BA_USING'],
    'dongchedi_article_post': ['etl_post', 'post_id', 600, 'BA_USING'],
    'dongchedi_koubei_post': ['etl_post', 'post_id', 600, 'BA_USING'],
    'dongchedi_comment': ['etl_comment', 'comment_id', 600, 'BA_USING'],
    'dongchedi_user_info': ['etl_user', 'user_id', 600, 'BA_USING'],
    'xinchuxing_community_post': ['etl_post', 'post_id', 700, 'BA_USING'],
    'xinchuxing_comment': ['etl_comment', 'comment_id', 700, 'BA_USING'],
    'xinchuxing_user_info': ['etl_user', 'user_id', 700, 'BA_USING'],
    '42hao_community_post': ['etl_post', 'post_id', 800, 'BA_USING'],
    '42hao_comment': ['etl_comment', 'comment_id', 800, 'BA_USING'],
    '42hao_user_info': ['etl_user', 'user_id', 800, 'BA_USING'],
    'douyin_search_post': ['etl_post', 'post_id', 900, 'BA_USING'],
    'douyin_comment': ['etl_comment', 'comment_id', 900, 'BA_USING'],
    'douyin_user_info': ['etl_user', 'user_id', 900, 'BA_USING'],
    'hupu_bbs_post': ['etl_post', 'post_id', 1000, 'BA_USING'],
    'hupu_bbs_comment': ['etl_comment', 'comment_id', 1000, 'BA_USING'],
    'hupu_user_info': ['etl_user', 'user_id', 1000, 'BA_USING'],
    'shipinhao_post': ['etl_post', 'post_id', 1200, 'BA_USING'],
    'shipinhao_comment': ['etl_comment', 'comment_id', 1200, 'BA_USING'],
    'shipinhao_user_info': ['etl_user', 'user_id', 1200, 'BA_USING'],
    'nga_post': ['etl_post', 'post_id', 1300, 'BA_USING'],
    'nga_comment': ['etl_comment', 'comment_id', 1300, 'BA_USING'],
    'nga_user_info': ['etl_user', 'user_id', 1300, 'BA_USING']
}

# insert_table与select_table对应关系
post_list = []
cmt_list = []
user_list = []
for key_tbl, value_tbl in insert_map_detail.items():
    if value_tbl[0] == 'etl_post':
        post_list.append(key_tbl)
    if value_tbl[0] == 'etl_comment':
        cmt_list.append(key_tbl)
    if value_tbl[0] == 'etl_user':
        user_list.append(key_tbl)

hobby_eng2chn = {
    'cheyouhui': '车友会',
    'finance': '金融',
    'play_car': '玩车',
    'parenting': '亲子',
    'read': '读书',
    'photography': '摄影',
    'home_furnishing': '家居',
    'cute_pet': '萌宠',
    'delicious_food': '美食',
    'movie': '影视',
    'create_together': '共创',
    'protection': '环保',
    'sports_fitness': '运动健身',
    'fashion_beauty': '时尚美妆',
    'art_design': '艺术设计',
    'e_sports': '游戏电竞',
    'technology': '科技数码',
    'travel': '旅行',
    'listen_music': '音乐'
}

def check_excluded_word(content, base_series_id, info_df):
    series_line = info_df[info_df['series_id'] == base_series_id]
    try:
        check_word_str = series_line['word_excluded'].iloc[0]
        for check_word in check_word_str.split("、"):
            if check_word in content.lower():
                print(f"含有排除词{check_word}，不进行以下post内容的插入：{content[0:20]}...")
                return True
    except:
        return False
    return False

def check_confirm_word(content, base_series_id, info_df):
    series_line = info_df[info_df['series_id'] == base_series_id]
    if not series_line.empty:
        if series_line['word_confirm'].iloc[0]:
            confirm_word_str = series_line['word_confirm'].iloc[0]
            for check_word in confirm_word_str.split("、"):
                if check_word in content.lower():
                    return True
        else:
            return True
    else:
        return True
    return False

def check_confused_series(content, base_series_id, info_df):
    series_line = info_df[info_df['series_id'] == base_series_id]
    series_list = []
    if not series_line.empty:
        if series_line['series_id_suspected'].iloc[0]:
            series_id_suspected_str = series_line['series_id_suspected'].iloc[0]
            for series_id_suspected in series_id_suspected_str.split("、"):
                series_suspected_line = info_df[info_df['series_id'] == int(series_id_suspected)]
                if not series_suspected_line.empty:
                    if series_suspected_line['word_confirm'].iloc[0]:
                        confirm_word_str = series_suspected_line['word_confirm'].iloc[0]
                        for check_word in confirm_word_str.split("、"):
                            if check_word in content.lower():
                                series_list.append(int(series_id_suspected))
                                break
    if len(series_list) == 0:
        return base_series_id
    else:
        new_series_id = random.choice(series_list)
        return new_series_id

def get_datetime_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def combine_text(df):
    data_list = df.tolist()
    return '\n'.join(i for i in data_list if i is not None)

def select_sql_json(select_ip, select_table, start_datetime, end_datetime):  # sql 执行数据库语句
    # if select_table == 'moment':
    #     select_sql = """
    #         select * from {table}
    #         where createtime >= '{start_datetime}' and createtime < '{end_datetime}';
    #         """.format(table=select_table, start_datetime=start_datetime, end_datetime=end_datetime)
    # elif select_table == 'momentcomment':
    #     select_sql = """
    #         select mc.id id , mc.momentid momentid, mc.createtime createtime, mc.content content, mc.root root,
    #         mc.rootid rootid, mc.createdby createdby, mc.commentscount commentscount, m.source from {table} mc
    #         left join moment m on m.id=mc.momentid where mc.createtime >= '{start_datetime}'
    #         and mc.createtime < '{end_datetime}';
    #         """.format(table=select_table, start_datetime=start_datetime, end_datetime=end_datetime)
    if select_table == 'bilibili_video_comment':
        select_sql = f"""
                    select c.*, p.video_id from {select_table} c
                    left join bilibili_video_post p on c.video_bvid=p.video_bvid where c.spider_datetime >='{start_datetime}'
                    and c.spider_datetime < '{end_datetime}'
                    order by comment_datetime desc
                    """
    # elif select_table == 'user_base':
    #     select_sql = """
    #             select u.user_id as user_id, u.nick_name as user_nickname, u.sex as user_gender, u.province_name as user_province,
    #             u.city_name as user_city, u.birthday as user_birth_date, u.signature as user_summary, u.badges as verified_reason,
    #             u.role as user_label, DATE_FORMAT(u.create_time,'%Y-%m-%d') as register_date, u.hobby as user_interests
    #             from bi.{table} u
    #             LEFT JOIN bi.member_info mi on u.user_id=mi.smart_id
    #             LEFT JOIN bi.member_integral_info m2 on mi.id=m2.member_id
    #             where (m2.points_status='enable' or m2.points_status is null)
    #             and left(user_id,4) != '9999'
    #             and date_format(u.create_time,'%Y-%m-%d') < current_date
    #             and update_time >= '{start_datetime}' and update_time < '{end_datetime}';
    #             """.format(table=select_table, start_datetime=start_datetime, end_datetime=end_datetime)
    elif select_table == 'xiaohongshu_search_post':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001001', CAST(xit.increment_id AS CHAR)) AS true_note_id, 
                            CONCAT('4001002', CAST(xit2.increment_id AS CHAR)) AS true_user_id 
                        FROM 
                            xiaohongshu_search_post  xspt 
                        INNER JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.note_id = xit.id AND xit.type_id = 1001
                        INNER JOIN 
                            xiaohongshu_id_transform xit2 
                        ON 
                            xspt.user_id = xit2.id AND  xit2.type_id = 1002
                        where xspt.spider_datetime >='{start_datetime}' and xspt.spider_datetime < '{end_datetime}'"""
    elif select_table == 'xiaohongshu_comment':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001001', CAST(xit.increment_id AS CHAR)) AS true_post_id, 
                            CONCAT('4001002', CAST(xit2.increment_id AS CHAR)) AS true_user_id,
                            CONCAT('4001003', CAST(xit3.increment_id AS CHAR)) AS true_comment_id, 
                            CONCAT('4001003', CAST(xit4.increment_id AS CHAR)) AS true_main_comment_id 
                        FROM 
                            xiaohongshu_comment xspt 
                        LEFT JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.post_id = xit.id AND xit.type_id = 1001
                        LEFT JOIN 
                            xiaohongshu_id_transform xit2 
                        ON 
                            xspt.user_id = xit2.id AND  xit2.type_id = 1002
                        LEFT JOIN 
                            xiaohongshu_id_transform xit3 
                        ON 
                            xspt.comment_id = xit3.id AND  xit3.type_id = 1003
                        LEFT JOIN 
                            xiaohongshu_id_transform xit4
                        ON 
                            xspt.main_comment_id = xit4.id AND xit4.type_id = 1003
                        where xspt.spider_datetime >='{start_datetime}' and xspt.spider_datetime < '{end_datetime}'"""
    elif select_table == 'xiaohongshu_user_info':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001002', CAST(xit.increment_id AS CHAR)) AS true_user_id 
                        FROM 
                            xiaohongshu_user_info xspt
                        LEFT JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.user_id = xit.id AND xit.type_id = 1002 
                        where xspt.spider_datetime >='{start_datetime}' and xspt.spider_datetime < '{end_datetime}'"""
    else:
        select_sql = f'''
        select * from {select_table} where spider_datetime>="{start_datetime}" and spider_datetime<"{end_datetime}";
        '''
    lst = []
    try:  # 调用函数建立连接
        conn = pymysql.connect(host=dic_connet[select_ip]['host'], port=dic_connet[select_ip]['port'],
                               user=dic_connet[select_ip]['user'], password=dic_connet[select_ip]['password'],
                               db=dic_connet[select_ip]['database'])
        df = pd.read_sql(select_sql, conn)  # DataFrame转为ndarray
        df1 = np.array(df)  # 获取列名
        column_list = list(df.columns)
        for row in df1:  # 循环每一行数据，组装成一个字典，然后得到字典的列表
            lst.append(dict(zip(column_list, list(row))))
        conn.close() # 关闭数据库连接
    except Exception as ex:
        print(ex)
    return lst

def select_sql_json4loss(select_ip, select_table):  # sql 执行数据库语句
    goal_table = insert_map_detail[select_table][0]
    select_key = insert_map_detail[select_table][1]
    plat_low = insert_map_detail[select_table][2]
    plat_high = plat_low+100
    if select_table in post_list:
        goal_key = 'post_id'
    elif select_table in cmt_list:
        goal_key = 'comment_id'
    else:
        goal_key = 'user_id'

    # if select_table == 'momentcomment':
    #     select_sql = f"""
    #             select mc.id id , mc.momentid momentid, mc.createtime createtime, mc.content content, mc.root root,
    #             mc.rootid rootid, mc.createdby createdby, mc.commentscount commentscount, m.source from {select_table} mc
    #             left join moment m on m.id=mc.momentid where mc.{select_key} not in
    #             (select {goal_key} from {goal_table} where platform_id >={plat_low} and platform_id < {plat_high});
    #             """
    if select_table == 'bilibili_video_comment':
        select_sql = f"""
                    select st.*, p.video_id from {select_table} st
                    left join bilibili_video_post p on st.video_bvid = p.video_bvid 
                    where not exists
                    (select 1 from {goal_table} gt where gt.{goal_key} = st.{select_key} 
                    and gt.platform_id >={plat_low} and gt.platform_id < {plat_high})
                    """
    # elif select_table == 'user_base':
    #     select_sql = f"""
    #             select u.user_id as user_id, u.nick_name as user_nickname, u.sex as user_gender, u.province_name as user_province,
    #             u.city_name as user_city, u.birthday as user_birth_date, u.signature as user_summary, u.badges as verified_reason,
    #             u.role as user_label, DATE_FORMAT(u.create_time,'%Y-%m-%d') as register_date, u.hobby as user_interests
    #             from bi.{select_table} u
    #             LEFT JOIN bi.member_info mi on u.user_id=mi.smart_id
    #             LEFT JOIN bi.member_integral_info m2 on mi.id=m2.member_id
    #             where (m2.points_status='enable' or m2.points_status is null)
    #             and left(user_id,4) != '9999'
    #             and date_format(u.create_time,'%Y-%m-%d') < current_date
    #             and {select_key} not in (select {goal_key} from ba_using.{goal_table} where media_id >={plat_low}
    #                                     and media_id < {plat_high});
    #             """
    elif select_table == 'xiaohongshu_search_post':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001001', CAST(xit.increment_id AS CHAR)) AS true_note_id, 
                            CONCAT('4001002', CAST(xit2.increment_id AS CHAR)) AS true_user_id 
                        FROM 
                            xiaohongshu_search_post  xspt 
                        INNER JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.note_id = xit.id AND xit.type_id = 1001
                        INNER JOIN 
                            xiaohongshu_id_transform xit2 
                        ON 
                            xspt.user_id = xit2.id AND  xit2.type_id = 1002
                         where not exists 
                        (select 1 from {goal_table} gt where gt.{goal_key} = CONCAT('4001001', CAST(xit.increment_id AS CHAR))
                        and gt.platform_id >={plat_low} and gt.platform_id < {plat_high})
                        """
    elif select_table == 'xiaohongshu_comment':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001001', CAST(xit.increment_id AS CHAR)) AS true_post_id, 
                            CONCAT('4001002', CAST(xit2.increment_id AS CHAR)) AS true_user_id,
                            CONCAT('4001003', CAST(xit3.increment_id AS CHAR)) AS true_comment_id, 
                            CONCAT('4001003', CAST(xit4.increment_id AS CHAR)) AS true_main_comment_id 
                        FROM 
                            xiaohongshu_comment xspt 
                        LEFT JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.post_id = xit.id AND xit.type_id = 1001
                        LEFT JOIN 
                            xiaohongshu_id_transform xit2 
                        ON 
                            xspt.user_id = xit2.id AND  xit2.type_id = 1002
                        LEFT JOIN 
                            xiaohongshu_id_transform xit3 
                        ON 
                            xspt.comment_id = xit3.id AND  xit3.type_id = 1003
                        LEFT JOIN 
                            xiaohongshu_id_transform xit4
                        ON 
                            xspt.main_comment_id = xit4.id AND xit4.type_id = 1003
                        where not exists 
                        (select 1 from {goal_table} gt where gt.{goal_key} = CONCAT('4001003', CAST(xit3.increment_id AS CHAR))
                        and gt.platform_id >={plat_low} and gt.platform_id < {plat_high})
                        """
    elif select_table == 'xiaohongshu_user_info':
        select_sql = f"""SELECT 
                            xspt.*, 
                            CONCAT('4001002', CAST(xit.increment_id AS CHAR)) AS true_user_id 
                        FROM 
                            xiaohongshu_user_info xspt
                        LEFT JOIN 
                            xiaohongshu_id_transform xit 
                        ON 
                            xspt.user_id = xit.id AND xit.type_id = 1002 
                        where not exists 
                        (select 1 from {goal_table} gt where gt.{goal_key} = CONCAT('4001002', CAST(xit.increment_id AS CHAR))
                        and gt.media_id = {plat_low})
                        """

    elif 'user' in select_table:
        select_sql = f"""
                select * from {select_table} st
                where not exists 
                (select 1 from {goal_table} gt where gt.{goal_key} = st.{select_key} 
                and gt.media_id = {plat_low})
                """
    else:
        select_sql = f"""
                select * from {select_table} st
                where not exists 
                (select 1 from {goal_table} gt where gt.{goal_key} = st.{select_key} 
                and gt.platform_id >={plat_low} and gt.platform_id < {plat_high})
                """
    lst = []
    # 调用函数建立连接
    #try:
    conn = pymysql.connect(host=dic_connet[select_ip]['host'], port=dic_connet[select_ip]['port'],
                           user=dic_connet[select_ip]['user'], password=dic_connet[select_ip]['password'],
                           db=dic_connet[select_ip]['database'])
    df = pd.read_sql(select_sql, conn)  # DataFrame转为ndarray
    df1 = np.array(df)  # 获取列名
    column_list = list(df.columns)
    for row in df1:  # 循环每一行数据，组装成一个字典，然后得到字典的列表
        lst.append(dict(zip(column_list, list(row))))
    conn.close() # 关闭数据库连接
    return lst

def get_flag(value):
    if type(value) is int:
        if value != 0:
            return 0
        else:
            return 1
    else:
        return 1

def get_platform_id(value):
    if value == "app":
        return 501
    elif value == "admin":
        return 502
    elif value == "cms":
        return 503

def get_hashtag(value):
    if value is not None:
        ls = eval((value))
        res = []
        for item in ls:
            hashtag = item["subject"]
            res.append(hashtag)
        result = "|".join(i for i in res)
        return result
    else:
        return None

# 原始数据发生改变，因此不使用此函数
# def get_content4moment(content_data):
#     if content_data is not None:
#         ls = eval(content_data)
#         word_list = []
#         img_list = []
#         for content_dict in ls:
#             if content_dict['type'] == 'txt':
#                 soup = BeautifulSoup(content_dict['data'], 'lxml')
#                 if soup.text != '':
#                     word_list.append(soup.text)
#             elif content_dict['type'] == 'img':
#                 img_list.append(content_dict['data'])
#             else:
#                 print('存在其他type种类!!!')
#         return '。'.join(word_list), str(img_list)
#     else:
#         return None, '[]'


def get_content4moment(content_data):
    if content_data is not None:
        img_src = []
        soup = BeautifulSoup(content_data, 'lxml')
        text = soup.text
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get('src')
            img_src.append(src)
        return text, str(img_src)
        # if soup.text != '':
        #             word_list.append(soup.text)
        #     elif content_dict['type'] == 'img':
        #         img_list.append(content_dict['data'])
        #     else:
        #         print('存在其他type种类!!!')
        # return '。'.join(word_list), str(img_list)
    else:
        return None, '[]'


def get_province(value):  # 从文本中解析城市信息
    province_list = ["北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门"]
    fenci = jieba.cut(value, cut_all=True)
    res = list(set(province_list) & set(fenci))
    if res:
        return res[0]
    else:
        return None

def get_city(value):  # 从文本中解析城市信息
    city_list = ["北京", "天津", "重庆", "上海", "合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "滁州", "阜阳", "宿州", "巢湖", "六安", "亳州", "池州", "宣城", "福州", "厦门", "莆田", "三明", "泉州", "漳州", "南平", "龙岩", "宁德", "兰州", "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南", "临夏", "甘南", "广州", "韶关", "深圳", "珠海", "汕头", "佛山", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮", "南宁", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左", "贵阳", "六盘水", "遵义", "安顺", "铜仁", "黔西南", "毕节", "黔东南", "黔南", "海口", "三亚", "石家庄", "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水", "哈尔滨", "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化", "大兴安岭", "郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳", "商丘", "信阳", "周口", "驻马店", "武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州", "恩施土家族苗族自治州", "长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西土家族苗族自治州", "呼和浩特", "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "兴安盟", "锡林郭勒盟", "乌兰察布盟", "巴彦淖尔盟", "阿拉善盟", "南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁", "南昌", "景德镇", "萍乡", "九江", "新余", "鹰潭", "赣州", "吉安", "宜春", "抚州", "上饶", "长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "延边朝鲜族自治州", "沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛", "银川", "石嘴山", "吴忠", "固原", "中卫", "西宁", "海东", "海北", "黄南", "海南", "果洛", "玉树", "海西", "太原", "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁", "济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "莱芜", "临沂", "德州", "聊城", "滨州", "菏泽", "成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾", "广安", "达州", "雅安", "巴中", "资阳", "阿坝", "甘孜", "凉山", "拉萨", "昌都", "山南", "日喀则", "那曲", "阿里", "林芝", "乌鲁木齐", "克拉玛依", "吐鲁番", "哈密", "昌吉", "博尔塔拉", "巴音郭楞", "阿克苏", "克孜勒苏", "喀什", "和田", "伊犁", "塔城", "阿勒泰", "石河子", "昆明", "曲靖", "玉溪", "保山", "昭通", "楚雄", "红河", "文山", "思茅", "西双版纳", "大理", "德宏", "丽江", "怒江", "迪庆", "临沧", "杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水", "西安", "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "榆林", "安康", "商洛", "台北", "高雄", "基隆", "台中", "台南", "新竹", "嘉义", "香港", "澳门"]
    fenci = jieba.cut(value, cut_all=True)
    res = list(set(city_list) & set(fenci))
    if res:
        return res[0]
    else:
        return None

def sort_user_base_interests(text):
    hobby_list_chn = []
    if text is not None:
        hobby_list_eng = eval(text)
        for hobby_eng in hobby_list_eng:
            try:
                hobby_list_chn.append(hobby_eng2chn[hobby_eng])
            except:
                print(hobby_eng)
    hobby_str = '|'.join(hobby_list_chn)
    if hobby_str == '':
        hobby_str = None
    return hobby_str

# 数据处理并插入
def insert_json_sql2etl(json_data, insert_ip, insert_table, select_table, cover_flag, identify_info_df, insert_mode = 'default'):
    insert_data = {}
    insert_data["upload_datetime"] = get_datetime_now()
    # 自定义部分——导入数据预处理（手动填写需要导入的字段名 及 对应的上游数据字段名）
    if select_table == 'autohome_wenzhang_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"]
        insert_data["comment_like_count"] = json_data["like_count"]
        # insert_data["comment_reply_count"] = json_data["reply_num"]
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["wenzhang_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["hot_degree"] = json_data["like_count"]
    elif select_table == 'autohome_luntan_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        if '本楼已被删除' in json_data["comment_content"]:
            insert_data["comment_content"] = ''
        else:
            try:
                insert_data["comment_content"] = json_data["comment_content"].replace('图片已删除', '').strip()
            except:
                insert_data["comment_content"] = json_data["comment_content"].strip()
        # insert_data["comment_like_count"] = json_data["like_count"]
        # insert_data["comment_reply_count"] = json_data["reply_num"]
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["tiezi_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["hot_degree"] = 0
    elif select_table == 'autohome_koubei_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        if '本楼已被删除' in json_data["comment_content"]:
            insert_data["comment_content"] = ''
        else:
            try:
                insert_data["comment_content"] = json_data["comment_content"].replace('图片已删除', '').strip()
            except:
                insert_data["comment_content"] = json_data["comment_content"].strip()
        # insert_data["comment_like_count"] = json_data["like_count"]
        # insert_data["comment_reply_count"] = json_data["reply_num"]
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = json_data["like_count"]
    elif select_table == 'autohome_wenzhang_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["wenzhang_id"]
        insert_data["user_id"] = json_data["author_id"]
        insert_data["post_datetime"] = json_data["wenzhang_datetime"]
        insert_data["post_content"] = json_data["wenzhang_content"]
        insert_data["post_subject"] = json_data["wenzhang_subject"]
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = json_data["wenzhang_country"]
        insert_data["publish_province"] = json_data["wenzhang_province"]
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["like_count"]
        insert_data["read_count"] = json_data["view_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["keyword"]
        insert_data["account_name"] = "搜索"
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 1000*json_data["comment_count"]+json_data["view_count"]+2*json_data["play_count"]+100*json_data["like_count"]
        insert_data["post_image"] = json_data["pic_list"]
        insert_data["post_url"] = json_data["wenzhang_url"]
    elif select_table == 'autohome_luntan_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["tiezi_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["tiezi_datetime"]
        try:
            insert_data["post_content"] = json_data["tiezi_content"].replace('图片已删除', '').strip()
        except:
            insert_data["post_content"] = json_data["tiezi_content"].strip()
        insert_data["post_subject"] = json_data["tiezi_subject"]
        # insert_data["like_count"] = json_data[""]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        # insert_data["keyword"] = json_data["keyword"]
        insert_data["account_name"] = json_data["account_name"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["publish_country"] = json_data["tiezi_country"]
        insert_data["publish_province"] = json_data["tiezi_province"]
        insert_data["hot_degree"] = int(json_data["read_count"]) + 72*int(json_data["comment_count"])
        insert_data["post_url"] = json_data["tiezi_url"]
    elif select_table == 'autohome_koubei_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = None
        insert_data["like_count"] = json_data["like_count"]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["post_url"] = json_data["koubei_url"]
        # insert_data["account_name"] = json_data["account_name"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 3*int(json_data["like_count"]) + 4*int(json_data["comment_count"])
    elif select_table == 'autohome_user_info':
        insert_data["media_id"] = json_data["platform_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = json_data["user_birth_date"]
        # insert_data["user_education"] = json_data[""]
        # insert_data["user_work"] = json_data[""]
        insert_data["user_summary"] = None
        insert_data["verified_flag"] = json_data["certified_flag"]
        # insert_data["verified_type"] = json_data["brand_id"]
        # insert_data["verified_reason"] = json_data["series_id"]
        # insert_data["user_label"] = json_data["tiezi_datetime"]
        insert_data["user_post_count"] = json_data["tiezi_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["vip_level"]
        insert_data["register_date"] = json_data["register_date"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == 'bilibili_video_post':
        insert_data["platform_id"] = 301
        insert_data["post_id"] = json_data["video_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["video_pubdate"]
        insert_data["post_content"] = json_data["video_summary"]
        insert_data["post_subject"] = json_data["video_title"]
        insert_data["post_hashtag"] = json_data["video_tag"]
        # insert_data["publish_province"] = ""
        # insert_data["publish_city"] = ""
        # insert_data["publish_device"] = ""
        insert_data["like_count"] = json_data["like_count"]
        insert_data["read_count"] = json_data["play_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        # insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["search_keyword"]
        insert_data["account_name"] = "搜索"
        # insert_data["brand_id"] = get_brand_id(json_data["video_summary"])
        # insert_data["series_id"] = get_series_id(json_data["video_summary"])
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 2*json_data["like_count"] + 15*json_data["favorite_count"] + 10*json_data["comment_count"]
        insert_data["post_url"] = json_data["video_url"]
    elif select_table == 'bilibili_video_comment':
        insert_data["platform_id"] = 301
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["like_count"]
        insert_data["comment_reply_count"] = json_data["reply_count"]
        insert_data["comment_main_flag"] = json_data["main_flag"]
        insert_data["comment_main_id"] = json_data["main_id"]
        insert_data["post_id"] = json_data["video_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 1*int(json_data["like_count"]) + 6*int(json_data["reply_count"])
    elif select_table == 'bilibili_video_danmu':
        insert_data["platform_id"] = 301
        insert_data["comment_id"] = json_data["danmu_comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["pub_datetime"]
        # insert_data["comment_province"] = ""
        insert_data["comment_content"] = json_data["danmu_content"].strip()
        # insert_data["comment_like_count"] = json_data["star"]
        # insert_data["comment_reply_count"] = json_data["reply"]
        # insert_data["comment_main_flag"] = json_data['main_flag']
        # insert_data["comment_main_id"] = json_data['main_id']
        insert_data["post_id"] = json_data["video_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 0
    elif select_table == 'bilibili_user_info':
        insert_data["media_id"] = 300
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        # insert_data["user_country"] = json_data["user_country"]
        # insert_data["user_province"] = json_data["user_province"]
        # insert_data["user_city"] = json_data["user_city"]
        # insert_data["true_country"] = json_data["true_country"]
        # insert_data["true_province"] = json_data["true_province"]
        # insert_data["user_birth_date"] = json_data["user_birth_date"]
        insert_data["user_education"] = json_data["user_school"]
        # insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["user_summary"]
        # insert_data["verified_flag"] = json_data["verified_flag"]
        # insert_data["verified_type"] = json_data["verified_type"]
        # insert_data["verified_reason"] = json_data["verified_reason"]
        # insert_data["user_label"] = json_data["user_label"]
        # insert_data["user_post_count"] = json_data["user_post_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["user_level"]
        # insert_data["register_date"] = json_data["register_date"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        # insert_data["user_type"] = json_data["user_type"]
        # insert_data["user_feature"] = json_data["user_feature"]
        # insert_data["summary_keyword"] = json_data["summary_keyword"]
        # insert_data["user_interests"] = json_data["user_interests"]
        # insert_data["user_car_owned"] = json_data["user_car_owned"]
        # insert_data["user_car_interested"] = json_data["user_car_interested"]
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == 'moment':
        insert_data["platform_id"] = get_platform_id(json_data["source"])
        insert_data["post_id"] = json_data["id"]
        insert_data["user_id"] = int(json_data["createdby"].replace("CMS", "9999999999").replace("smarter_unknown", "1111111111"))
        insert_data["post_datetime"] = json_data["createtime"][:19]
        insert_data["post_content"], insert_data['post_image'] = get_content4moment(json_data["content"])
        # insert_data["post_content"] = json_data["content"]
        if json_data["subject"] == '无命名':
            insert_data["post_subject"] = ''
        else:
            insert_data["post_subject"] = json_data["subject"]
        insert_data["post_hashtag"] = get_hashtag(json_data["topics"])
        # insert_data["publish_province"] = ""
        # insert_data["publish_city"] = ""
        # insert_data["publish_device"] = ""
        insert_data["like_count"] = int(json_data["likescount"])
        insert_data["read_count"] = int(json_data["viewcount"])
        insert_data["comment_count"] = int(json_data["commentscount"])
        insert_data["repost_count"] = int(json_data["sharecount"])
        insert_data["spider_datetime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # insert_data["keyword"] = ""
        insert_data["account_name"] = json_data["source"]
        insert_data["brand_id"] = 45
        if any(word if word in (json_data["subject"]+json_data["content"]) else False for word in ['#3', '三号', '3号', '精灵3', '精灵三']):
            insert_data["series_id"] = 7044
        elif any(word if word in (json_data["subject"]+json_data["content"]) else False for word in ['#1', '一号', '1号', '精灵1', '精灵一']):
            insert_data["series_id"] = 6369
        else:
            insert_data["series_id"] = 999999
        insert_data["hot_degree"] = 50*int(json_data["favoritescount"]) + 8*int(json_data["commentscount"]) + 5*int(json_data["likescount"]) + 20*int(json_data["sharecount"])
    elif select_table == 'momentcomment':
        insert_data["platform_id"] = get_platform_id(json_data["source"])
        insert_data["comment_id"] = json_data["id"]
        insert_data["user_id"] = json_data["createdby"]
        insert_data["comment_datetime"] = json_data["createtime"]
        # insert_data["comment_province"] = ""
        insert_data["comment_content"] = json_data["content"]
        # insert_data["comment_like_count"] = None
        # insert_data["comment_reply_count"] = None
        insert_data["comment_main_flag"] = get_flag(json_data["root"])
        insert_data["comment_main_id"] = json_data["rootid"]
        insert_data["post_id"] = int(json_data["momentid"])
        insert_data["spider_datetime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        insert_data["hot_degree"] = int(json_data["commentscount"])
    elif select_table == 'weibo_auth_post' or select_table == 'weibo_search_post':
        insert_data["platform_id"] = 101
        insert_data["post_id"] = json_data["id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["account_name"] = json_data['screen_name']
        insert_data["post_datetime"] = json_data["created_at"]
        insert_data["post_content"] = json_data["text"].strip()
        insert_data["series_id"] = json_data["series_id"]
        insert_data["post_subject"] = None
        insert_data["post_hashtag"] = json_data["topics"]
        # insert_data["publish_province"] = get_province(json_data["location"])
        # insert_data["publish_city"] = get_city(json_data["location"])
        insert_data["publish_device"] = json_data["source"]
        insert_data["like_count"] = json_data["attitudes_count"]
        insert_data["read_count"] = None
        insert_data["comment_count"] = json_data["comments_count"]
        insert_data["repost_count"] = json_data["reposts_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        if "search" in select_table:
            insert_data["keyword"] = json_data["search_keyword"]
            insert_data["hot_degree"] = json_data["attitudes_count"] + 4*json_data["comments_count"]
        else:
            insert_data["keyword"] = None
            insert_data["hot_degree"] = json_data["attitudes_count"] + 8*json_data["comments_count"]
        img_list = json_data["pics"].split(',')
        insert_data["post_image"] = str(img_list)
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'weibo_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["comment_user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        if json_data["main_comment_flag"] == 0:
            insert_data["comment_content"] = re.sub(r'\回复@.*?\:', '', insert_data["comment_content"])
        insert_data["comment_like_count"] = json_data["comment_like_count"]
        # insert_data["comment_reply_count"] = str(json_data["comment_reply_count"]).replace("nan", "None")
        insert_data["comment_reply_count"] = json_data["comment_reply_count"]
        insert_data["comment_main_flag"] = json_data["main_comment_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        # if 'nan' in insert_data["comment_main_id"] or insert_data["comment_main_flag"] == 1:
        #     insert_data["comment_main_id"] = None
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 1 * json_data["comment_like_count"]
    elif select_table == 'weibo_user_info':
        insert_data["media_id"] = json_data["media_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = json_data["birth_date"]
        insert_data["user_education"] = json_data["user_education"]
        insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["user_summary"]
        insert_data["verified_flag"] = json_data["verified_flag"]
        insert_data["verified_type"] = json_data["verified_type"]
        insert_data["verified_reason"] = json_data["verified_reason"]
        insert_data["user_label"] = json_data["user_label"]
        insert_data["user_post_count"] = json_data["weibo_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["vip_level"]
        insert_data["register_date"] = json_data["register_time"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == 'user_base':
        insert_data["media_id"] = 500
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        gender = json_data["user_gender"]
        if gender == 'M':
            insert_data["user_gender"] = '男'
        elif gender == 'F':
            insert_data["user_gender"] = '女'
        else:
            insert_data["user_gender"] = None
        insert_data["user_country"] = '中国'
        # if json_data["user_province"] in ['上海', '北京', '天津','重庆']:
        #     insert_data["user_province"] = json_data["user_province"] + '市'
        # if json_data["user_city"] in ['上海市', '北京市', '天津市', '重庆市']:
        #     insert_data["user_city"] = json_data["user_city"].replace('市', '城区')
        # try:
        #     insert_data["user_birth_date"] = json_data["user_birth_date"].strftime('%Y-%m-%d')
        # except:
        #     insert_data["user_birth_date"] = None
        try:
            insert_data["user_province"] = prov2goodprov_dict[json_data["user_province"]]
        except:
            insert_data["user_province"] = None
        try:
            if json_data["user_city"].endswith('市') and len(json_data["user_city"]) > 2:
                cityname = json_data["user_city"][:-1]
            elif json_data["user_city"].endswith('地区') and len(json_data["user_city"]) > 3:
                cityname = json_data["user_city"][:-2]
            else:
                cityname = json_data["user_city"]
            insert_data["user_city"] = city2goodcity_dict[cityname]
        except:
            insert_data["user_city"] = None
        # insert_data["user_education"] = json_data["user_education"]
        # insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["user_summary"]
        # insert_data["verified_flag"] = json_data["verified_flag"]
        # insert_data["verified_type"] = json_data["verified_type"]
        insert_data["verified_reason"] = json_data["verified_reason"]
        insert_data["user_label"] = json_data["user_label"]
        # insert_data["user_post_count"] = json_data["weibo_count"]
        # insert_data["following_count"] = json_data["following_count"]
        # insert_data["follower_count"] = json_data["follower_count"]
        # insert_data["user_level"] = json_data["vip_level"]
        insert_data["register_date"] = json_data["register_date"]
        insert_data["user_interests"] = sort_user_base_interests(json_data["user_interests"])
        insert_data["spider_datetime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    elif select_table == 'xiaohongshu_user_info':
        if json_data['user_id'] == 0:
            return
        insert_data["media_id"] = 400
        insert_data["user_id"] = json_data["true_user_id"]
        if str(json_data["user_id"]) == '4001002859':
            print()
        insert_data["user_nickname"] = json_data["user_nickname"]
        if json_data['user_gender'] == '1':
            insert_data["user_gender"] = "女"
        elif json_data['user_gender'] == '0':
            insert_data["user_gender"] = "男"
        else:
            insert_data["user_gender"] = None
        if json_data['age']:
            insert_data['user_birth_date'] = f"{datetime.date.today().year - int(json_data['age'].strip('岁'))}-01-01"
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["user_summary"]
        insert_data["verified_flag"] = json_data["verified_flag"]
        insert_data["verified_reason"] = json_data["verified_reason"]
        insert_data["user_post_count"] = json_data["note_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["level"]
        insert_data["user_url"] = json_data["user_url"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    elif select_table == 'xiaohongshu_comment':
        if json_data['user_id'] == 0:
            return
        if json_data['post_id'] == 0:
            return
        insert_data["platform_id"] = 401
        insert_data["comment_id"] = json_data["true_comment_id"]
        insert_data["user_id"] = json_data["true_user_id"]
        insert_data["comment_datetime"] = json_data["comment_publish_time"]
        insert_data['comment_country'] = json_data['comment_country']
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["comment_like_count"]
        insert_data["comment_reply_count"] = str(json_data["comment_reply_count"])
        if json_data["comment_id"] == json_data["true_main_comment_id"]:
            insert_data["comment_main_flag"] = 1
            insert_data["comment_main_id"] = None
        else:
            insert_data["comment_main_flag"] = 0
            insert_data["comment_main_id"] = json_data["true_main_comment_id"]
        insert_data["post_id"] = json_data["true_post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 5*json_data["comment_like_count"] + 4*json_data["comment_reply_count"]
    elif select_table == 'xiaohongshu_search_post':
        if json_data['user_id'] == 0:
            return
        if json_data['note_id'] == 0:
            return
        insert_data["platform_id"] = 401
        insert_data["post_id"] = json_data["true_note_id"]
        insert_data["user_id"] = json_data["true_user_id"]
        insert_data["account_name"] = json_data['user_name']
        insert_data["post_datetime"] = json_data["created_at"]
        insert_data["post_content"] = json_data["note_content"].strip()
        insert_data["post_subject"] = json_data["title"]
        insert_data["read_count"] = json_data["view_count"]
        insert_data["like_count"] = json_data["likes_count"]
        insert_data["read_count"] = None
        insert_data["repost_count"] = json_data["shared_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["search_keyword"]
        insert_data["account_name"] = "搜索"
        insert_data['post_url'] =  json_data['post_url']
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data['publish_country'] = json_data['publish_country']
        insert_data["publish_province"] = json_data['publish_province']
        insert_data["hot_degree"] = 1*json_data['likes_count'] + 2*json_data['collected_count'] + 2*json_data['shared_count']
    elif select_table == 'hupu_bbs_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = json_data["post_title"]
        # insert_data["like_count"] = json_data[""]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["post_url"] = json_data["url"]
        insert_data["keyword"] = json_data["keyword"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["publish_country"] = json_data["post_country"]
        insert_data["publish_province"] = json_data["post_province"]
        insert_data["hot_degree"] = int(insert_data["comment_count"]) + int(json_data["read_count"]) * 100
    elif select_table == 'hupu_bbs_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["like_count"]
        insert_data["comment_reply_count"] = json_data["reply_count"]
        insert_data["comment_main_flag"] = json_data["main_comment_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = int(json_data["like_count"]) + int(json_data["reply_count"]) * 10
    elif select_table == 'hupu_user_info':
        insert_data["media_id"] = 1000
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = json_data["user_birth_date"]
        insert_data["user_url"] = json_data["user_url"]
        insert_data["user_summary"] = None
        insert_data["user_post_count"] = json_data["user_post_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["user_level"]
        insert_data["register_date"] = json_data["register_date"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    elif select_table == 'nga_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = json_data["post_title"]
        # insert_data["like_count"] = json_data[""]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["post_url"] = json_data["url"]
        insert_data["keyword"] = json_data["keyword"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["publish_country"] = json_data["post_country"]
        insert_data["publish_province"] = json_data["post_province"]
        # insert_data["hot_degree"] = int(insert_data["comment_count"]) + int(json_data["read_count"]) * 100
    elif select_table == 'nga_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["like_count"]
        insert_data["comment_reply_count"] = json_data["reply_count"]
        insert_data["comment_main_flag"] = json_data["main_comment_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        # insert_data["hot_degree"] = int(json_data["like_count"]) + int(json_data["reply_count"]) * 10
    elif select_table == 'nga_user_info':
        insert_data["media_id"] = 1300
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = json_data["user_birth_date"]
        insert_data["user_url"] = json_data["user_url"]
        insert_data["user_summary"] = None
        insert_data["user_post_count"] = json_data["user_post_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["user_level"]
        insert_data["register_date"] = json_data["register_date"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    elif select_table == 'smart_tucaoba_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["smart_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        # insert_data["comment_country"] = json_data["comment_country"]
        # insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        # insert_data["comment_like_count"] = json_data["star"]
        # insert_data["comment_reply_count"] = json_data["reply"]
        # insert_data["comment_main_flag"] = json_data['main_flag']
        # insert_data["comment_main_id"] = json_data['main_id']
        insert_data["post_id"] = 1000000003
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 0
    elif select_table == 'dongchedi_community_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = json_data["post_title"]
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = json_data["post_country"]
        insert_data["publish_province"] = json_data["post_province"]
        insert_data["post_type"] = None
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["digg_count"]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = None
        insert_data["account_name"] = None
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 2*json_data["digg_count"] + json_data["read_count"] + 5*json_data["comment_count"]
        insert_data["post_image"] = json_data["pic_url"]
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'dongchedi_article_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = json_data["post_title"]
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = json_data["post_country"]
        insert_data["publish_province"] = json_data["post_province"]
        insert_data["post_type"] = None
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["digg_count"]
        insert_data["read_count"] = json_data["view_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = None
        insert_data["account_name"] = None
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 5 * json_data["digg_count"] + json_data["view_count"] + 10 * json_data["comment_count"]
        insert_data["post_image"] = json_data["pic_url"]
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'dongchedi_koubei_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = None
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = None
        insert_data["publish_province"] = None
        insert_data["post_type"] = None
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["like_count"]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = None
        insert_data["account_name"] = None
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 5 * json_data["like_count"] + json_data["read_count"] + 10 * json_data["comment_count"]
        insert_data["post_image"] = json_data["pic_url"]
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'dongchedi_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data['digg_count']
        insert_data["comment_reply_count"] = None
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = json_data['digg_count']
    elif select_table == 'dongchedi_user_info':
        insert_data["media_id"] = json_data['media_id']
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = json_data["user_birth_date"]
        insert_data["user_education"] = None
        insert_data["user_work"] = None
        insert_data["user_summary"] = json_data["user_summary"]
        insert_data["verified_flag"] = None
        insert_data["verified_type"] = None
        insert_data["verified_reason"] = None
        insert_data["user_label"] = json_data["user_label"]
        insert_data["user_post_count"] = None
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["vip_level"]
        insert_data["register_date"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == 'xinchuxing_community_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"]
        insert_data["post_subject"] = json_data["post_title"]
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = json_data['post_country']
        insert_data["publish_province"] = json_data['post_province']
        insert_data["post_type"] = None
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["like_count"]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["search_keyword"]
        insert_data["account_name"] = None
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 1*json_data["read_count"] + 3*json_data["comment_count"] + 4*json_data["like_count"]  # 要优化
        insert_data["post_image"] = None
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'xinchuxing_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["like_count"]
        insert_data["comment_reply_count"] = json_data["reply_count"]
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = json_data["like_count"] + 2*json_data["reply_count"]
    elif select_table == 'xinchuxing_user_info':
        insert_data["media_id"] = json_data["media_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_birth_date"] = None
        insert_data["user_education"] = None
        insert_data["user_work"] = None
        insert_data["user_summary"] = json_data['user_introduce']
        insert_data["verified_flag"] = None
        insert_data["verified_type"] = None
        insert_data["verified_reason"] = None
        insert_data["user_label"] = None
        insert_data["user_post_count"] = None
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["vip_level"]
        insert_data["register_date"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_interests"] = None
        insert_data["user_car_owned"] = json_data["auth_car_info"]
        insert_data["user_car_interested"] = None
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == '42hao_community_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["content"].strip()
        insert_data["post_subject"] = json_data["post_title"]
        insert_data["post_hashtag"] = json_data["labels"]
        insert_data["like_count"] = json_data["like_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["post_url"] = json_data["url"]
        insert_data["post_image"] = json_data["pic_url"]
        # insert_data["hot_degree"] = 1*insert_data["like_count"] + 2*insert_data["comment_count"]  # 这里要修改
    elif select_table == '42hao_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_main_flag"] = json_data["comment_main_flag"]
        insert_data["comment_main_id"] = json_data["comment_main_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = json_data["like_count"]
    elif select_table == '42hao_user_info':
        insert_data["media_id"] = 800
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["user_summary"] = json_data['introduce']
        # insert_data["user_post_count"] = json_data["post_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_car_owned"] = json_data["author_car_info_paid"]
        insert_data["user_car_interested"] = json_data["author_car_info_intention"]
    elif select_table == 'shipinhao_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["publish_country"] = json_data["publish_country"]
        insert_data["publish_province"] = json_data["publish_province"]
        insert_data["post_hashtag"] = None
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_title"].strip()
        insert_data["repost_count"] = json_data["forward_count"]
        insert_data["like_count"] = json_data["like_count"]
        insert_data["comment_count"] = json_data["comment_count"]
        # insert_data["repost_count"] = json_data["shared_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["keyword"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["post_url"] = json_data["video_url"]
        insert_data["hot_degree"] =json_data["forward_count"] + json_data["comment_count"] + json_data["like_count"]
    elif select_table == 'shipinhao_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data["comment_country"] = json_data["comment_country"]
        insert_data["comment_province"] = json_data["comment_province"]
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["like_count"]
        # insert_data["comment_reply_count"] = json_data["comment_reply_count"]
        insert_data["comment_main_flag"] = json_data["main_comment_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = json_data["like_count"]
    elif select_table == 'shipinhao_user_info':
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["media_id"] = json_data["media_id"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        insert_data["user_city"] = json_data["user_city"]
        insert_data["true_country"] = json_data["ip_country"]
        insert_data["true_province"] = json_data["ip_province"]
        insert_data["true_city"] = None
        # insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["user_summary"]
        # insert_data["verified_flag"] = json_data["verified_flag"]
        # insert_data["verified_reason"] = json_data["verified_reason"]
        # insert_data["user_post_count"] = json_data["note_count"]
        # insert_data["following_count"] = json_data["following_count"]
        # insert_data["follower_count"] = json_data["follower_count"]
        # insert_data["user_level"] = json_data["level"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    elif select_table == 'douyin_search_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["post_datetime"] = json_data["post_datetime"]
        insert_data["post_content"] = json_data["post_content"].strip()
        insert_data["post_subject"] = None
        insert_data["post_hashtag"] = None
        insert_data["publish_country"] = None
        insert_data["publish_province"] = None
        insert_data["publish_device"] = None
        insert_data["like_count"] = json_data["likes_count"]
        insert_data["read_count"] = None
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["repost_count"] = json_data["shared_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["keyword"] = json_data["search_keyword"]
        insert_data["account_name"] = None
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["hot_degree"] = 20 * json_data["shared_count"] + 10 * json_data["comment_count"] + json_data["likes_count"]
        insert_data["post_image"] = json_data["cover_pic"]
        insert_data["post_url"] = json_data["post_url"]
    elif select_table == 'douyin_comment':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data['comment_country'] = json_data['comment_country']
        insert_data["comment_province"] = json_data['comment_province']
        insert_data["comment_content"] = json_data["comment_content"].strip()
        insert_data["comment_like_count"] = json_data["comment_like_count"]
        insert_data["comment_reply_count"] = json_data["comment_reply_count"]
        insert_data["comment_main_flag"] = json_data["main_comment_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        insert_data["post_id"] = json_data["post_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["hot_degree"] = 10 * json_data["comment_reply_count"] + json_data["comment_like_count"]
    elif select_table == 'douyin_user_info':
        insert_data["media_id"] = json_data["media_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_nickname"]
        insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = None
        insert_data["user_province"] = None
        insert_data["user_city"] = None
        insert_data["true_country"] = json_data["ip_country"]
        insert_data["true_province"] = json_data["ip_province"]
        insert_data["true_city"] = json_data["ip_city"]
        insert_data["user_birth_date"] = json_data["user_birthday"]
        insert_data["user_education"] = None
        insert_data["user_work"] = None
        insert_data["user_summary"] = json_data["user_summary"]
        insert_data["verified_flag"] = None
        insert_data["verified_type"] = None
        insert_data["verified_reason"] = None
        insert_data["user_label"] = json_data["user_tags"]
        insert_data["user_post_count"] = json_data["note_count"]
        insert_data["following_count"] = json_data["following_count"]
        insert_data["follower_count"] = json_data["follower_count"]
        insert_data["user_level"] = json_data["user_level"]
        insert_data["register_date"] = None
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["user_interests"] = None
        insert_data["user_car_owned"] = None
        insert_data["user_car_interested"] = None
        insert_data["user_url"] = json_data["user_url"]
    elif select_table == 'wechat_post':
        insert_data["platform_id"] = json_data["platform_id"]
        insert_data["post_id"] = json_data["wenzhang_id"]
        insert_data["user_id"] = json_data["author_id"]
        insert_data["post_datetime"] = json_data["wenzhang_datetime"]
        insert_data["post_content"] = json_data["wenzhang_content"].strip()
        insert_data["post_subject"] = json_data["wenzhang_title"]
        insert_data["post_url"] = json_data["wenzhang_url"]
        insert_data["read_count"] = json_data["read_count"]
        insert_data["like_count"] = json_data["like_count"]
        insert_data["keyword"] = json_data["keyword"]
        insert_data["comment_count"] = json_data["comment_count"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
        insert_data["brand_id"] = json_data["brand_id"]
        insert_data["series_id"] = json_data["series_id"]
        insert_data["publish_country"] = json_data["wenzhang_country"]
        insert_data["publish_province"] = json_data["wenzhang_province"]
        insert_data["hot_degree"] = json_data["comment_count"]
    elif select_table == 'wechat_user_info':
        insert_data["media_id"] = 1101
        insert_data["user_id"] = json_data["user_id"]
        insert_data["user_nickname"] = json_data["user_name"]
        # insert_data["user_gender"] = json_data["user_gender"]
        insert_data["user_country"] = json_data["user_country"]
        insert_data["user_province"] = json_data["user_province"]
        # insert_data["user_city"] = json_data["user_city"]
        # insert_data["user_work"] = json_data["user_work"]
        insert_data["user_summary"] = json_data["summary"]
        # insert_data["verified_flag"] = json_data["verified_flag"]
        # insert_data["verified_reason"] = json_data["verified_reason"]
        # insert_data["user_post_count"] = json_data["note_count"]
        # insert_data["following_count"] = json_data["following_count"]
        # insert_data["follower_count"] = json_data["follower_count"]
        # insert_data["user_level"] = json_data["level"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    elif select_table == 'wechat_comment':
        insert_data["platform_id"] = 1101
        insert_data["comment_id"] = json_data["comment_id"]
        insert_data["user_id"] = json_data["user_id"]
        insert_data["comment_datetime"] = json_data["comment_datetime"]
        insert_data['comment_country'] = json_data['user_country']
        insert_data["comment_province"] = json_data['user_province']
        insert_data["comment_content"] = json_data["comment"].strip()
        # insert_data["comment_like_count"] = json_data["comment_like_count"]
        # insert_data["comment_reply_count"] = json_data["comment_reply_count"]
        insert_data["comment_main_flag"] = json_data["main_id_flag"]
        insert_data["comment_main_id"] = json_data["main_comment_id"]
        insert_data["post_id"] = json_data["wechat_id"]
        insert_data["spider_datetime"] = json_data["spider_datetime"]
    else:
        sys.exit()
    if select_table in post_list:
        try:
            identify_content = (insert_data["post_content"] + insert_data['post_subject']).replace(" ", "").lower()
        except:
            identify_content = (insert_data["post_content"]).replace(" ", "").lower()
        # 1.判断是否有排除词，有这个词就直接跳过插入
        excluded_flag = check_excluded_word(identify_content.strip(), insert_data["series_id"], identify_info_df)
        if excluded_flag:
            return
        # 2.判断是否有确认词，有这个词就保持series_id，没有的话就继续检查混淆车型
        confirm_flag = check_confirm_word(identify_content.strip(), insert_data["series_id"], identify_info_df)
        if not confirm_flag:
            insert_data["series_id"] = check_confused_series(identify_content.strip(), insert_data["series_id"], identify_info_df)
        insert_data["post_keyword"] = None  # todo: 需要优化关键词的抽取逻辑
    if select_table in cmt_list:
        insert_data["comment_keyword"] = None    # todo: 需要优化关键词的抽取逻辑

    # 判断用户类型，抽取用户简介中的关键词
    feature_list = []
    type_list = []
    # 对于smart的车主和代理商，这里做一道特殊处理，专门识别是否是smart相关用户
    if select_table in user_list:
        # 检查方式1：检查昵称中是否包含某个异常类型关键词
        keyword, user_type1 = gc.speacial_identify_summmary(insert_data['user_nickname'])
        if user_type1:
            feature_list.append('昵称中包含"{}"'.format(keyword))
            type_list.append(user_type1)
        # 检查方式2：检查简介中是否包含某个异常类型关键词
        keyword, user_type2 = gc.speacial_identify_summmary(insert_data['user_summary'])
        if user_type2 and user_type1 != user_type2:
            feature_list.append('简介中包含"{}"'.format(keyword))
            type_list.append(user_type2)
        insert_data['user_feature'] = '|'.join(feature_list)
        insert_data['user_type'] = '|'.join(type_list)
        if insert_data['user_feature'] == '':
            insert_data['user_feature'] = None
        if insert_data['user_type'] == '':
            insert_data['user_type'] = None
        # 用户简介的关键词提取
        try:
            keyword_list = []
            user_summary = insert_data["user_summary"]
            keyword_out = gc.keywords_extraction(user_summary, 3)
            for word_score in keyword_out:
                keyword_list.append(word_score['word'])
            insert_data['summary_keyword'] = '|'.join(keyword_list)
        except:
            insert_data['summary_keyword'] = ''
    # 对于实时化的插入，需要直接对一些需要实时处理的字段进行插入，此处代码暂不使用
    if insert_mode == 'realtime':
        text_all = ''
        if select_table in post_list :
            if (insert_data["post_content"] is not None) and insert_data["post_content"] != '':
                text_all += insert_data["post_content"]
            if (insert_data["post_subject"] is not None) and insert_data["post_subject"] != '':
                text_all += insert_data["post_subject"]
        if select_table in cmt_list:
            if (insert_data["comment_content"] is not None) and insert_data["comment_content"] != '':
                text_all += insert_data["comment_content"]
        emo_score, emo_pn = gc.calculate_emotion_score(text_all)
        insert_data['emo_score_neg'] = round(1 - emo_score, 2)
        insert_data['emo_score_pos'] = round(emo_score, 2)
        insert_data['emo_pn'] = emo_pn
    # 写入数据库
    uf.dict2mysql(dic_connet, insert_ip, insert_data, insert_table, cover_flag)

def start_sql_insert_process(select_tbl, start_dt, end_dt, mode='all'):
    if select_tbl in post_list:
        search_sql = f'select series_id, series_id_suspected, word_confirm, word_excluded from spider_schedule_list'
        identify_info_df = uf.read_sql2df(insert_ip, dic_connet, search_sql)
    else:
        identify_info_df = pd.DataFrame()
    insert_tbl = insert_map_detail[select_tbl][0]
    print(f'\n-----当前将{select_tbl}导入{insert_tbl}中-----')
    select_ip = insert_map_detail[select_tbl][3]
    cover_flag = True
    if mode == 'all':
        res = select_sql_json(select_ip, select_tbl, start_dt, end_dt)
    elif mode == 'loss':
        res = select_sql_json4loss(select_ip, select_tbl)
    for data in tqdm(res, desc=f'当前将{select_tbl}导入{insert_tbl}中', ncols=100):
        for (k, v) in data.items():
            try:
                if np.isnan(data[k]):
                    data[k] = None
            except:
                continue
        try:
            insert_json_sql2etl(data, insert_ip, insert_tbl, select_tbl, cover_flag, identify_info_df)
        except Exception as e:
            print(e)
            error_message = f"{datetime.datetime.now()} - 错误信息: {str(e)}\n数据插入失败： {data}\n"
            with open('error.log', 'a', encoding='utf-8') as log_file:
                log_file.write(error_message)
            print("错误信息已记录到 error.log 文件中")
            print('数据插入失败：', data)

# def mysql_transmit_data(select_ip, insert_ip, select_tbl, start_datetime, end_datetime, cover_flag):
#     insert_tbl = insert_map_detail[select_tbl][0]
#     print(f'\n-----当前将{select_tbl}导入{insert_tbl}中-----')
#     res = select_sql_json(select_ip, select_tbl, start_datetime, end_datetime)
#     if len(res) == 0:
#         print('此次数据库查询无数据...')
#     else:
#         for data in tqdm(res, desc=f'当前将{select_tbl}导入{insert_tbl}中', ncols=100):
#             for (k, v) in data.items():
#                 try:
#                     if np.isnan(data[k]):
#                         data[k] = None
#                 except:
#                     continue
#             try:
#                 insert_json_sql2etl(data, insert_ip, insert_tbl, select_tbl, cover_flag)
#             except Exception as e:
#                 print(e)
#                 print('数据插入失败：', data)
