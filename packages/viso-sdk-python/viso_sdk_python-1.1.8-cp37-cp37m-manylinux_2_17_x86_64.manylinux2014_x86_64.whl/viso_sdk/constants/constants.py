# =====================================================================================================================
# architectures
class ARCHITECTURE:
    AMD64 = "amd64"
    ARMV7HF = "armv7hf"
    AARCH64 = "aarch64"


# =====================================================================================================================
# frameworks
class FRAMEWORK:
    TF = "tensorflow"
    TF_GPU = "tensorflow_gpu"
    TF_LITE = "tensorflow_lite"
    OPENVINO = "openvino"
    TORCH = "torch"
    TORCH_GPU = "torch_gpu"
    KERAS = "keras"
    CAFFE = "caffe"
    FURIOSA = "furiosa"
    MmDetection = "mmdetection"
    MmDetection_GPU = "mmdetection_gpu"
    TensorRT = "tensorrt"
    ONNX = "onnx"
    OTHER = "other"


# =====================================================================================================================
# devices
class DEVICE:
    DEFAULT = 'CPU'

    # tensorflow devices
    class TF:
        CPU = "CPU"
        GPU = "nGPU"  # nvidia GPU

    class OPENVINO:
        CPU = "CPU"
        MYRIAD = "MYRIAD"
        GPU = "iGPU"  # intel GPU
        GNA = "GNA"
        # FPGA = "FPGA"
        # HDDL = "HDDL"

    class TF_LITE:
        CPU = "CPU"  # CPU
        eTPU = "eTPU"  # Edge TPU
        GPU = "nGPU"

    class TORCH:
        CPU = "CPU"
        CUDA = "CUDA"

    class CAFFE:
        CPU = "CPU"

    class KERAS:
        CPU = "CPU"

    class FURIOSA:
        CPU = "CPU"
        CUDA = "CUDA"
        NPU = "NPU"

    class MmDetection:
        CPU = "CPU"

    class MmDetection_GPU:
        CPU = "CPU"
        CUDA = "CUDA"

    class TensorRT:
        CPU = "CPU"
        CUDA = "CUDA"

    class ONNX:
        CPU = "CPU"
        CUDA = "CUDA"


# =====================================================================================================================
SUPPORT_DEVICES = {
    ARCHITECTURE.AMD64: {
        FRAMEWORK.TF: [DEVICE.TF.CPU],
        FRAMEWORK.TF_GPU: [DEVICE.TF.CPU, DEVICE.TF.GPU],
        # TENSORFLOW_LITE: [TF_LITE_CPU, TF_LITE_eTPU],  # TF_LITE_nGPU
        FRAMEWORK.OPENVINO: [DEVICE.OPENVINO.CPU, DEVICE.OPENVINO.MYRIAD, DEVICE.OPENVINO.GPU, DEVICE.OPENVINO.GNA],
        # OV_FPGA, OV_HDDL
        FRAMEWORK.TORCH: [DEVICE.TORCH.CPU],
        FRAMEWORK.TORCH_GPU: [DEVICE.TORCH.CPU, DEVICE.TORCH.CUDA],
        FRAMEWORK.CAFFE: [DEVICE.CAFFE.CPU],
        FRAMEWORK.KERAS: [DEVICE.KERAS.CPU],
        FRAMEWORK.FURIOSA: [DEVICE.FURIOSA.CPU, DEVICE.FURIOSA.CUDA],
        FRAMEWORK.MmDetection: [DEVICE.MmDetection.CPU],
        FRAMEWORK.MmDetection_GPU: [DEVICE.MmDetection.CPU, DEVICE.MmDetection_GPU.CUDA],
        FRAMEWORK.TensorRT: [DEVICE.TensorRT.CPU, DEVICE.TensorRT.CUDA],
        FRAMEWORK.ONNX: [DEVICE.ONNX.CPU, DEVICE.ONNX.CUDA],
    },
    ARCHITECTURE.AARCH64: {
        FRAMEWORK.TF: [DEVICE.TF.CPU],
        FRAMEWORK.TF_LITE: [DEVICE.TF_LITE.CPU, DEVICE.TF_LITE.eTPU],
        FRAMEWORK.TORCH: [DEVICE.TORCH.CPU],
        FRAMEWORK.TORCH_GPU: [DEVICE.TORCH.CPU, DEVICE.TORCH.CUDA],
        FRAMEWORK.OPENVINO: [DEVICE.OPENVINO.CPU],  # OpenVINO for ARM64 is CPU only
        FRAMEWORK.MmDetection: [DEVICE.MmDetection.CPU],
        FRAMEWORK.MmDetection_GPU: [DEVICE.MmDetection.CPU, DEVICE.MmDetection_GPU.CUDA],
        FRAMEWORK.TensorRT: [DEVICE.TensorRT.CPU, DEVICE.TensorRT.CUDA]
    },
    ARCHITECTURE.ARMV7HF: {}
}


# =====================================================================================================================
# model types
class MODEL_TYPE:
    INTERNAL = "internal"
    TF_V1 = "TF_V1"
    TF_V2 = "TF_V2"
    TF_YOLO = "TF_YOLO"
    OPENVINO = "OPENVINO"
    TF_LITE = "TF_LITE"
    TORCH = "TORCH"
    KERAS = "KERAS"
    CAFFE = "CAFFE"
    TensorRT = "TensorRT"
    OTHER = "other"


# =====================================================================================================================
# object keys
class KEY:
    # detection object keys
    CLASS_ID = "class_id"
    SCORE = "confidence"
    LABEL = "label"
    TLWH = "rect"
    ROI_ID = 'roi_id'
    ROI_NAME = "roi_name"

    #
    STATUS = "status"

    # tracking object keys
    TID = "tid"
    TRACE = "trace"
    COLOR = "color"

    # recognition property object keys
    ATTRIBUTE = "attribute"
    PROPERTY = "property"


# ----- [MQTT & REDIS] ----------------------------------------------------------
class PREFIX:
    class REDIS:
        LOCAL = "redis"
        STATUS = "viso/container_status"

    class MQTT:
        LOCAL = "viso/mqtt"
        CLOUD = "viso_cloud/mqtt"

        DEBUG = "viso_debug/mqtt"


# ----- [MQTT & REDIS] ----------------------------------------------------------

AVAILABLE_METADATA_MODES = ["mqtt", "redis"]


class MetaDataMODE:
    MQTT = "mqtt"
    REDIS = "redis"


# =====================================================================================================================
# publish object keys
class PublishData:
    ROI = "roi"
    TRACK = "track"
    COUNT = "count"
    SAVE_PATH = "save_path"
    DETECT = "result"
    TIME_STAMP = "timestamp"
    FRAME_ID = "frame_id"
    REFERENCE_POINT = "ref_pos"
    OCR = "ocr"
    BARCODE = "barcode"
    CROWD = "crowd"
    CROWD_POINTS = "crowd_points"
    CHANGED_OBJS = "changed_objs"
    ANALYTICS = "analytics"
    ANALYTICS_ROI = "analytics_roi"
