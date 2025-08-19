from typing import Iterable

import numpy as np

from python_phoxi_sensor import PhoXiSensor

from jacobi import Camera, Studio, Intrinsics
from jacobi_vision import Image, ImageType, ColorImage, DepthImage, RGBDImage


class PhoXiCameraDriver:
    """Photoneo PhoXi camera driver."""

    def __init__(self, name: str, image_type: ImageType | None = None, camera: Camera | None = None, sync_with_studio: bool = False, **kwargs):
        self.name = name
        self.image_type = image_type if image_type else ImageType.RGBD
        self.camera = camera
        self.studio = Studio() if sync_with_studio else None
        self.intrinsics = None  # Only after first image

        self.sensor = PhoXiSensor(name)

    def __del__(self):
        self.disconnect()

    def connect(self) -> bool:
        return self.sensor.start()

    def disconnect(self):
        self.sensor.stop()

    def _read_frame(self, image_type: ImageType | None = None) -> Image:
        match (image_type if image_type else self.image_type):
            case ImageType.Color:
                result = ColorImage(data=np.array(self.sensor.get_texture()))
            case ImageType.Depth:
                result = DepthImage(data=np.array(self.sensor.get_depth_map()))
            case _:
                result = RGBDImage(color=np.array(self.sensor.get_texture()), depth=np.array(self.sensor.get_depth_map()))

        # Update intrinsics
        intr = self.sensor.intrinsics
        self.intrinsics = Intrinsics(intr.fx, intr.fy, intr.cx, intr.cy, result.width, result.height)
        result.camera_matrix = self.intrinsics.as_matrix()
        return result

    def get_image(self, image_type: ImageType | None = None) -> Image | None:
        if not self.sensor.frames():
            return None
        return self._read_frame(image_type)

    async def get_image_async(self, image_type: ImageType | None = None) -> Image | None:
        if not await self.sensor.frames_async():
            return None
        return self._read_frame(image_type)

    def stream(self, image_type: ImageType | None = None) -> Iterable[Image]:
        while True:
            yield self.get_image(image_type)
