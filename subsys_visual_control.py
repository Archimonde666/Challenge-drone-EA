from parameters import RAD2DEG, FPS
from subsys_read_user_input import RCStatus
from subsys_select_target_marker import MarkerStatus


class VisualControl:
    """
    Automatically controls the Tello.
    Input: MarkerStatus class containing information about the selected ARUCO code (distance and angles between
    marker and UAV, etc...)
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 0.1
    KP_UD_CTRL = 0.3
    KI_UD_CTRL = 0.4
    KP_YAW_CTRL = 2 * 10**-3
    previous_i_dy = 0
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

        # Left/Right velocity control
        # dx = target_marker.m_distance * numpy.sin(target_marker.m_angle)
        dx = target_marker.dx
        RCStatus.a = int(cls.KP_LR_CTRL * dx)

        # Forward/Backward velocity control
        rb_threshold = 40
        RCStatus.b = rb_threshold - int(rb_threshold * abs(target_marker.m_angle)/70)

        # Up/Down velocity control
        dy = target_marker.dy
        i_dy = cls.previous_i_dy + dy * 1 / FPS
        cls.previous_i_dy = i_dy
        RCStatus.c = - int(cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)

        # Yaw velocity control
        RCStatus.d = int(RAD2DEG * cls.KP_YAW_CTRL * target_marker.dx)
