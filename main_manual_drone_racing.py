import logging
import time
import parameters
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput
from subsys_markers_detected import MarkersDetected
from subsys_select_target_marker import SelectTargetMarker
from subsys_tello_sensors import TelloSensors
from subsys_tello_actuators import TelloActuators


def setup():
    parameters.ENV.status = parameters.ENV.SIMULATION
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
                                                           rc_yaw_threshold=20,
                                                           rc_height_threshold=20)

    # Retrieve UAV front camera frame
    frame = TelloSensors.run(mode_status)

    # Search for all ARUCO markers in the frame
    markers_status, frame = MarkersDetected.run(frame)

    # Select the ARUCO marker to reach first
    marker_status = SelectTargetMarker.run(frame,
                                           markers_status,
                                           parameters.DRONE_POS,
                                           offset=(-4, 0))

    # Send manual commands to the UAV (automatic mode disabled)
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
