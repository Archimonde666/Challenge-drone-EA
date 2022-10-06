import math
from typing import List, NewType

Distance = NewType('Pixels', float)
Angle = NewType('Radians', float)
ScreenPosition = NewType('tuple(Pixels, Pixels)', tuple[int, int])

RED: tuple = (255, 0, 0)
GREEN: tuple = (0, 255, 0)
BLUE: tuple = (0, 0, 255)

DEG2RAD: float = math.pi / 180
RAD2DEG: float = 180 / math.pi

FPS: int = 120
# Simulator frame dimensions : (480, 640, 3)
# Real Tello frame dimensions : (720, 960, 3)
IMG_SIZE: tuple[int, int] = (640, 480)
SCREEN_SIZE: tuple[int, int] = (800, 480)
DRONE_POS: ScreenPosition = ScreenPosition((IMG_SIZE[0] // 2, IMG_SIZE[1] // 2))

LAPS: bool = True
highest_marker_index: int = 10

SIGHT_V_ANGLE: Angle = Angle(42 * DEG2RAD)
SIGHT_H_ANGLE: Angle = Angle(53.6 * RAD2DEG)


class ENV:
    REAL: int = 0
    SIMULATION: int = 1
    status: int = REAL


class RUN:
    STOP: bool = False
    START: bool = True


class MODE:
    EMERGENCY: int = 0
    TAKEOFF: int = 1
    LAND: int = 2
    MANUAL_FLIGHT: int = 3
    AUTO_FLIGHT: int = 4


class RunStatus:
    value: bool = RUN.STOP


def merge_dicts(dict_list: List[dict]) -> dict:
    merged_dict: dict = {}
    for dictionary in dict_list:
        merged_dict.update(dictionary)
    return merged_dict
