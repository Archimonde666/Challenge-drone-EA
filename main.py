import logging
import parameters
from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput, ModeStatus, RCStatus
from subsys_markers_detected import MarkersDetector, DetectedMarkersStatus
from subsys_select_target_marker import SelectTargetMarker, MarkersMemory
from subsys_tello_sensors import TelloSensors
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import VisualControl


def setup():
    MarkersMemory.setup(parameters.highest_marker_index)
    Display.setup()
    ReadUserInput.setup()
    SelectTargetMarker.setup()
    tello, frame_reader = init_env()
    tello.LOGGER.setLevel(logging.WARN)
    TelloActuators.setup(tello)
    TelloSensors.setup(tello, frame_reader)
    return 1


def init_env() -> (Tello, BackgroundFrameRead):
    # Init Tello python object that interacts with the Tello UAV
    tello = None
    if parameters.ENV.status == parameters.ENV.SIMULATION:
        Tello.CONTROL_UDP_PORT_CLIENT = 9000
        tello = Tello("127.0.0.1", image_received_method=image_processing)
    elif parameters.ENV.status == parameters.ENV.REAL:
        Tello.CONTROL_UDP_PORT_CLIENT = Tello.CONTROL_UDP_PORT
        tello = Tello("192.168.10.1", image_received_method=image_processing)
    tello.connect()
    tello.streamoff()
    tello.streamon()
    try:
        frame_reader = tello.get_frame_read()
        parameters.RUN.status = parameters.RUN.START
    except Exception as exc:
        parameters.RUN.status = parameters.RUN.STOP
        raise exc
    return tello, frame_reader


def image_processing():
    if setup_finished:
        # Retrieve UAV front camera frame and internal variables
        TelloSensors.run()

        # Search for all ARUCO markers in the frame
        frame = MarkersDetector.run(TelloSensors.frame)
        # Select the ARUCO marker to reach first
        marker_status = SelectTargetMarker.run(frame,
                                               DetectedMarkersStatus,
                                               offset=(-4, 0))
        # Get the velocity commands from the automatic control module
        if ModeStatus.value == parameters.MODE.AUTO_FLIGHT:
            VisualControl.run(marker_status)
        # Send the commands to the UAV
        TelloActuators.run(RCStatus)
        # Update pygame display window
        variables_to_print = parameters.merge_dicts([TelloSensors.__get_dict__(),
                                                     ModeStatus.__get_dict__(),
                                                     RCStatus.__get_dict__(),
                                                     marker_status.__get_dict__(),
                                                     MarkersMemory.__get_dict__()])
        Display.run(frame, variables_to_print)
    else:
        print('Frame received before the end of setup, unable to process it yet -> Frame dismissed')


def stop():
    TelloActuators.stop()


if __name__ == "__main__":
    setup_finished = setup()
    # The run_pygame_loop() is a while loop that breaks only when the flight is finished
    # This loop constantly checks for new user inputs, and updates the
    # pygame window with the latest available frame
    flight_finished = ReadUserInput.run_pygame_loop()
    stop()
