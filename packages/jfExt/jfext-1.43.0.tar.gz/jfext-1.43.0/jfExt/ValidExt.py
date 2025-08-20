# -*- coding: utf-8 -*-
"""
jf-ext.ValidExt.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import re


def valid_url(url):
    """
    >>> url检测
    """
    match = re.match(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", url)
    if match:
        return True
    else:
        return False


def valid_ip(ip):
    """
    >>> ip有效性验证
    :param {String} ip:
    :return {Bool}:
    """
    ip_exp = re.compile(
        '^(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.'
        '(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.'
        '(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.'
        '(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])$')
    if ip_exp.match(ip):
        return True
    else:
        return False


def valid_email(email):
    """
    >>> 邮箱有效性验证
    :param {String} email:
    :return {Boolean}
    """
    if len(email) > 7:
        if re.match(
                "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                email) is not None:
            return True
    return False


def valid_mobile(mobile):
    """
    >>> 手机号码有效性验证
    :param {String} mobile:
    :return {Bool}
    """
    mobile_exp = re.compile(
        "^(13[0-9]|14[01345789]|15[0-9]|17[012356789]|18[0-9])[0-9]{8}$")
    if mobile_exp.match(mobile):
        return True
    else:
        return False


def valid_chinese_identify_card(id_number):
    """
    >>> 中国身份证号码验证
    :param {String} id_number:
    :return: {Boolean}
    """
    if type(id_number) is int:
        id_number = str(id_number)
    if type(id_number) is str:
        try:
            int(id_number[:17])
        except ValueError:
            return False
    regex = r'^(^[1-9]\d{7}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}$)|' \
            r'(^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])((\d{4})|\d{3}[Xx])$)$'
    if len(re.findall(regex, id_number)) == 0:
        return False
    if len(id_number) == 15:
        return True
    if len(id_number) == 18:
        w_i = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        t_i = ['1', '0', 'x', '9', '8', '7', '6', '5', '4', '3', '2']
        sum_c = 0
        code = id_number[:17]
        for i in range(17):
            sum_c += int(code[i]) * w_i[i]
        if id_number[17:].lower() == t_i[sum_c % 11]:
            return True
    return False
