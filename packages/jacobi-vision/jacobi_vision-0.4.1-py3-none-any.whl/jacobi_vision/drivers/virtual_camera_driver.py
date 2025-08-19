from itertools import chain
import json
import logging
from pathlib import Path
from random import choice
from typing import Iterable

from jacobi import Camera, Intrinsics, Studio
from ..image import ColorImage, DepthImage, Image, ImageType, RGBDImage


class VirtualCameraDriver:
    """Virutal camera driver to load images from the file system."""

    def __init__(
        self,
        path: Path,
        image_type: ImageType | None = None,
        intrinsics: Intrinsics | Path | None = None,
        camera: Camera | None = None,
        sync_with_studio: bool = False,
        **kwargs,
    ):
        self.image_type = image_type if image_type else ImageType.Color
        self.camera = camera
        self.studio = Studio() if sync_with_studio else None
        self.intrinsics = self.load_intrinsics_from_file(intrinsics) if isinstance(intrinsics, Path) else intrinsics

        match self.image_type:
            case ImageType.Color:
                self.image_list = list(chain(path.rglob('*.png'), path.rglob('*.jpg'), path.rglob('*.jpeg')))
            case ImageType.Depth:
                self.image_list = list(path.rglob('*.npy'))
            case ImageType.RGBD:
                color_images = list(chain(path.rglob('*color.png'), path.rglob('*color.jpg'), path.rglob('*color.jpeg')))
                self.image_list = list(filter(lambda p: (p.parent / f"{p.stem.replace('color', 'depth')}.npy").exists(), color_images))

        self.image_list.sort()

        logging.info('%s Images found', len(self.image_list))

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    @staticmethod
    def load_intrinsics_from_file(path: Path):
        with path.open('r') as f:
            data = json.load(f)

        return Intrinsics(
            data['focal_length_x'], data['focal_length_y'],
            data['optical_center_x'], data['optical_center_y'],
            data['width'], data['height'],
        )

    def get_image(self, image_type: ImageType | None = None, idx: int | None = None) -> Image | None:
        if idx is None:
            image_path = choice(self.image_list)
        else:
            if idx >= len(self.image_list):
                return None

            image_path = self.image_list[idx]

        match (image_type if image_type else self.image_type):
            case ImageType.RGBD:
                return RGBDImage.load_from_file(image_path, intrinsics=self.intrinsics)
            case ImageType.Depth:
                return DepthImage.load_from_file(image_path, intrinsics=self.intrinsics)
            case _:
                return ColorImage.load_from_file(image_path, intrinsics=self.intrinsics)

    async def get_image_async(self, image_type: ImageType | None = None, idx: int | None = None) -> Image | None:
        return self.get_image(image_type, idx)

    def stream(self, image_type: ImageType | None = None) -> Iterable[Image]:
        for i in range(len(self.image_list)):
            try:
                yield self.get_image(image_type, i)
            except IndexError:
                return
