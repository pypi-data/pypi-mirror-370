# -*- coding: utf-8 -*-
"""
jf-ext.GeoExt.py
~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from math import radians, cos, sin, asin, sqrt


def geo_distance(lng1, lat1, lng2, lat2):
    """
    >>> 经纬度距离计算
    #公式计算两点间距离(km)
    :param {Float} lng1: 坐标1 经度
    :param {Float} lat1: 坐标1 维度
    :param {Float} lng2: 坐标2 经度
    :param {Float} lat2: 坐标2 维度
    """
    # 经纬度转换成弧度
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000   # 地球平均半径, 6371km
    distance = round(distance / 1000, 3)
    return distance
