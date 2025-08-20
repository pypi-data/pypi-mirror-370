# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.StringExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import re
import random
import difflib
from check_digit_EAN13.check_digit import get_check_digit


def string_rm_blank(string):
    """
    >>> 替换字符串中空格 -> _
    :param {String} string: 带空格字符串
    :return {String}: 替换后字符串
    """
    return string.replace(" ", "_", 1000)


def string_rm_html_tag(text):
    """
    >>> 替换字符串中 html标签
    :param {String} text:
    :return {String}:
    """
    pattern = re.compile(r'<[^>]+>', re.S)
    res = pattern.sub('', text)
    return res


def string_remove_non_ascii(text):
    """
    >>> 替换字符串中 非ASCII 字符串
    :param {String} text:
    :return {String}:
    """
    return ''.join([i if ord(i) < 128 else " " for i in text])


def string_key_filter(s):
    """
    >>> 过滤wordpress字符中&编码问题
    """
    if isinstance(s, str):
        s = str(s).replace('&#8211;', '-', 100)
        s = str(s).replace('&amp;', '&', 100)
        s = str(s).replace('，', ',', 100)
        s = str(s).replace('\\', ',', 100)
    return s


def string_random(str_len):
    """
    随机生成指定长度的字符串
    :param {Int} str_len: 指定长度
    :return {string}:
    """
    res = ''
    for i in range(str_len):
        res += chr(int(random.random() * 100) % 26 + 65)

    return res


def string_similar(s1, s2):
    """
    >>> 字符串相似度计算
    :param {String} s1: 字符串1
    :param {String} s2: 字符串s
    :return {}: 相似度
    """
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def string_omit_middle(str, keep_len=5):
    """
    >>> 字符串省略中间部分
    :param {String} str: 待处理字符串
    :param {Integer} keep_len: 前后保留长度
    :return {String}: 处理后字符串
    """
    # 判断保留长度是否是否大于字符串本身, 并返回
    if keep_len >= (len(str) - 4) / 2:
        return str
    start_part = str[:keep_len]
    end_part = str[-keep_len:]
    res = "{}...{}".format(start_part, end_part)
    return res


def string_gen_ean13(country_code="789", company_code="0000", product_code="00000"):
    """
    >>> 字符串 - 生成EAN13
    :param {String} country_code: 国家代码(3位)
    :param {String} company_code: 公司代码(4位)
    :param {String} product_code: 产品代码(5位)
    :return {String}
    """
    new_barcode = "%s%04s%05s" % (country_code, company_code, product_code)
    if len(new_barcode) != 12:
        return ""
    if not new_barcode.isdigit():
        return ""
    actual_barcode_number = get_check_digit(new_barcode)
    return actual_barcode_number


def string_check_ean13(barcode):
    """
    >>> 字符串 - 检测EAN13
    :param {String} barcode: 原始barcode
    :return {String}
    """
    if len(barcode) != 12 and len(barcode) != 13:
        return barcode
    if not barcode.isdigit():
        return barcode
    actual_barcode_number = get_check_digit(barcode)
    return actual_barcode_number


def string_upper_each_word(content):
    """
    >>> 字符串 - 大写所有单词
    """
    while ("  " in content):
        content = content.replace("  ", " ", 100)
    title_en_words = content.split(" ")

    new_title_en_words = []
    for i in title_en_words:
        tmp = i
        if i[0].isalpha():
            tmp = "{}{}".format(i[0].upper(), i[1:])
        new_title_en_words.append(tmp)
    new_title_en = " ".join(new_title_en_words)
    return new_title_en


if __name__ == '__main__':
    print(string_gen_ean13('687', '1234', '12341'))
    print(string_check_ean13("7890005790533"))
    print(string_upper_each_word("火漆蜡粒玻璃瓶装 Fire paint wax particles glass bottle 30*70 30ml"))
