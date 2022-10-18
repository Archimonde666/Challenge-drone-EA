import numpy

from parameters import ENV, MODE, MARKERS_INTERVAL, GREEN, RED, BLUE, LAPS
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
    passing_gate_distance_goal: float = 0.0
    marker_size_target: int = 0

    marker_size: float = 0.0
    marker_size_threshold: int = 0
    d: float = 0.0
    marker_offset_tolerance: int = 0
    dh: float = 0.0
    marker_misalignment_tolerance: float = 0.0

    @classmethod
    def setup(cls):
        if ENV.status == ENV.REAL:
            cls.KP_LR_CTRL = 300
            cls.KI_LR_CTRL = 0
            cls.KP_FB_CTRL = 4
            cls.KP_UD_CTRL = 0.2
            cls.KI_UD_CTRL = 0.02
            cls.KP_YAW_CTRL = 0.20
            cls.KI_YAW_CTRL = 0.003

            cls.forgetting_factor = 0.7

            cls.auto_research_yaw_rate = -50
            cls.passing_gate_forward_speed = 60
            cls.passing_gate_distance_goal = 0.7

            cls.marker_size_target = 70
            cls.marker_size_threshold = 55
            cls.marker_offset_tolerance = 20
            cls.marker_misalignment_tolerance = 0.5

        elif ENV.status == ENV.SIMULATION:
            cls.KP_LR_CTRL = 200
            cls.KI_LR_CTRL = 0
            cls.KP_FB_CTRL = 7
            cls.KP_UD_CTRL = 0.1
            cls.KI_UD_CTRL = 0
            cls.KP_YAW_CTRL = 0.085  # 0.05
            cls.KI_YAW_CTRL = 0

            cls.forgetting_factor = 0.7

            cls.auto_research_yaw_rate = 15
            cls.passing_gate_forward_speed = 50
            cls.passing_gate_distance_goal = 2.5

            cls.marker_size_target = 75
            cls.marker_size_threshold = 55
            cls.marker_offset_tolerance = 35
            cls.marker_misalignment_tolerance = 0.01

    @classmethod
    def run(cls, dt: float) -> type(RCStatus):
        dx = MarkerStatus.target_pt[0] - TelloSensors.trajectory_point[0]
        dy = MarkerStatus.target_pt[1] - TelloSensors.trajectory_point[1]
        dh = MarkerStatus.height_lr_delta
        d = numpy.sqrt(dx ** 2 + dy ** 2)

        passing_gate_distance = TelloSensors.x
        marker_size = max(MarkerStatus.height, MarkerStatus.width)

        if MODE.status == MODE.AUTO_RESEARCH:
            RCStatus.a = 0
            RCStatus.b = 0
            RCStatus.c = 0
            RCStatus.d = cls.auto_research_yaw_rate

        elif MarkersMemory.passing_gate:
            cls.passing_gate_distance = passing_gate_distance
            RCStatus.a = 0
            RCStatus.b = cls.passing_gate_forward_speed
            RCStatus.c = 0
            RCStatus.d = 0

            # Conditions to exit the "passing gate" state :
            # - if the target marker is not the last one -> makes sure that the UAV goes forward for a certain amount
            #   of distance to go through the gate before reaching the next one
            # - Same behaviour if the target marker is the last one and the LAPS function is toggled
            # - If the target marker is the last one and the LAPS function is not active -> makes sure that the UAV
            #   goes forward for a higher amount of distance to reach the finish line before stopping
            if ((passing_gate_distance > cls.passing_gate_distance_goal
                 and MarkersMemory.current_target_marker_id != MARKERS_INTERVAL[1])
                or (passing_gate_distance > 2 * cls.passing_gate_distance_goal
                    and MarkersMemory.current_target_marker_id == MARKERS_INTERVAL[1]
                    and not LAPS)
                or (passing_gate_distance > cls.passing_gate_distance_goal
                    and MarkersMemory.current_target_marker_id == MARKERS_INTERVAL[1]
                    and LAPS)):
                MarkersMemory.get_new_target()
                MarkersMemory.update_target()
                cls.previous_i_h = 0
                cls.previous_i_dh = 0
                cls.previous_i_dx = 0
                cls.previous_i_dy = 0

        # Conditions to enter the "passing gate" state :
        # - Make sure that the UAV is close enough to the gate (marker_size large enough)
        # - Make sure that the UAV is correctly aligned with the normal direction of the ARUCO code (dh small enough)
        # - Make sure that the UAV yaw and height are correctly adjusted to have the target point in the center of
        #   the screen (d small enough)
        elif marker_size > cls.marker_size_threshold \
                and abs(dh) < cls.marker_misalignment_tolerance \
                and d < cls.marker_offset_tolerance:
            print('Passing gate...')
            MarkersMemory.passing_gate = True
            RCStatus.reset()
            TelloSensors.reset_position_estimate()

        elif MarkerStatus.id != -1:

            # Left/Right velocity control
            i_dh = cls.forgetting_factor * cls.previous_i_dh + dh * dt
            cls.previous_i_dh = i_dh
            RCStatus.a = - int((cls.KP_LR_CTRL * dh * cls.marker_size_threshold
                                / marker_size + cls.KI_LR_CTRL * i_dh)
                               * MarkersMemory.markers_screen_pos[str(MarkerStatus.id)]['reliability'])

            # Forward/Backward velocity control
            RCStatus.b = int(cls.KP_FB_CTRL
                             * numpy.sign(cls.marker_size_target - marker_size)
                             * numpy.sqrt(abs(cls.marker_size_target - marker_size))
                             * MarkersMemory.markers_screen_pos[str(MarkerStatus.id)]['reliability'])

            # Up/Down velocity control
            i_dy = cls.previous_i_dy + dy * dt
            cls.previous_i_dy = i_dy
            RCStatus.c = - int((cls.KP_UD_CTRL * dy + cls.KI_UD_CTRL * i_dy)
                               * MarkersMemory.markers_screen_pos[str(MarkerStatus.id)]['reliability'])

            # Yaw velocity control
            i_dx = cls.forgetting_factor * cls.previous_i_dx + dx * dt
            cls.previous_i_dx = i_dx
            RCStatus.d = int((cls.KP_YAW_CTRL * dx + cls.KI_YAW_CTRL * i_dx)
                             * MarkersMemory.markers_screen_pos[str(MarkerStatus.id)]['reliability'])

            # Saving variables to make them accessible through the cls.__get_dict__() method
            cls.dh = dh
            cls.d = numpy.sqrt(dx ** 2 + dy ** 2)
            cls.marker_size = max(MarkerStatus.height, MarkerStatus.width)

        else:  # The program should never reach this point
            print('Unhandled scenario detected in VisualControl, switching back to manual control')
            RCStatus.reset()
            MODE.status = MODE.MANUAL_FLIGHT
            MarkersMemory.current_target_marker_id = MARKERS_INTERVAL[0]

    @classmethod
    def __get_dict__(cls):
        x = round(cls.passing_gate_distance, 3)
        ms = round(cls.marker_size, 3)
        d = round(cls.d)
        dh = round(cls.dh, 3)
        if MarkersMemory.passing_gate:
            vsc: dict = {'x': (x, RED) if x < cls.passing_gate_distance_goal else (x, GREEN),
                         'marker size': (ms, BLUE),
                         'offset error': (d, BLUE),
                         'alignment': (dh, BLUE)
                         }
        else:
            vsc: dict = {'x': (x, BLUE),
                         'marker size': (ms, RED) if ms < cls.marker_size_threshold else (ms, GREEN),
                         'offset error': (d, RED) if d > cls.marker_offset_tolerance else (d, GREEN),
                         'alignment': (dh, RED) if dh > cls.marker_misalignment_tolerance else (dh, GREEN)
                         }
        return vsc
