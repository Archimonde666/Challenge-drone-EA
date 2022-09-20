import pygame
from typing import List


class Gamepad:
    keyboard_map: dict = dict(name='Keyboard',
                              axes={},
                              buttons={pygame.K_ESCAPE: 'Stop',
                                       pygame.K_SPACE: 'Emergency',
                                       pygame.K_t: 'Takeoff',
                                       pygame.K_l: 'Land',
                                       pygame.K_LEFT: 'Left',
                                       pygame.K_RIGHT: 'Right',
                                       pygame.K_UP: 'Forward',
                                       pygame.K_DOWN: 'Backward',
                                       pygame.K_z: 'Up',
                                       pygame.K_s: 'Down',
                                       pygame.K_d: 'Yaw+',
                                       pygame.K_q: 'Yaw-'}
                              )
    map_list: List[dict] = [dict(name='Logitech Extreme 3D',
                                 axes={0: 'Roll',
                                       1: 'Pitch',
                                       2: 'Yaw',
                                       3: 'Height'},
                                 buttons={0: 'Stop',        # Button 1
                                          1: 'Takeoff',     # Button 2
                                          2: 'Land',        # Button 3
                                          3: 'Emergency',   # Button 4
                                          }),

                            dict(name='Controller (Xbox One For Windows)',
                                 axes={0: 'Roll',           # Left stick left/right
                                       1: 'Pitch',          # Left stick up/down
                                       2: 'Yaw',            # Right stick left/right
                                       3: 'Height',         # Right stick up/down
                                       4: 'Yaw-',           # Left trigger
                                       5: 'Yaw+'            # Right trigger
                                       },
                                 buttons={0: 'Takeoff',     # A
                                          1: 'Land',        # B
                                          2: 'Emergency',   # X
                                          3: 'Stop',        # Y
                                          }),

                            dict(name='Default',
                                 axes={0: 'Roll',           # Left stick left/right
                                       1: 'Pitch',          # Left stick up/down
                                       2: 'Yaw',            # Right stick left/right
                                       3: 'Height',         # Right stick up/down
                                       4: 'Yaw-',           # Left trigger
                                       5: 'Yaw+'            # Right trigger
                                       },
                                 buttons={0: 'Takeoff',     # A
                                          1: 'Land',        # B
                                          2: 'Emergency',   # X
                                          3: 'Stop',        # Y
                                          })
                            ]
