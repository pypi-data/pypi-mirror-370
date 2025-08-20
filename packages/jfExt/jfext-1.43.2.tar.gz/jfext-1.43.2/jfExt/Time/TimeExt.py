# -*- coding: utf-8 -*-
"""
jf-ext.Time.TimeExt.py
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import time
import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def time_now_timestamp():
    """
    >>> 时间: 当前时间戳
    :return {Int}: 13位时间戳
    """
    millis = int(round(time.time()))
    return millis


def time_now_string():
    """
    >>> 获取当前时间 String
    :return {String}: the time of now (String)
    """
    now = time.time()
    return time_timestamp_to_string(now)


def time_time_to_string(time_data):
    """
    >>> 时间转换 String
    :return {String}: the time (String)
    """
    return time.strftime(TIME_FORMAT, time_data)


def time_time_to_date(time_data):
    """
    >>> 时间型 -> 日期形
    """
    return datetime.datetime.fromtimestamp(time.mktime(time_data))


def time_time_to_timestamp(time_data):
    """
    >>> 时间型 -> 时间戳
    :return {Int}: 13位时间戳
    """
    millis = int(time.mktime(time_data) * 1000)
    return millis


def time_string_to_date(time_string):
    """
    >>> 时间字符串型 -> 日期形
    """
    return time_time_to_date(time_string_to_time(time_string))


def time_string_to_time(time_string):
    """
    >>> 时间字符串型 -> 时间形
    """
    try:
        return time.strptime(time_string, TIME_FORMAT)
    except Exception:
        pass
    try:
        return time.strptime(time_string, DATE_FORMAT)
    except Exception:
        pass


def time_timestamp_to_string(ts):
    """
    >>> 时间: 时间戳转换时间字符串
    :param {Int} ts: 13 / 10 位时间戳
    :return {String}: 时间字符串
    """
    if 13 == len(str(ts)):
        ts = ts / 1000.0
    time_local = time.localtime(ts)
    time_str = time.strftime(TIME_FORMAT, time_local)
    return time_str


def time_second_before_now_ts(second):
    """
    >>> 时间: 几秒前 时间字符串
    :param {Int} second: 之前几秒
    :return {String}: 时间字符串
    """
    return int(datetime.datetime.timestamp((datetime.datetime.now() - datetime.timedelta(seconds=second))) * 1000)


def time_minute_before_now_ts(minute):
    """
    >>> 时间: 几分钟前 时间字符串
    :param {Int} minute: 之前几分钟
    :return {String}: 时间字符串
    """
    return int(datetime.datetime.timestamp((datetime.datetime.now() - datetime.timedelta(minutes=minute))) * 1000)


def time_hour_before_now_ts(hour):
    """
    >>> 时间: 几小时前 时间字符串
    :param {Int} minute: 之前几小时
    :return {String}: 时间字符串
    """
    return int(datetime.datetime.timestamp((datetime.datetime.now() - datetime.timedelta(hours=hour))) * 1000)


def time_second_before_now_string(second):
    """
    >>> 时间: 几秒前 时间字符串
    :param {Int} second: 之前几秒
    :return {String}: 时间字符串
    """
    return (datetime.datetime.now() - datetime.timedelta(seconds=second)).strftime(TIME_FORMAT)


def time_minute_before_now_string(minute):
    """
    >>> 时间: 几分钟前 时间字符串
    :param {Int} minute: 之前几分钟
    :return {String}: 时间字符串
    """
    return (datetime.datetime.now() - datetime.timedelta(minutes=minute)).strftime(TIME_FORMAT)


def time_hour_before_now_string(hour):
    """
    >>> 时间: 几小时前 时间字符串
    :param {Int} minute: 之前几小时
    :return {String}: 时间字符串
    """
    return (datetime.datetime.now() - datetime.timedelta(hours=hour)).strftime(TIME_FORMAT)


def time_diff_time_by_time_string(time_str_a, time_str_b):
    """
    >>> 时间: 时间差
    :param {String} time_str_a: 时间字符串A (早)
    :param {String} time_str_b: 时间字符串B (晚)
    :return {[Int, Int, Int, Int]}: [day, hour, minute, second]
    """
    date_a = datetime.datetime.strptime(time_str_a, "%Y-%m-%d %H:%M:%S")
    date_b = datetime.datetime.strptime(time_str_b, "%Y-%m-%d %H:%M:%S")
    diff_duration = date_b - date_a
    day = diff_duration.days
    hour = int(diff_duration.seconds / 3600)
    minute = int((diff_duration.seconds % 3600) / 60)
    second = int(diff_duration.seconds % 60)
    return [day, hour, minute, second]
