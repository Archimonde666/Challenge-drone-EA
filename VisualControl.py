import numpy

from parameters import RAD2DEG, FPS
from RCStatus import RCStatus
from MarkersMemory import MarkersMemory
from TelloSensors import TelloSensors
from MarkerStatus import MarkerStatus
# from TelloActuators import TelloActuators


class VisualControl:
    """
    Automatically controls the Tello.
    Input: MarkerStatus class containing information about the selected ARUCO code (distance and angles between
    marker and UAV, etc...)
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 0.005
    KI_LR_CTRL = 0.001
    KP_FB_CTRL = 0.5
    KP_UD_CTRL = 0.1
    KI_UD_CTRL = 0.05
    # KP_YAW_CTRL = 1 * 10**-3
    KP_YAW_CTRL = 0
    KI_YAW_CTRL = 200
    previous_i_h = 0
    previous_i_dh = 0
    previous_i_dx = 0
    previous_i_dy = 0
    cmp: int = 0  # Counts the successive frames without any detected marker

    @classmethod
    def run(cls) -> type(RCStatus):
        if MarkersMemory.passing_gate:
            dh = 0
            dx = 0
            dy = 0

            # RCStatus.reset()
            # if MarkersMemory.cmp < 1:
            # TelloActuators.tello.send_command_without_return('forward 50')
            # TelloActuators.tello.move_forward(50)
        else:
            dh = MarkerStatus.height_lr_delta
            dx = MarkerStatus.target_pt[0] - TelloSensors.trajectory_point[0]
            dy = MarkerStatus.target_pt[1] - TelloSensors.trajectory_point[1]

        if MarkersMemory.current_target_marker_id != -1:
            # Left/Right velocity control
            # i_dh = cls.previous_i_dh + dh * 1 / FPS
            # cls.previous_i_dh = dh
            # RCStatus.a = - int(cls.KP_LR_CTRL * dh + cls.KI_LR_CTRL * i_dh)

            i_dx = cls.previous_i_dx + dx * 1 / FPS
            cls.previous_i_dx = i_dx
            RCStatus.a = int(RAD2DEG * cls.KP_LR_CTRL * dx + cls.KI_LR_CTRL * i_dx)

            # Forward/Backward velocity control
            # rb_threshold = 40
            # RCStatus.b = rb_threshold - int(rb_threshold * abs(target_marker.m_angle)/70)
            RCStatus.b = int(cls.KP_FB_CTRL * (70 - MarkerStatus.width))

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * 1 / FPS
            cls.previous_i_dy = i_dy
            RCStatus.c = - int(cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)

            # Yaw velocity control
            h = dh
            if dx > 250:
                dx2 = 250
            elif dx < -250:
                dx2 = -250
            else:
                dx2 = dx

            i_h = 0.8 * cls.previous_i_h + h * 1 / FPS
            RCStatus.d = int(
                (cls.KP_YAW_CTRL * h + cls.KI_YAW_CTRL * i_h)
                * numpy.sqrt(numpy.abs(250 * numpy.sign(h) - dx2) / 250))
            # i_dx = cls.previous_i_dx + dx * 1 / FPS
            # cls.previous_i_dx = i_dx
            # RCStatus.d = int(RAD2DEG * cls.KP_YAW_CTRL * dx + cls.KI_YAW_CTRL * i_dx)
