from parameters import ScreenPosition, Angle, Distance, MARKER_OFFSET, MODE
from MarkersDetector import MarkersDetector
from MarkersMemory import MarkersMemory
from MarkerStatus import MarkerStatus
from RCStatus import RCStatus
# from TelloSensors import TelloSensors

from typing import List

import numpy
# import cv2


class TargetMarkerSelector:
    """
    Selects the marker to reach first from the list of markers detected by the Tello onboard camera,
    then returns the corresponding MarkerStatus class filled with the position of the Tello relatively
    to this marker
    """

    @classmethod
    def setup(cls):
        MarkerStatus.reset()

    @classmethod
    def run(cls, frame):
        target_marker_id, corners = cls._get_target_marker(MarkersDetector.ids, MarkersDetector.corners)
        if target_marker_id == -1:
            # If no markers are found on the current frame, the short-term memory provides
            # data on the last screen position of the targeted marker
            try:
                target_marker_id = MarkersMemory.current_target_marker_id
                corners = MarkersMemory.markers_screen_pos[str(target_marker_id)]['corners']
                reliability = MarkersMemory.markers_screen_pos[str(target_marker_id)]['reliability']
                if reliability < 0.25:
                    MarkerStatus.reset()
                    if MODE.status == MODE.AUTO_FLIGHT:
                        print('Target marker lost for too long, switching back to manual mode')
                        RCStatus.reset()
                        MODE.status = MODE.MANUAL_FLIGHT
                    return
                br, bl, tl, tr = corners[0], corners[1], corners[2], corners[3]
            except KeyError:
                MarkerStatus.reset()
                if MODE.status == MODE.AUTO_FLIGHT:
                    print('Target marker never seen before, switching back to manual mode')
                    RCStatus.reset()
                    MODE.status = MODE.MANUAL_FLIGHT
                return
        else:
            br, bl, tl, tr = corners[0], corners[1], corners[2], corners[3]

        center_pt = cls._get_midpoint([br, bl, tl, tr])
        left_pt = cls._get_midpoint([bl, tl])
        right_pt = cls._get_midpoint([br, tr])
        bottom_pt = cls._get_midpoint([br, bl])
        top_pt = cls._get_midpoint([tl, tr])

        height = cls._length_segment(bottom_pt, top_pt)
        l_height = cls._length_segment(tl, bl)
        r_height = cls._length_segment(tr, br)
        width = cls._length_segment(left_pt, right_pt)
        t_width = cls._length_segment(tl, tr)
        b_width = cls._length_segment(bl, br)

        offset = ScreenPosition((int(MARKER_OFFSET[0] * width),
                                 int(MARKER_OFFSET[1] * height)))
        target_pt = ScreenPosition((center_pt[0] + offset[0],
                                    center_pt[1] + offset[1]))

        # update output
        MarkerStatus.id = target_marker_id
        MarkerStatus.corners = corners
        MarkerStatus.center_pt = center_pt
        MarkerStatus.left_pt = left_pt
        MarkerStatus.right_pt = right_pt
        MarkerStatus.bottom_pt = bottom_pt
        MarkerStatus.top_pt = top_pt
        MarkerStatus.offset = offset
        MarkerStatus.target_pt = target_pt
        MarkerStatus.height = height
        MarkerStatus.height_lr_delta = l_height - r_height
        MarkerStatus.width = width
        MarkerStatus.width_tb_delta = t_width - b_width

    @staticmethod
    def _get_target_marker(ids, corners) -> (int, List[ScreenPosition]):
        target_id = -1
        target_corners = []

        if ids is not None:
            for i in range(len(ids)):
                marker_id = ids[i][0]
                if (marker_id == MarkersMemory.current_target_marker_id
                        and MarkersMemory.current_target_marker_id != -1):
                    target_id = marker_id
                    target_corners = corners[i][0]
        return target_id, target_corners

    @staticmethod
    def _get_midpoint(corners: List[ScreenPosition]) -> ScreenPosition:
        # corners = [p1,p2,p3,p4] with pi = (xi, yi)
        xc = yc = 0
        n = len(corners)
        for x, y in corners:
            xc += x
            yc += y
        xc = int(xc / n)
        yc = int(yc / n)
        midpoint = (xc, yc)
        return ScreenPosition(midpoint)

    @staticmethod
    def _angle_between(p1: ScreenPosition, p2: ScreenPosition) -> Angle:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        alpha = numpy.arctan2(dy, dx)
        return alpha

    @staticmethod
    def _length_segment(p1: ScreenPosition, p2: ScreenPosition) -> Distance:
        length = numpy.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return Distance(length)
