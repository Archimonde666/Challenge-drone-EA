import numpy

from DJITelloPy.djitellopy.tello import Tello
from parameters import MODE, IMG_SIZE, SIGHT_H_ANGLE, SIGHT_V_ANGLE, DEG2RAD
from RCStatus import RCStatus
from TelloActuators import TelloActuators


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

    target_point_offset: tuple[int, int] = (0, 0)
    frame: numpy.ndarray = numpy.ndarray(IMG_SIZE)

    @classmethod
    def setup(cls, tello: Tello):
        cls.tello = tello

    @classmethod
    def run(cls):
        cls.update_target_point()
        if MODE.status == MODE.TAKEOFF:
            MODE.status = MODE.MANUAL_FLIGHT
            cls.tello.takeoff()
        elif MODE.status == MODE.LAND:
            cls.tello.land()
            MODE.status = -1
        elif MODE.status == MODE.EMERGENCY:
            cls.tello.emergency()
            MODE.status = -1
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
        if MODE.status == MODE.MANUAL_FLIGHT or MODE.status == MODE.AUTO_FLIGHT:
            TelloActuators.update_rc_command(rc_status)

    @classmethod
    def update_target_point(cls):
        dx = int((IMG_SIZE[0]/2) * (cls.roll * DEG2RAD / SIGHT_H_ANGLE))
        dy = int((IMG_SIZE[1]/2) * (cls.pitch * DEG2RAD / SIGHT_V_ANGLE))
        cls.target_point_offset = (dx, dy)

    @classmethod
    def __get_dict__(cls) -> dict:
        sensors: dict = {'Battery': cls.battery,
                         'Roll': cls.roll,
                         'Pitch': cls.pitch,
                         'Yaw': cls.yaw}
        return sensors
