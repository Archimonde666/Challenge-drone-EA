import cv2
from typing import List

import numpy


class DetectedMarkersStatus:
    """
    Contains data to describe a list of several markers
    """
    corners = []
    ids = []


# subsystem
class MarkersDetected:
    """
    Detects every marker on the frame coming from the Tello front camera,
    then returns a single DetectedMarkersStatus class containing data for all detected markers
    """
    PARAM_DRAW_MARKERS: bool = True

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def run(cls, frame: numpy.ndarray) -> (type(DetectedMarkersStatus), numpy.ndarray):
        cp_frame = frame.copy()
        corners, ids = cls.__find_markers(cp_frame)
        if cls.PARAM_DRAW_MARKERS and ids is not None:
            cls.__draw_markers(cp_frame, corners, ids)
        DetectedMarkersStatus.ids = ids
        DetectedMarkersStatus.corners = corners
        return DetectedMarkersStatus, cp_frame

    @classmethod
    def stop(cls):
        pass

    @classmethod
    def __find_markers(cls, frame: numpy.ndarray) -> (List[tuple], List[int]):
        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        return corners, ids

    @classmethod
    def __draw_markers(cls, frame: numpy.ndarray, corners: List[tuple], ids: List[int]):
        cv2.aruco.drawDetectedMarkers(frame, corners, ids, borderColor=(100, 0, 240))
