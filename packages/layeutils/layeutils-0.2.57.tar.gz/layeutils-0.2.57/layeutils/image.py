import os

import cairosvg
from PIL import Image


def convert_svg_to_png(svg_file_path, png_sizes):
    """convert_svg_to_png

    Args:
        svg_file_path (_type_): _description_
        png_sizes (_type_): format [[64,64],[128,128]]
    """
    for size in png_sizes:
        output_file_path = os.path.splitext(svg_file_path)[0] + f"_{size[0]}x{size[1]}.png"
        cairosvg.svg2png(url=svg_file_path, write_to=output_file_path, output_width=size[0], output_height=size[1])


def convert_png_to_ico(png_file_path):
    # 打开PNG文件
    png_image = Image.open(png_file_path)
    output_file_path = os.path.splitext(png_file_path)[0] + f".ico"

    # 保存为ICO文件
    png_image.save(output_file_path, format="ICO")
