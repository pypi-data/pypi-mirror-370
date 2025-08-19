import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from jacobi import Frame
from jacobi_vision import ImageType, ColorImage
from jacobi_vision.drivers import VirtualCameraDriver

from .ball import detect_ball


def load_frame(path: Path) -> Frame:
    """Load a frame from a .json file into a numpy array."""
    with path.open('r') as f:
        data = json.load(f)
    return Frame.from_matrix(data['matrix'])


def to_numpy(frame: Frame) -> np.ndarray:
    return np.array(frame.matrix).reshape((4, 4)).T


def minimize_rotation_point(a, b) -> tuple[Frame, np.ndarray, float]:
    """Solves the problem of type x * a = b * y, with affine transformations x and b as well as positions a and y."""

    def objective(params):
        x = to_numpy(Frame.from_euler(*params[0:6]))
        y = np.concatenate((params[6:9], [1.0]))  # To homogenous coordinate

        error = 0.0
        for point, frame in zip(a, b):
            point_4d = np.concatenate((point, [1.0]))
            diff = x @ point_4d - to_numpy(frame) @ y
            error += np.inner(diff, diff)
        return error

    initial_params = np.zeros(9)
    result = minimize(objective, initial_params)

    robot_to_camera = Frame.from_euler(*result.x[0:6])
    tcp_to_marker = result.x[6:9]

    accuracy = np.sqrt(result.fun)
    return robot_to_camera, tcp_to_marker, accuracy


def analyze(args):
    print('Analyze images and calculate extrinsic calibration.')
    marker_positions, tcp_frames = [], []

    # Load images
    camera = VirtualCameraDriver(args.directory, image_type=ImageType.RGBD, intrinsics=args.directory / 'calibration.json')
    for i, image_path in enumerate(camera.image_list):
        image = camera.get_image(idx=i)

        # Detect the marker
        match args.marker:
            case 'ball':
                position, (labeled) = detect_ball(image)
            case _:
                raise NotImplementedError

        labeled_image = ColorImage(labeled)
        labeled_image.save(image_path.parent / f'{image_path.stem}-labeled.jpg')

        if position is None:
            continue

        marker_positions.append(position)

        # Load TCP frame
        tcp_frame_path = image_path.parent / f"{str(image_path.stem).replace('color', 'tcp-frame')}.json"
        tcp_frames.append(load_frame(tcp_frame_path))

    robot_to_camera, _, accuracy = minimize_rotation_point(marker_positions, tcp_frames)
    print(f'Using {len(tcp_frames)} images and TCP frames.')
    print(f'Robot to Camera transformation: {robot_to_camera}')

    if args.project:
        from jacobi import Planner, Studio  # pylint: disable=import-outside-toplevel

        planner = Planner.load_from_studio(args.project)
        robot = planner.environment.get_robot()
        camera = planner.environment.get_camera()

        camera.origin = robot.origin * robot_to_camera
        print(f'Camera origin in world frame: {camera.origin}')

        if args.studio:
            studio = Studio()
            studio.update_camera(camera)

    print(f'Calibration accuracy: {1000 * accuracy:0.1f} [mm]')
