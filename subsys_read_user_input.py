from parameters import RunStatus, RUN, MODE
from subsys_gamepad import Gamepad
from typing import List
import pygame


class KeyStatus:
    """
    Represents the status of a key on the keyboard
    """

    is_pressed: bool = False
    type_pressed: int = None  # Index of the key


class RCStatus:
    """
    Contains the velocity commands that will be forwarded to the Tello
        a : Left / Right velocity
        b : Forward / Backward velocity
        c : Upward / Downward velocity
        d : Yaw rate
    """

    a: int = 0  # Left / Right velocity
    b: int = 0  # Forward / Backward velocity
    c: int = 0  # Upward / Downward velocity
    d: int = 0  # Yaw velocity

    @classmethod
    def __get_dict__(cls) -> dict:
        rc: dict = {'a': cls.a,
                    'b': cls.b,
                    'c': cls.c,
                    'd': cls.d}
        return rc
    
    @classmethod
    def toStr(cls):
        return "rc " + str(cls.a) + " " + str(cls.b) + " " + str(cls.c) + " " + str(cls.d)
    

class ModeStatus:
    """
    Contains the current flight mode status
    (EMERGENCY, TAKEOFF, LAND, FLIGHT)
    """
    value: int = MODE.LAND

    @classmethod
    def __get_dict__(cls) -> dict:
        ms: dict = {'Mode': cls.value}
        return ms


class ReadUserInput:
    """
    Handles the user inputs to manually control the Tello
    The controls are defined in the subsys_gamepad.py -> Gamepad class
    """

    joysticks: List[pygame.joystick.Joystick] = []
    joystick_maps: List[dict] = []
    rc_threshold: 3*[int] = [100, 100, 100]

    @classmethod
    def setup(cls,
              rc_roll_pitch_threshold: int = 100,
              rc_height_threshold: int = 20,
              rc_yaw_threshold: int = 20) -> (type(RCStatus), type(KeyStatus), type(ModeStatus)):
        cls.rc_threshold = [rc_roll_pitch_threshold, rc_height_threshold, rc_yaw_threshold]
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
            except ValueError:
                print('No configured map for connected gamepad -> using default configuration')
                gp_map = [gp['name'] for gp in Gamepad.map_list].index('Default')
                cls.joystick_maps.append(Gamepad.map_list[gp_map])
            joystick.init()

    @classmethod
    def run_pygame_loop(cls):
        while True:
            for event in pygame.event.get():
                cls.run(event)
            pygame.display.update()
            if RunStatus.value == RUN.STOP:
                break
        return 1

    @classmethod
    def run(cls, event):
        try:
            if event.type == pygame.QUIT:
                RunStatus.value = RUN.STOP
            elif event.type == pygame.JOYAXISMOTION:
                if ModeStatus.value == MODE.AUTO_FLIGHT and abs(event.value) > 0.1:
                    print('User input detected, automatic control module disabled')
                    ModeStatus.value = MODE.MANUAL_FLIGHT
                KeyStatus.is_pressed = True
                axis = cls.joystick_maps[event.joy]['axes'][event.axis]
                KeyStatus.type_pressed = axis
                cls.axis_motion(axis, event.value)
            elif event.type == pygame.JOYBUTTONDOWN:
                KeyStatus.is_pressed = True
                button = cls.joystick_maps[event.joy]['buttons'][event.button]
                KeyStatus.type_pressed = button
                cls.buttons(button, KeyStatus)
            elif event.type == pygame.JOYBUTTONUP:
                KeyStatus.is_pressed = False
                KeyStatus.type_pressed = None
            elif event.type == pygame.KEYDOWN:
                KeyStatus.is_pressed = True
                button = Gamepad.keyboard_map['buttons'][event.key]
                KeyStatus.type_pressed = button
                cls.buttons(button, KeyStatus)
            elif event.type == pygame.KEYUP:
                KeyStatus.is_pressed = False
                button = Gamepad.keyboard_map['buttons'][event.key]
                KeyStatus.type_pressed = None
                cls.buttons(button, KeyStatus)
        except KeyError as e:
            print('No axis/button/key found with index', e, 'in the Gamepad map')

    @classmethod
    def buttons(cls, button: str, key_status: type(KeyStatus)):
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
        elif button == 'Automatic flight' and key_status.is_pressed:
            ModeStatus.value = MODE.AUTO_FLIGHT
        elif ModeStatus.value == MODE.AUTO_FLIGHT and key_status.is_pressed:
            ModeStatus.value = MODE.MANUAL_FLIGHT
            print('User input detected, automatic control module disabled')

        if button == 'Left':
            RCStatus.a = - key_status.is_pressed * int(cls.rc_threshold[0])
        elif button == 'Right':
            RCStatus.a = key_status.is_pressed * int(cls.rc_threshold[0])
        elif button == 'Forward':
            RCStatus.b = key_status.is_pressed * int(cls.rc_threshold[0])
        elif button == 'Backward':
            RCStatus.b = - key_status.is_pressed * int(cls.rc_threshold[0])
        elif button == 'Up':
            RCStatus.c = key_status.is_pressed * int(cls.rc_threshold[1])
        elif button == 'Down':
            RCStatus.c = - key_status.is_pressed * int(cls.rc_threshold[1])
        elif button == 'Yaw+':
            RCStatus.d = key_status.is_pressed * int(cls.rc_threshold[2])
        elif button == 'Yaw-':
            RCStatus.d = - key_status.is_pressed * int(cls.rc_threshold[2])

    @classmethod
    def axis_motion(cls, axis: str, value: float):
        if axis == 'Roll':
            RCStatus.a = int(cls.rc_threshold[0] * value)
        elif axis == 'Pitch':
            RCStatus.b = - int(cls.rc_threshold[0] * value)
        elif axis == 'Height':
            RCStatus.c = - int(cls.rc_threshold[1] * value)
        elif axis == 'Yaw':
            RCStatus.d = int(cls.rc_threshold[2] * value)
        elif axis == 'Yaw+':
            RCStatus.d = int(cls.rc_threshold[2] * 0.5 * (value + 1))
        elif axis == 'Yaw-':
            RCStatus.d = int(cls.rc_threshold[2] * 0.5 * (value - 1))
