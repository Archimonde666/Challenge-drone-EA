from parameters import RAD2DEG, FPS, MODE
from RCStatus import RCStatus
from MarkersMemory import MarkersMemory
from TargetMarkerSelector import TargetMarkerSelector
from MarkerStatus import MarkerStatus


class VisualControl:
    """
    Automatically controls the Tello.
    Input: MarkerStatus class containing information about the selected ARUCO code (distance and angles between
    marker and UAV, etc...)
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 0.1
    KP_UD_CTRL = 0.1
    KI_UD_CTRL = 0.05
    KP_YAW_CTRL = 1 * 10**-3
    previous_i_dy = 0
    cmp: int = 0  # Counts the successive frames without any detected marker

    @classmethod
    def run(cls, target_marker: MarkerStatus) -> type(RCStatus):
        if MarkersMemory.passing_gate:
            dx = 0
            dy = 0
        else:
            dx = target_marker.center_pt[0] + TargetMarkerSelector.offset[0] - TargetMarkerSelector.target_point[0]
            dy = target_marker.center_pt[1] + TargetMarkerSelector.offset[1] - TargetMarkerSelector.target_point[1]

        if MarkersMemory.current_target_marker_id != -1:
            # Left/Right velocity control
            RCStatus.a = int(cls.KP_LR_CTRL * dx)

            # Forward/Backward velocity control
            rb_threshold = 40
            RCStatus.b = rb_threshold - int(rb_threshold * abs(target_marker.m_angle)/70)

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * 1 / FPS
            cls.previous_i_dy = i_dy
            RCStatus.c = - int(cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)

            # Yaw velocity control
            RCStatus.d = int(RAD2DEG * cls.KP_YAW_CTRL * dx)
        elif not MarkersMemory.passing_gate:
            print('Sequence finished, landing')
            MODE.status = MODE.LAND
