# marker.py (非原创)
`作者：https://github.com/2Dou/watermarker`


为图片添加文字水印
可设置文字**大小、颜色、旋转、间隔、透明度**

# usage

需要 Python 3.8 或更高版本，以及 Pillow：

`python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

```
usage: marker.py [-h] [-f FILE] [-m MARK] [-o OUT] [-c COLOR] [-s SPACE] [-a ANGLE] [--font-family FONT_FAMILY] [--font-height-crop FONT_HEIGHT_CROP] [--size SIZE]
                 [--opacity OPACITY] [--quality QUALITY] [--max-size MAX_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  image file path or directory, default is ./input
  -m MARK, --mark MARK  watermark content, default is empty (no watermark)
  -o OUT, --out OUT     image output directory, default is ./output
  -c COLOR, --color COLOR
                        text color like '#000000', default is #8B8B1B
  -s SPACE, --space SPACE
                        space between watermarks, default is 75
  -a ANGLE, --angle ANGLE
                        rotate angle of watermarks, default is 30
  --font-family FONT_FAMILY
                        font family of text, default is 'font/biff.ttf' beside this script
                        using font in system just by font file name
                        for example 'PingFang.ttc', which is default installed on macOS
  --font-height-crop FONT_HEIGHT_CROP
                        change watermark font height crop
                        float will be parsed to factor; int will be parsed to value
                        default is '1.2', meaning 1.2 times font size
                        this useful with CJK font, because line height may be higher than size
  --size SIZE           font size of text, default is 50
  --opacity OPACITY     opacity of watermarks, default is 0.15
  --quality QUALITY     quality of output images (1-100), default is 80
  --max-size MAX_SIZE   maximum output file size, e.g. 500KB or 1MB; may resize
```

# 使用

`python3 marker.py -f ./input/test.webp -m  添加水印`

批量处理：`python marker.py -f ./input -m "仅供测试" -o ./output`

- `-f` 默认 `./input`，`-m` 默认空字符串；文字为空或全为空白时不添加水印，仍按输出格式和质量设置保存图片。
- 直接运行 `python marker.py`，会读取当前工作目录下已有的 `input` 目录，输出到 `./output`。
- 字号和裁剪高度必须大于 0，间距不能小于 0，透明度为 0–1，图片质量为 1–100。
- 自动创建多级输出目录；同名输出文件直接覆盖，输出目录与输入目录相同时会覆盖原图。
- 批量处理跳过子目录和不识别的扩展名；图片损坏或保存失败时继续处理其余文件。
- PNG（包括 `.PNG`）、WebP 和 TIFF 保留透明通道，水印使用 Alpha 合成。
- 全部处理成功退出码为 0；有图片失败或目录中没有图片为 1；参数错误为 2。

运行回归测试：`python -m unittest -v test_marker.py`

# 压缩图片

将 `input` 内的图片压缩至每张不超过 500 KB，输出到 `output`：

```powershell
python marker.py --max-size 500KB
```

压缩并添加水印：

```powershell
python marker.py -m "仅供参考" --max-size 500KB
```

指定单张图片和目标大小：

```powershell
python marker.py -f ./input/test.jpg --max-size 1MB
```

- `--max-size` 可用 `B`、`KB`、`MB`，单位不区分大小写，不写单位按 KB 处理；1 KB = 1024 字节。
- 支持 JPEG、PNG、WebP，保留文件格式和名称，同名直接覆盖。不传此参数时保持原来的保存方式。
- JPEG/WebP 先在 `--quality`（默认 80）与 20 之间降低质量；用户指定质量低于 20 时，以指定值为下限。仍超限时等比例缩小尺寸。
- PNG 先优化无损编码，仍超限时缩小尺寸，保留透明通道；缩小尺寸会减少图像细节。
- 无水印且原文件已小于或等于目标大小时，直接保留原文件内容。
- 输出压缩前后大小和最终宽高。目标小到无法生成有效图片时报告失败，不写入该输出文件，批量处理继续。

![](作者：https://github.com/2Dou/watermarker)
