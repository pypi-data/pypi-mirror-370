import base64
import cv2
import numpy as np
from typing import Any, Optional, Union


from viso_sdk.constants import PREFIX
from viso_sdk.logging.logger import get_logger


logger = get_logger("REDIS")


class Encoder:
    JPG = ".jpg"
    BMP = ".bmp"


class PayloadVersion:
    VERSION_0 = 0  # "0.x"  # base64 + jpg_encoded string only
    VERSION_1 = 1  # "1.x"  # jpg_encoded/no_encode + meta_data


def gen_redis_key_local(node_id, port):
    return f"{PREFIX.REDIS.LOCAL}_{node_id}_{port}"


def gen_redis_key_status(node_id):
    return f"{PREFIX.REDIS.STATUS}_{node_id}"


def base64_to_img(b64_bytes: bytes) -> Union[None, np.ndarray]:
    """
    Convert base64 string to opencv frame
    Args:
        b64_bytes:

    Returns:

    """
    try:
        str_frame = base64.b64decode(b64_bytes)
        image = cv2.imdecode(  # pylint: disable=no-member
            np.frombuffer(str_frame, dtype=np.uint8), -1
        )
        return image
    except Exception as err:
        logger.warning(f"Failed to convert base64 to image - {err}")
    return None


def img_to_base64str(image: np.ndarray, zoom_ratio: Optional[float] = 1.0):
    """
        Convert opencv frame to base64 encoded string
    Args:
        image:
        zoom_ratio:

    Returns:

    """
    if zoom_ratio != 1.0:
        image = cv2.resize(  # pylint: disable=no-member
            image, None, fx=zoom_ratio, fy=zoom_ratio
        )
    ret, jpg = cv2.imencode(Encoder.JPG, image)  # pylint: disable=no-member
    jpg_as_text = base64.b64encode(jpg)
    if ret:
        return jpg_as_text
    else:
        return None


def img_to_str(image: np.ndarray, encoder=None, with_base64=False):
    """

    Args:
        image:
        encoder: None, .jpg, .bmp
        with_base64: True, False
    Returns:

    """
    try:
        if encoder is None:
            encoded_img = image

        elif encoder.lower() in [Encoder.BMP, Encoder.JPG]:
            """Convert opencv frame to jpg/bmp string"""
            ret, encoded_img = cv2.imencode(encoder.lower(), image)  # pylint: disable=no-member
            if not ret:
                logger.warning(f"Failed to encode image with mode {encoder}")
                return None
        else:
            logger.warning(f'Not defined encoder {encoder}. It should be one of [{Encoder.JPG}, {Encoder.BMP}]')
            # encoded_img = None
            return None

        if with_base64 is True:
            """Convert opencv ndarray to base64 encoded string"""
            img_as_base64 = base64.b64encode(encoded_img)  # bytes
            # frame_as_text = img_as_base64.decode()
            return img_as_base64.decode()  # str
        else:
            # DeprecationWarning: tostring() is deprecated. Use tobytes() instead.
            # frame_as_text = frame_as_bytes.decode()
            img_as_bytes = encoded_img.tobytes()
            return img_as_bytes.decode()

    except Exception as err:
        logger.warning(err)
        return None


def str_to_img(img_as_str, encoder=None, with_base64=False):
    """

    Args:
        img_as_str:
        encoder:
        with_base64:

    Returns:

    """
    try:
        if with_base64 is True:
            img_as_str = img_as_str.encode("ascii")
            img_as_str = base64.b64decode(img_as_str)
        else:
            pass

        if encoder is None:
            img = np.fromstring(img_as_str, dtype=np.uint8)
        elif encoder.lower() in [Encoder.BMP, Encoder.JPG]:
            img = cv2.imdecode(np.frombuffer(img_as_str, dtype=np.uint8), -1)
        else:
            logger.warning(f'Not defined encoder {encoder}. It should be one of [{Encoder.BMP}, {Encoder.JPG}]')
            return None
        return img
    except Exception as err:
        logger.warning(err)
        return None


def resize(img: np.ndarray, zoom=1.0, size=None):
    try:
        if img is None:
            return None

        if zoom != 1.0:
            img = cv2.resize(  # pylint: disable=no-member
                img, None, fx=zoom, fy=zoom
            )

        if size is not None and isinstance(size, tuple):
            img_w, img_h = size
            if img.shape[:2] == [img_h, img_w]:
                return img
            else:
                img = cv2.resize(img, (int(img_w), int(img_h)), fx=zoom, fy=zoom)

        return img

    except Exception as err:
        logger.warning(err)
        return None
