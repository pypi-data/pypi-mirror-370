# -*- coding: utf-8 -*-
"""
jf-ext.PrintExt.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from icecream import ic  # noqa:


class bcolors:
    """
    >>> 打印颜色
    """
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

    HLERROR   = "\33[41m"
    HLWARNING = "\33[43m"
    HLGREEN   = "\33[42m"
    HLBLUE    = "\33[44m"
    HLPINK    = "\33[45m"


def print_title(title, console=False):
    """
    >>> 打印标题行
    :param {String} title:
    """
    print("")
    print("")
    if not console:
        print(get_color_text_by_style('*' * 50, 0))
        print(get_color_text_by_style(title, 0))
        print(get_color_text_by_style('*' * 50, 0))
    else:
        print('👺' * 30)
        print("👺 {}".format(title))
        print('👺' * 30)


def print_sub_title(sub_title, console=False):
    """
    >>> 打印小标题行
    :param {String} sub_title:
    """
    if not console:
        print(get_color_text_by_style('-' * 25, 1))
        print(get_color_text_by_style(sub_title, 1))
        print(get_color_text_by_style('-' * 25, 1))
    else:
        print('👽' * 20)
        print("👽 {}".format(sub_title))
        print('👽' * 20)


def get_color_text_by_style(text, style):
    """
    >>> 提供带颜色的文字 by style
    :param {Integer} style:
        - 0: 红色字体
    :return {String}:
    """
    if style == 0:
        return "\033[31m{}\033[0m".format(text)
    if style == 1:
        return "\033[32m{}\033[0m".format(text)


def get_color_text_by_type(text, color_type):
    """
    >>> 提供带颜色的文字 by type
    :param {num} color_type:
    :return {String}:
    """
    return color_type + text + bcolors.ENDC


def print_processing(cur_idx, max_idx):
    """
    >>> 打印当前进度
    :param {Integer} cur_idx: 当前进度
    :param {Integer} max_idx: 最大进度
    """
    percentage = int(float(cur_idx * 1.0 / max_idx) * 10000) / 100.0
    msg = "[{}%] {} / {}".format(percentage, cur_idx, max_idx)
    print(get_color_text_by_style(msg, 1))
    print(get_color_text_by_style('-' * 25, 1))
