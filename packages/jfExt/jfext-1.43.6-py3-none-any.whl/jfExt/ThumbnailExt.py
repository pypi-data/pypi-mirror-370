# -*- coding: utf-8 -*-
"""
jfExt.ThumbnailExt.py
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2023 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from icecream import ic # noqa
import importlib.resources
from PIL import Image, ImageDraw, ImageFont
import random
import os


def thumbnail_generate_by_str(text, size=128, bg_color=None, font_path=None):
    """
    生成带字母的正方形 avatar。

    :param text: 要显示的文字（取前两个字母大写）
    :param size: 输出图片大小（正方形）
    :param bg_color: 背景颜色, RGB tuple, 例如 (0,128,255)。不传则随机。
    :param font_path: 字体文件路径，不传则使用默认系统字体。
    :return: Pillow Image 对象
    """
    # 取前两个字母大写
    # text = (text[:2] if text else "##").upper()
    text = (text[:2] if text else "").upper()

    # 背景颜色
    if bg_color is None:
        while True:
            bg_color = tuple(random.randint(0,255) for _ in range(3))
            if sum(bg_color) <= 510:  # 太亮的颜色舍弃
                break

    # 创建正方形图片
    img = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # 字体路径和大小
    if font_path is None:
        # font_path = os.path.join(os.path.dirname(__file__), "data", "Inconsolata.otf")
        font_path = importlib.resources.files("jfExt").joinpath("data", "Inconsolata.otf")

    # 动态计算最大字体，让文字撑满图片
    font_size = size
    while font_size > 1:
        font = ImageFont.truetype(font_path, int(font_size))
        bbox = draw.textbbox((0,0), text, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        if w <= size and h <= size:
            break
        font_size -= 1

    # 居中位置
    x = (size - w) / 2
    # y = (size - 512) / 2
    y = 0

    # 自动选择字体颜色：背景亮色用黑色，暗色用白色
    # font_color = (0,0,0) if sum(bg_color) > 382 else (255,255,255)
    font_color = (255, 255, 255)

    # 绘制文字，加粗效果（简单叠加）
    offset_unit = 5
    offsets = [(0,0),(offset_unit,0),(0,offset_unit),(offset_unit,offset_unit)]
    for ox, oy in offsets:
        draw.text((x+ox, y+oy), text, font=font, fill=font_color)

    return img


# pragma mark - Main
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    avatar = thumbnail_generate_by_str("Ba", size=512)
    avatar.save("avatar.png")
