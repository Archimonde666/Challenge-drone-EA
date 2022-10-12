import numpy

from DJITelloPy.djitellopy.tello import Tello
from parameters import MODE, IMG_SIZE, SIGHT_H_ANGLE, SIGHT_V_ANGLE, DEG2RAD, DRONE_POS, ScreenPosition, ENV
from parameters import SIGHT_V_ANGLE_OFFSET


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
    height: int = 0
    ax: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    x: float = 0.0
    yaw_reference: int = 0

    trajectory_point: ScreenPosition = (0, 0)
    frame: numpy.ndarray = numpy.ndarray(IMG_SIZE)

    @classmethod
    def setup(cls, tello: Tello):
        cls.tello = tello
        cls.reset_position_estimate()

    @classmethod
    def run(cls, dt):
        cls.update_trajectory_point()
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
        cls.estimate_position(dt)

    @classmethod
    def update_state(cls):
        state = cls.tello.get_current_state()
        cls.battery = state['bat']
        cls.roll = state['roll']
        cls.pitch = state['pitch']
        cls.yaw = state['yaw']
        cls.height = state['h']
        cls.ax = - state['agx'] / 100

        if ENV.status == ENV.SIMULATION:
            vx = state['vgx'] / 100
            vy = state['vgy'] / 100
            cls.vx = - vx * numpy.sin(cls.yaw * DEG2RAD) + vy * numpy.cos(cls.yaw * DEG2RAD)
        elif ENV.status == ENV.REAL:
            vx = state['vgx'] / 10
            vy = state['vgy'] / 10
            cls.vx = vx * numpy.cos(cls.yaw * DEG2RAD) + vy * numpy.sin(cls.yaw * DEG2RAD)

    @classmethod
    def reset_position_estimate(cls):
        cls.x = 0

    @classmethod
    def estimate_position(cls, dt):
        cls.x = cls.x + cls.vx * dt
        if abs(cls.x) > 100:
            cls.reset_position_estimate()

    @classmethod
    def update_trajectory_point(cls):
        dx = int((IMG_SIZE[0] / 2) * (cls.roll * DEG2RAD / SIGHT_H_ANGLE))
        y = int(IMG_SIZE[1] * numpy.tan(SIGHT_V_ANGLE_OFFSET + (cls.pitch * DEG2RAD))
                / (numpy.tan((SIGHT_V_ANGLE / 2) + SIGHT_V_ANGLE_OFFSET + (cls.pitch * DEG2RAD))
                   + numpy.tan((SIGHT_V_ANGLE / 2) - SIGHT_V_ANGLE_OFFSET - (cls.pitch * DEG2RAD))))
        cls.trajectory_point = ScreenPosition((DRONE_POS[0] + dx, y))

    @classmethod
    def __get_dict__(cls) -> dict:
        sensors: dict = {'Battery': cls.battery,
                         'Roll': cls.roll,
                         'Pitch': cls.pitch,
                         'Yaw': cls.yaw,
                         'Height': cls.height,
                         'ax': round(cls.ax, 6),
                         'vx': round(cls.vx, 3),
                         'vy': round(cls.vy, 3),
                         'x': round(cls.x, 3)}
        return sensors
