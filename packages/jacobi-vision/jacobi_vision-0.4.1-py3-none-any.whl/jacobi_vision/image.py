from abc import ABC, abstractmethod
from base64 import b64encode
from enum import Enum
from pathlib import Path

import cv2
import numpy as np

from jacobi import DepthMap, Intrinsics


class ImageType(str, Enum):
    """Image type regarding color and depth channels."""

    Color = 'rgb'
    Depth = 'd'
    RGBD = 'rgbd'


class Image(ABC):
    """Base image class."""

    def __init__(self, image_type: ImageType, shape: list[int], camera_matrix: np.ndarray | None = None, intrinsics: Intrinsics | None = None):
        self.image_type = image_type
        self.width = shape[1]
        self.height = shape[0]
        self.channels = shape[2] if len(shape) >= 3 else 1

        self.camera_matrix = camera_matrix if camera_matrix is not None else intrinsics.as_matrix() if intrinsics else None

    def __repr__(self) -> str:
        return f'<Image type={self.image_type} width={self.width} height={self.height}>'

    @abstractmethod
    def show(self):
        """Show the image using the PIL library. Needs to be installed separately."""

    def project(self, points: np.ndarray) -> np.ndarray:
        """Project 3D points from camera frame to 2D pixels in image frame.

        Args:
            points (np.ndarray): An n x 3 array of the points to be deprojected.

        Returns:
            np.ndarray: The n x 2 array of pixels in the image frame.
        """
        if self.camera_matrix is None:
            raise RuntimeError('Camera matrix is not defined.')

        points_normalized = points / points[:, 2:3]
        pixels = self.camera_matrix @ points_normalized.T
        return pixels.T[:, :2]

    def deproject(self, pixels: np.ndarray) -> np.ndarray:
        """Deproject 2D pixels from image frame to 3D points in camera frame.

        Args:
            pixels (np.ndarray): An n x 3 array of the pixels to be deprojected. First row are the coordinates of the pixels along the x-axis,
            second row are the coordinates of the pixels along the y-axis, and third row are the depth values for each pixel.

        Returns:
            np.ndarray: The n x 3 array of points in the camera frame.
        """
        pixels_homogeneous = np.hstack((pixels[:, :2], np.ones((pixels.shape[0], 1))))
        points_normalized = (np.linalg.inv(self.camera_matrix) @ pixels_homogeneous.T).T
        return points_normalized * pixels[:, 2:3]


class ColorImage(Image):
    """An RGB image with color data."""

    def __init__(self, data: np.ndarray, camera_matrix: np.ndarray | None = None, intrinsics: Intrinsics | None = None):
        super().__init__(ImageType.Color, data.shape, camera_matrix, intrinsics)
        self.data = data

    @staticmethod
    def load_from_file(path: Path, **kwargs):
        """Load a color image from a file path."""
        data = cv2.imread(str(path))
        if data is None:
            raise FileNotFoundError(f"Could not find image file at '{path}'.")
        return ColorImage(data=cv2.cvtColor(data, cv2.COLOR_BGR2RGB), **kwargs)

    def save(self, path: Path | str) -> None:
        data = cv2.cvtColor(self.data, cv2.COLOR_RGB2BGR) if self.channels == 3 else self.data
        cv2.imwrite(str(path), data)

    def encode(self) -> str:
        """Encode as string for Jacobi Studio visualization.

        Returns:
            str: The image encoded as a base64 string.
        """
        _, buffer = cv2.imencode('.png', cv2.cvtColor(self.data, cv2.COLOR_RGB2BGRA))
        return b64encode(buffer).decode()

    def show(self) -> None:
        from PIL import Image as PILImage  # pylint: disable=import-outside-toplevel

        img = PILImage.fromarray(self.data)
        img.show()


