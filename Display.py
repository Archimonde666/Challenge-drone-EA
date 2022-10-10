import numpy
import pygame
import cv2
from parameters import RED, GREEN, BLUE, IMG_SIZE, SCREEN_SIZE, ScreenPosition, DRONE_POS, DEG2RAD
from parameters import SIGHT_V_ANGLE, SIGHT_V_ANGLE_OFFSET, SIGHT_H_ANGLE
from MarkerStatus import MarkerStatus
from TargetMarkerSelector import TargetMarkerSelector
from TelloSensors import TelloSensors

from typing import Any


class Display:
    """
    Displays the frame acquired by the Tello camera and the marker detection results
    on a pygame window
    """
    # Parameters
    SCREEN: pygame.Surface = None

    LEFT_MARGIN: int = 5
    TOP_MARGIN: int = 0
    INTER_LINE: int = 20

    FONT_PANEL_INFO: pygame.font.Font = None

    # global Variables
    pos_img_in_screen: tuple = (0, 0)
    current_line: int = TOP_MARGIN
    log_dict: dict = {}

    @classmethod
    def setup(cls):
        # Init pygame
        pygame.init()
        pygame.font.init()
        cls.FONT_PANEL_INFO = pygame.font.Font('freesansbold.ttf', 18)

        # create pygame screen
        shift_left = SCREEN_SIZE[0] - IMG_SIZE[0]
        cls.pos_img_in_screen = (shift_left, 0)
        cls.SCREEN = pygame.display.set_mode(SCREEN_SIZE)

    @classmethod
    def run(cls, frame: numpy.ndarray, variables_dict: dict):
        cls.draw(frame)
        cls.SCREEN.fill([0, 0, 0])
        for key in variables_dict:
            cls._log(f"{key}: ", f"{variables_dict[key]}")
        frame = numpy.rot90(frame)
        frame = numpy.flipud(frame)
        frame = pygame.surfarray.make_surface(frame)
        cls._update_log()
        cls.SCREEN.blit(frame, cls.pos_img_in_screen)

    @classmethod
    def _log(cls, title: str, value: Any):
        """ We use the title argument as key in dictionary to save the position of the log in screen"""
        if title in cls.log_dict:
            cls.log_dict[title]['value'] = value
        else:
            next_line = cls.current_line + cls.INTER_LINE
            position = (cls.LEFT_MARGIN, next_line)
            cls.log_dict[title] = {"pos": position, 'value': value}
            cls.current_line = next_line

    @classmethod
    def _update_log(cls):
        for title, item in cls.log_dict.items():
            text = f"{title} {item['value']}"
            panel_info = cls.FONT_PANEL_INFO.render(text, True, RED)
            cls.SCREEN.blit(panel_info, item['pos'])

    @classmethod
    def draw(cls, frame: numpy.ndarray):
        if MarkerStatus.id == -1:
            return
        cv2.aruco.drawDetectedMarkers(frame,
                                      numpy.array([[MarkerStatus.corners]]),
                                      numpy.array([[MarkerStatus.id]]),
                                      borderColor=RED)
        cv2.line(frame,
                 MarkerStatus.top_pt,
                 MarkerStatus.bottom_pt,
                 RED, 2)
        cv2.line(frame,
                 MarkerStatus.left_pt,
                 MarkerStatus.right_pt,
                 RED, 2)

        top_pt_with_offset = tuple(numpy.array(MarkerStatus.top_pt) + numpy.array(TargetMarkerSelector.offset))
        bottom_pt_with_offset = tuple(numpy.array(MarkerStatus.bottom_pt) + numpy.array(TargetMarkerSelector.offset))
        left_pt_with_offset = tuple(numpy.array(MarkerStatus.left_pt) + numpy.array(TargetMarkerSelector.offset))
        right_pt_with_offset = tuple(numpy.array(MarkerStatus.right_pt) + numpy.array(TargetMarkerSelector.offset))

        cv2.line(frame,
                 top_pt_with_offset,
                 bottom_pt_with_offset,
                 RED, 2)
        cv2.line(frame,
                 left_pt_with_offset,
                 right_pt_with_offset,
                 RED, 2)

        pitch = TelloSensors.pitch * DEG2RAD
        horizon_y = numpy.tan(SIGHT_V_ANGLE_OFFSET + pitch) / (
                    numpy.tan((SIGHT_V_ANGLE / 2) + SIGHT_V_ANGLE_OFFSET + pitch)
                    + numpy.tan((SIGHT_V_ANGLE / 2) - SIGHT_V_ANGLE_OFFSET - pitch))
        lh = (0, horizon_y)
        rh = (IMG_SIZE[0], horizon_y)

        # cv2.line(frame,
        #          lh,
        #          rh,
        #          (0, 0, 0), 1)

        target_point = ScreenPosition((DRONE_POS[0] + TelloSensors.target_point_offset[0],
                                       DRONE_POS[1] + TelloSensors.target_point_offset[1]))
        cv2.drawMarker(frame,
                       target_point,
                       color=GREEN,
                       markerType=cv2.MARKER_CROSS,
                       thickness=2)
        cv2.drawMarker(frame,
                       DRONE_POS,
                       color=RED,
                       markerType=cv2.MARKER_CROSS,
                       thickness=2)
        cv2.line(frame,
                 target_point,
                 TargetMarkerSelector.marker_pos,
                 BLUE, 2)
