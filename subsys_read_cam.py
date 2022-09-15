import cv2
import numpy


class ReadCAM:
    vid: cv2.VideoCapture = None  # video capture object

    @classmethod
    def setup(cls):
        # ref to use camera with opencv: https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
        # define a video capture object
        cls.vid = cv2.VideoCapture(0)

    @classmethod
    def run(cls) -> numpy.ndarray:
        ret, frame = cls.vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    @classmethod
    def stop(cls):
        cls.vid.release()
