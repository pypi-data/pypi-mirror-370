# -*- coding: utf-8 -*-
"""
jfExt.ImageExt.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import tempfile
import numpy as np
from fake_useragent import UserAgent
# from PIL import Image
# from PIL import ImageChops
import requests
from jfExt.fileExt import *
from jfExt.BasicType.StringExt import string_random
from jfExt.ValidExt import *


# pragma mark - define
# --------------------------------------------------------------------------------
r = requests.session()
ua = UserAgent()
headers = {
    'user-agent': ua.chrome
}


def image_to_square(in_file, out_file, size=1024, background_color=(255, 255, 255)):
    """
    >>> 图片转换成正方形
    :param {String} in_file: 图片读取地址
    :param {String} out_file: 图片输出地址
    :param {Int} size: 图片长度/宽度
    :param {(Int, Int, Int)} background_color: 背景颜色
    """
    from PIL import Image  # noqa
    image = Image.open(in_file)
    image = image.convert('RGB')
    w, h = image.size
    # 创建背景图，颜色值为127
    background = Image.new('RGB', size=(max(w, h), max(w, h)), color=(255, 255, 255))
    # 一侧需要填充的长度
    length = int(abs(w - h) // 2)
    # 粘贴的位置
    box = (length, 0) if w < h else (0, length)
    background.paste(image, box)
    # 缩放
    image_data = background.resize((1024, 1024))
    # background.show()
    image_data.save(out_file)


def image_detect_image_border(in_file, direction, color_threshold=20, border_threshold=0.05):
    """
    >>> 图片检测边框
    :param {String} in_file: 图片读取地址
    :param {String} direction: 检测方向
    :param {Int} threshold: 阈值
    :returns {Int}: 边框宽度
    """
    from PIL import Image  # noqa
    # 打开图像
    image = Image.open(in_file)
    # 获取图像尺寸
    image_width, image_height = image.size
    # 获取图像像素数据
    pixels = np.array(image)

    def scan_pixels(start, step, max_value, axis, background_color):
        border_width = 0
        for i in range(start, max_value, step):
            if axis == "horizontal":
                pixels_list = pixels[:, i, :]
            else:
                pixels_list = pixels[i, :, :]
            # 计算每个像素与背景颜色的颜色差异
            diffs = np.linalg.norm(pixels_list - background_color, axis=1)
            # 计算颜色差异大于阈值的像素数量
            different_pixels_count = np.sum(diffs > color_threshold)
            # 如果不同像素的比例小于边框阈值，则认为是边框
            if (different_pixels_count / len(pixels_list)) < border_threshold:
                border_width += 1
            else:
                break
        return border_width

    # 选择背景颜色（假设背景颜色为左上角像素）
    background_color = pixels[0, 0]
    if direction == "horizontal":
        left_border_width = scan_pixels(0, 1, image_width, "horizontal", background_color)
        right_border_width = scan_pixels(image_width - 1, -1, -1, "horizontal", background_color)
        return left_border_width, right_border_width
    elif direction == "vertical":
        top_border_height = scan_pixels(0, 1, image_height, "vertical", background_color)
        bottom_border_height = scan_pixels(image_height - 1, -1, -1, "vertical", background_color)
        return top_border_height, bottom_border_height


def image_fit_border_ratio(in_file, out_file, target_ratio=0.8, target_size=(1024, 1024), background_color=(255, 255, 255)):
    """
    >>> 图片适配边框比例
    :param {String} in_file: 图片读取地址
    :param {String} out_file: 图片输出地址
    :param {(Int, Int)} target_size: 目标尺寸
    :param {(Int, Int, Int)} background_color: 背景颜色
    """
    from PIL import Image  # noqa
    img = Image.open(in_file)
    cur_ratio = image_calc_border_ratio(in_file, background_color)
    if cur_ratio < target_ratio:
        print(cur_ratio, target_ratio, "主物体 -> big")
        # 主物体进行放大
        width, height = img.size
        percent = cur_ratio / target_ratio
        crop_width = int(width * percent)
        crop_height = int(height * percent)
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        img = img.crop((left, top, right, bottom))
        # 缩放到指定尺寸
        # 判断Pillow版本并选择合适的滤波器
        if hasattr(Image, 'Resampling'):
            # Pillow 10.0.0及以上版本
            img = img.resize(target_size, Image.LANCZOS)
        else:
            # Pillow 10.0.0以下版本
            img = img.resize(target_size, Image.ANTIALIAS)
        # 保存图片
        img.save(out_file)
    if cur_ratio > target_ratio:
        print(cur_ratio, target_ratio, "主物体 -> small")
        # 主物体进行缩小
        img = Image.open(in_file)
        # 计算目标宽高
        target_width = int(img.height * cur_ratio / target_ratio)
        # 创建目标大小的白色背景图（正方形）
        target_img = Image.new('RGB', (target_width, target_width), (255, 255, 255))
        # 将原图片粘贴到目标图中心
        offset = ((target_width - img.width) // 2, (target_width - img.height) // 2)
        target_img.paste(img, offset)
        target_img.save(out_file)
    print(f"已处理文件：{out_file}")


def image_calc_border_ratio(image_path, background_color=(255, 255, 255), threshold=30):
    """
    >>> 图片边框比例
    :param {String} image_path: 图片地址
    :param {(Int, Int, Int)} background_color: 背景颜色
    :param {Int} threshold: 阈值
    :returns {Float}: 边框比例
    """
    from PIL import Image  # noqa
    img = Image.open(image_path)
    width, height = img.size
    img_array = np.array(img)
    mask = np.sum(np.abs(img_array - background_color), axis=2) > threshold
    nonzero_indices = np.nonzero(mask)
    min_x, min_y = np.min(nonzero_indices[1]), np.min(nonzero_indices[0])
    max_x, max_y = np.max(nonzero_indices[1]), np.max(nonzero_indices[0])
    border_width = max_x - min_x + 1
    border_height = max_y - min_y + 1
    border_ratio = max(border_width, border_height) / max(width, height)
    return border_ratio


def image_center_object(in_file, out_file):
    """
    >>> 图片居中
    :param {String} in_file: 图片读取地址
    :param {String} out_file: 图片输出地址
    :param {(Int, Int)} horizontal_border_widths: 水平边框宽度
    :param {(Int, Int)} vertical_border_heights: 垂直边框高度
    """
    from PIL import Image  # noqa
    # 打开图像
    image = Image.open(in_file)
    # 获取图像尺寸
    image_width, image_height = image.size
    # 计算水平边框款对
    horizontal_border_widths = image_detect_image_border(in_file, "horizontal")
    # 计算垂直边框高度
    vertical_border_heights = image_detect_image_border(in_file, "vertical")
    # 计算水平方向上图片应该移动的像素值
    move_pixels_horizontal = (horizontal_border_widths[1] - horizontal_border_widths[0]) // 2
    # 计算垂直方向上图片应该移动的像素值
    move_pixels_vertical = (vertical_border_heights[1] - vertical_border_heights[0]) // 2
    print("{}, {}".format(move_pixels_horizontal, move_pixels_vertical))
    # 创建一个新的图像，大小与原图相同
    centered_image = Image.new('RGB', (image_width, image_height), (255, 255, 255))
    # 将原图粘贴到新图像上，使其在水平和垂直方向上都居中
    centered_image.paste(image, (move_pixels_horizontal, move_pixels_vertical))
    # 保存新图像
    centered_image.save(out_file)


def image_resize_width(in_file, out_file, new_width=1024):
    """
    >>> 图片修改尺寸, 固定宽度
    :param {String} in_file: 图片读取地址
    :param {String} out_file: 图片输出地址
    :param {Int} width: 图片宽度
    """
    from PIL import Image  # noqa
    image_data = Image.open(in_file)
    width, height = image_data.size
    rate = new_width / 1.0 / width
    new_height = rate * height
    new_width = int(new_width)
    new_height = int(new_height)
    new_image_data = image_data.resize((new_width, new_height))
    new_image_data.save(out_file)


def image_vertical_concat(image_paths, out_path, out_size_width=None, save_quality=50):
    """
    >>> 进行图片的复制拼接
    :param {[String]} image_paths: 图片路径数组
    :param {String} out_path: 图片输出路径
    :param {Int} out_size_width: 输出图片统一宽度
    :param {Int} save_quality: 图片输出质量(0~100) default 50
    """
    from PIL import Image  # noqa
    image_files = []
    out_size_height = 0
    max_size_width = 0
    # 读取所有用于拼接的图片
    for image_path in image_paths:
        image = Image.open(image_path)
        image_files.append(image)
        image_width, image_height = image.size
        if image_width > max_size_width:
            max_size_width = image_width
    if out_size_width is None:
        out_size_width = max_size_width
    # 计算输出图片高度
    out_size_height = 0
    for image in image_files:
        image_width, image_height = image.size
        rate = out_size_width / 1.0 / image_width
        new_height = rate * image_height
        new_height = int(new_height)
        out_size_height += new_height
    # 创建成品图的画布
    target_image = Image.new('RGB', (out_size_width, out_size_height))
    # 对图片进行逐行拼接
    start_y = 0
    for image in image_files:
        # 图片resize
        image_width, image_height = image.size
        rate = out_size_width / 1.0 / image_width
        new_height = rate * image_height
        new_width = int(out_size_width)
        new_height = int(new_height)
        image = image.resize((new_width, new_height))
        target_image.paste(image, (0, start_y))
        start_y += new_height
    # 成品图保存
    target_image.save(out_path, quality=save_quality)


def image_diff(image_a_url, image_b_url):
    """
    >>> 网络图片比较是否相同
    :param {String} image_a_url: 图片A url
    :param {String} image_b_url: 图片B url
    :return {Boolean}: 图片是否相同
    """
    image_a_md5 = string_random(32)
    image_b_md5 = string_random(32)
    # 读取image_a
    with tempfile.NamedTemporaryFile() as fp:
        try:
            if valid_url(image_a_url):
                res = r.get(image_a_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_a_md5 = file_get_file_md5(fp.name)
        except Exception:
            import traceback
            traceback.print_exc()
            pass
    # 读取image_b
    with tempfile.NamedTemporaryFile(suffix=".png") as fp:
        try:
            if valid_url(image_b_url):
                res = r.get(image_b_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_b_md5 = file_get_file_md5(fp.name)
        except Exception:
            pass
    if image_a_md5 != image_b_md5:
        return True
    return False


def image_md5(image_url):
    """
    >>> 网络图片比较是否相同
    :param {String} image_url: 图片 url
    :return {String}: 图片md5
    """
    image_md5 = string_random(32)
    # 读取image_a
    with tempfile.NamedTemporaryFile() as fp:
        try:
            if valid_url(image_url):
                res = r.get(image_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_md5 = file_get_file_md5(fp.name)
        except Exception:
            import traceback
            traceback.print_exc()
            pass
    return image_md5


def image_url_exist(image_url):
    """
    >>> 网络图片是否存在
    :param {String} image_url:
    :return {Boolean}: 网络图片是否存在
    """
    if valid_url(image_url):
        res = r.get(image_url, timeout=2, headers=headers)
        if res.status_code == 200:
            return True
    return False


def image_download(image_url, file_path):
    """
    >>> 网络图片下载
    :param {String}: image_url:
    :param {String} file_path:
    """
    if valid_url(image_url):
        with open(file_path, 'wb') as fp:
            res = r.get(image_url, timeout=5, headers=headers)
            if res.status_code == 200:
                fp.write(res.content)
            return res.status_code
    return 999


# pragma mark - Private
# --------------------------------------------------------------------------------
def color_similarity(color1, color2):
    """
    >>> 颜色相似度
    :param color1: 颜色1
    :param color2: 颜色2
    return distance: 相似度
    """
    distance = sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)) ** 0.5
    return distance


# pragma mark - Main
# --------------------------------------------------------------------------------
if __name__ == '__main__':
    a = "https://test.megaplus.co.nz/wp-content/uploads/2023/01/placeholder_v1-398.png"
    b = "https://images.megabit.co.nz/images/megaplus/logo/placeholder_v1.png"
    # b = "https://test-api.megaplus.co.nz/static/upload/imgs/6c8e4f6a45a542ba962a48623b6722fc.jpg"
    print(image_diff(a, b))
    print(image_md5((a)))
    image_download(b, '/Users/jifu/Downloads/123.png')
