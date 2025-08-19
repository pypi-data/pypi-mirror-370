import numpy as np
import cv2
from PIL import ImageDraw, Image

from viso_sdk.visualize.palette import get_rgba_color
from viso_sdk.visualize import utils

# from viso_sdk.logging import get_logger
# logger = get_logger("vis-roi")


class VizPolygonDraw:
    def __init__(self,
                 show_roi=True,
                 roi_color=utils.DEFAULT_ROI_COLOR,
                 outline_color=utils.DEFAULT_ROI_COLOR,
                 outline_thickness=utils.DEFAULT_ROI_OUTLINE_THICKNESS,
                 show_label=False,
                 label_size=utils.DEFAULT_LABEL_SIZE,
                 label_color=utils.DEFAULT_LABEL_COLOR
                 ):

        self.show_roi = show_roi
        self.show_label = show_label

        self.default_font = utils.init_font(font_size=int(label_size))

        if roi_color is None:
            roi_color = utils.DEFAULT_ROI_COLOR
        self.default_roi_color = get_rgba_color(roi_color)

        if outline_color is None:
            if roi_color is not None:
                outline_color = [roi_color[0] + 10, roi_color[1] + 10, roi_color[2] + 10, roi_color[3]]
            else:
                outline_color = utils.DEFAULT_ROI_OUTLINE_COLOR
        self.default_outline_color = get_rgba_color(outline_color)

        if outline_thickness is None:
            outline_thickness = utils.DEFAULT_ROI_OUTLINE_THICKNESS
        self.default_outline_thickness = int(outline_thickness)

        self.label_color = get_rgba_color(label_color)

    def _draw_polygon_(
            self,
            draw: ImageDraw.Draw,
            polygon,
            outline_color=None,
            # outline_thickness=None,
            fill=True,
            fill_color=None
    ):
        if fill:
            if fill_color is None:
                fill_color = self.default_roi_color
        else:
            fill_color = None

        if outline_color is None:
            outline_color = self.default_outline_color

        # if outline_thickness is None:
        #     outline_thickness = self.default_outline_thickness

        draw.polygon(xy=polygon,
                     fill=fill_color,
                     outline=outline_color)

        return draw

    def draw_polygon_rois(
            self,
            img,
            rois,
            fill_color=None,
            outline_color=None
    ):
        img_h, img_w = img.shape[:2]

        # Convert the image to RGB (OpenCV uses BGR)
        cv_im_rgba = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)

        # Pass the image to PIL
        pil_base_im = Image.fromarray(cv_im_rgba, "RGBA")

        pil_viz_im = Image.new("RGBA", pil_base_im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_viz_im, "RGBA")

        if fill_color is None:
            fill_color = self.default_roi_color
        if outline_color is None:
            outline_color = self.default_outline_color

        for roi in rois:
            if np.max(roi['polygon']) < 1.0:
                polygon = (roi['polygon'] * np.array([img_w, img_h])).astype(int).reshape(-1).tolist()
                x0, y0 = np.average((roi['polygon'] * np.array([img_w, img_h])), axis=0)
            else:
                polygon = (roi['polygon']).astype(int).reshape(-1).tolist()
                x0, y0 = np.average(np.array(roi['polygon']), axis=0)

            label = roi.get('roi_name', '')

            # if outline_thickness is None:
            #     outline_thickness = self.default_outline_thickness
            draw.polygon(xy=polygon,
                         fill=self.default_roi_color if fill_color is None else fill_color,
                         outline=self.default_outline_color if outline_color is None else outline_color)

            if self.show_label:
                utils.put_text(
                    draw=draw,
                    font=self.default_font,
                    pos=(x0, y0),
                    large_padding=True,
                    text=label,
                    text_color=self.label_color,
                    show_shadow=True,
                    show_bg=False,
                    bg_thickness=-1
                )

        pil_out = Image.alpha_composite(pil_base_im, pil_viz_im)
        cv_im_processed = cv2.cvtColor(np.array(pil_out), cv2.COLOR_RGBA2BGR)
        return cv_im_processed

    def draw_line_rois(
            self,
            img,
            lines,
            labels,
            label_font=None,
            label_color=None,
            line_color=None,
            line_thickness=None
    ):
        img_h, img_w, = img.shape[:2]

        cv_im_rgba = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)

        # Pass the image to PIL
        pil_base_im = Image.fromarray(cv_im_rgba, "RGBA")

        pil_viz_im = Image.new("RGBA", pil_base_im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_viz_im, "RGBA")

        for line_idx, line in enumerate(lines):
            [(x1, y1), (x2, y2)] = line
            if max(x1, y1, x2, y2) < 1.0:
                x1 = x1 * img_w
                y1 = y1 * img_h
                x2 = x2 * img_w
                y2 = y2 * img_h

            draw.line(xy=[(x1, y1), (x2, y2)],
                      fill=self.default_roi_color if line_color is None else line_color,
                      width=self.default_outline_thickness if line_thickness is None else line_thickness)

            # get text label
            if labels is not None and len(labels) > line_idx:
                label = labels[line_idx]
            else:
                label = f"line_{line_idx + 1}"
            x0, y0 = int((x1 + x2) // 2), int((y1 + y2) // 2)
            utils.put_text(
                draw=draw,
                font=self.default_font if label_font is None else label_font,
                pos=(x0, y0),
                large_padding=True,
                text=label,
                text_color=self.label_color if label_color is None else label_color,
                show_shadow=True,
                show_bg=False
            )

        pil_out = Image.alpha_composite(pil_base_im, pil_viz_im)
        cv_im_processed = cv2.cvtColor(np.array(pil_out), cv2.COLOR_RGBA2BGR)
        return cv_im_processed
