from parameters import DEG2RAD, RAD2DEG
from subsys_read_user_input import RCStatus
import numpy as np


class VisualControl:
    KP_LR_CTRL = 0.2
    KP_YAW_CTRL = 0.5
    cmp = 0

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def run(cls, target_marker, drone_status):
        if target_marker.id == -1:
            RCStatus.c = 0
            RCStatus.d = int(0.99*RCStatus.d)    # yaw_velocity
            RCStatus.a = int(0.99*RCStatus.a)    # left_right_velocity
            # wait for the drone to pass the last Gate
            if cls.cmp > 10:
                RCStatus.b = int(0.99*RCStatus.b)  # for_back_velocity

            cls.cmp = cls.cmp + 1
            return RCStatus
        cls.cmp = 0
        # Get the angle and the distance between the marker and the drone
        phi = int(target_marker.m_angle * RAD2DEG)
        distance = target_marker.m_distance

        # Yaw velocity control
        RCStatus.d = int(cls.KP_YAW_CTRL * phi)

        # Left/Right velocity control
        dx = distance * np.sin(phi*DEG2RAD)
        RCStatus.a = int(cls.KP_LR_CTRL * dx)

        # Forward/Backward velocity control
        rb_threshold = 40
        RCStatus.b = rb_threshold - int(rb_threshold * abs(phi)/70)

        # Up/Down velocity control
        RCStatus.c = 0

        return RCStatus

    @classmethod
    def stop(cls):
        pass
