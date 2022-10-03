import av
import cv2
import numpy

from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead, TelloException
from parameters import MODE, IMG_SIZE
from subsys_read_user_input import ModeStatus
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import RCStatus
from typing import Union


class TelloSensors:
    """
    Retrieves the attitude and battery level from onboard Tello sensors
    Calls the high-level functions from the Tello API to handle Takeoff, Landing and Emergency flight modes
    """

    tello: Tello = None
    CAP: Union[cv2.VideoCapture,
               BackgroundFrameRead] = None
    battery: int = 0
    roll: int = 0
    pitch: int = 0
    yaw: int = 0

    frame: numpy.ndarray = numpy.ndarray(IMG_SIZE)

    @classmethod
    def setup(cls, tello: Tello):
        cls.tello = tello

    @classmethod
    def run(cls):
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
    def update_frame(cls):
        """Thread worker function to retrieve frames using PyAV
        Internal method, you normally wouldn't call this yourself.
        """
        # noinspection PyUnresolvedReferences
        try:
            for frame in cls.tello.container.decode(video=0):
                cls.frame = numpy.array(frame.to_image())
                if cls.tello.stopped:
                    cls.tello.container.close()
                    break
        except av.error.ExitError:
            raise TelloException('Do not have enough frames for decoding, please try again or increase video fps '
                                 'before get_frame_read()')

    @classmethod
    def update_rc(cls, rc_status: RCStatus):
        if ModeStatus.value == MODE.MANUAL_FLIGHT or ModeStatus.value == MODE.AUTO_FLIGHT:
            TelloActuators.update_rc_command(rc_status)

    @classmethod
    def __get_dict__(cls) -> dict:
        sensors: dict = {'Battery': cls.battery,
                         'Roll': cls.roll,
                         'Pitch': cls.pitch,
                         'Yaw': cls.yaw}
        return sensors
