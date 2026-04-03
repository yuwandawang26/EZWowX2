#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EZWowX2 Icon Generator
生成程序图标 (EZAssistedX2.ico)
"""

import os
import sys

def generate_icon():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[ERROR] 需要安装 Pillow: pip install pillow")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'EZAssistedX2.ico')

    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (25, 25, 30, 0))
        draw = ImageDraw.Draw(img)

        margin = int(size * 0.1)
        inner_size = size - 2 * margin

        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=int(size * 0.15),
            fill=(60, 60, 70, 255),
            outline=(100, 180, 255, 255),
            width=int(size * 0.03)
        )

        center = size // 2
        letter_offset = int(size * 0.02)

        font_size = int(size * 0.55)
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "E"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = center - text_width // 2
        y = center - text_height // 2 - letter_offset

        shadow_color = (0, 0, 0, 80)
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font)

        text_color = (100, 180, 255, 255)
        draw.text((x, y), text, fill=text_color, font=font)

        underline_y = y + text_height + int(size * 0.08)
        underline_width = int(inner_size * 0.5)
        underline_x = center - underline_width // 2
        line_thickness = max(1, int(size * 0.04))
        draw.rectangle(
            [underline_x, underline_y, underline_x + underline_width, underline_y + line_thickness],
            fill=(255, 200, 50, 255)
        )

        dot_radius = max(1, int(size * 0.04))
        dot_y = underline_y + line_thickness + int(size * 0.06)
        draw.ellipse(
            [center - dot_radius, dot_y - dot_radius, center + dot_radius, dot_y + dot_radius],
            fill=(80, 220, 120, 255)
        )

        images.append(img)

    images[0].save(output_path, format='ICO', sizes=[(s, s) for s in sizes], append_images=images[1:])

    print(f"[OK] Icon generated: {output_path}")
    print(f"     Sizes: {sizes}")
    return True

if __name__ == "__main__":
    if generate_icon():
        sys.exit(0)
    else:
        sys.exit(1)
