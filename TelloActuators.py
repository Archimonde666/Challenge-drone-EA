from DJITelloPy.djitellopy.tello import Tello
from RCStatus import RCStatus


class TelloActuators:
    """
    Sends the velocity commands to the Tello
    """
    tello: Tello = None
    previous_RCstate = None

    @classmethod
    def setup(cls, tello: Tello):
        cls.tello = tello

    @classmethod
    def send_rc_command(cls):
        """Update routine. Send velocities to Tello.
        """
        if RCStatus.toStr() != cls.previous_RCstate:
            cls.tello.send_rc_control(
                RCStatus.a,  # left_right_velocity,
                RCStatus.b,  # for_back_velocity,
                RCStatus.c,  # up_down_velocity,
                RCStatus.d,  # yaw_velocity,
            )
            cls.previous_RCstate = RCStatus.toStr()

    @classmethod
    def stop(cls):
        cls.tello.end()
