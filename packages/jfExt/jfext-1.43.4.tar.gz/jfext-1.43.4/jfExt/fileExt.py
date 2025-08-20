# -*- coding: utf-8 -*-
"""
jfExt.fileExt.py
~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from icecream import ic # noqa
import xlwt
import os
import time
import xlsxwriter
import requests
from io import BytesIO
from PIL import Image
import hashlib
from jfExt.EncryptExt import generate_md5

# pragma mark - Private
# --------------------------------------------------------------------------------
def TimeStampToTime(timestamp):
    '''
    >>> 把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12
    '''
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


# pragma mark - Public
# --------------------------------------------------------------------------------
def file_get_file_size(file_path):
    '''
    >>> 获取文件的大小,结果保留两位小数, 单位为MB
    '''
    file_path = file_path.encode('utf8')
    fsize = os.path.getsize(file_path)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


def file_get_file_accesstime(file_path):
    '''
    >>> 获取文件的访问时间
    '''
    file_path = file_path.encode('utf8')
    t = os.path.getatime(file_path)
    return TimeStampToTime(t)


def file_get_file_createtime(file_path):
    '''
    >>> 获取文件的创建时间
    '''
    file_path = file_path.encode('utf8')
    t = os.path.getctime(file_path)
    return TimeStampToTime(t)


def file_get_file_modifytime(file_path):
    '''
    >>> 获取文件的修改时间
    '''
    file_path = file_path.encode('utf8')
    t = os.path.getmtime(file_path)
    return TimeStampToTime(t)


def file_get_file_md5(file_path):
    """
    计算文件的md5
    :param file_name:
    :return:
    """
    m = hashlib.md5()       # 创建md5对象
    with open(file_path, 'rb') as f_obj:
        while True:
            data = f_obj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象
    return m.hexdigest()    # 返回md5对象


# pragma mark - EXCEL
# --------------------------------------------------------------------------------
def excel_gen_by_dict(file_path, titles, data_dict):
    """
    >>> excel导出到文件
    :param {String} file_path: 目标文件路径
    :param {List} titles: 标题列表
    :param {Dictionary} data_dict: 数据
    :return {String}: 保存文件的路径
    """
    workbook = xlwt.Workbook(encoding='utf-8')
    booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
    t = 1
    for i in range(len(titles)):
        title = titles[i]
        booksheet.write(0, i, title)
    for product in data_dict:
        for i in range(len(titles)):
            title = titles[i]
            value = product.get(title, '')
            if isinstance(value, dict) or isinstance(value, list):
                continue
            booksheet.write(t, i, value)
        t += 1
    workbook.save(file_path)
    return file_path

def excel_gen_by_dict_with_sub_dict(file_path, titles, data_dict):
    """
    >>> excel导出到文件
    :param {String} file_path: 目标文件路径
    :param {List} titles: 标题列表
    :param {Dictionary} data_dict: 数据
    :return {String}: 保存文件的路径
    """
    workbook = xlwt.Workbook(encoding='utf-8')
    booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
    t = 1
    for i in range(len(titles)):
        title = titles[i]
        booksheet.write(0, i, title)
    for product in data_dict:
        titles_hash = set()
        for key in product.keys():
            values = product[key]
            if isinstance(values, list):
                continue
            if isinstance(values, dict):
                for sub_key in values.keys():
                    if sub_key in titles:
                        idx = titles.index(sub_key)
                        sub_values = values[sub_key]
                        if isinstance(sub_values, list) or isinstance(sub_values, dict):
                            continue
                        if sub_key in titles_hash:
                            continue
                        titles_hash.add(sub_key)
                        booksheet.write(t, idx, sub_values)
            if key in titles:
                idx = titles.index(key)
                if key in titles_hash:
                    continue
                titles_hash.add(key)
                booksheet.write(t, idx, values)
        t += 1
    workbook.save(file_path)
    return file_path


def excel_gen_by_dict_with_image(file_path, titles, data_list, image_columns=[], image_size=100, tmp_path=None):
    """
    >>> excel导出到文件 支持图片
    : param {String} file_path: 目标文件路径
    : param {List} titles: 标题列表
    : param {List} data_list: 数据
    : param {List} image_columns: 图片列
    : param {Int} image_size: 图片尺寸
    : return {String}: 保存文件的路径
    """
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    has_image = False
    for i in range(len(titles)):
        title = titles[i]
        # 如果是图片列,设置宽度为 image_size
        if title in image_columns:
            # 该处为字符宽度, 字符宽度 = (像素数 - 5) / 7
            worksheet.set_column(i, i, (image_size - 5) / 7)
            has_image = True
        worksheet.write(0, i, title)
    t = 1
    for product in data_list:
        for i in range(len(titles)):
            title = titles[i]
            value = product.get(title, '')
            # 如果有图片列
            if has_image:
                worksheet.set_row(t, image_size)
            if isinstance(value, dict) or isinstance(value, list):
                continue
            if title in image_columns:
                try:
                    # 获取文件名和扩展名
                    file_name, file_extension = os.path.splitext(os.path.basename(value))
                    tmp_image_file = os.path.join(tmp_path, "{}{}".format(file_name, file_extension))
                    # 如果本地缓存存在读取缓存
                    if not os.path.exists(tmp_image_file):
                        response = requests.get(value)
                        image_data = None
                        if response.status_code == 200:
                            image_data = BytesIO(response.content)
                            # 获取图片尺寸
                            img = Image.open(image_data)
                            original_width, original_height = img.size
                            # 计算图片缩放比例
                            x_scale = image_size / original_width
                            y_scale = image_size / original_height
                            # 重置内存数据游标以便再次读取图片
                            image_data.seek(0)
                        worksheet.insert_image(t, i, 'image.jpg', {'image_data': image_data, 'x_scale': x_scale, 'y_scale': y_scale})
                        # 写入临时文件
                        if tmp_path:
                            # 如果图像是调色板模式（P），则转换为 RGB 模式
                            if img.mode == 'P':
                                img = img.convert('RGB')
                            # 如果图像是 RGBA 模式，则转换为 RGB 模式
                            if img.mode == 'RGBA':
                                img = img.convert('RGB')
                            # 图片压缩为 256 * 256
                            img = img.resize((256, 256), Image.Resampling.LANCZOS)
                            img.save(tmp_image_file, quality=70)
                    else:
                        # 获取图片尺寸
                        img = Image.open(tmp_image_file)
                        original_width, original_height = img.size
                        # 计算图片缩放比例
                        x_scale = image_size / original_width
                        y_scale = image_size / original_height
                        # 重置内存数据游标以便再次读取图片
                        worksheet.insert_image(t, i, tmp_image_file, {'x_scale': x_scale, 'y_scale': y_scale})
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            else:
                worksheet.write(t, i, value)
        t += 1
    workbook.close()
    return file_path
