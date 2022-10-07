from parameters import ScreenPosition, Distance, Angle, RAD2DEG
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

    # angle and distance between marker and drone
    m_angle: Angle = Angle(0)
    m_distance: Distance = Distance(0)

    height: Distance = Distance(0)
    width: Distance = Distance(0)

    @classmethod
    def reset(cls):
        cls.id = -1
        cls.corners = []
        cls.center_pt = ScreenPosition((0, 0))
        cls.top_pt = ScreenPosition((0, 0))
        cls.bottom_pt = ScreenPosition((0, 0))
        cls.left_pt = ScreenPosition((0, 0))
        cls.right_pt = ScreenPosition((0, 0))
        cls.m_angle = Angle(0)
        cls.m_distance = Distance(0)
        cls.height = Distance(0)
        cls.width = Distance(0)

    @classmethod
    def __get_dict__(cls) -> dict:
        ms: dict = {'id': cls.id,
                    'm_angle': int(cls.m_angle * RAD2DEG),
                    'm_distance': cls.m_distance,
                    'm_height': cls.height,
                    'm_width': cls.width}
        return ms
