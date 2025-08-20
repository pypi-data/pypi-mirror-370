# -*- coding: utf-8 -*-
"""
jf-ext.CurrencyExt.py
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def currency_display_by_int(number):
    """
    >>> money: 金额 书面化 (千位 ,)
    :param {Int} number: 金额
    :return {String}: 金额书面化字符串
    """
    tmp = format(number, ',')
    return tmp


def currency_to_int_times_100(x):
    """
    >>> 金额 -> int * 100
    :param {Float} x:
    :returns {Integer}
    """
    if isinstance(x, float) or isinstance(x, int):
        return int(round(x * 100))
    return 0


def currency_int_to_currency_divide_100(x):
    """
    >>> int -> 金额 / 100
    :param {Int} x:
    :returns {Integer}
    """
    if isinstance(x, int):
        return int(round(x)) / 100.0
    return 0
