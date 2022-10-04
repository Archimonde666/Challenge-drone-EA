from parameters import DEG2RAD, RAD2DEG
from subsys_read_user_input import RCStatus
from subsys_select_target_marker import MarkerStatus
import numpy


class VisualControl:
    """
    Automatically controls the Tello.
    Input: MarkerStatus class containing information about the selected ARUCO code (distance and angles between
    marker and UAV, etc...)
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 0.2
    KP_YAW_CTRL = 0.5
    cmp: int = 0  # Counts the successive frames without any detected marker

    @classmethod
    def run(cls, target_marker: MarkerStatus) -> type(RCStatus):
        if target_marker.id == -1:  # When no markers are detected, smoothly stops the UAV
            RCStatus.c = 0                          # up_down_velocity
            RCStatus.d = int(0.99*RCStatus.d)       # yaw_velocity
            RCStatus.a = int(0.99*RCStatus.a)       # left_right_velocity
            if cls.cmp > 10:        # Waits for the UAV to pass the last Gate while decreasing its forward velocity
                RCStatus.b = int(0.99*RCStatus.b)   # for_back_velocity
            cls.cmp = cls.cmp + 1
            return RCStatus
        cls.cmp = 0

        # Gets the angle and the distance between the marker and the drone
        phi = int(target_marker.m_angle * RAD2DEG)
        distance = target_marker.m_distance

        # Yaw velocity control
        RCStatus.d = int(cls.KP_YAW_CTRL * phi)

        # Left/Right velocity control
        dx = distance * numpy.sin(phi*DEG2RAD)
        RCStatus.a = int(cls.KP_LR_CTRL * dx)

        # Forward/Backward velocity control
        rb_threshold = 40
        RCStatus.b = rb_threshold - int(rb_threshold * abs(phi)/70)

        # Up/Down velocity control
        RCStatus.c = 0
