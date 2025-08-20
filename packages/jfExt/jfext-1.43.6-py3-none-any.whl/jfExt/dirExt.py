# -*- coding: utf-8 -*-
"""
jfExt.dirExt.py
~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import os


def dir_tar_current_path():
    """
    >>> 当前目录下所有子文件夹打包成tar
    """
    paths = os.listdir('./')
    for path in paths:
        if os.path.isdir(path) and (len(path) > 0 and path[0] != '.'):
            cmd = 'tar cvf "{}.tar" "{}"'.format(path, path)
            print(os.system(cmd))


def dir_untar_current_path(force=True):
    """
    >>> 当前目录下所有tar包解压
    :param {Boolean} force: 是否强制覆盖 Default: False
    """
    paths = os.listdir('./')
    for path in paths:
        if not os.path.isdir(path) and (len(path) > 0 and path[-4:] == '.tar'):
            # 判断是否为非强制模式
            if not force:
                # 判断是否含有解压后文件夹
                if path[:-4] in paths and os.path.isdir(path[:-4]):
                    continue
                print(path)
            cmd = 'tar xvf "{}"'.format(path)
            print(os.system(cmd))


if __name__ == '__main__':
    dir_tar_current_path()
