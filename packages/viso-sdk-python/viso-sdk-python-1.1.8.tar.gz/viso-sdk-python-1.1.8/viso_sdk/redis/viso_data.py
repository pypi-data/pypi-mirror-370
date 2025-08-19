import time
import json

from .utils import img_to_str, str_to_img, Encoder, base64_to_img, img_to_base64str


class MetaSource:
    id = None
    type = None
    name = None
    source_name = None
    source_key = None
    output_port_idx = None
    frame_id = None
    ts = None

    def __init__(self, src_node=None, src_output_port=None, src_name=None):
        if src_node is None:
            # src_node = {}
            pass
        else:
            self.id = src_node.get('id', None)
            self.type = src_node.get('type', None)
            self.name = src_node.get('name', None)
            self.source_name = src_name if src_name else f'{src_node.get("type")}_{src_output_port}'
            self.source_key = f"{src_node.get('id')}_{src_output_port}"
            self.output_port_idx = src_output_port
            self.frame_id = None
            self.ts = time.time()

    def update(self, source_info):
        for key, val in source_info.items():
            if val:
                if not hasattr(self, key) or getattr(self, key) != val:
                    setattr(self, key, val)

    def to_dict(self):
        return self.__dict__


class MetaModule:
    id = None
    type = None
    # name = None
    feed_port_idx = None

    def __init__(self, cur_node=None, feed_port_idx=None):
        if cur_node is None:
            # cur_node = {}
            pass
        else:
            self.id = cur_node.get("id", None)
            self.type = cur_node.get("type", None)
            self.feed_port_idx = feed_port_idx

    def to_dict(self):
        return self.__dict__

    def update(self, module_info):
        for key, val in module_info.items():
            if val:
                if not hasattr(self, key) or getattr(self, key) != val:
                    setattr(self, key, val)


class MetaFrameFormat:
    encoder = None
    with_base64 = False

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return self.__dict__

    def update(self, frame_format_info):
        for key, val in frame_format_info.items():
            if val:
                if not hasattr(self, key) or getattr(self, key) != val:
                    setattr(self, key, val)


class Meta:
    # src_node = {}, src_port = None
    # source = MetaSource()
    # module = MetaModule()

    def __init__(self,
                 cur_node, feed_idx,
                 src_node, src_port, src_name):
        self.ts = time.time()
        self.module = MetaModule(cur_node=cur_node, feed_port_idx=feed_idx)
        self.source = MetaSource(src_node=src_node, src_output_port=src_port, src_name=src_name)
        self.frame_format = MetaFrameFormat()

    def update_source(self, source_info=None):
        if source_info is None:
            source_info = {}
        self.source.update(source_info)

    def update_frame_format(self, frame_format_info=None):
        if frame_format_info is None:
            frame_format_info = {}
        self.frame_format.update(frame_format_info)

    def update_module(self, module_info=None):
        if module_info is None:
            module_info = {}
        self.module.update(module_info)

    def to_dict(self):
        return {
            "ts": time.time(),
            "source": self.source.to_dict(),
            "module": self.module.to_dict(),
            "frame_format": self.frame_format.to_dict()
        }


class VisoData:
    frame = None
    result = None

    def __init__(self, feed_idx, cur_node, src_node=None, src_port=None, src_name=None):
        """

        Args:
            feed_idx: the input index at current module
            cur_node: current module
        """
        self.meta = Meta(cur_node=cur_node, feed_idx=feed_idx,
                         src_node=src_node, src_port=src_port, src_name=src_name)
        # self.meta.module.__init__(cur_node=cur_node, feed_port_idx=feed_idx)
        # self.meta.source.__init__(src_node=src_node, src_output_port=src_port, src_name=src_name)

    def parse_viso_data(self, data, version=1, encoder=None, with_base64=None):
        """

        Args:
            data:  data from redis - dict or redis_string
            version:
            encoder:
            with_base64:

        Returns:

        """
        if version == 0:
            # return str_to_img(img_as_str=data, encoder=Encoder.JPG, with_base64=True)
            return base64_to_img(b64_bytes=data)
        else:
            if isinstance(data, bytes):
                data = json.loads(data.decode())

            # meta.source - keep information comes form previous module
            self.meta.update_source(source_info=data.get('meta', {}).get("source"))

            # meta.module - keep info initialized at init()
            # self.meta.update_module(module_info=)

            # meta.frame_format
            self.meta.update_frame_format(data.get('meta', {}).get("frame_format"))

            # frame data
            frame_data = data.get('frame', None)
            if frame_data:
                # if custom encoding format is applied, then update frame_format info
                encoder = encoder if encoder is not None else self.meta.frame_format.encoder
                with_base64 = with_base64 if with_base64 is not None else self.meta.frame_format.with_base64
                data['frame'] = str_to_img(img_as_str=frame_data, encoder=encoder, with_base64=with_base64)
            else:
                data['frame'] = None
            return data

    def create_viso_data(self, version=1, ext_info=None, result=None, frame=None,
                         encoder=Encoder.JPG, with_base64=False):
        """
            Generate payload to publish
        Args:
            with_base64:
            encoder:
            version:
                0.x -> publish frame data only into redis port
                1.x or later -> publish frame + metadata into redis port
            ext_info: extra information to add meta
            result: processing result e.g. detections
            frame: processed frame cv2.ndarray

        Returns:
            {
                "meta": {
                    "ts":
                    "module": {},
                    "source": {},
                    "frame_format": {}
                }
                "frame": {},
                "result": {}
            }

        """
        if version > 0:
            meta_data = self.meta.to_dict()

            # additional info
            if ext_info and isinstance(ext_info, dict):
                for key, val in ext_info.items():
                    meta_data[key] = val

            # result
            if result is None:
                result = []

            if frame is not None:
                encoder = encoder if encoder is not None else self.meta.frame_format.encoder
                with_base64 = with_base64 if with_base64 is not None else self.meta.frame_format.with_base64
                frame_as_text = img_to_str(image=frame, encoder=encoder, with_base64=with_base64)
                # if custom encoding format is applied, then update frame_format info
                meta_data['frame_format'] = {
                    "encoder": encoder,
                    "with_base64": with_base64
                }
            else:
                frame_as_text = None

            payload = {
                "meta": meta_data,
                "result": result,
                "frame": frame_as_text
            }
            return payload
        else:  # version 0.2.15 or lower
            if frame is not None:
                # return img_to_str(image=frame, encoder=Encoder.JPG, with_base64=True)
                return img_to_base64str(image=frame)
            else:
                return None
