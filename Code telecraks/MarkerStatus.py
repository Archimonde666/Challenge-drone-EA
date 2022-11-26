from parameters import ScreenPosition, Distance, DRONE_POS
from typing import List


class MarkerStatus:
    """
    Contains data about the marker that is selected as the target to be reached
    """

    id: int = -1
    corners: List[ScreenPosition] = []

    # Origin axis
    center_pt: ScreenPosition = ScreenPosition((0, 0))
    # Horizontal axis
    top_pt: ScreenPosition = ScreenPosition((0, 0))
    bottom_pt: ScreenPosition = ScreenPosition((0, 0))
    # Vertical axis
    left_pt: ScreenPosition = ScreenPosition((0, 0))
    right_pt: ScreenPosition = ScreenPosition((0, 0))
    offset: ScreenPosition = ScreenPosition((0, 0))

    target_pt: ScreenPosition = ScreenPosition(DRONE_POS)

    height: Distance = Distance(0)
    width: Distance = Distance(0)

    height_lr_delta = Distance(0)
    width_tb_delta = Distance(0)

    @classmethod
    def reset(cls):
        cls.id = -1
        cls.corners = []
        cls.center_pt = ScreenPosition((0, 0))
        cls.top_pt = ScreenPosition((0, 0))
        cls.bottom_pt = ScreenPosition((0, 0))
        cls.left_pt = ScreenPosition((0, 0))
        cls.right_pt = ScreenPosition((0, 0))
        cls.offset = ScreenPosition((0, 0))
        cls.target_pt = ScreenPosition(DRONE_POS)
        cls.height = Distance(0)
        cls.width = Distance(0)
        cls.height_lr_delta = Distance(0)
        cls.width_tb_delta = Distance(0)

    @classmethod
    def __get_dict__(cls) -> dict:
        ms: dict = {'id': cls.id,
                    'm_height': cls.height,
                    'm_width': cls.width,
                    'dh': cls.height_lr_delta*100}
        return ms
