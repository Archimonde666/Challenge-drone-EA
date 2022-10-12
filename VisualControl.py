import numpy

from parameters import RAD2DEG, ENV
from RCStatus import RCStatus
from MarkersMemory import MarkersMemory
from TelloSensors import TelloSensors
from MarkerStatus import MarkerStatus


class VisualControl:
    """
    Automatically controls the Tello.
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 0.001
    KI_LR_CTRL = 0.0005
    KP_FB_CTRL = 0.5
    KP_UD_CTRL = 0.1
    KI_UD_CTRL = 0.01
    # KP_YAW_CTRL = 1 * 10**-3
    KP_YAW_CTRL = 0
    KI_YAW_CTRL = 30
    previous_i_h = 0
    previous_i_dh = 0
    previous_i_dx = 0
    previous_i_dy = 0
    cmp: int = 0  # Counts the successive frames without any detected marker

    @classmethod
    def run(cls, dt: float) -> type(RCStatus):
        dh = MarkerStatus.height_lr_delta
        dx = MarkerStatus.target_pt[0] - TelloSensors.trajectory_point[0]
        dy = MarkerStatus.target_pt[1] - TelloSensors.trajectory_point[1]

        if MarkersMemory.passing_gate:
            RCStatus.a = 0
            if ENV.status == ENV.SIMULATION:
                RCStatus.b = 25
            elif ENV.status == ENV.REAL:
                RCStatus.b = int(10 * (1 - TelloSensors.x))
            RCStatus.c = 0
            RCStatus.d = 0
            if (ENV.status == ENV.SIMULATION and TelloSensors.x > 2.5) \
                    or (ENV.status == ENV.REAL and abs(1 - TelloSensors.x) < 0.1):
                MarkersMemory.update_target()

        elif (MarkerStatus.height > 55 or MarkerStatus.width > 55) \
                and dh == 0 and dx < 5:
            print('Passing gate...')
            MarkersMemory.passing_gate = True
            MarkersMemory.get_new_target()
            RCStatus.reset()
            TelloSensors.reset_position_estimate()

        else:
            # Left/Right velocity control
            i_dx = cls.previous_i_dx + dx * dt
            cls.previous_i_dx = i_dx
            RCStatus.a = int(RAD2DEG * cls.KP_LR_CTRL * dx + cls.KI_LR_CTRL * i_dx)

            # Forward/Backward velocity control
            # rb_threshold = 40
            # RCStatus.b = rb_threshold - int(rb_threshold * abs(target_marker.m_angle)/70)
            RCStatus.b = int(cls.KP_FB_CTRL * (60 - MarkerStatus.width))
            # print(RCStatus.b)

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * dt
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

            i_h = 0.7 * cls.previous_i_h + h * dt
            RCStatus.d = int(
                (cls.KP_YAW_CTRL * h + cls.KI_YAW_CTRL * i_h)
                * numpy.sqrt(numpy.abs(250 * numpy.sign(h) - dx2) / 250))
