# -*- coding: utf-8 -*-
"""
jf-ext.SingletonExt.py
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def Singleton(cls):
    """
    >>> 单例模块 装饰器
    """
    instances = {}

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton
