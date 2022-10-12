from parameters import RUN, MODE
from MarkersMemory import MarkersMemory
from RCStatus import RCStatus
from Gamepad import Gamepad

from typing import List
import pygame


class UserInputReader:
    """
    Handles the user inputs to manually control the Tello
    The controls are defined in the Gamepad.py -> Gamepad class
    """

    joysticks: List[pygame.joystick.Joystick] = []
    joystick_maps: List[dict] = []
    rc_threshold: 3*[int] = [100, 100, 100]

    @classmethod
    def setup(cls,
              rc_roll_pitch_threshold: int = 5,
              rc_height_threshold: int = 20,
              rc_yaw_threshold: int = 20):
        cls.rc_threshold = [rc_roll_pitch_threshold, rc_height_threshold, rc_yaw_threshold]
        RUN.status = RUN.START
        MODE.status = -1
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
            if RUN.status == RUN.STOP:
                break
        return 1

    @classmethod
    def run(cls, event):
        button = None
        key_pressed = False
        try:
            if event.type == pygame.QUIT:
                RUN.status = RUN.STOP
            elif event.type == pygame.JOYAXISMOTION:
                if (MODE.status == MODE.AUTO_FLIGHT or MODE.status == MODE.AUTO_RESEARCH) and abs(event.value) > 0.1:
                    print('User input detected, automatic control module disabled')
                    RCStatus.reset()
                    MODE.status = MODE.MANUAL_FLIGHT
                axis = cls.joystick_maps[event.joy]['axes'][event.axis]
                cls.axis_motion(axis, event.value)
            elif event.type == pygame.JOYBUTTONDOWN:
                key_pressed = True
                button = cls.joystick_maps[event.joy]['buttons'][event.button]
            elif event.type == pygame.JOYBUTTONUP:
                key_pressed = False
                button = cls.joystick_maps[event.joy]['buttons'][event.button]
            elif event.type == pygame.KEYDOWN:
                key_pressed = True
                button = Gamepad.keyboard_map['buttons'][event.key]
            elif event.type == pygame.KEYUP:
                key_pressed = False
                button = Gamepad.keyboard_map['buttons'][event.key]

            if button is not None:
                cls.buttons(button, key_pressed)
        except KeyError as e:
            print('No axis/button/key found with index', e, 'in the Gamepad map')

    @classmethod
    def buttons(cls, button: str, key_pressed: bool):
        if button == 'Stop' and key_pressed:
            RCStatus.reset()
            RUN.status = RUN.STOP
        elif button == 'Emergency' and key_pressed:
            RCStatus.reset()
            MODE.status = MODE.EMERGENCY
        elif button == 'Takeoff' and key_pressed:
            RCStatus.reset()
            MODE.status = MODE.TAKEOFF
        elif button == 'Land' and key_pressed:
            RCStatus.reset()
            MODE.status = MODE.LAND
        elif button == 'Automatic flight' and key_pressed:
            RCStatus.reset()
            MODE.status = MODE.AUTO_FLIGHT
        elif MODE.status == MODE.AUTO_FLIGHT and key_pressed:
            RCStatus.reset()
            MarkersMemory.passing_gate = False
            MODE.status = MODE.MANUAL_FLIGHT
            print('User input detected, automatic control module disabled')

        if button == 'Left':
            RCStatus.a = - key_pressed * int(cls.rc_threshold[0])
        elif button == 'Right':
            RCStatus.a = key_pressed * int(cls.rc_threshold[0])
        elif button == 'Forward':
            RCStatus.b = key_pressed * int(cls.rc_threshold[0])
        elif button == 'Backward':
            RCStatus.b = - key_pressed * int(cls.rc_threshold[0])
        elif button == 'Up':
            RCStatus.c = key_pressed * int(cls.rc_threshold[1])
        elif button == 'Down':
            RCStatus.c = - key_pressed * int(cls.rc_threshold[1])
        elif button == 'Yaw+':
            RCStatus.d = key_pressed * int(cls.rc_threshold[2])
        elif button == 'Yaw-':
            RCStatus.d = - key_pressed * int(cls.rc_threshold[2])

    @classmethod
    def axis_motion(cls, axis: str, value: float):
        if axis == 'Roll':
            if abs(value) > 0.1:
                RCStatus.a = int(cls.rc_threshold[0] * value)
            else:
                RCStatus.a = 0
        elif axis == 'Pitch':
            if abs(value) > 0.1:
                RCStatus.b = - int(cls.rc_threshold[0] * value)
            else:
                RCStatus.b = 0
        elif axis == 'Height':
            if abs(value) > 0.1:
                RCStatus.c = - int(cls.rc_threshold[1] * value)
            else:
                RCStatus.c = 0
        elif axis == 'Yaw':
            if abs(value) > 0.1:
                RCStatus.d = int(cls.rc_threshold[2] * value)
            else:
                RCStatus.d = 0
        elif axis == 'Yaw+':
            if abs(value) > 0.1:
                RCStatus.d = int(cls.rc_threshold[2] * 0.5 * (value + 1))
            else:
                RCStatus.d = 0
        elif axis == 'Yaw-':
            if abs(value) > 0.1:
                RCStatus.d = int(cls.rc_threshold[2] * 0.5 * (value - 1))
            else:
                RCStatus.d = 0
