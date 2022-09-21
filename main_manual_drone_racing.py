import logging
import time
from parameters import ENV, RunStatus, FPS, DRONE_POS
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput
from subsys_markers_detected import MarkersDetected
from subsys_select_target_marker import SelectTargetMarker
from subsys_tello_sensors import TelloSensors
from subsys_tello_actuators import TelloActuators
from typing import List


def setup():
    ENV.status = ENV.SIMULATION
    TelloSensors.setup()
    TelloSensors.TELLO.LOGGER.setLevel(logging.WARN)
    TelloActuators.setup(TelloSensors.TELLO)
    Display.setup()
    ReadUserInput.setup()
    MarkersDetected.setup()
    SelectTargetMarker.setup()


def run():
    # Get user input (keyboard, gamepad, joystick)
    rc_status, key_status, mode_status = ReadUserInput.run(rc_roll_pitch_threshold=100,
                                                           rc_yaw_threshold=40,
                                                           rc_height_threshold=40)

    # Retrieve UAV front camera frame
    frame, drone_state = TelloSensors.run(mode_status)

    # Search for all ARUCO markers in the frame
    markers_status, frame = MarkersDetected.run(frame)

    # Select the ARUCO marker to reach first
    marker_status = SelectTargetMarker.run(frame,
                                           markers_status,
                                           DRONE_POS,
                                           offset=(-4, 0))

    # Send manual commands to the UAV (automatic mode disabled)
    TelloActuators.run(rc_status)

    # Update pygame display window
    variables_to_print = merge_dicts([drone_state.__getDict__(),
                                      mode_status.__getDict__(),
                                      rc_status.__getDict__(),
                                      marker_status.__getDict__()])
    Display.run(frame, variables_to_print)

    # Wait for a new frame to be available
    time.sleep(1 / FPS)


def merge_dicts(dict_list: List[dict]) -> dict:
    merged_dict: dict = {}
    for dictionary in dict_list:
        merged_dict.update(dictionary)
    return merged_dict


def stop():
    Display.stop()
    TelloSensors.stop()
    MarkersDetected.stop()
    SelectTargetMarker.stop()


if __name__ == "__main__":
    setup()
    while RunStatus.value:
        run()
    stop()
