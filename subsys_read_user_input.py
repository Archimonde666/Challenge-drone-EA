from parameters import RunStatus, RUN, MODE
from subsys_gamepad import Gamepad
from typing import List
import pygame


class KeyStatus:
    """
    Represents the status of a key on the keyboard
    """

    is_pressed: bool = False
    type_pressed: int = None    # Index of the key


class RCStatus:
    """
    Contains the velocity commands that will be forwarded to the Tello
        a : Left / Right velocity
        b : Forward / Backward velocity
        c : Upward / Downward velocity
        d : Yaw velocity
    """

    a: int = 0  # Left / Right velocity
    b: int = 0  # Forward / Backward velocity
    c: int = 0  # Upward / Downward velocity
    d: int = 0  # Yaw velocity


class ModeStatus:
    """
    Contains the current flight mode status
    (EMERGENCY, TAKEOFF, LAND, FLIGHT)
    """
    value: int = MODE.LAND


class ReadUserInput:
    """
    Handles the keyboard inputs to manually control the Tello
    The controls are:
        - T: Takeoff
        - L: Land
        - Space: Emergency 
        - Arrow keys: Forward, backward, left and right.
        - Q and D: Counterclockwise and clockwise rotations (yaw)
        - Z and S: Up and down
        - Esc: Quit
    """

    joysticks: List[pygame.joystick.Joystick] = []
    joystick_maps: List[dict] = []

    @classmethod
    def setup(cls):
        RunStatus.value = RUN.START
        ModeStatus.value = -1
        pygame.joystick.init()
        cls.joysticks = [pygame.joystick.Joystick(j) for j in range(pygame.joystick.get_count())]
        print(len(cls.joysticks), 'joystick(s) found')
        for joystick in cls.joysticks:
            name = joystick.get_name()
            try:
                gp_map = [gp['name'] for gp in Gamepad.map_list].index(name)
                cls.joystick_maps.append(Gamepad.map_list[gp_map])
                print('Gamepad map successfully loaded for', name)
                # TODO
                # remove print and replace it by an INFO log
            except ValueError:
                print('No configured map for connected gamepad -> using default configuration')
                gp_map = [gp['name'] for gp in Gamepad.map_list].index('Default')
                cls.joystick_maps.append(Gamepad.map_list[gp_map])
            joystick.init()

    @classmethod
    def run(cls, rc_threshold: int) -> (type(RCStatus), type(KeyStatus), type(ModeStatus)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RunStatus.value = RUN.STOP
            elif event.type == pygame.JOYAXISMOTION:
                try:
                    axis = cls.joystick_maps[event.joy]['axes'][event.axis]
                    cls.axis_motion(axis, event.value, rc_threshold)
                except KeyError:
                    print('No axis found with index', event.axis, 'in the Gamepad map')
                    # TODO
                    # remove print and replace it by a WARN log
            elif event.type == pygame.JOYBUTTONDOWN:
                try:
                    KeyStatus.is_pressed = True
                    button = cls.joystick_maps[event.joy]['buttons'][event.button]
                    KeyStatus.type_pressed = button
                    cls.buttons(button, rc_threshold, KeyStatus)
                except KeyError:
                    print('No button found with index', event.button, 'in the Gamepad map')
                    # TODO
                    # remove print and replace it by a WARN log
            elif event.type == pygame.JOYBUTTONUP:
                KeyStatus.is_pressed = False
                KeyStatus.type_pressed = None
            elif event.type == pygame.KEYDOWN:
                try:
                    KeyStatus.is_pressed = True
                    button = Gamepad.keyboard_map['buttons'][event.key]
                    KeyStatus.type_pressed = button
                    cls.buttons(button, rc_threshold, KeyStatus)
                except KeyError:
                    print('No key found with index', event.key, 'in the keyboard map')
                    # TODO
                    # remove print and replace it by a WARN log
            elif event.type == pygame.KEYUP:
                try:
                    KeyStatus.is_pressed = False
                    button = Gamepad.keyboard_map['buttons'][event.key]
                    KeyStatus.type_pressed = None
                    cls.buttons(button, rc_threshold, KeyStatus)
                except KeyError:
                    print('No key found with index', event.key, 'in the keyboard map')
                    # TODO
                    # remove print and replace it by a WARN log
        return RCStatus, KeyStatus, ModeStatus

    # inter functions
    @classmethod
    def __key_down(cls, key: int, rc_threshold: int):
        """
        Update velocities based on key pressed
        Arguments:
            key: pygame key index (int)
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
    def __key_up(cls, key: int):
        """
        Update velocities based on key released
        Arguments:
            key: pygame key index (int)
        """
        # left_right_velocity
        if key == pygame.K_RIGHT or key == pygame.K_LEFT:
            RCStatus.a = 0

        # for_back_velocity
        elif key == pygame.K_UP or key == pygame.K_DOWN:
            RCStatus.b = 0

        # up_down_velocity
        elif key == pygame.K_z or key == pygame.K_s:
            RCStatus.c = 0

        # yaw_velocity
        elif key == pygame.K_d or key == pygame.K_q:
            RCStatus.d = 0

    @classmethod
    def buttons(cls, button: str, rc_threshold: int, key_status: type(KeyStatus)):
        if button == 'Stop' and key_status.is_pressed:
            RCStatus.a = 0
            RCStatus.b = 0
            RCStatus.c = 0
            RCStatus.d = 0
            RunStatus.value = RUN.STOP
        elif button == 'Emergency' and key_status.is_pressed:
            ModeStatus.value = MODE.EMERGENCY
        elif button == 'Takeoff' and key_status.is_pressed:
            ModeStatus.value = MODE.TAKEOFF
        elif button == 'Land' and key_status.is_pressed:
            ModeStatus.value = MODE.LAND
        elif button == 'Left':
            RCStatus.a = - key_status.is_pressed * int(rc_threshold)
        elif button == 'Right':
            RCStatus.a = key_status.is_pressed * int(rc_threshold)
        elif button == 'Forward':
            RCStatus.b = key_status.is_pressed * int(rc_threshold)
        elif button == 'backward':
            RCStatus.b = - key_status.is_pressed * int(rc_threshold)
        elif button == 'Up':
            RCStatus.c = key_status.is_pressed * int(rc_threshold)
        elif button == 'Down':
            RCStatus.c = - key_status.is_pressed * int(rc_threshold)
        elif button == 'Yaw+':
            RCStatus.d = key_status.is_pressed * int(rc_threshold)
        elif button == 'Yaw-':
            RCStatus.d = - key_status.is_pressed * int(rc_threshold)

    @classmethod
    def axis_motion(cls, axis: str, value: float, rc_threshold: int):
        if axis == 'Roll':
            RCStatus.a = int(rc_threshold * value)
        elif axis == 'Pitch':
            RCStatus.b = - int(rc_threshold * value)
        elif axis == 'Height':
            RCStatus.c = - int(rc_threshold * value)
        elif axis == 'Yaw':
            RCStatus.d = int(rc_threshold * value)
        elif axis == 'Yaw+':
            RCStatus.d = int(rc_threshold * 0.5 * (value + 1))
        elif axis == 'Yaw-':
            RCStatus.d = int(rc_threshold * 0.5 * (value - 1))
