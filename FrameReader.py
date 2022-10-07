from queue import LifoQueue
from djitellopy.tello import BackgroundFrameRead

from parameters import RUN, IMG_SIZE

import cv2
import numpy


class FrameReader:
    # The purpose of this class is to put every received frame from the Tello in a queue
    # (This step is mandatory as the frames are passed from one thread to another)
    # Since only the last received frame is important to control the UAV, we can dismiss the older ones that
    # have not been processed in time.
    frames_queue: LifoQueue = None
    frame_reader: BackgroundFrameRead = None

    @classmethod
    def setup(cls, frame_reader: BackgroundFrameRead):
        cls.frame_reader = frame_reader
        cls.frames_queue = LifoQueue()

    @classmethod
    def update_frame(cls):
        if cls.frame_reader.stopped:
            RUN.status = RUN.STOP
        else:
            cls.frames_queue.put_nowait(cls.frame_reader.frame)

    @classmethod
    def flush_old_frames(cls):
        cls.frames_queue = LifoQueue()

    @classmethod
    def get_most_recent_frame(cls) -> numpy.ndarray:
        raw_frame = cls.frames_queue.get()
        frame = cv2.resize(raw_frame, IMG_SIZE)
        cls.flush_old_frames()
        return frame
