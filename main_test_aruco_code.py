import time
from parameters import RunStatus, FPS, DRONE_POS
from subsys_display_view import Display
from subsys_read_cam import ReadCAM
from subsys_read_user_input import ReadUserInput
from subsys_markers_detected import MarkersDetected
from subsys_select_target_marker import SelectTargetMarker
from typing import List


def setup():
    ReadCAM.setup()
    Display.setup()
    ReadUserInput.setup()
    MarkersDetected.setup()
    SelectTargetMarker.setup()


def run():
    # Get user input (keyboard, gamepad, joystick)
    _, __, ___ = ReadUserInput.run(rc_roll_pitch_threshold=100,
                                   rc_height_threshold=40,
                                   rc_yaw_threshold=40)

    # Retrieve frame from a connected webcam
    frame = ReadCAM.run()

    # Search for all ARUCO markers in the frame
    markers_status, frame = MarkersDetected.run(frame)

    # Select the ARUCO marker to reach first
    marker_status = SelectTargetMarker.run(frame,
                                           markers_status,
                                           DRONE_POS,
                                           offset=(0, 0))

    # Update pygame display window
    variables_to_print = merge_dicts([marker_status.__getDict__()])
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
    ReadCAM.stop()
    MarkersDetected.stop()
    SelectTargetMarker.stop()


if __name__ == "__main__":
    setup()
    while RunStatus.value:
        run()
    stop()
