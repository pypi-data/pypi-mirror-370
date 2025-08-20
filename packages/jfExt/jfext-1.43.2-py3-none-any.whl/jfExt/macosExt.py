# -*- coding: utf-8 -*-
"""
jfExt.macosExt.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2023 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from icecream import ic # noqa

import os

def macos_notify(title, message):
    """
    >>> macos通知
    """
    os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')


if __name__ == '__main__':
    macos_notify("脚本提示", "任务执行完毕！")
