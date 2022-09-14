import cv2
import numpy

from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead
from parameters import ENV, MODE, RUN
from subsys_read_user_input import ModeStatus
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import RCStatus
from typing import Union


class DroneStatus:
    battery = 0
    roll = 0
    pitch = 0
    yaw = 0


class TelloSensors:
    """
    Retrieves the attitude and battery level from onboard Tello sensors
    Calls the high-level functions from the Tello API to handle Takeoff, Landing and Emergency flight modes
    """

    TELLO: Tello = None
    CAP: Union[cv2.VideoCapture,
               BackgroundFrameRead] = None
    mode: int = -1

    @classmethod
    def setup(cls):
        if ENV.status == ENV.SIMULATION:
            cls.__init_sim_env()
        elif ENV.status == ENV.REAL:
            cls.__init_real_env()
        elif ENV.status == ENV.DEBUG:
            cls.__init_debug_env()

    @classmethod
    def stop(cls):
        # Call it always before finishing. To deallocate resources.
        cls.TELLO.end()

    @classmethod
    def run(cls, mode_status: ModeStatus) -> (numpy.ndarray, type(DroneStatus)):
        # input
        if mode_status.value == MODE.TAKEOFF:
            cls.TELLO.takeoff()
            mode_status.value = MODE.FLIGHT
        elif mode_status.value == MODE.LAND:
            cls.TELLO.land()
            mode_status.value = -1
        elif mode_status.value == MODE.EMERGENCY:
            cls.TELLO.emergency()
            mode_status.value = -1

        cls.mode = mode_status.value
        # output
        DroneStatus.battery = cls.TELLO.get_battery()
        DroneStatus.roll = cls.TELLO.get_roll()
        DroneStatus.pitch = cls.TELLO.get_pitch()
        DroneStatus.yaw = cls.TELLO.get_yaw()
        return cls.image(), DroneStatus

    @classmethod
    def update_rc(cls, rc_status: RCStatus):
        if cls.mode == MODE.FLIGHT:
            TelloActuators.update_rc_command(rc_status)

    @classmethod
    def image(cls) -> numpy.ndarray:
        """
        Gets the frame from the front camera of the UAV,
        or gets the frame from a webcam connected to the PC if the DEBUG mode is active
        """

        image = None
        if ENV.status == ENV.SIMULATION or ENV.status == ENV.REAL:
            if cls.CAP.stopped:
                RUN.status = RUN.STOP
            else:
                image = cls.CAP.frame

        elif ENV.status == ENV.DEBUG:
            if cls.CAP.isOpened():
                _, image = cls.CAP.read()
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                RUN.status = RUN.STOP
        return image

    # Private Methods

    @classmethod
    def __init_sim_env(cls):
        # Init Tello object that interacts with the Tello drone
        Tello.CONTROL_UDP_PORT_CLIENT = 9000
        cls.TELLO = Tello("127.0.0.1")

        cls.TELLO.connect()

        cls.TELLO.streamoff()
        cls.TELLO.streamon()

        try:
            cls.CAP = cls.TELLO.get_frame_read()
            RUN.status = RUN.START
        except:
            RUN.status = RUN.STOP

    @classmethod
    def __init_real_env(cls):
        # Init Tello object that interacts with the Tello drone
        Tello.CONTROL_UDP_PORT_CLIENT = Tello.CONTROL_UDP_PORT
        cls.TELLO = Tello("192.168.10.1")
        cls.TELLO.connect()

        # In case streaming is on. This happens when we quit this program without the escape key.
        # self.tello.set_video_resolution(Tello.RESOLUTION_480P)
        # self.tello.set_video_fps(Tello.FPS_30)
        # self.tello.set_video_bitrate(Tello.BITRATE_4MBPS)

        cls.TELLO.streamoff()
        cls.TELLO.streamon()
        try:
            cls.CAP = cls.TELLO.get_frame_read()
            RUN.status = RUN.START
        except:
            RUN.status = RUN.STOP

    @classmethod
    def __init_debug_env(cls):
        Tello.CONTROL_UDP_PORT_CLIENT = 9000
        cls.TELLO = Tello("127.0.0.1")
        cls.TELLO.connect()
        try:
            cls.CAP = cv2.VideoCapture(0)
            RUN.status = RUN.START
        except:
            print("can not detect camera!")
            RUN.status = RUN.STOP
