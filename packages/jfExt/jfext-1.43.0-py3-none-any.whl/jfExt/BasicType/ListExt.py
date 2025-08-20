# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.ListExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def list_to_string(obj):
    """
    >>> list -> string
    :param {List} obj:
    :return {String}:
    """
    if isinstance(obj, list):
        return str(obj)
    return obj


def list_diff(listA, listB):
    """
    >>> list比较
    :param {List} listA:
    :param {List} listB:
    :return {Boolean}: 是否相同
    """
    listA = sorted(listA)
    listB = sorted(listB)
    if listA == listB:
        return False
    return True
