from parameters import MODE, LAPS, highest_marker_index
from MarkersDetector import MarkersDetector
from MarkerStatus import MarkerStatus
from RCStatus import RCStatus


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

    @classmethod
    def update_memory(cls):
        for key in cls.markers_screen_pos.keys():
            cls.markers_screen_pos[key]['reliability'] = 0.9875 * cls.markers_screen_pos[key]['reliability']
        if MarkersDetector.ids is not None:
            for i in range(len(MarkersDetector.ids)):
                marker_id = MarkersDetector.ids[i][0]
                if marker_id <= highest_marker_index:
                    cls.markers_screen_pos[str(marker_id)] = dict(corners=MarkersDetector.corners[i][0],
                                                                  reliability=1)

        if cls.current_target_marker_id == -1 and MODE.status == MODE.AUTO_FLIGHT:
            print('Automatic flight finished')
            MarkerStatus.reset()
            RCStatus.reset()
            MODE.status = MODE.MANUAL_FLIGHT

    @classmethod
    def get_new_target(cls):
        if cls.current_target_marker_id < highest_marker_index:
            cls.current_target_marker_id += 1
        elif LAPS:
            MarkersMemory.current_target_marker_id = 0
        else:
            MarkersMemory.current_target_marker_id = -1

    @classmethod
    def update_target(cls):
        if cls.current_target_marker_id != -1:
            cls.passing_gate = False
            print('Gate passed, looking for gate n°', cls.current_target_marker_id)
        else:
            cls.passing_gate = False
            print('Last gate passed')

    @classmethod
    def __get_dict__(cls):
        try:
            mm: dict = {'Target id': cls.current_target_marker_id,
                        'Trust (%)': 100 * cls.markers_screen_pos[str(cls.current_target_marker_id)]['reliability']}
        except KeyError:
            mm: dict = {'Target id': cls.current_target_marker_id,
                        'Trust (%)': 'N/D'}
        return mm
