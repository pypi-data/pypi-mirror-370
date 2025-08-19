import cv2
import numpy as np

from PIL import ImageDraw, Image
from viso_sdk.constants import KEY

from viso_sdk.visualize.palette import get_rgba_color_with_palette_id, get_rgba_color
from viso_sdk.visualize import utils


def trace_to_pts(trace, img_sz, ref_pos=(.5, .5)):
    img_w, img_h = img_sz
    pts = []
    for tlwh in trace:
        x, y, w, h = tlwh

        pos_x, pos_y = x + (w * ref_pos[0]), y + (h * ref_pos[1])

        if w < 1.0 and h < 1.0:
            pts.append((int(pos_x * img_w), int(pos_y * img_h)))
        else:
            pts.append((int(pos_x), int(pos_y)))
    return pts


class BorderType:
    CIRCLE = "circle"
    RECT = "rectangle"
    BBOX = "bbox"
    POINT = "point"


class VizObjectDraw:
    def __init__(self, bbox_color, bbox_thickness=1, text_size=15, text_color=utils.DEFAULT_TXT_COLOR):
        self.border_color = get_rgba_color(bbox_color) if bbox_color is not None else utils.DEFAULT_ROI_OUTLINE_COLOR
        self.border_thickness = int(bbox_thickness)

        self.default_font = utils.init_font(font_size=int(text_size))
        self.text_color = get_rgba_color(text_color) if text_color is not None else utils.DEFAULT_LABEL_COLOR

    def represent_rect(
            self,
            draw,
            tlwh,
            show_border=True,
            outline_color=utils.DEFAULT_ROI_OUTLINE_COLOR, thickness=1, fill_color=None,
            show_label=True,
            label="",
            label_color=utils.DEFAULT_LABEL_COLOR,
            label_bg_color=utils.DEFAULT_ROI_OUTLINE_COLOR
    ):
        x, y, w, h = tlwh
        if show_border:
            draw.rectangle(xy=[(x, y), (x + w, y + h)], fill=fill_color, outline=outline_color, width=thickness)
            label_pos = (x, y)
        else:
            label_pos = (x + w // 2, y + h // 2)

        if len(label) > 0 and show_label:
            utils.put_text(
                font=self.default_font,
                draw=draw,
                pos=label_pos,
                text=label,
                text_color=label_color,
                show_bg=True,
                bg_thickness=-1,
                bg_color=label_bg_color,
                # show_shadow=False
            )

    def represent_circle(
            self,
            draw,
            tlwh,
            show_border=True,
            outline_color=utils.DEFAULT_ROI_OUTLINE_COLOR, thickness=1, fill_color=None,
            show_label=True,
            label="",
            label_color=utils.DEFAULT_LABEL_COLOR,
            label_bg_color=utils.DEFAULT_ROI_OUTLINE_COLOR
    ):
        x, y, w, h = tlwh
        radius = (w + h) // 2
        center = (x + w // 2, y + h // 2)
        if show_border:
            draw.ellipse(xy=(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
                         fill=fill_color,
                         outline=outline_color,
                         width=thickness)
            label_pos = (x + w // 2, y)
        else:
            label_pos = center

        if len(label) > 0 and show_label:
            utils.put_text(
                font=self.default_font,
                draw=draw,
                pos=label_pos,
                text=label,
                text_color=label_color,
                show_bg=True,
                bg_thickness=-1,
                bg_color=label_bg_color,
                # show_shadow=False
            )

    def represent_point(
            self,
            draw,
            tlwh,
            show_border=True,
            outline_color=utils.DEFAULT_ROI_OUTLINE_COLOR, thickness=1, fill_color=None,
            show_label=False,
            label="",
            label_color=utils.DEFAULT_LABEL_COLOR,
            label_bg_color=utils.DEFAULT_ROI_OUTLINE_COLOR,
            ref_pos=(0.5, 0.5)
    ):

        x, y, w, h = tlwh
        radius = thickness
        center = int(x + w * (1 + ref_pos[0])), int(y + h * (1 + ref_pos[1]))

        new_tlwh = [center[0] - radius, center[1] - radius, radius, radius]
        self.represent_circle(
            draw=draw,
            tlwh=new_tlwh,
            show_border=show_border,
            outline_color=outline_color, thickness=thickness, fill_color=outline_color,
            show_label=show_label,
            label=label,
            label_color=label_color,
            label_bg_color=label_bg_color
        )

    def draw_trace_line(
            self,
            draw,
            trace,
            line_color,
            thickness,
            ref_pos=(0.5, 0.5),
            limit=10
    ):
        img_w, img_h = draw.im.size[:2]
        pts = trace_to_pts(trace=trace, img_sz=[img_w, img_h], ref_pos=ref_pos)[-limit:]

        line_color = self.border_color if line_color is None else line_color
        for i in range(len(pts) - 1):
            _pt0 = (int(pts[i][0]), int(pts[i][1]))
            _pt1 = (int(pts[i + 1][0]), int(pts[i + 1][1]))

            draw.line(xy=[_pt0, _pt1], fill=line_color, width=thickness)

    def draw_objects(
            self,
            draw,  # ImageDraw.Draw,
            objs,  # list
            show_border=True,
            border_type=BorderType.RECT,  # "circle"
            random_color=False,
            random_color_key=None,
            show_label=True,
            show_confidence=True,
            show_classname=True,
            show_class_id=False,
            show_tid=False,
            show_trace=False,
            trace_len_limit=10,
            ref_pos=(0.5, 0.5)
    ):
        img_w, img_h = draw.im.size[:2]
        for obj_ind, obj in enumerate(objs):
            tlwh = obj[KEY.TLWH]
            if tlwh[2] < 1.0:
                x, y, w, h = (np.array(tlwh) * np.array([img_w, img_h, img_w, img_h])).astype(int).tolist()
            else:
                x, y, w, h = np.array(tlwh).astype(int).tolist()

            # determine border and trace color
            if random_color:
                if random_color_key in obj.keys():
                    palette_id = obj.get(random_color_key, 0)
                elif KEY.TID in obj.keys():
                    palette_id = obj.get(KEY.TID, 0)
                elif KEY.CLASS_ID in obj.keys():
                    palette_id = obj.get(KEY.CLASS_ID, 0)
                else:
                    palette_id = obj_ind
                border_color = get_rgba_color_with_palette_id(palette_id=palette_id)
            else:
                border_color = self.border_color if self.border_color is not None else utils.DEFAULT_ROI_OUTLINE_COLOR

            # label to print
            label = []
            if show_tid and KEY.TID in obj.keys():
                label.append(f"tid {obj.get(KEY.TID, '')}")
            if show_class_id and KEY.CLASS_ID in obj.keys():
                label.append(f"{obj.get(KEY.CLASS_ID, '')}")
            if show_classname and KEY.LABEL in obj.keys():
                label.append(f"{obj.get(KEY.LABEL, '')}")
            if show_confidence and KEY.SCORE in obj.keys():
                label.append(f"{float(obj.get(KEY.SCORE)):.2f}")
            label = " ".join(label)

            if border_type in [BorderType.RECT, BorderType.BBOX]:
                self.represent_rect(
                    draw=draw,
                    tlwh=[x, y, w, h],
                    show_border=show_border,
                    outline_color=border_color, thickness=self.border_thickness, fill_color=None,
                    show_label=show_label,
                    label=label,
                    label_color=self.text_color,
                    label_bg_color=border_color
                )
            elif border_type in [BorderType.CIRCLE]:
                self.represent_circle(
                    draw=draw,
                    tlwh=[x, y, w, h],
                    show_border=show_border,
                    outline_color=border_color, thickness=self.border_thickness, fill_color=None,
                    show_label=show_label,
                    label=label,
                    label_color=self.text_color,
                    label_bg_color=border_color
                )
            elif border_type in [BorderType.POINT]:
                self.represent_point(
                    draw=draw,
                    tlwh=[x, y, w, h],
                    show_border=show_border,
                    outline_color=border_color, thickness=self.border_thickness * 3, fill_color=border_color,
                    show_label=show_label,
                    label=label,
                    label_color=self.text_color,
                    label_bg_color=border_color,
                    ref_pos=ref_pos
                )
            else:
                pass

            if show_trace and KEY.TRACE in obj.keys() and trace_len_limit > 0:
                self.draw_trace_line(
                    draw, trace=obj.get(KEY.TRACE),
                    line_color=border_color, thickness=self.border_thickness,
                    ref_pos=ref_pos,
                    limit=trace_len_limit
                )
        return draw

    def draw_detections(
            self,
            img,
            detections,
            show_bbox=True,
            random_color=False,
            show_label=True,
            show_confidence=True,
            show_classname=True,
            show_class_id=True
    ):
        # Convert the image to RGB (OpenCV uses BGR)
        cv_im_rgba = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)

        # Pass the image to PIL
        pil_base_im = Image.fromarray(cv_im_rgba, "RGBA")

        pil_viz_im = Image.new("RGBA", pil_base_im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_viz_im, "RGBA")

        self.draw_objects(
            draw=draw,
            objs=detections,
            show_border=show_bbox,
            random_color=random_color,
            border_type=BorderType.RECT,
            show_label=show_label,
            show_classname=show_classname,
            show_confidence=show_confidence,
            show_class_id=show_class_id,
            show_tid=False,
            show_trace=False
        )

        pil_out = Image.alpha_composite(pil_base_im, pil_viz_im)
        cv_im_processed = cv2.cvtColor(np.array(pil_out), cv2.COLOR_RGBA2BGR)
        return cv_im_processed

    def draw_tracks(
            self,
            img,
            tracks,
            show_bbox=True,
            random_color=False,
            show_label=True,
            show_classname=True,
            show_track_id=False,
            show_trace=True,
            trace_len_limit=5,
            ref_pos=(0.5, 0.5)
    ):
        # Convert the image to RGB (OpenCV uses BGR)
        cv_im_rgba = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)

        # Pass the image to PIL
        pil_base_im = Image.fromarray(cv_im_rgba, "RGBA")

        pil_viz_im = Image.new("RGBA", pil_base_im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(pil_viz_im, "RGBA")

        self.draw_objects(
            draw=draw,
            objs=tracks,
            show_border=show_bbox,
            random_color=random_color,
            border_type=BorderType.RECT,
            show_label=show_label,
            show_confidence=False,
            show_class_id=False,
            show_classname=show_classname,
            show_tid=show_track_id,
            show_trace=show_trace,
            trace_len_limit=trace_len_limit,
            ref_pos=ref_pos
        )

        pil_out = Image.alpha_composite(pil_base_im, pil_viz_im)
        cv_im_processed = cv2.cvtColor(np.array(pil_out), cv2.COLOR_RGBA2BGR)
        return cv_im_processed
