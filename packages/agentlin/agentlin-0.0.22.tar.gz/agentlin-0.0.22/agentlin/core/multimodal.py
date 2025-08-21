from io import BytesIO
import base64
import os
import re
from typing_extensions import Union
import requests
from PIL import Image, ImageDraw, ImageFont
from loguru import logger


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def base64_to_image(base64_str: str) -> Image.Image:
    """
    Convert a base64 string to an image.
    """
    # 使用正则表达式匹配并移除任意类型的数据URL前缀
    pattern = r'^data:image/[^;]+;base64,'
    base64_str = re.sub(pattern, '', base64_str, count=1)

    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    return image


def read_image_http_url(image_url: str) -> Image.Image:
    # 使用 requests 获取图像的二进制数据
    response = requests.get(image_url)
    image_data = response.content

    # 使用 Pillow 将二进制数据转换为 Image.Image 对象
    image = Image.open(BytesIO(image_data))
    return image


def read_image_file_path(image_path: str) -> Image.Image:
    """
    从文件路径读取图像并返回 Image.Image 对象。
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    image = Image.open(image_path)
    return image


def text_image_meta(image: Image.Image) -> str:
    width, height = image.size
    return f"width={width} height={height}"


def image_content(image: Union[Image.Image, str], image_id: Union[str, int]) -> list[dict]:
    if isinstance(image, str):
        # 如果是字符串，可能是文件路径,URL 或 base64 字符串
        if image.startswith("http://") or image.startswith("https://"):
            image = read_image_http_url(image)
        elif image.startswith("data:image/"):
            image = base64_to_image(image)
        elif os.path.exists(image) and os.path.isfile(image):
            image = read_image_file_path(image)
    assert isinstance(image, Image.Image), "Image must be a PIL Image object or a valid image path/URL/base64 string"
    meta_info = text_image_meta(image)  # 原始图像的元信息
    image = scale_to_fit_and_add_scale_bar(image)  # 缩放并添加比例尺
    img_b64 = image_to_base64(image)  # 缩放后的图像
    return [
        {
            "type": "text",
            "text": f"<image {meta_info}>",
            "id": image_id,
        },
        {
            "type": "image_url",
            "image_url": {
                "url": img_b64,
            },
            "id": image_id,
        },
        {
            "type": "text",
            "text": f"</image {meta_info}>",
            "id": image_id,
        },
    ]


def scale_to_fit(image: Image.Image, target_size: tuple[int, int] = (512, 512)) -> Image.Image:
    """
    将图像缩放到适合目标大小的尺寸，同时保持原始宽高比。

    args:
        image: PIL.Image.Image
            要缩放的图像。
        target_size: tuple[int, int]
            目标大小，格式为 (width, height)。

    return: PIL.Image.Image
        缩放后的图像。
    """
    original_width, original_height = image.size
    target_width, target_height = target_size

    # 计算缩放比例
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    scale_ratio = min(width_ratio, height_ratio)
    if scale_ratio >= 1:
        # 如果图像已经小于或等于目标大小，则不需要缩放
        return image

    # 计算新的尺寸
    new_width = round(original_width * scale_ratio)
    new_height = round(original_height * scale_ratio)

    # 缩放图像
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_image


def add_scale_bar(
    image: Image.Image,
    spacing=64,
    color=(0, 0, 0),
    font_size=12,
    left_margin=50,
    top_margin=50,
    tick_length=8,
    tick_width=2,
    text_offset=2,
    origin_size: tuple[int, int] = None,
):
    """
    为图像添加顶部和左侧标尺，并将文字标签放在空白边距中，不与原图重叠。

    args:
        image: PIL.Image.Image
            要添加标尺的图像。
        spacing: int
            刻度之间的间隔，单位为像素。
        color: tuple
            刻度线和文字的颜色，RGB格式。
        font_size: int
            文字的字体大小。
        left_margin: int
            左侧边距的宽度，单位为像素。
        top_margin: int
            顶部边距的高度，单位为像素。
        tick_length: int
            刻度线的长度，单位为像素。
        tick_width: int
            刻度线的宽度，单位为像素。
        text_offset: int
            文字与刻度线之间的距离，单位为像素。
        origin_size: tuple[int, int]
            原图的尺寸，格式为 (width, height)。如果未提供，则使用图像的实际尺寸。
    return: PIL.Image.Image

    示例用法
    ```
    img = Image.open("/Pictures/example.png")
    out = add_scale_bar(
        img,
        spacing=100,
        color=(0, 0, 0),
        font_size=12,
        left_margin=50,
        top_margin=50,
        tick_length=8,
        text_offset=4,
        origin_size=(img.width, img.height)  # 可选，指定原图尺寸
    )
    out
    ```
    """
    # 加载字体
    try:
        font_path = "C:/Windows/Fonts/arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    w, h = image.size
    new_w, new_h = w + left_margin, h + top_margin

    # 创建背景画布并粘贴原图
    mode = image.mode
    bg = (255, 255, 255) if mode == "RGB" else (255,)
    canvas = Image.new(mode, (new_w, new_h), bg)
    canvas.paste(image, (left_margin, top_margin))

    draw = ImageDraw.Draw(canvas)

    # 计算文字宽高的 helper
    def text_dimensions(txt):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    origin_width, origin_height = origin_size if origin_size else (w, h)

    # 顶部刻度和文字
    x_ticks = range(0, w + 1, spacing)
    for i, x in enumerate(x_ticks):
        # 计算刻度线的 x 坐标
        px = left_margin + x
        if i == len(x_ticks) - 1:
            # 最后一个刻度线在右侧边界
            px = new_w - tick_width
        # 刻度线
        draw.line([(px, top_margin), (px, top_margin - tick_length)], width=tick_width, fill=color)
        # 文字
        origin_x = x * origin_width // w  # 将刻度值映射到原图尺寸
        if i == len(x_ticks) - 1:
            origin_x = origin_width  # 确保最后一个刻度值是原图宽度
        txt = str(origin_x)
        tw, th = text_dimensions(txt)
        tx = px - tw / 2
        if i == len(x_ticks) - 1:
            # 最后一个刻度的文字放在刻度线的左边
            tx = tx - tw / 2
        ty = top_margin - tick_length - th - text_offset
        draw.text((tx, ty), txt, fill=color, font=font)

    # 左侧刻度和文字
    y_ticks = range(0, h + 1, spacing)
    for i, y in enumerate(y_ticks):
        # 计算刻度线的 y 坐标
        py = top_margin + y
        if i == len(y_ticks) - 1:
            # 最后一个刻度线在底部边界
            py = new_h - tick_width
        # 刻度线
        draw.line([(left_margin, py), (left_margin - tick_length, py)], width=tick_width, fill=color)
        # 文字
        origin_y = y * origin_height // h  # 将刻度值映射到原图尺寸
        if i == len(y_ticks) - 1:
            origin_y = origin_height
        txt = str(origin_y)
        tw, th = text_dimensions(txt)
        tx = left_margin - tick_length - tw - text_offset
        ty = py - th / 2
        if i == len(y_ticks) - 1:
            # 最后一个刻度的文字放在刻度线的上边
            ty = ty - th / 3 * 2
        draw.text((tx, ty), txt, fill=color, font=font)

    return canvas


def scale_to_fit_and_add_scale_bar(image: Image.Image, debug=False) -> Image.Image:
    origin_width, origin_height = image.size
    target_width, target_height = 512, 512
    if debug:
        logger.debug(f"原图尺寸: {origin_width}x{origin_height}, 目标尺寸: {target_width}x{target_height}")
    image = scale_to_fit(image, target_size=(target_width, target_height))  # 缩放图片到目标大小，为了省 image tokens
    if debug:
        logger.debug(f"缩放后图片尺寸: {image.size[0]}x{image.size[1]}")
    image = add_scale_bar(image, origin_size=(origin_width, origin_height))  # 保持缩放后的比例尺为原图的比例尺，方便模型在原图上定位坐标和长宽用于裁剪
    if debug:
        logger.debug(f"添加比例尺后图片尺寸: {image.size[0]}x{image.size[1]}")
    return image


def is_text_content(content: list[dict]) -> bool:
    return all(item.get("type") == "text" for item in content)

def is_multimodal_content(content: list[dict]) -> bool:
    return any(item.get("type") != "text" for item in content)