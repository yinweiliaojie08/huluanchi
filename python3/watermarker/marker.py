#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import io
import os
import re
import sys
import math
import textwrap

from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops


def parse_max_size(value):
    '''目标大小支持 B/KB/MB，未写单位时按 KB 处理。'''
    match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(B|KB|MB)?\s*', value, re.IGNORECASE)
    if not match:
        raise argparse.ArgumentTypeError('use a positive size such as 500KB or 1MB')
    multiplier = {'B': 1, 'KB': 1024, 'MB': 1024 * 1024}[(match[2] or 'KB').upper()]
    try:
        size = int(float(match[1]) * multiplier)
    except (ValueError, OverflowError):
        raise argparse.ArgumentTypeError('size is too large')
    if size < 1:
        raise argparse.ArgumentTypeError('size must be at least 1 byte')
    return size


def compress_image(image, extension, quality, max_bytes):
    '''先降低 JPEG/WebP 质量，再按比例缩小尺寸，返回符合大小限制的编码。'''
    formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.jpe': 'JPEG',
               '.png': 'PNG', '.webp': 'WEBP'}
    image_format = formats.get(extension)
    if image_format is None:
        raise ValueError('--max-size supports JPEG, PNG and WebP only')

    def encode(current, current_quality):
        options = {'quality': current_quality}
        if image_format == 'JPEG':
            options['optimize'] = True
        elif image_format == 'PNG':
            options = {'optimize': True, 'compress_level': 9}
        elif image_format == 'WEBP':
            options['method'] = 6
        with io.BytesIO() as buffer:
            current.save(buffer, format=image_format, **options)
            return buffer.getvalue()

    current = image.copy()
    try:
        while True:
            data = encode(current, quality)
            if len(data) <= max_bytes:
                return data, current.size
            if image_format in ('JPEG', 'WEBP'):
                # 优先保留尺寸，在质量下限和用户指定质量之间搜索。
                minimum = min(20, quality)
                data = encode(current, minimum)
                if len(data) <= max_bytes:
                    best = data
                    low, high = minimum + 1, quality - 1
                    while low <= high:
                        middle = (low + high) // 2
                        candidate = encode(current, middle)
                        if len(candidate) <= max_bytes:
                            best = candidate
                            low = middle + 1
                        else:
                            high = middle - 1
                    return best, current.size
            if current.size == (1, 1):
                raise ValueError('target size is too small for this image format; increase --max-size')
            scale = min(0.9, max(0.1, math.sqrt(max_bytes / len(data)) * 0.9))
            size = (max(1, int(current.width * scale)),
                    max(1, int(current.height * scale)))
            resized = current.resize(size, Image.Resampling.LANCZOS)
            current.close()
            current = resized
    finally:
        current.close()


def add_mark(imagePath, mark, args):
    '''
    添加水印，然后保存图片
    '''
    original_bytes = os.path.getsize(imagePath)
    with Image.open(imagePath) as im:
        image = mark(im)
    name = os.path.basename(imagePath)
    try:
        os.makedirs(args.out, exist_ok=True)
        new_name = os.path.join(args.out, name)
        extension = os.path.splitext(new_name)[1].lower()
        if extension not in ('.png', '.webp', '.tif', '.tiff'):
            converted = image.convert('RGB')
            image.close()
            image = converted
        if args.max_size is None:
            image.save(new_name, quality=args.quality)
            print(name + " Success.")
        else:
            if extension not in ('.jpg', '.jpeg', '.jpe', '.png', '.webp'):
                raise ValueError('--max-size supports JPEG, PNG and WebP only')
            if not args.mark.strip() and original_bytes <= args.max_size:
                # 无水印且原文件已达标时直接保留原编码，避免重复压缩。
                with open(imagePath, 'rb') as source:
                    data = source.read()
                size = image.size
            else:
                data, size = compress_image(image, extension, args.quality, args.max_size)
            # 压缩完成后才打开输出文件，同名覆盖也不会提前截断原图。
            with open(new_name, 'wb') as output:
                output.write(data)
            print('{} Success. {:.1f} KB -> {:.1f} KB, {}x{}'.format(
                name, original_bytes / 1024, len(data) / 1024, *size))
    finally:
        image.close()


def set_opacity(im, opacity):
    '''
    设置水印透明度
    '''
    if not 0 <= opacity <= 1:
        raise ValueError('opacity must be between 0 and 1')

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def crop_image(im):
    '''裁剪图片边缘空白'''
    bg = Image.new(mode='RGBA', size=im.size)
    diff = ImageChops.difference(im, bg)
    del bg
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def mark_height(size, value):
    '''整数表示像素，小数或科学计数法表示字号倍数。'''
    try:
        height = int(value)
    except ValueError:
        height = round(size * float(value))
    if height <= 0:
        raise ValueError('font height must be greater than zero')
    return height


