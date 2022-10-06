import logging
import time

import parameters
from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead
from subsys_display_view import Display
from subsys_read_user_input import ReadUserInput, ModeStatus, RCStatus
from subsys_markers_detected import MarkersDetector, DetectedMarkersStatus
from subsys_select_target_marker import SelectTargetMarker
from subsys_tello_sensors import TelloSensors, FrameReader
from subsys_tello_actuators import TelloActuators
from subsys_visual_control import VisualControl
from threading import Thread


def setup():
    Display.setup()
    ReadUserInput.setup()
    SelectTargetMarker.setup()
    tello, frame_reader = init_env()
    tello.LOGGER.setLevel(logging.WARN)
    FrameReader.setup(frame_reader)
    TelloActuators.setup(tello)
    TelloSensors.setup(tello)
    frame_reception_check = ImageProcess.setup(timeout=2)
    return frame_reception_check


def init_env() -> (Tello, BackgroundFrameRead):
    # Init Tello python object that interacts with the Tello UAV
    tello = None
    if parameters.ENV.status == parameters.ENV.SIMULATION:
        Tello.CONTROL_UDP_PORT_CLIENT = 9000
        tello = Tello("127.0.0.1", image_received_method=FrameReader.update_frame)
    elif parameters.ENV.status == parameters.ENV.REAL:
        Tello.CONTROL_UDP_PORT_CLIENT = Tello.CONTROL_UDP_PORT
        tello = Tello("192.168.10.1", image_received_method=FrameReader.update_frame)
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


class ImageProcess:
    # The image processing features are run in a separate thread in order to allow the pygame window update
    # and the Tello frames reception at a high rate, even during time-expensive image processing computations.
    # Then, the processed frame is always the most recent one, and the not-processed outdated frames are dismissed.
    stop_request = False
    image_processing_thread: Thread = None

    @classmethod
    def setup(cls, timeout: int = 2):
        # Warning : Blocking code in the main thread !!!
        # Since the program cannot perform any image process before having received a frame from the Tello,
        # this part of the program waits for the first frame to be available before finishing the setup.
        start_time = time.time()
        print('ImageProcess | Attempting to get frame...')
        while True:
            if not FrameReader.frames_queue.empty():
                frame_received = True
                print('ImageProcess | Frame received')
                break
            if time.time() - start_time > timeout:
                print('ImageProcess | Timeout reached, no frame received')
                frame_received = False
                stop()
                break
        if frame_received:
            cls.image_processing_thread = Thread(target=cls.run)
            cls.image_processing_thread.start()
        return frame_received

    @classmethod
    def run(cls):
        print('Image processing thread started')
        while True:
            if cls.stop_request:
                break
            # Retrieve UAV internal variables
            TelloSensors.run()
            # Retrieve most recent frame from the Tello
            frame = FrameReader.get_most_recent_frame()
            # Search for all ARUCO markers in the frame
            frame_with_markers = MarkersDetector.run(frame)
            # Select the ARUCO marker to reach first
            marker_status = SelectTargetMarker.run(frame_with_markers,
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
                                                         marker_status.__get_dict__()])
            Display.run(frame_with_markers, variables_to_print)
        print('Image processing thread stopped')

    @classmethod
    def stop(cls):
        cls.stop_request = True
        cls.image_processing_thread.join()


def stop():
    # Important : first stop ImageProcess, then stop TelloActuator or pygame will crash
    ImageProcess.stop()
    TelloActuators.stop()


if __name__ == "__main__":
    setup_ok = setup()
    if setup_ok:
        # The run_pygame_loop() is a while loop that breaks only when the flight is finished
        # This loop constantly checks for new user inputs, and updates the
        # pygame window with the latest available frame
        flight_finished = ReadUserInput.run_pygame_loop()
        stop()
    else:
        stop()
