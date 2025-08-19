from typing import Iterable

import cv2
import numpy as np
import pyrealsense2 as rs

from jacobi import Camera, Intrinsics, Studio
from jacobi_vision import Image, ImageType, ColorImage, DepthImage, RGBDImage


class RealSenseCameraDriver:
    """Intel RealSense camera driver."""

    DEFAULT_CONFIG = {
        'color_image_width': 640,
        'color_image_height': 480,
        'depth_image_width': 640,
        'depth_image_height': 480,
        'frames_per_second': 30,
    }
    INITIAL_WAIT = 10  # [s]

    def __init__(
        self,
        image_type: ImageType | None = None,
        camera: Camera | None = None,
        sync_with_studio: bool = False,
        filter_depth: bool = False,
        **kwargs,
    ):
        self.image_type = image_type if image_type else ImageType.RGBD
        self.camera = camera
        self.studio = Studio() if sync_with_studio else None
        self.filter_depth = filter_depth
        self.intrinsics: Intrinsics | None = None

        self._pipeline = None

    def __del__(self):
        self.disconnect()

    def connect(self) -> bool:
        self._config = rs.config()
        self._pipeline = rs.pipeline()
        self._pipeline_wrapper = rs.pipeline_wrapper(self._pipeline)
        self._profile = self._config.resolve(self._pipeline_wrapper)
        self._align = rs.align(rs.stream.color)

        self._spatial_filter = rs.spatial_filter()
        self._hole_filling = rs.hole_filling_filter()

        device = self._profile.get_device()
        if len(device.sensors) == 0:
            return False

        # Configure the streams and start the camera
        color_width, color_height = self.DEFAULT_CONFIG['color_image_width'], self.DEFAULT_CONFIG['color_image_height']
        depth_width, depth_height = self.DEFAULT_CONFIG['depth_image_width'], self.DEFAULT_CONFIG['depth_image_height']
        self._config.enable_stream(rs.stream.color, color_width, color_height, rs.format.bgr8, self.DEFAULT_CONFIG['frames_per_second'])
        self._config.enable_stream(rs.stream.depth, depth_width, depth_height, rs.format.z16, self.DEFAULT_CONFIG['frames_per_second'])
        self._pipeline.start(self._config)

        # Get the depth scale from the depth stream
        self._depth_scale = device.first_depth_sensor().get_depth_scale()

        # Wait for auto-exposure
        for _ in range(self.INITIAL_WAIT):
            self._pipeline.wait_for_frames()

        # Get the intrinsics from the color stream
        frames = self._pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        intr = color_frame.profile.as_video_stream_profile().intrinsics
        self.intrinsics = Intrinsics(intr.fx, intr.fy, intr.ppx, intr.ppy, int(color_width), int(color_height))
        return True

    def disconnect(self) -> None:
        if self._pipeline:
            self._pipeline.stop()

    @staticmethod
    def post_process_depth_frame(depth_frame, decimation_magnitude=1.0, spatial_magnitude=2.0, spatial_smooth_alpha=0.5,
                                    spatial_smooth_delta=20, temporal_smooth_alpha=0.4, temporal_smooth_delta=20):
        # Post processing possible only on the depth_frame
        assert depth_frame.is_depth_frame()

        # Available filters and control options for the filters
        decimation_filter = rs.decimation_filter()
        spatial_filter = rs.spatial_filter()
        temporal_filter = rs.temporal_filter()

        filter_magnitude = rs.option.filter_magnitude
        filter_smooth_alpha = rs.option.filter_smooth_alpha
        filter_smooth_delta = rs.option.filter_smooth_delta

        # Apply the control parameters for the filter
        decimation_filter.set_option(filter_magnitude, decimation_magnitude)
        spatial_filter.set_option(filter_magnitude, spatial_magnitude)
        spatial_filter.set_option(filter_smooth_alpha, spatial_smooth_alpha)
        spatial_filter.set_option(filter_smooth_delta, spatial_smooth_delta)
        temporal_filter.set_option(filter_smooth_alpha, temporal_smooth_alpha)
        temporal_filter.set_option(filter_smooth_delta, temporal_smooth_delta)

        # Apply the filters
        filtered_frame = decimation_filter.process(depth_frame)
        filtered_frame = spatial_filter.process(filtered_frame)
        return temporal_filter.process(filtered_frame)

    def _get_color(self, frames) -> np.ndarray:
        color_frame = frames.get_color_frame()
        if not color_frame:
            raise RuntimeError('Could not get color frame.')
        return cv2.cvtColor(np.asanyarray(color_frame.get_data()), cv2.COLOR_BGR2RGB)

    def _get_depth(self, frames) -> np.ndarray:
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            raise RuntimeError('Could not get depth frame.')

        if self.filter_depth:
            depth_frame = self.post_process_depth_frame(depth_frame)

        return np.asanyarray(depth_frame.get_data()) * self._depth_scale

    def get_image(self, image_type: ImageType | None = None) -> Image | None:
        if not self._pipeline:
            return None

        frames = self._pipeline.wait_for_frames()
        frames = self._align.process(frames)

        match (image_type if image_type else self.image_type):
            case ImageType.Color:
                return ColorImage(data=self._get_color(frames), intrinsics=self.intrinsics)
            case ImageType.Depth:
                return DepthImage(data=self._get_depth(frames), intrinsics=self.intrinsics)
            case _:
                return RGBDImage(color=self._get_color(frames), depth=self._get_depth(frames), intrinsics=self.intrinsics)

    async def get_image_async(self, image_type: ImageType | None = None) -> Image | None:
        return self.get_image(image_type)

    def stream(self, image_type: ImageType | None = None) -> Iterable[Image]:
        while True:
            yield self.get_image(image_type)
