from .simulated_camera_driver import SimulatedCameraDriver
from .virtual_camera_driver import VirtualCameraDriver

other_drivers = []

try:
    from jacobi_mechmind_driver import MechMindCameraDriver  # noqa: F401
    other_drivers.append('MechMindCameraDriver')
except ModuleNotFoundError:
    pass

try:
    from jacobi_phoxi_driver import PhoXiCameraDriver  # noqa: F401
    other_drivers.append('PhoXiCameraDriver')
except ModuleNotFoundError:
    pass

try:
    from jacobi_realsense_driver import RealSenseCameraDriver  # noqa: F401
    other_drivers.append('RealSenseCameraDriver')
except ModuleNotFoundError:
    pass


def CameraDriver(model: str, **kwargs):  # noqa: N802
    match model.lower():
        case 'mechmind':
            return MechMindCameraDriver(**kwargs)
        case 'phoxi':
            return PhoXiCameraDriver(**kwargs)
        case 'realsense':
            return RealSenseCameraDriver(**kwargs)
        case 'simulated':
            return SimulatedCameraDriver(**kwargs)
        case 'virtual':
            return VirtualCameraDriver(**kwargs)
        case _:
            raise NotImplementedError(f'Camera model not supported: {model}')


__all__ = ['CameraDriver', 'SimulatedCameraDriver', 'VirtualCameraDriver'] + other_drivers
