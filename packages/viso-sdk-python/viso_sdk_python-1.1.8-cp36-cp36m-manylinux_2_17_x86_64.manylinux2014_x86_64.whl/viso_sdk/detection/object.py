import numpy as np


from .utils.nms import non_max_suppression_cv
from viso_sdk.constants import KEY


class BaseDetect:
    def __init__(self, model_dir, labels_to_detect=None, score_threshold=0.3, iou_threshold=0.3,
                 input_size=None, device=None):
        self.model_dir = model_dir
        self.labels_to_det = labels_to_detect
        self.score_threshold = score_threshold
        self.iou_threshold = iou_threshold

        if input_size is None:
            self.input_size = None
        elif isinstance(input_size, list):
            self.input_size = input_size[:2]
        else:
            self.input_size = (input_size, input_size)

        self.device = device


class Detection:

    def __init__(self, class_id, label, score, tlwh, roi_id='', roi_name=''):
        self.class_id = int(class_id)
        self.label = str(label)
        self.score = float(score)

        self.tlwh = self.__get_tlwh(tlwh)

        self.roi_id = str(roi_id)
        self.roi_name = str(roi_name)

    @staticmethod
    def __get_tlwh(tlwh, frame_sz=None):
        if frame_sz is None:
            frame_sz = [1.0, 1.0]

        frame_w, frame_h = frame_sz
        x, y, w, h = tlwh if isinstance(tlwh, np.ndarray) else np.array(tlwh)
        if w > 1.0:
            if frame_w != 1.0:
                xmin = max(x, 0) / frame_w
                ymin = max(y, 0) / frame_h
                xmax = min((x + w), frame_w) / frame_w
                ymax = min((y + h), frame_h) / frame_h
            else:
                xmin = x
                ymin = y
                xmax = x + w
                ymax = y + h
        else:
            xmin = max(x, 0)
            ymin = max(y, 0)
            xmax = min((x + w), 1.0)
            ymax = min((y + h), 1.0)
        return np.array([xmin, ymin, xmax - xmin, ymax - ymin], dtype=float)

    def to_dict(self):
        return {
            KEY.CLASS_ID: int(self.class_id),
            KEY.LABEL: str(self.label),
            KEY.SCORE: round(float(self.score), 2),
            KEY.TLWH: np.array(self.tlwh).round(3).tolist(),
            KEY.ROI_ID: str(self.roi_id),
            KEY.ROI_NAME: str(self.roi_name),
        }


def filter_iou_threshold(detections, score_threshold, iou_threshold, img_sz):
    img_w, img_h = img_sz
    scores = []
    boxes = []
    for detection in detections:
        scores.append(detection.score)
        boxes.append(np.array(detection.tlwh) * np.array([img_w, img_h, img_w, img_h]))
    indices = non_max_suppression_cv(scores=scores, boxes=boxes,
                                     score_threshold=score_threshold,
                                     iou_threshold=iou_threshold)

    # size filtering
    filtered_detections = []
    for ind in indices:
        filtered_detections.append(detections[ind])

    return filtered_detections


def filter_labels(detections, labels_to_detect):
    if labels_to_detect is not None and len(labels_to_detect) > 0:
        filtered_detections = []
        for detection in detections:
            label = detection.label
            if label in labels_to_detect:
                filtered_detections.append(detection)
        return filtered_detections
    else:
        return detections
