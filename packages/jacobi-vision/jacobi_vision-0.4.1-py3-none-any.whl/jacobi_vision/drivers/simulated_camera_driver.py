import base64
from time import sleep
from typing import Iterable

import cv2
import numpy as np

from jacobi import Camera, CameraStream, Studio
from ..image import Image, ImageType, ColorImage, DepthImage, RGBDImage


class SimulatedCameraDriver:
    """Simulated camera driver for Jacobi Studio."""

    def __init__(self, camera: Camera | None = None, image_type: ImageType | None = None, studio: Studio | None = None, **kwargs):
        self.camera = camera
        self.image_type = image_type if image_type else ImageType.Color
        self.studio = studio if studio else Studio()
        self.intrinsics = self.camera.intrinsics if self.camera else None

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def get_color(self) -> np.ndarray:
        encoded = self.studio.get_camera_image_encoded(CameraStream.Color, self.camera)
        image = np.frombuffer(base64.b64decode(encoded), np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def get_depth(self) -> np.ndarray:
        encoded = self.studio.get_camera_image_encoded(CameraStream.Depth, self.camera)
        decoded = base64.decodebytes(bytes(encoded, 'utf-8'))
        image = np.frombuffer(decoded, np.float32).reshape((480, 640, 4))
        return np.copy(image[:, :, :1].squeeze(-1))

    def get_image(self, image_type: ImageType | None = None) -> Image | None:
        match (image_type if image_type else self.image_type):
            case ImageType.Color:
                return ColorImage(data=self.get_color(), intrinsics=self.intrinsics)
            case ImageType.Depth:
                return DepthImage(data=self.get_depth(), intrinsics=self.intrinsics)
            case _:
                return RGBDImage(color=self.get_color(), depth=self.get_depth(), intrinsics=self.intrinsics)

    async def get_image_async(self, image_type: ImageType | None = None) -> Image | None:
        return self.get_image(image_type)

    def stream(self, image_type: ImageType | None = None) -> Iterable[Image]:
        while True:
            yield self.get_image(image_type)
            sleep(0.1)  # [s]
