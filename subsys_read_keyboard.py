from parameters import RunStatus, RUN, MODE
import pygame


class KeyStatus:
    is_pressed = False
    type_pressed = None


class RCStatus:
    a = 0  # Left / Right velocity
    b = 0  # Forward / Backward velocity
    c = 0  # Upward / Downward velocity
    d = 0  # Yaw velocity


class ModeStatus:
    value = MODE.LAND


class ReadKeyboard:
    """Maintains the Tello display and moves it through the keyboard keys.
    Press escape key to quit.
    The controls are:
        - T: Takeoff
        - L: Land
        - Space: Emergency 
        - Arrow keys: Forward, backward, left and right.
        - Q and D: Counter clockwise and clockwise rotations (yaw)
        - Z and S: Up and down.
    """
    @classmethod
    def setup(cls):
        RunStatus.value = RUN.START
        ModeStatus.value = -1

    @classmethod
    def run(cls, rc_threshold):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                RunStatus.value = RUN.STOP

            elif event.type == pygame.KEYDOWN:
                KeyStatus.is_pressed = True
                KeyStatus.type_pressed = event.key

                if event.key == pygame.K_ESCAPE:
                    RunStatus.value = RUN.STOP

                elif event.key == pygame.K_SPACE:
                    ModeStatus.value = MODE.EMERGENCY
                elif event.key == pygame.K_t:
                    ModeStatus.value = MODE.TAKEOFF
                elif event.key == pygame.K_l:
                    ModeStatus.value = MODE.LAND

                else:
                    cls.__key_down(event.key, rc_threshold)

            elif event.type == pygame.KEYUP:

                KeyStatus.is_pressed = False
                KeyStatus.type_pressed = None
                cls.__key_up(event.key)
        return RCStatus, KeyStatus, ModeStatus

    # inter functions
    @classmethod
    def __key_down(cls, key, rc_threshold):
        """
        Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        # left_right_velocity
        if key == pygame.K_RIGHT:
            RCStatus.a = rc_threshold
        elif key == pygame.K_LEFT:
            RCStatus.a = - rc_threshold

        # for_back_velocity
        elif key == pygame.K_UP:
            RCStatus.b = rc_threshold
        elif key == pygame.K_DOWN:
            RCStatus.b = -rc_threshold

        # up_down_velocity
        elif key == pygame.K_z:
            RCStatus.c = rc_threshold
        elif key == pygame.K_s:
            RCStatus.c = -rc_threshold

        # yaw_velocity
        elif key == pygame.K_d:
            RCStatus.d = rc_threshold
        elif key == pygame.K_q:
            RCStatus.d = -rc_threshold

    @classmethod
    def __key_up(cls, key):
        """
        Update velocities based on key released
        Arguments:
            key: pygame key

        """
        # left_right_velocity
        if (key == pygame.K_RIGHT or key == pygame.K_LEFT):
            RCStatus.a = 0
        # for_back_velocity
        elif(key == pygame.K_UP or key == pygame.K_DOWN):
            RCStatus.b = 0
        # up_down_velocity
        elif(key == pygame.K_z or key == pygame.K_s):
            RCStatus.c = 0
        # yaw_velocity
        elif(key == pygame.K_d or key == pygame.K_q):
            RCStatus.d = 0
