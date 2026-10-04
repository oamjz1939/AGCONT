#!/usr/bin/env python3
"""
UI Spotlight 标注工具 (跨平台: macOS / Windows / Linux)
纯依赖 Pillow，支持从本地文件或直接从系统剪贴板读取图片。
接收归一化坐标 [ymin, xmin, ymax, xmax]，在图上绘制聚光灯与红框并自动弹出预览。
"""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageGrab

def load_source_image(image_path: str = None, use_clipboard: bool = False) -> Image.Image:
    # 优先从剪贴板读取（若指定了 --clipboard 或未提供 --image）
    if use_clipboard or not image_path:
        clip_data = ImageGrab.grabclipboard()
        if isinstance(clip_data, Image.Image):
            return clip_data.convert("RGBA")
        elif isinstance(clip_data, list) and clip_data and Path(clip_data[0]).is_file():
            return Image.open(clip_data[0]).convert("RGBA")
        else:
            raise ValueError("剪贴板中未检测到图片！请确认刚刚截取的图片已在剪贴板中。")
    
    img_path = Path(image_path).expanduser().resolve()
    if not img_path.exists():
        raise FileNotFoundError(f"未找到图片文件: {img_path}")
    return Image.open(img_path).convert("RGBA")

def annotate_image(
    image_path: str = None,
    use_clipboard: bool = False,
    box: list[float] = None,
    output_path: str = None,
    auto_open: bool = True
):
    base_img = load_source_image(image_path, use_clipboard)
    width, height = base_img.size

    ymin, xmin, ymax, xmax = box

    # 将 0-1000 归一化比例转换为实际像素坐标
    x1 = int(xmin * width / 1000)
    y1 = int(ymin * height / 1000)
    x2 = int(xmax * width / 1000)
    y2 = int(ymax * height / 1000)

    # 边界保护
    x1, x2 = max(0, min(x1, x2)), min(width, max(x1, x2))
    y1, y2 = max(0, min(y1, y2)), min(height, max(y1, y2))

    # 1. 聚光灯遮罩：背景暗化 40%，目标区域保持透亮
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 100))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0, 0))
    annotated = Image.alpha_composite(base_img, mask)

    # 2. 绘制醒目红框
    draw = ImageDraw.Draw(annotated)
    line_width = max(3, int(min(width, height) * 0.003))
    red_color = (255, 59, 48, 255)

    for offset in range(line_width):
        draw.rectangle([x1 - offset, y1 - offset, x2 + offset, y2 + offset], outline=red_color)

    result_img = annotated.convert("RGB")

    # 可选保存（仅当用户显式指定 --output 时写入文件）
    if output_path:
        out_file = Path(output_path).expanduser().resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        result_img.save(out_file)
        print(f"标注已保存至: {out_file}")

    # 3. 纯内存原生跨平台弹出预览
    if auto_open:
        result_img.show(title="UI Spotlight")
        print("已通过系统默认查看器弹出标注图。")

def main():
    parser = argparse.ArgumentParser(description="UI Spotlight 跨平台标注工具")
    parser.add_argument("--image", default=None, help="待标注的原图路径（若不提供，默认从剪贴板读取）")
    parser.add_argument("--clipboard", action="store_true", help="强制从系统剪贴板读取图片")
    parser.add_argument("--box", nargs=4, type=float, required=True, help="归一化坐标: ymin xmin ymax xmax (范围 0 到 1000)")
    parser.add_argument("--output", default="", help="可选保存路径（不指定则纯内存预览不落盘）")
    parser.add_argument("--no-open", action="store_true", help="不自动弹出打开图片")

    args = parser.parse_args()
    annotate_image(
        image_path=args.image,
        use_clipboard=args.clipboard or (args.image is None),
        box=args.box,
        output_path=args.output or None,
        auto_open=not args.no_open
    )

if __name__ == "__main__":
    main()
