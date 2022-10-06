from queue import LifoQueue

import cv2
import numpy

from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead
from parameters import MODE, IMG_SIZE, RUN, RunStatus
from subsys_read_user_input import ModeStatus
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import RCStatus


class TelloSensors:
    """
    Retrieves the attitude and battery level from onboard Tello sensors
    Calls the high-level functions from the Tello API to handle Takeoff, Landing and Emergency flight modes
    """

    tello: Tello = None
    battery: int = 0
    roll: int = 0
    pitch: int = 0
    yaw: int = 0

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


class FrameReader:
    frames_queue: LifoQueue = LifoQueue()
    frame_reader: BackgroundFrameRead = None

    @classmethod
    def setup(cls, frame_reader: BackgroundFrameRead):
        cls.frame_reader = frame_reader

    @classmethod
    def update_frame(cls):
        if cls.frame_reader.stopped:
            RunStatus.value = RUN.STOP
        else:
            cls.frames_queue.put_nowait(cls.frame_reader.frame)

    @classmethod
    def flush_old_frames(cls):
        cls.frames_queue = LifoQueue()

    @classmethod
    def get_most_recent_frame(cls) -> numpy.ndarray:
        raw_frame = cls.frames_queue.get()
        frame = cv2.resize(raw_frame, IMG_SIZE)
        cls.flush_old_frames()
        return frame

