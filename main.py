import asyncio
import logging
import parameters
from DJITelloPy.djitellopy.tello import Tello
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput, ModeStatus, RCStatus, pygame_event_loop_check
from subsys_markers_detected import MarkersDetected, DetectedMarkersStatus
from subsys_select_target_marker import SelectTargetMarker
from subsys_tello_sensors import TelloSensors
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import VisualControl



def setup():
    tello = init_env()
    tello.LOGGER.setLevel(logging.WARN)
    TelloActuators.setup(tello)
    TelloSensors.setup(tello)
    Display.setup()
    VisualControl.setup()
    ReadUserInput.setup()
    MarkersDetected.setup()
    SelectTargetMarker.setup()


def init_env() -> Tello:
    # Init Tello object that interacts with the Tello UAV
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
        _ = tello.get_frame_read()
        parameters.RUN.status = parameters.RUN.START
    except Exception as exc:
        parameters.RUN.status = parameters.RUN.STOP
        raise exc
    return tello


def image_processing():
    if TelloActuators.tello is not None and TelloSensors.tello is not None and 0 == 1:
        # Retrieve UAV front camera frame and internal variables
        TelloSensors.update_frame()
        TelloSensors.run()

        # Search for all ARUCO markers in the frame
        frame = MarkersDetected.run(TelloSensors.frame)

        # Select the ARUCO marker to reach first
        marker_status = SelectTargetMarker.run(frame,
                                               DetectedMarkersStatus,
                                               parameters.DRONE_POS,
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
                                                     marker_status.__get_dict__()])
        Display.run(frame, variables_to_print)
    else:
        print('Frame received')


def stop():
    Display.stop()
    TelloActuators.stop()
    MarkersDetected.stop()
    SelectTargetMarker.stop()


if __name__ == "__main__":
    setup()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    event_queue = asyncio.Queue()

    pygame_async_task = loop.run_in_executor(None, pygame_event_loop_check, loop, event_queue)
    user_input_task = asyncio.ensure_future(ReadUserInput.run(event_queue), loop=loop)
    try:
        loop.run_forever()
    except Exception as e:
        raise e
    finally:
        stop()
