import os
import cv2
import unittest

from viso_sdk.visualize.base import BaseVisualization


TEST_DIR = os.path.abspath(os.path.join(__file__, os.pardir))


class TestVisualization(unittest.TestCase):
    def setUp(self) -> None:
        config = {}
        roi_node = {}

        self.text_vis_params = dict(
            text_color=config.get('text_color', (255, 255, 255, 0.6)),  # RGBA
            text_size=config.get('text_size', 15)
        )
        self.object_vis_params = dict(
            bbox_color=config.get('bbox_color', (255, 50, 50, 0.8)),  # RGBA
            bbox_thickness=config.get('bbox_thickness', 1),
            text_color=config.get('text_color', (255, 255, 255, 1.0)),  # RGBA
            text_size=config.get('text_size', 15),
            show_label=config.get('show_label', True),
            show_confidence=config.get('show_confidence', True)
        )
        self.roi_vis_params = dict(
            roi_color=roi_node.get('roi_color', (255, 150, 113, 0.4)),
            outline_color=roi_node.get('outline_color', None),
            outline_thickness=roi_node.get('outline_thickness', 1),
            show_label=roi_node.get('show_label', True),
            label_size=roi_node.get('label_size', 20),
            label_color=roi_node.get('label_color', (255, 255, 255, 1.0))
        )

        self.viz = BaseVisualization(
            text_vis_params=self.text_vis_params,
            object_vis_params=self.object_vis_params,
            roi_vis_params=self.roi_vis_params
        )

    def test_show_object_detection(self):
        test_img = cv2.imread(os.path.join(TEST_DIR, "sample.png"))
        test_objs = [
            {'class_id': 1,
             'confidence': 0.77,
             'label': 'person',
             'rect': [0.506, 0.154, 0.228, 0.713],
             'roi_id': '',
             'roi_name': ''}
        ]
        show = self.viz.draw_detections(
            img=test_img, detections=test_objs,
            show_label=self.object_vis_params.get('show_label', True),
            show_confidence=self.object_vis_params.get('show_confidence', True)
        )

        show = self.viz.put_text(
            img=show,
            font=None,
            text="\n".join(["Line 1 person Bottom: 518",
                            "Line 2 person Top: 16"]),
            text_color=None,
            pos=(50, 50),
            align="center",
            large_padding=True
        )

        show = self.viz.put_text(
            img=show,
            font=None,
            text="\n".join(["Line 1 person Bottom: 518",
                            "Line 2 person Top: 16"]),
            text_color=None,
            pos=(200, 200),
            large_padding=False
        )

        # cv2.imwrite("result.jpg", show)
        self.assertEqual(show.shape, test_img.shape)


if __name__ == '__main__':
    unittest.main()
