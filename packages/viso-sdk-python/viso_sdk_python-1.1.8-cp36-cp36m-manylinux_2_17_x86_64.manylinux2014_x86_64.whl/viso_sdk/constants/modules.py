class Module:
    """
        modules container mqtt and redis ports as individual
    """

    class Region:
        type = 'region-of-interest'

        class RoiType:
            polygon = 'polygon'
            rectangle = 'rectangle'
            section = 'section'

    class RegionSelection:
        type = 'region-selection'

    class MultipleObjectDetection:
        type = "multiple-object-detection"

    class VideoFeed:
        type = "video-feed"

    class ColorRecognition:
        type = 'color-recognition'

    class ReIdObjectTracking:
        type = 'reid-object-tracking'

    class ObjectCount:
        type = "object-count"

    """
        modules publish metadata in redis string together
    """

    class Roi:
        type = 'roi'

        class RoiType:
            polygon = 'polygon'
            rectangle = 'rectangle'
            section = 'section'

    class VideoSource:
        type = "video-source"

    class ObjectDetection:
        type = "object-detection"

    class ObjectTracking:
        type = 'object-tracking'

    class FrameViewer:
        type = "frame-viewer"

    """
        modules which has v2 UI
    """

    class VFVideoFile:
        type = "video-feed-video-file"

    class VFIpCamera:
        type = "video-feed-ip-camera"

    class VFUsbCamera:
        type = "video-feed-usb-camera"

    class VideoViewer:
        type = "video-view"

    class VideoFeedVideoFile:
        type = "video-feed-video-file"

    class VideoFeedIpCamera:
        type = "video-feed-ip-camera"

    class VideoFeedUSBCamera:
        type = "video-feed-usb-camera"

    class DetectionTracking:
        type = "detection-tracking"

    class ObjectDetectionTracking:
        type = "object-detection-tracking"

    class OpticalCharacterRecognition:
        type = "optical-character-recognition"

    class BarcodeReader:
        type = "barcode-reader"

    class CrowdEstimation:
        type = "crowd-estimation"

    class ObjectIdentifier:
        type = "object-identifier"

    class ObjectChangeMonitoring:
        type = "object-change-monitoring"

    class ObjectMovementAnalytics:
        type = "object-movement-analytics"

    class CppDetectionTracking:
        type = "cpp-detection-tracking"
