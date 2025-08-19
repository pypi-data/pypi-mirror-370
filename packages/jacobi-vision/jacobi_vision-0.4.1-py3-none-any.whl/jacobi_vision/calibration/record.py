from datetime import datetime
import json

from jacobi_vision.drivers import CameraDriver


def RobotDriver(model: str, host: str):  # noqa: N802
    from jacobi import Robot, Planner  # pylint: disable=import-outside-toplevel
    robot = Robot.from_model(model)
    planner = Planner(robot, 0.01)

    if 'abb' in model:
        from jacobi.drivers import ABBDriver  # pylint: disable=import-outside-toplevel
        return robot, ABBDriver(planner, host=host)
    if 'fanuc' in model:
        from jacobi.drivers import FanucDriver  # pylint: disable=import-outside-toplevel
        return robot, FanucDriver(planner, host=host)
    if 'universal' in model:
        from jacobi.drivers import UniversalDriver  # pylint: disable=import-outside-toplevel
        return robot, UniversalDriver(planner, host=host)
    if 'yaskawa' in model:
        from jacobi.drivers import YaskawaDriver  # pylint: disable=import-outside-toplevel
        return robot, YaskawaDriver(planner, host=host)
    raise NotImplementedError


def record(args):
    print('Record an image.')

    camera = CameraDriver(args.camera, name=args.name)

    args.output.mkdir(exist_ok=True)
    datetime_id = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    image_path = args.output / f'{datetime_id}-color.png'
    frame_path = args.output / f'{datetime_id}-tcp-frame.json'

    # Get robot joint position
    if args.robot:
        robot, driver = RobotDriver(model=args.robot, host=args.robot_host)
        tcp_frame = robot.calculate_tcp(driver.current_joint_position)

        with frame_path.open('w') as f:
            json.dump({'type': 'frame', 'matrix': tcp_frame.matrix}, f)

    # Get image
    image = camera.get_image()
    image.save(image_path)

    # Save intrinsic camera calibration
    calibration_path = args.output / 'calibration.json'
    if not calibration_path.exists():
        camera.intrinsics.save(calibration_path)
