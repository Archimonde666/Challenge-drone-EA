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
        if rc_status.toStr() != cls.previous_RCstate :
            cls.tello.send_rc_control(
                rc_status.a,  # left_right_velocity,
                rc_status.b,  # for_back_velocity,
                rc_status.c,  # up_down_velocity,
                rc_status.d,  # yaw_velocity,
            )
            cls.previous_RCstate = rc_status.toStr()

    @classmethod
    def stop(cls):
        cls.tello.end()
