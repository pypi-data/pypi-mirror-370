# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.FloatExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2018 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def float_to_precision(x):
    """
    >>> 指定float精度
    :param {Float} x:
    :returns {Float}
    """
    if isinstance(x, float) or isinstance(x, int):
        return float('%0.2f' % x)
    else:
        return None
