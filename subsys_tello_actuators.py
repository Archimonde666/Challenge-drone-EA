from DJITelloPy.djitellopy.tello import Tello
from subsys_read_user_input import RCStatus


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
    def run(cls, rc_status: type(RCStatus)):
        cls.update_rc_command(rc_status)

    @classmethod
    def update_rc_command(cls, rc_status: RCStatus):
        """Update routine. Send velocities to Tello.
        """
        rc_status.c = int(rc_status.c * 0.5)
        if rc_status.toStr() != cls.previous_RCstate:
            cls.tello.set_speed(100)
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
