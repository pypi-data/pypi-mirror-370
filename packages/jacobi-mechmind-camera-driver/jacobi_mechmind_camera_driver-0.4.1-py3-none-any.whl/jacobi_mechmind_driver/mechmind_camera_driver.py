from typing import Iterable

from mecheye.area_scan_3d_camera import Camera, CameraIntrinsics, CameraResolutions, Frame2D, Frame3D, Frame2DAnd3D
import numpy as np

from jacobi import Camera as JacobiCamera, Intrinsics, Studio
from jacobi_vision import Image, ImageType, ColorImage, DepthImage, RGBDImage


class MechMindCameraDriver:
    """Mech-Mind camera driver."""

    def __init__(self, image_type: ImageType | None = None, camera: JacobiCamera | None = None, sync_with_studio: bool = False, **kwargs):
        self.image_type = image_type if image_type else ImageType.RGBD
        self.camera = camera
        self.studio = Studio() if sync_with_studio else None
        self.intrinsics: Intrinsics | None = None

        self.sensor = None

    def __del__(self):
        self.disconnect()

    def connect(self) -> bool:
        camera_infos = Camera.discover_cameras()
        if not camera_infos:
            return False

        self.sensor = Camera()
        error_status = self.sensor.connect(camera_infos[0])
        if not error_status.is_ok():
            return False

        resolutions = CameraResolutions()
        self.sensor.get_camera_resolutions(resolutions)

        intrinsics = CameraIntrinsics()
        self.sensor.get_camera_intrinsics(intrinsics)

        matix = intrinsics.depth.camera_matrix
        self.intrinsics = Intrinsics(matix.fx, matix.fy, matix.cx, matix.cy, resolutions.depth.width, resolutions.depth.height)
        # dist = intrinsics.depth.camera_distortion
        # self.intrinsics.distortion_parameters = [dist.k1, dist.k2, dist.p1, dist.p2, dist.k3]
        return True

    def disconnect(self):
        if self.sensor:
            self.sensor.disconnect()

    def _get_color(self, frame: Frame2D | Frame2DAnd3D) -> np.ndarray:
        if isinstance(frame, Frame2DAnd3D):
            frame = frame.frame_2d()
        color_image = frame.get_color_image()
        if not color_image:
            raise RuntimeError('Could not get color frame.')
        return color_image.data()

    def _get_depth(self, frame: Frame3D | Frame2DAnd3D) -> np.ndarray:
        if isinstance(frame, Frame2DAnd3D):
            frame = frame.frame_3d()
        depth_map = frame.get_depth_map()
        if not depth_map:
            raise RuntimeError('Could not get depth frame.')
        return depth_map.data() / 1000.0

    def get_image(self, image_type: ImageType | None = None) -> Image | None:
        if not self.sensor:
            return None

        match (image_type if image_type else self.image_type):
            case ImageType.Color:
                frame_2d = Frame2D()
                self.sensor.capture_2d(frame_2d)
                return ColorImage(data=self._get_color(frame_2d), intrinsics=self.intrinsics)
            case ImageType.Depth:
                frame_3d = Frame3D()
                self.sensor.capture_3d(frame_3d)
                return DepthImage(data=self._get_depth(frame_3d), intrinsics=self.intrinsics)
            case _:
                frame_3d = Frame3D()
                frame_left, frame_right = Frame2D(), Frame2D()
                self.sensor.capture_3d(frame_3d)
                self.sensor.capture_stereo_2d(frame_left, frame_right, isRectified=True)
                color = self._get_color(frame_left)
                depth = self._get_depth(frame_3d)
                return RGBDImage(color, depth, intrinsics=self.intrinsics)

    async def get_image_async(self, image_type: ImageType | None = None) -> Image | None:
        return self.get_image(image_type)

    def stream(self, image_type: ImageType | None = None) -> Iterable[Image]:
        while True:
            yield self.get_image(image_type)
