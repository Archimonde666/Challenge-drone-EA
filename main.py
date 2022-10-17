import logging
import time
from threading import Thread
from DJITelloPy.djitellopy.tello import Tello, BackgroundFrameRead

from Display import Display
from FrameReader import FrameReader
from RCStatus import RCStatus
from MarkersDetector import MarkersDetector
from TelloSensors import TelloSensors
from MarkersMemory import MarkersMemory
from MarkerStatus import MarkerStatus
from parameters import MODE, RUN, ENV, merge_dicts
from TargetMarkerSelector import TargetMarkerSelector
from TelloActuators import TelloActuators
from UserInputReader import UserInputReader
from VisualControl import VisualControl


def setup():
    Display.setup()
    UserInputReader.setup(rc_roll_pitch_threshold=100,
                          rc_height_threshold=20,
                          rc_yaw_threshold=40)
    TargetMarkerSelector.setup()
    MarkersMemory.setup(first_marker_id=1)
    tello, frame_reader = init_env()
    tello.LOGGER.setLevel(logging.WARN)
    fh = logging.FileHandler(filename='Tello.log')
    fileLogFormat = '%(asctime)s - %(levelname)s - %(message)s'
    fileFormatter = logging.Formatter(fileLogFormat)
    Tello.LOGGER.addHandler(fh)
    FrameReader.setup(frame_reader)
    TelloActuators.setup(tello)
    TelloSensors.setup(tello)
    frame_reception_check = ImageProcess.setup(timeout=2)
    return frame_reception_check


def init_env() -> (Tello, BackgroundFrameRead):
    # Init Tello python object that interacts with the Tello UAV
    tello = None
    if ENV.status == ENV.SIMULATION:
        Tello.CONTROL_UDP_PORT_CLIENT = 9000
        tello = Tello("127.0.0.1", image_received_method=FrameReader.update_frame)
    elif ENV.status == ENV.REAL:
        Tello.CONTROL_UDP_PORT_CLIENT = Tello.CONTROL_UDP_PORT
        tello = Tello("192.168.10.1", image_received_method=FrameReader.update_frame)
    tello.connect()
    tello.streamoff()
    tello.streamon()
    try:
        frame_reader = tello.get_frame_read()
        RUN.status = RUN.START
    except Exception as exc:
        RUN.status = RUN.STOP
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
        previous_frame_time = 0
        while True:
            if cls.stop_request:
                break
            frame_time = time.time()
            dt = frame_time - previous_frame_time
            # Retrieve UAV internal variables
            TelloSensors.run(dt)
            # Retrieve most recent frame from the Tello
            frame = FrameReader.get_most_recent_frame()
            # Search for all ARUCO markers in the frame
            frame_with_markers = MarkersDetector.run(frame)
            # Update the last screen position of all makers
            MarkersMemory.update_memory()
            # Select the ARUCO marker to reach first
            TargetMarkerSelector.run()
            # Get the velocity commands from the automatic control module
            if MODE.status == MODE.AUTO_FLIGHT or MODE.status == MODE.AUTO_RESEARCH:
                VisualControl.run(dt)
            # Send the commands to the UAV
            TelloActuators.send_rc_command()
            # Update pygame display window
            variables_to_print = merge_dicts([TelloSensors.__get_dict__(),
                                              RCStatus.__get_dict__(),
                                              MarkerStatus.__get_dict__(),
                                              MarkersMemory.__get_dict__(),
                                              {'FPS': int(1/dt)}
                                              ])
            Display.run(frame_with_markers, variables_to_print)
            previous_frame_time = frame_time
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
        flight_finished = UserInputReader.run_pygame_loop()
        stop()
    else:
        stop()
