# -*- coding: utf-8 -*-
"""
jfExt.binConversion.py
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def dec_to_any_base(num, base):  # Maximum base - 36
    """
    >>> 进制转换
    :param {Int} num: 原始数字
    :param {Int} base: 目标进制
    :return {String}: 转换后数值
    """
    base_num = ""
    while num > 0:
        dig = int(num % base)
        if dig < 10:
            base_num += str(dig)
        else:
            base_num += chr(ord('A') + dig - 10)  # Using uppercase letters
        num //= base
    base_num = base_num[::-1]  # To reverse the string
    return base_num


if __name__ == '__main__':
    tmp = dec_to_any_base(100000000, 21)
    print(tmp, type(tmp))
    # tmp = int(tmp)
    # print(tmp, type(tmp))
