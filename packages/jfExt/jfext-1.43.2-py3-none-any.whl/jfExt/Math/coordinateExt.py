# -*- coding: utf-8 -*-
"""
jfExt.coordinateExt.py
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import math


def coord_calc_distance(coord_a, coord_b):
    """
    >>> 计算坐标间距离
    :param {Tuple} a: 坐标A (x, y)
    :param {Tuple} b: 坐标B (x, y)
    :return {Float}: 两点间距离
    """
    dis = math.sqrt(pow((coord_a[0] - coord_b[0]), 2) + pow((coord_a[1] - coord_b[1]), 2))
    return dis


def coord_rotate(coord, degree):
    """
    >>> 坐标旋转
    :param {Tuple} coord: 坐标
    :param {} degree: 旋转角度
    :param {Tuple}: 旋转后坐标
    """
    x = coord[0]
    y = coord[1]
    new_x = int(x * math.cos(degree) + y * math.sin(degree))
    new_y = int(y * math.cos(degree) - x * math.sin(degree))
    return (new_x, new_y)


if __name__ == '__main__':
    print(coord_calc_distance((300, 0), (0, 300)))
    print(coord_calc_distance((1, 0), (0, 1)))