class BaseDepthImage(Image):
    """Internal class to share common methods for depth images."""

    def __init__(self, depth, image_type: ImageType, camera_matrix: np.ndarray | None = None, intrinsics: Intrinsics | None = None):
        super().__init__(image_type, depth.shape, camera_matrix, intrinsics)
        self.depth = depth

    def to_point_cloud(self, mask=None) -> np.ndarray:
        """Deproject all pixels to 3D points (x, y, z).

        Args:
            mask (np.ndarray): A dense binary mask of segment to include in the point cloud.

        Returns:
            np.ndarray: The n x 3 array of points in the camera frame.
        """
        if self.camera_matrix is None:
            raise RuntimeError('Camera matrix is not defined.')

        depth_tmp = self.depth.copy()
        if mask is not None:
            depth_tmp[mask == 0] = np.nan

        rows, cols = depth_tmp.shape
        x_grid, y_grid = np.meshgrid(np.arange(cols), np.arange(rows))

        x = (x_grid - self.camera_matrix[0, 2]) / self.camera_matrix[0, 0]
        y = (y_grid - self.camera_matrix[1, 2]) / self.camera_matrix[1, 1]
        points = np.stack([x * depth_tmp, y * depth_tmp, depth_tmp], axis=-1).reshape(-1, 3)

        # Filter out points with NaN z values
        valid_mask = ~np.isnan(points[:, 2]) & (points[:, 2] > 0.0)
        return points[valid_mask]

    def to_depth_map(self, scale=1) -> DepthMap:
        """Orthographically project depth map object for collision checking.

        Args:
            scale (float): Factor by which the depth map is scaled down.

        Returns:
            DepthMap: The depth map object for collision checking.
        """
        points = self.to_point_cloud()
        points_max = np.max(points, axis=0)
        points_min = np.min(points, axis=0)

        image_size = (self.width // scale, self.height // scale)
        scene_size = (points_max[0] - points_min[0], points_max[1] - points_min[1])
        max_depth = points_max[2]
        scene_center = points_min + 0.5 * (points_max - points_min)

        depth_image = DepthImage.from_point_cloud(points, image_size, scene_size, max_depth, scene_center)
        return DepthMap(depth_image.data, scene_size[0], scene_size[1])

    def deproject(self, pixels: np.ndarray) -> np.ndarray:
        """Deproject 2D pixels from image frame to 3D points in camera frame.

        Args:
            pixels (np.ndarray): An n x 2 or n x 3 array of the pixels to be deprojected. First row are the coordinates along the x-axis,
            second row are the coordinates of the pixels along the y-axis, and an optional third row are depth values for each pixel.

        Returns:
            np.ndarray: The n x 3 array of points in the camera frame.
        """
        if pixels.shape[1] == 3:
            return super().deproject(pixels)

        # Get depth values for the given pixel coordinates
        pixels = pixels.astype(int)
        depths = self.depth[pixels[:, 1], pixels[:, 0]]
        pixels_3d = np.column_stack([pixels, depths])
        return super().deproject(pixels_3d)

    def render_depth(self, min_depth: float | None = None, max_depth: float | None = None) -> ColorImage:
        """Render the depth component into a grayscale image."""
        min_depth = min_depth if min_depth is not None else np.nanmin(self.depth)
        max_depth = max_depth if max_depth is not None else np.nanmax(self.depth)
        depth_normalized = self.depth.copy()
        depth_normalized[np.isnan(depth_normalized)] = max_depth
        depth_normalized[depth_normalized == 0.0] = max_depth
        depth_normalized = 255 * (max_depth - depth_normalized) / (max_depth - min_depth)
        return ColorImage(data=depth_normalized, camera_matrix=self.camera_matrix)


class DepthImage(BaseDepthImage):
    """An RGB image with color data."""

    def __init__(self, data: np.ndarray, camera_matrix: np.ndarray | None = None, intrinsics: Intrinsics | None = None):
        super().__init__(data, ImageType.Depth, camera_matrix, intrinsics)
        self.data = self.depth

    @staticmethod
    def load_from_file(path: Path, **kwargs):
        """Load a depth image from a numpy array at the given file path."""
        return DepthImage(data=np.load(path), **kwargs)

    def save(self, path: Path | str) -> None:
        np.save(path, self.data)

    @staticmethod
    def from_point_cloud(
        points: np.ndarray,
        image_size: tuple[int, int],
        scene_size: tuple[float, float],
        max_depth: float | None = None,
        scene_center=(0.0, 0.0),
        **kwargs,
    ):
        """Create a depth image by rendering a point cloud orthographically.

        Args:
            points (np.ndarray): An n x 3 array of the points in camera frame.
            image_size (tuple[int, int]): Width and height of the image.
            scene_size (tuple[float, float]): Width and eight of the complete scene to render.
            max_depth (float): Maximum depth of the depth image. Calculated automatically if None.
            scene_center (tuple[float, float]): Center of the depth map.

        Returns:
            DepthImage: The rendered depth image.
        """
        if points.shape[0] == 0:
            return DepthImage(data=np.full(image_size[::-1], max_depth), **kwargs)

        if max_depth is None:
            max_depth = np.max(points[:, 2])

        depth_buffer = np.full(image_size[::-1], max_depth)

        # Pre-compute grid cell sizes and scene boundaries
        pixel_width = scene_size[0] / image_size[0]
        pixel_height = scene_size[1] / image_size[1]
        scene_origin = (scene_center[0] - 0.5 * scene_size[0], scene_center[1] + 0.5 * scene_size[1])

        # Project all points to pixel coordinates at once
        pixel_x = ((points[:, 0] - scene_origin[0]) / pixel_width).astype(np.int32)
        pixel_y = ((scene_origin[1] - points[:, 1]) / pixel_height).astype(np.int32)

        # Extract valid points image boundaries
        valid_points = ((pixel_x >= 0) & (pixel_x < image_size[0]) & (pixel_y >= 0) & (pixel_y < image_size[1]))
        valid_x = pixel_x[valid_points]
        valid_y = pixel_y[valid_points]
        valid_depths = points[valid_points, 2]

        # Use efficient in-place minimum operation to update depth buffer
        # This automatically handles the case of multiple points per pixel
        np.minimum.at(depth_buffer, (valid_y, valid_x), valid_depths)
        return DepthImage(data=depth_buffer, **kwargs)

    def show(self) -> None:
        self.render_depth().show()


class RGBDImage(BaseDepthImage):
    """An RGBD image with color and depth data."""

    def __init__(self, color: np.ndarray, depth: np.ndarray, camera_matrix: np.ndarray | None = None, intrinsics: Intrinsics | None = None):
        super().__init__(depth, ImageType.RGBD, camera_matrix, intrinsics)
        self.color = color
        self.channels = 4

    def apply(self, alpha=1.0, beta=0.0):
        self.color = np.clip(alpha * self.color.astype(np.uint16) + beta, 0, 255).astype(np.uint8)

    @staticmethod
    def load_from_file(color_path: Path, **kwargs):
        """Load an RGBD image from two image files: A color image and a depth image as a numpy array. Given the path of the color image,
           the depth path is transformed by replacing 'color' with 'depth' in the filename and using the `.npy` suffix.
        """
        color_data = cv2.imread(str(color_path))
        if color_data is None:
            raise FileNotFoundError(f"Could not find image file at '{color_path}'.")
        depth_path = color_path.parent / f"{color_path.stem.replace('color', 'depth')}.npy"
        return RGBDImage(color=cv2.cvtColor(color_data, cv2.COLOR_BGR2RGB), depth=np.load(depth_path), **kwargs)

    def save(self, color_path: Path | str) -> None:
        if isinstance(color_path, str):
            color_path = Path(color_path)

        color_data = cv2.cvtColor(self.color, cv2.COLOR_RGB2BGR) if self.channels == 3 else self.color
        depth_path = color_path.parent / f"{color_path.stem.replace('color', 'depth')}.npy"
        cv2.imwrite(str(color_path), color_data)
        np.save(depth_path, self.depth)

    def show(self) -> None:
        from PIL import Image as PILImage  # pylint: disable=import-outside-toplevel

        img_color = PILImage.fromarray(self.color)
        img_depth = PILImage.fromarray(self.render_depth().data)

        combined_image = PILImage.new('RGB', (img_color.width + img_depth.width, img_color.height))
        combined_image.paste(img_color, (0, 0))
        combined_image.paste(img_depth, (img_color.width, 0))
        combined_image.show()
