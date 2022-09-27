import time
import parameters
from subsys_display_view import Display
from subsys_read_cam import ReadCAM
from subsys_read_user_input import ReadUserInput
from subsys_markers_detected import MarkersDetected
from subsys_select_target_marker import SelectTargetMarker


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
                                           parameters.DRONE_POS,
                                           offset=(0, 0))

    # Update pygame display window
    variables_to_print = parameters.merge_dicts([marker_status.__getDict__()])
    Display.run(frame, variables_to_print)

    # Wait for a new frame to be available
    time.sleep(1 / parameters.FPS)


def stop():
    Display.stop()
    ReadCAM.stop()
    MarkersDetected.stop()
    SelectTargetMarker.stop()


if __name__ == "__main__":
    setup()
    while parameters.RunStatus.value:
        run()
    stop()
