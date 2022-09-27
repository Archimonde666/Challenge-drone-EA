import math
from typing import List


# color parameters
RED: tuple = (255, 0, 0)
BLUE: tuple = (0, 0, 255)

DEG2RAD: float = math.pi/180
RAD2DEG: float = 180/math.pi

FPS: int = 120
IMG_SIZE: tuple = (640, 480)
DRONE_POS: tuple = (IMG_SIZE[0]//2, 480)
SCREEN_SIZE: tuple = (800, 480)


class ENV:
    REAL: int = 0
    SIMULATION: int = 1
    DEBUG: int = 2
    status: int = SIMULATION


class RUN:
    STOP: bool = False
    START: bool = True


class MODE:
    EMERGENCY: int = 0
    TAKEOFF: int = 1
    LAND: int = 2
    FLIGHT: int = 3


class RunStatus:
    value: bool = RUN.STOP


def merge_dicts(dict_list: List[dict]) -> dict:
    merged_dict: dict = {}
    for dictionary in dict_list:
        merged_dict.update(dictionary)
    return merged_dict
