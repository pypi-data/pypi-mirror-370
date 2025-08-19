import cv2
import numpy as np
from scipy.optimize import least_squares


def fit_sphere(points: np.ndarray, radius: float):
    def residuals(params, points):
        return np.linalg.norm(points - params, axis=1) - radius

    initial_guess = np.mean(points, axis=0)
    return least_squares(residuals, initial_guess, args=(points,), ftol=1e-5, xtol=1e-5)


def ransac_sphere(points: np.ndarray, radius: float, iterations: int, threshold=0.005, minimum_points=64):
    best_params = None
    best_inliers = []
    best_std_dev = None

    if points.shape[0] < minimum_points:
        return best_params, best_inliers, best_std_dev

    for _ in range(iterations):
        sample = points[np.random.choice(points.shape[0], 4, replace=False)]
        result = fit_sphere(sample, radius=radius)

        distances = np.linalg.norm(points - result.x, axis=1)
        inlier_idxs = np.where(np.abs(distances - radius) <= threshold)
        inliers = points[inlier_idxs]
        std_dev = np.std(distances[inlier_idxs]) if len(inlier_idxs[0]) else 0.0

        if len(inliers) > len(best_inliers):
            best_params = result.x
            best_inliers = inliers
            best_std_dev = std_dev

    return best_params, best_inliers, best_std_dev


def detect_circles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT,
        dp=1,              # Inverse ratio of accumulator resolution
        minDist=30,        # Minimum distance between centers
        param1=100,        # Upper threshold for edge detection
        param2=80,         # Threshold for center detection
        minRadius=8, maxRadius=256,
    )
    return np.uint16(np.around(circles))[0] if circles is not None else []


def create_dense_mask(image_shape, circle):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    center, radius = (circle[0], circle[1]), circle[2]
    cv2.circle(mask, center, radius, 255, -1)
    return mask


def detect_ball(image, radius=0.03, visualize=False):
    circles = detect_circles(image.color)
    labeled = image.color.copy()

    best_std_dev = 0.002  # Upper threshold
    best_position = None
    # best_inliers = None
    best_circle = None
    for circle in circles:
        cv2.circle(labeled, (circle[0], circle[1]), circle[2], (0, 255, 0), 1)

        mask = create_dense_mask(image.color.shape, circle)
        points = image.to_point_cloud(mask=mask)

        position, _, std_dev = ransac_sphere(points, radius=radius, iterations=32)
        if std_dev is None:
            continue

        if best_std_dev is None or std_dev < best_std_dev:
            best_std_dev = std_dev
            best_position = position
            # best_inliers = inliers
            best_circle = circle

    # if visualize:
    #     import open3d as o3d
    #     pcd = o3d.geometry.PointCloud()
    #     pcd.points = o3d.utility.Vector3dVector(best_inliers if best_inliers is not None else [])
    #     o3d.visualization.draw_geometries([pcd])

    if best_circle is not None:
        cv2.circle(labeled, (best_circle[0], best_circle[1]), best_circle[2], (0, 255, 255), 2)
        cv2.circle(labeled, (best_circle[0], best_circle[1]), 2, (255, 0, 0), 2)

    return best_position, (labeled)
