import os
import PIL
from PIL import ImageFont

from viso_sdk.constants import FONTS_DIR
from viso_sdk.logging import get_logger
from viso_sdk.visualize.palette import get_rgba_color, get_rgba_color_with_palette_id

pil_version = PIL.__version__
logger = get_logger("vis-font")


DEFAULT_FONT_SIZE = 15
DEFAULT_FONT_NAME = "Roboto-Medium"
DEFAULT_TXT_COLOR = get_rgba_color((255, 255, 255, 1.0))
# DEFAULT_TXT_THICKNESS = 1
DEFAULT_SHADOW_COLOR = get_rgba_color((0, 0, 0, 1.0))
DEFAULT_OPACITY = 100


DEFAULT_ROI_COLOR = get_rgba_color((255, 150, 113, 0.4))
DEFAULT_ROI_OUTLINE_COLOR = get_rgba_color((70, 70, 70, 1.0))
DEFAULT_ROI_OUTLINE_THICKNESS = 1
DEFAULT_LABEL_COLOR = get_rgba_color((255, 255, 255, 0.4))
DEFAULT_LABEL_SIZE = 50


def get_adjust_bbox_thick(img_sz):
    img_h, img_w = img_sz
    bbox_thick = int(0.5 * (img_h + img_w) / 1000)
    if bbox_thick < 2:
        bbox_thick = 2

    return bbox_thick


def get_text_size(draw, text, font, xy=(10, 10)):
    # calculate area to put text
    if pil_version < "10.0.0":
        text_width, text_height = draw.textsize(text, font)
    else:
        # Get the bounding box of the text
        bbox = draw.textbbox(xy, text, font=font)

        # Calculate the dimensions of the bounding box
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    # # multi-line text
    # if "\n" in text:
    #     text_height = text.count('\n') * text_height
    return text_width, text_height


def get_supported_fonts(fonts_dir=FONTS_DIR):
    font_names = [os.path.splitext(fn)[0] for fn in os.listdir(fonts_dir) if os.path.splitext(fn)[1] == '.ttf']
    return font_names


def get_adjusted_font(bbox_size):
    box_width, box_height = bbox_size

    font_size = max(int(box_height * 0.8), 10)
    font = init_font(font_size=font_size)

    return font


def get_adjusted_font_with_bbox(bbox_size, str_len):
    box_width, box_height = bbox_size

    font_size_by_height = max(int(box_height * 0.8), 10)
    font_size_by_width = max(int(box_width / str_len * 2), 10)
    font_size = min(font_size_by_width, font_size_by_height)
    font = init_font(font_size=font_size)

    return font


def init_font(font_name=None, font_size=DEFAULT_FONT_SIZE):
    fonts = get_supported_fonts(FONTS_DIR)
    if font_name is not None and os.path.isabs(font_name) and os.path.exists(font_name):
        font_file = font_name
    elif font_name in fonts:
        # logger.warning(f"can not fine such font file {font_name}, use default {fonts[0]}")
        font_file = os.path.join(FONTS_DIR, f"{font_name}.ttf")
    else:
        # logger.warning(f"font_name is not specified, use default {fonts[0]}")
        font_file = os.path.join(FONTS_DIR, f"{fonts[0]}.ttf")
        # font_file = os.path.join(FONTS_DIR, f"SIMSUN.ttf")

    # logger.info(f"load font {font_name}")
    font = ImageFont.truetype(font_file, font_size)
    return font


def put_text(
        draw,
        font,
        pos,  # tlwh
        text,
        text_color=DEFAULT_TXT_COLOR,
        align="left",
        large_padding=False,
        show_bg=False,  # background
        bg_thickness=-1,
        bg_color=DEFAULT_ROI_COLOR,
        show_shadow=False,
        shadow_color=DEFAULT_SHADOW_COLOR,
        spacing=4
):
    """

    Args:
        draw: PIL.Draw object
        font: font object to put text
        pos: rectangle coordinates to put text - tlwh (x, y, w, h)
        text: text string
        text_color:
        align: left or center
        large_padding: information or title?
        show_bg: True / False
            show background(rectangle) or not
        bg_color: DEFAULT_ROI_COLOR
            RGBA color
        bg_thickness: background(rectangle) thickness
            if bck_thickness = -1: fill out rectangle with solid color
            else: draw rectangle border with specified thickness
        show_shadow:
            True / False
        shadow_color:
            RGBA color
        spacing: line space
    Returns:

    """
    text_width, text_height = get_text_size(draw=draw, text=text, font=font, xy=pos[:2])
    num_lines = text.count("\n") + 1

    if not spacing:
        spacing = max(int(text_height // num_lines // 8), 1)

    if large_padding:
        padding_left = spacing * 8
        padding_top = spacing * 4
    else:
        padding_left = spacing
        padding_top = spacing

    if len(pos) == 4:  # bbox
        x, y, w, h = pos[:4]
    else:
        x, y = pos[:2]
        w, h = text_width, text_height

    x1 = x
    y1 = y
    x2 = x + w + padding_left * 2
    y2 = y + h + padding_top * 2

    # Calculate the center coordinates of the bbox
    x_cen_bbox = (x1 + x2) // 2
    y_cen_bbox = (y1 + y2) // 2

    # Calculate the position to center the text
    if align == "left":
        x_text = x1 + padding_left
        y_text = y_cen_bbox - text_height // 2
    else:  # center
        x_text = x_cen_bbox - text_width // 2
        y_text = y_cen_bbox - text_height // 2

    if show_bg:
        if bg_thickness == -1:
            # put filled text rectangle
            draw.rectangle(xy=[(x1, y1), (x2, y2)], fill=bg_color)
        else:
            draw.rectangle(xy=[(x1, y1), (x2, y2)], outline=bg_color, width=bg_thickness)
    else:
        pass

    # shadow effect
    if show_shadow:
        draw.multiline_text(
            (x_text + 1, y_text + 1),
            font=font, text=text, fill=shadow_color,
            spacing=spacing,
            align=align)

    # put text above rectangle
    draw.multiline_text(
        (x_text, y_text),
        font=font, text=text, fill=text_color,
        spacing=spacing,
        align=align)

    return draw
