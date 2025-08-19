"""
Modeul for UPC (User PC)
"""
from __future__ import annotations
import _bindings
import numpy
import typing
__all__: list[str] = ['GripperDeviceName', 'MasterArm', 'MasterArmDeviceName', 'initialize_device']
class MasterArm:
    class ControlInput:
        target_operating_mode: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.int32]]
        target_position: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]
        target_torque: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]
        def __init__(self) -> None:
            ...
    class State:
        def __init__(self) -> None:
            ...
        @property
        def T_left(self) -> numpy.ndarray[tuple[typing.Literal[4], typing.Literal[4]], numpy.dtype[numpy.float64]]:
            ...
        @property
        def T_right(self) -> numpy.ndarray[tuple[typing.Literal[4], typing.Literal[4]], numpy.dtype[numpy.float64]]:
            ...
        @property
        def button_left(self) -> _bindings.DynamixelBus.ButtonState:
            ...
        @property
        def button_right(self) -> _bindings.DynamixelBus.ButtonState:
            ...
        @property
        def gravity_term(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            ...
        @property
        def operating_mode(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.int32]]:
            ...
        @property
        def q_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            ...
        @property
        def qvel_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            ...
        @property
        def torque_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            ...
    DOF: typing.ClassVar[int] = 14
    DeviceCount: typing.ClassVar[int] = 16
    LeftToolId: typing.ClassVar[int] = 129
    MaximumTorque: typing.ClassVar[float] = 4.0
    RightToolId: typing.ClassVar[int] = 128
    TorqueScaling: typing.ClassVar[float] = 0.5
    def __init__(self, dev_name: str = '/dev/rby1_master_arm') -> None:
        ...
    def initialize(self, verbose: bool = False) -> list[int]:
        ...
    def set_control_period(self, control_period: float) -> None:
        ...
    def set_model_path(self, model_path: str) -> None:
        ...
    def start_control(self, control: typing.Callable[[MasterArm.State], MasterArm.ControlInput]) -> None:
        ...
    def stop_control(self) -> None:
        ...
def initialize_device(device_name: str) -> None:
    """
    Initialize a USB device with the given name
    """
GripperDeviceName: str = '/dev/rby1_gripper'
MasterArmDeviceName: str = '/dev/rby1_master_arm'
