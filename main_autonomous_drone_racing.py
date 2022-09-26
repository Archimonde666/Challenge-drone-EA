import logging
import time
import parameters
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput
from subsys_markers_detected import MarkersDetected
from subsys_select_target_marker import SelectTargetMarker
from subsys_tello_sensors import TelloSensors
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import VisualControl


def setup():
    parameters.ENV.status = parameters.ENV.SIMULATION
    TelloSensors.setup()
    TelloSensors.TELLO.LOGGER.setLevel(logging.WARN)
    TelloActuators.setup(TelloSensors.TELLO)
    Display.setup()
    VisualControl.setup()
    ReadUserInput.setup()
    MarkersDetected.setup()
    SelectTargetMarker.setup()


def run():
    # Get user input (keyboard, gamepad, joystick)
    rc_status_1, key_status, mode_status = ReadUserInput.run(rc_roll_pitch_threshold=100,
                                                             rc_height_threshold=20,
                                                             rc_yaw_threshold=20)

    # Retrieve UAV front camera frame and internal variables
    frame = TelloSensors.run(mode_status)

    # Search for all ARUCO markers in the frame
    markers_status, frame = MarkersDetected.run(frame)

    # Select the ARUCO marker to reach first
    marker_status = SelectTargetMarker.run(frame,
                                           markers_status,
                                           parameters.DRONE_POS,
                                           offset=(-4, 0))

    # Get the velocity commands from the automatic control module
    rc_status_2 = VisualControl.run(marker_status)

    # The user input is prioritized -> if the keyboard is used, the automatic control
    # will not interfere with the manual control commands
    if key_status.is_pressed:
        rc_status = rc_status_1
    else:
        rc_status = rc_status_2

    # Send the commands to the UAV
    TelloActuators.run(rc_status)

    # Update pygame display window
    variables_to_print = parameters.merge_dicts([TelloSensors.__get_dict__(),
                                                 mode_status.__get_dict__(),
                                                 rc_status.__get_dict__(),
                                                 marker_status.__get_dict__()])
    Display.run(frame, variables_to_print)

    # Wait for a new frame to be available
    time.sleep(1 / parameters.FPS)


def stop():
    Display.stop()
    TelloSensors.stop()
    MarkersDetected.stop()
    SelectTargetMarker.stop()


if __name__ == "__main__":
    setup()
    while parameters.RunStatus.value:
        run()
    stop()
