import cv2
import numpy

from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead
from parameters import MODE, IMG_SIZE, RUN, RunStatus, SIGHT_H_ANGLE, SIGHT_V_ANGLE, DEG2RAD
from subsys_read_user_input import ModeStatus, RCStatus
from subsys_tello_actuators import TelloActuators
from typing import Union


class TelloSensors:
    """
    Retrieves the attitude and battery level from onboard Tello sensors
    Calls the high-level functions from the Tello API to handle Takeoff, Landing and Emergency flight modes
    """

    tello: Tello = None
    frame_reader = None
    CAP: Union[cv2.VideoCapture,
               BackgroundFrameRead] = None
    battery: int = 0
    roll: int = 0
    pitch: int = 0
    yaw: int = 0

    target_point_offset: tuple[int, int] = (0, 0)

    frame: numpy.ndarray = numpy.ndarray(IMG_SIZE)

    @classmethod
    def setup(cls, tello: Tello, frame_reader: BackgroundFrameRead):
        cls.tello = tello
        cls.frame_reader = frame_reader

    @classmethod
    def run(cls):
        if cls.frame_reader.stopped:
            RunStatus.value = RUN.STOP
        else:
            cls.frame = cv2.resize(cls.frame_reader.frame, IMG_SIZE)
        cls.update_target_point()
        if ModeStatus.value == MODE.TAKEOFF:
            ModeStatus.value = MODE.MANUAL_FLIGHT
            cls.tello.takeoff()
        elif ModeStatus.value == MODE.LAND:
            cls.tello.land()
            ModeStatus.value = -1
        elif ModeStatus.value == MODE.EMERGENCY:
            cls.tello.emergency()
            ModeStatus.value = -1
        cls.update_state()

    @classmethod
    def update_state(cls):
        state = cls.tello.get_current_state()
        cls.battery = state['bat']
        cls.roll = state['roll']
        cls.pitch = state['pitch']
        cls.yaw = state['yaw']

    @classmethod
    def update_rc(cls, rc_status: RCStatus):
        if ModeStatus.value == MODE.MANUAL_FLIGHT or ModeStatus.value == MODE.AUTO_FLIGHT:
            TelloActuators.update_rc_command(rc_status)

    @classmethod
    def update_target_point(cls):
        dx = int((IMG_SIZE[0]/2) * (cls.roll * DEG2RAD / (SIGHT_H_ANGLE/2)))
        dy = int((IMG_SIZE[1]/2) * (cls.pitch * DEG2RAD / (SIGHT_V_ANGLE/2)))
        cls.target_point_offset = (dx, dy)

    @classmethod
    def __get_dict__(cls) -> dict:
        sensors: dict = {'Battery': cls.battery,
                         'Roll': cls.roll,
                         'Pitch': cls.pitch,
                         'Yaw': cls.yaw}
        return sensors