def gen_mark(args):
    '''
    生成mark图片，返回添加水印的函数
    '''
    if not args.mark.strip():
        return lambda im: im.convert('RGBA')

    # 字体宽度、高度
    width = len(args.mark) * args.size
    height = mark_height(args.size, args.font_height_crop)

    # 创建水印图片(宽度、高度)
    mark = Image.new(mode='RGBA', size=(width, height))

    # 生成文字
    draw_table = ImageDraw.Draw(im=mark)
    draw_table.text(xy=(0, 0),
                    text=args.mark,
                    fill=args.color,
                    font=ImageFont.truetype(args.font_family,
                                            size=args.size))
    del draw_table

    # 裁剪空白
    mark = crop_image(mark)
    if not mark.getbbox():
        raise ValueError('watermark is empty; check text and font height crop')

    # 透明度
    set_opacity(mark, args.opacity)

    def mark_im(im):
        ''' 在im图片上添加水印 im为打开的原图'''

        # 计算斜边长度
        c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))

        # 以斜边长度为宽高创建大图（旋转后大图才足以覆盖原图）
        mark2 = Image.new(mode='RGBA', size=(c, c))

        # 在大图上生成水印文字，此处mark为上面生成的水印图片
        y, idx = 0, 0
        while y < c:
            # 制造x坐标错位
            x = -int((mark.size[0] + args.space) * 0.5 * idx)
            idx = (idx + 1) % 2

            while x < c:
                # 在该位置粘贴mark水印图片
                mark2.paste(mark, (x, y))
                x = x + mark.size[0] + args.space
            y = y + mark.size[1] + args.space

        # 将大图旋转一定角度
        mark2 = mark2.rotate(args.angle)

        # 裁剪到原图尺寸后按 alpha 合成，避免重复应用透明度。
        left = -int((im.width - c) / 2)
        top = -int((im.height - c) / 2)
        with mark2.crop((left, top, left + im.width, top + im.height)) as overlay:
            with im.convert('RGBA') as base:
                result = Image.alpha_composite(base, overlay)
        mark2.close()
        return result

    return mark_im


def main():
    parse = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parse.add_argument("-f", "--file", type=str, default="./input",
                       help="image file path or directory, default is ./input")
    parse.add_argument("-m", "--mark", type=str, default="",
                       help="watermark content, default is empty (no watermark)")
    parse.add_argument("-o", "--out", default="./output",
                       help="image output directory, default is ./output")
    parse.add_argument("-c", "--color", default="#8B8B1B", type=str,
                       help="text color like '#000000', default is #8B8B1B")
    parse.add_argument("-s", "--space", default=75, type=int,
                       help="space between watermarks, default is 75")
    parse.add_argument("-a", "--angle", default=30, type=int,
                       help="rotate angle of watermarks, default is 30")
    parse.add_argument("--font-family", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font', 'biff.ttf'), type=str,
                       help=textwrap.dedent('''\
                       font family of text, default is 'font/biff.ttf' beside this script
                       using font in system just by font file name
                       for example 'PingFang.ttc', which is default installed on macOS
                       '''))
    parse.add_argument("--font-height-crop", default="1.2", type=str,
                       help=textwrap.dedent('''\
                       change watermark font height crop
                       float will be parsed to factor; int will be parsed to value
                       default is '1.2', meaning 1.2 times font size
                       this useful with CJK font, because line height may be higher than size
                       '''))
    parse.add_argument("--size", default=50, type=int,
                       help="font size of text, default is 50")
    parse.add_argument("--opacity", default=0.15, type=float,
                       help="opacity of watermarks, default is 0.15")
    parse.add_argument("--quality", default=80, type=int,
                       help="quality of output images (1-100), default is 80")
    parse.add_argument("--max-size", type=parse_max_size, default=None,
                       help="maximum output file size, e.g. 500KB or 1MB (bare number: KB); may resize")

    args = parse.parse_args()

    if args.size <= 0:
        parse.error('--size must be greater than zero')
    if args.space < 0:
        parse.error('--space must be zero or greater')
    if not 0 <= args.opacity <= 1:
        parse.error('--opacity must be between 0 and 1')
    if not 1 <= args.quality <= 100:
        parse.error('--quality must be between 1 and 100')
    if not os.path.exists(args.file):
        parse.error('--file does not exist: ' + args.file)
    if not args.out.strip():
        parse.error('--out must not be empty')
    try:
        mark = gen_mark(args)
    except (OSError, ValueError, OverflowError) as exc:
        parse.error('cannot create watermark: ' + str(exc))

    try:
        if os.path.isdir(args.file):
            Image.init()
            extensions = Image.registered_extensions()
            files = []
            for name in sorted(os.listdir(args.file)):
                path = os.path.join(args.file, name)
                if os.path.isfile(path) and os.path.splitext(name)[1].lower() in extensions:
                    files.append(path)
                else:
                    print(name + ' Skipped (not an image file).')
        else:
            files = [args.file]
    except OSError as exc:
        parse.error('cannot read input: ' + str(exc))

    if not files:
        print('No image files found.', file=sys.stderr)
        return 1
    failed = 0
    for path in files:
        try:
            add_mark(path, mark, args)
        except (OSError, ValueError, KeyError, Image.DecompressionBombError) as exc:
            failed += 1
            print(os.path.basename(path) + ' Failed: ' + str(exc), file=sys.stderr)
    print('Completed: {} succeeded, {} failed.'.format(len(files) - failed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
