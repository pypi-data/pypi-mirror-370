# -*- coding: utf-8 -*-
"""
jfExt.OrderExt.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import random
from .Time.TimeExt import *


def order_gen_order_reference(order_type, date_string=None):
    """
    >>> order类: 生成订单 reference
    :param {String} order_type: 订单类型
    :param {String} date_string: 时间字符串 (default: None, 用当前时间)
    """
    if not date_string:
        date_string = time_now_string()
    date_string = date_string.replace("-", "", 10)
    date_string = date_string.replace(" ", "-", 10)
    date_string = date_string.replace(":", "", 10)
    random_id = random.randint(100, 999)
    order_reference = "{}-{}-{}".format(order_type, date_string, random_id)
    return order_reference
