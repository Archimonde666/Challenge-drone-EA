import numpy

from parameters import ENV, MODE
from RCStatus import RCStatus
from MarkersMemory import MarkersMemory
from TelloSensors import TelloSensors
from MarkerStatus import MarkerStatus


class VisualControl:
    """
    Automatically controls the Tello.
    Output: RCStatus class containing velocity commands that will be forwarded to the UAV
    """
    KP_LR_CTRL = 5 * 60
    KI_LR_CTRL = 0
    KP_FB_CTRL = 4
    KP_UD_CTRL = 0.2
    KI_UD_CTRL = 0.02
    # KP_YAW_CTRL = 1 * 10**-3
    KP_YAW_CTRL = 0.20
    KI_YAW_CTRL = 0.003
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
        d = numpy.sqrt(dx ** 2 + dy ** 2)
        # print(d)

        if MODE.status == MODE.AUTO_RESEARCH:
            RCStatus.a = 0
            RCStatus.b = 20
            RCStatus.c = 0
            RCStatus.d = -50

        elif MarkersMemory.passing_gate:
            RCStatus.a = 0
            if ENV.status == ENV.SIMULATION:
                RCStatus.b = 25
            elif ENV.status == ENV.REAL:
                RCStatus.b = 60
            RCStatus.c = 0
            RCStatus.d = 0
            if (ENV.status == ENV.SIMULATION and TelloSensors.x > 2.5) \
                    or (ENV.status == ENV.REAL and TelloSensors.x > 0.7):
                MarkersMemory.get_new_target()
                MarkersMemory.update_target()
                cls.previous_i_h = 0
                cls.previous_i_dh = 0
                cls.previous_i_dx = 0
                cls.previous_i_dy = 0

        elif (MarkerStatus.height > 55 or MarkerStatus.width > 55) \
                and abs(dh) < 0.5 and d < 20:
            print('Passing gate...')
            MarkersMemory.passing_gate = True
            RCStatus.reset()
            TelloSensors.reset_position_estimate()

        else:
            # Left/Right velocity control
            i_dh = 0.7 * cls.previous_i_dh + dh * dt
            cls.previous_i_dh = i_dh
            RCStatus.a = -int(cls.KP_LR_CTRL * dh + cls.KI_LR_CTRL * i_dh)

            # Forward/Backward velocity control
            # rb_threshold = 40
            # RCStatus.b = rb_threshold - int(rb_threshold * abs(target_marker.m_angle)/70)
            RCStatus.b = int(
                numpy.sign(70 - max(MarkerStatus.width, MarkerStatus.height)) * cls.KP_FB_CTRL * numpy.sqrt(
                    abs(70 - max(MarkerStatus.width, MarkerStatus.height))))

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * dt
            cls.previous_i_dy = i_dy
            RCStatus.c = - int(cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)

            # Yaw velocity control
            i_dx = 0.7 * cls.previous_i_dx + dx * dt
            cls.previous_i_dx = i_dx
            RCStatus.d = int(cls.KP_YAW_CTRL * dx + cls.KI_YAW_CTRL * i_dx)
