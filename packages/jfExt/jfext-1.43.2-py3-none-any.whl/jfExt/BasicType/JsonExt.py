# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.JsonExit.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from datetime import datetime, date


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def json_flatten_extend(original, extend, mapping={}):
    """
    >>> json字典拍平拓展
    """
    if not isinstance(original, dict) or not isinstance(extend, dict) or not isinstance(mapping, dict):
        return original
    for key in extend.keys():
        # mapping 字段
        if key in mapping.keys():
            new_key = mapping[key]
            original[new_key] = extend[key]
            continue
        # 插入非冲突key
        if key not in original.keys():
            original[key] = extend[key]
            continue
