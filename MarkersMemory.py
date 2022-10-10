from parameters import FPS


class MarkersMemory:
    """
    Saves the last on-screen position of every marker in a dictionary
    markers_screen_pos_memory ->    [0] -> {marker n°0 corners positions: 4*[ScreenPosition],
                                            marker n°0 reliability: float}
                                    [1] -> {marker n°1 corners position: 4*[ScreenPosition],
                                            marker n°1 reliability: float}
                                    :
    """
    current_target_marker_id: int = 1
    passing_gate: bool = False
    cmp: int = 0
    markers_screen_pos: dict = {}
    highest_marker_id: int = 10

    @classmethod
    def setup(cls, highest_marker_index: int = 10):
        cls.highest_marker_id = highest_marker_index

    @classmethod
    def update(cls, ids, corners):
        for key in cls.markers_screen_pos.keys():
            cls.markers_screen_pos[key]['reliability'] = 0.98 * cls.markers_screen_pos[key]['reliability']
        if ids is not None:
            for i in range(len(ids)):
                marker_id = ids[i][0]
                if marker_id <= cls.highest_marker_id:
                    cls.markers_screen_pos[str(marker_id)] = dict(corners=corners[i][0],
                                                                  reliability=1)
        if cls.passing_gate:
            if cls.cmp > 0.1 * FPS and cls.current_target_marker_id != -1:
                cls.cmp = 0
                cls.passing_gate = False
                print('Gate passed, looking for gate n°', cls.current_target_marker_id)
            elif cls.cmp > 0.5 * FPS and cls.current_target_marker_id == -1:
                cls.cmp = 0
                cls.passing_gate = False
                print('Last gate passed')
            else:
                cls.cmp += 1

    @classmethod
    def __get_dict__(cls):
        try:
            mm: dict = {'Target id': cls.current_target_marker_id,
                        'Trust (%)': 100 * cls.markers_screen_pos[str(cls.current_target_marker_id)]['reliability']}
        except KeyError:
            mm: dict = {'Target id': 'N/D',
                        'Trust (%)': 'N/D'}
        return mm
