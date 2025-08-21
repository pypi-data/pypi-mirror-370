# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 日期、时间工具
import re
import time
import datetime


CN_NUM = {'〇': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
          '零': '0', '壹': '1', '贰': '2', '叁': '3', '肆': '4', '伍': '5', '陆': '6', '柒': '7', '捌': '8', '玖': '9',
          '两': '2'}


def get_date_format(format_str):
    """
    获取日期
    :param format_str: "%Y-%m-%d %H:%M:%S"
    :return:
    """
    return time.strftime(format_str, time.localtime())


def get_date():
    """
    获取秒级日期
    :return: 2020-02-26 10:31:02
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_date_ms():
    """
    获取毫秒级日期
    :return: 2021-08-20 14:46:43.805594
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def get_y_m_d():
    """
    获取日期
    :return: 2020_02_26
    """
    return time.strftime("%Y_%m_%d", time.localtime())


def get_timestamp_second():
    """
    秒级时间戳
    :return: 1582684262.161325
    """
    return time.time()


def get_timestamp_ms():
    """
    毫秒级时间戳
    :return: 1582684262161
    """
    return int(round(time.time() * 1000))


def get_timestamp_ws():
    """
    微秒级时间戳
    :return: 1582684262161369
    """
    return int(round(time.time() * 1000000))


def compare_time(time1: str, time2: str):
    """
    比较两个字符型日期大小 日期格式:%Y年%m月%d日
    :param time1: 第1个时间
    :param time2: 第2个时间
    :return: 整数  <0 time1 早于 time2  ;  =0 time1 = time2 ; >0 time1 晚于 time2
    """
    def trans_cn2d(cn_str):
        return ''.join([CN_NUM[i] if i in CN_NUM else i for i in cn_str])

    if re.match(r'(\d{4}-\d{1,2}-\d{1,2})',time1):
        format_str = '%Y-%m-%d'
    elif re.match(r'(\d{4}年\d{1,2}月\d{1,2}日)',time1):
        format_str = '%Y年%m月%d日'
    elif re.match(r'(\d{4}/\d{1,2}/\d{1,2})',time1):
        format_str = '%Y/%m/%d'
    elif re.match(r'(.{4}年.{1,2}月.{1,3}日)',time1):
        format_str = 'CN年CN月CN日'
    else:
        format_str = '%Y-%m-%d'

    if format_str == 'CN年CN月CN日':
        import cn2an
        time1_cn = trans_cn2d(time1[:time1.index('年')]) \
                   + time1[time1.index('年'):time1.index('年') + 1] + \
                   str(cn2an.cn2an(time1[time1.index('年') + 1:time1.index('月')], 'normal')) \
                   + time1[time1.index('月'):time1.index('月') + 1] + \
                   str(cn2an.cn2an(time1[time1.index('月') + 1:time1.index('日')], 'normal')) \
                   + time1[time1.index('日'):time1.index('日') + 1]
        time2_cn = trans_cn2d((time2[:time2.index('年')])) \
                   + time2[time2.index('年'):time2.index('年') + 1] + \
                   str(cn2an.cn2an(time2[time2.index('年') + 1:time2.index('月')], 'normal')) \
                   + time2[time2.index('月'):time2.index('月') + 1] + \
                   str(cn2an.cn2an(time2[time2.index('月') + 1:time2.index('日')], 'normal')) \
                   + time2[time2.index('日'):time2.index('日') + 1]
        # print(time1_cn,time2_cn)
        s_time = time.mktime(time.strptime(time1_cn, '%Y年%m月%d日'))
        e_time = time.mktime(time.strptime(time2_cn, '%Y年%m月%d日'))
        if int(s_time) == int(e_time):
            return 1
        return int(s_time) - int(e_time)

    s_time = time.mktime(time.strptime(time1, format_str))
    e_time = time.mktime(time.strptime(time2, format_str))
    # print('s_time is:', s_time)
    # print('e_time is:', e_time)
    if int(s_time) == int(e_time):
        return 1
    return int(s_time) - int(e_time)


if __name__ == '__main__':
    print(compare_time('2019年02月03日', '2019年02月04日'))
    print(compare_time('二0一6年一月十日', '2〇1七年七月十七日'))
    print(compare_time('二〇一六年一月十日', '二〇一七年七月十七日'))
    print(compare_time('2021年12月31日', '2022年12月31日'))
    print(compare_time('2021-12-31', '2021-12-19'))
    print(compare_time('2021/12/31', '2021/12/19'))
    print(get_date_format("%Y%m%d%H%M%S"))
    print(get_date())
    print(get_date_ms())
    print(get_y_m_d())
    print(get_timestamp_second())
    print(get_timestamp_second())
    print(get_timestamp_ms())
    print(get_timestamp_ms())
    print(get_timestamp_ws())
    print(get_timestamp_ws())
    pass
