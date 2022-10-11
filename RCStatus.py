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
    def reset(cls):
        cls.a = 0
        cls.b = 0
        cls.c = 0
        cls.d = 0

    @classmethod
    def __get_dict__(cls) -> dict:
        rc: dict = {'a': cls.a,
                    'b': cls.b,
                    'c': cls.c,
                    'd': cls.d}
        return rc
