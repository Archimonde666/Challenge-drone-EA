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
    KP_LR_CTRL: float = 0.0
    KI_LR_CTRL: float = 0.0
    KP_FB_CTRL: float = 0.0
    KP_UD_CTRL: float = 0.0
    KI_UD_CTRL: float = 0.0
    KP_YAW_CTRL: float = 0.0
    KI_YAW_CTRL: float = 0.0

    previous_i_h: float = 0.0
    previous_i_dh: float = 0.0
    previous_i_dx: float = 0.0
    previous_i_dy: float = 0.0
    forgetting_factor: float = 0.0

    auto_research_yaw_rate: int = 0
    passing_gate_forward_speed: int = 0
    passing_gate_distance: float = 0.0
    marker_size_target: int = 0

    marker_size_threshold: int = 0
    marker_offset_tolerance: int = 0
    marker_misalignment_tolerance: float = 0.0

    @classmethod
    def setup(cls):
        if ENV.status == ENV.REAL:
            cls.KP_LR_CTRL = 5 * 60
            cls.KI_LR_CTRL = 0
            cls.KP_FB_CTRL = 4
            cls.KP_UD_CTRL = 0.2
            cls.KI_UD_CTRL = 0.02
            cls.KP_YAW_CTRL = 0.20
            cls.KI_YAW_CTRL = 0.003

            cls.forgetting_factor = 0.7

            cls.auto_research_yaw_rate = -50
            cls.passing_gate_forward_speed = 60
            cls.passing_gate_distance = 0.7
            cls.marker_size_target = 70

            cls.marker_size_threshold: int = 55
            cls.marker_offset_tolerance: int = 20
            cls.marker_misalignment_tolerance: float = 0.5

        elif ENV.status == ENV.SIMULATION:
            cls.KP_LR_CTRL = 5 * 60
            cls.KI_LR_CTRL = 0
            cls.KP_FB_CTRL = 4
            cls.KP_UD_CTRL = 0.2
            cls.KI_UD_CTRL = 0.02
            cls.KP_YAW_CTRL = 0.20
            cls.KI_YAW_CTRL = 0.003

            cls.forgetting_factor = 0.7

            cls.auto_research_yaw_rate = -20
            cls.passing_gate_forward_speed = 25
            cls.passing_gate_distance = 2.5
            cls.marker_size_target = 70
            cls.marker_size_threshold = 55

            cls.marker_size_threshold: int = 55
            cls.marker_offset_tolerance: int = 20
            cls.marker_misalignment_tolerance: float = 0.5

    @classmethod
    def run(cls, dt: float) -> type(RCStatus):
        dh = MarkerStatus.height_lr_delta
        dx = MarkerStatus.target_pt[0] - TelloSensors.trajectory_point[0]
        dy = MarkerStatus.target_pt[1] - TelloSensors.trajectory_point[1]
        d = numpy.sqrt(dx ** 2 + dy ** 2)

        if MODE.status == MODE.AUTO_RESEARCH:
            RCStatus.a = 0
            RCStatus.b = 0
            RCStatus.c = 0
            RCStatus.d = cls.auto_research_yaw_rate

        elif MarkersMemory.passing_gate:
            RCStatus.a = 0
            RCStatus.b = cls.passing_gate_forward_speed
            RCStatus.c = 0
            RCStatus.d = 0
            if TelloSensors.x > cls.passing_gate_distance:
                MarkersMemory.get_new_target()
                MarkersMemory.update_target()
                cls.previous_i_h = 0
                cls.previous_i_dh = 0
                cls.previous_i_dx = 0
                cls.previous_i_dy = 0

        elif max(MarkerStatus.height, MarkerStatus.width) > cls.marker_size_threshold \
                and abs(dh) < cls.marker_misalignment_tolerance \
                and d < cls.marker_offset_tolerance:
            print('Passing gate...')
            MarkersMemory.passing_gate = True
            RCStatus.reset()
            TelloSensors.reset_position_estimate()

        else:
            # Left/Right velocity control
            i_dh = cls.forgetting_factor * cls.previous_i_dh + dh * dt
            cls.previous_i_dh = i_dh
            RCStatus.a = - int(cls.KP_LR_CTRL * dh + cls.KI_LR_CTRL * i_dh)

            # Forward/Backward velocity control
            RCStatus.b = int(cls.KP_FB_CTRL
                             * numpy.sign(cls.marker_size_target - max(MarkerStatus.width, MarkerStatus.height))
                             * numpy.sqrt(abs(cls.marker_size_target - max(MarkerStatus.width, MarkerStatus.height))))

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * dt
            cls.previous_i_dy = i_dy
            RCStatus.c = - int(cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)

            # Yaw velocity control
            i_dx = cls.forgetting_factor * cls.previous_i_dx + dx * dt
            cls.previous_i_dx = i_dx
            RCStatus.d = int(cls.KP_YAW_CTRL * dx + cls.KI_YAW_CTRL * i_dx)
