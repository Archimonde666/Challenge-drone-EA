from parameters import MODE, LAPS, markers_interval, ENV
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
    current_target_marker_id: int = 0
    passing_gate: bool = False
    cmp: int = 0
    markers_screen_pos: dict = {}
    forgetting_factor: float = 0.0

    @classmethod
    def setup(cls, first_marker_id: int = 0):
        cls.current_target_marker_id = first_marker_id
        if ENV.status == ENV.REAL:
            cls.forgetting_factor = 0.9875
        elif ENV.status == ENV.SIMULATION:
            cls.forgetting_factor = 0.94

    @classmethod
    def update_memory(cls):
        # if at least one marker is detected, ...
        if MarkersDetector.ids is not None:
            # ... let's browse the markers in the frame
            for i in range(len(MarkersDetector.ids)):
                marker_id = MarkersDetector.ids[i][0]
                # if the marker index is higher than the maximum expected one,
                # the marker is discarded
                if marker_id <= markers_interval[1]:
                    # If the marker already exists in the memory, ...
                    if any(str(marker_id) == key for key in cls.markers_screen_pos.keys()):
                        # ... let's update the memory with the last seen corners
                        # and increase the reliability level
                        cls.markers_screen_pos[str(marker_id)]['corners'] = MarkersDetector.corners[i][0]
                        if cls.markers_screen_pos[str(marker_id)]['reliability'] < 0.25:
                            cls.markers_screen_pos[str(marker_id)]['reliability'] = 0.25
                        else:
                            cls.markers_screen_pos[str(marker_id)]['reliability'] = \
                                cls.forgetting_factor * (cls.markers_screen_pos[str(marker_id)]['reliability'] - 1) + 1
                    else:
                        # If the marker does not exist in the memory (if it is seen for the 1st time),
                        # let's allocate a memory field for it.
                        cls.markers_screen_pos[str(marker_id)] = dict(corners=MarkersDetector.corners[i][0],
                                                                      reliability=0.25)

            for saved_marker_id in cls.markers_screen_pos.keys():
                if all(saved_marker_id != str(MarkersDetector.ids[i][0]) for i in range(len(MarkersDetector.ids))):
                    # For all markers in the memory, if they are not detected on the frame,
                    # let's decrease their reliability level
                    cls.markers_screen_pos[saved_marker_id]['reliability'] = \
                        cls.forgetting_factor * cls.markers_screen_pos[saved_marker_id]['reliability']
        else:
            # If no markers are detected on the frame,
            # let's decrease the reliability level of every marker in the memory
            for key in cls.markers_screen_pos.keys():
                cls.markers_screen_pos[key]['reliability'] = \
                    cls.forgetting_factor * cls.markers_screen_pos[key]['reliability']

        if cls.current_target_marker_id == -1 and MODE.status == MODE.AUTO_FLIGHT:
            print('Automatic flight finished')
            MarkerStatus.reset()
            RCStatus.reset()
            MODE.status = MODE.MANUAL_FLIGHT

    @classmethod
    def get_new_target(cls):
        if cls.current_target_marker_id < markers_interval[1]:
            cls.current_target_marker_id += 1
        elif LAPS:
            MarkersMemory.current_target_marker_id = markers_interval[0]
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
                        'Trust (%)': round(
                            100 * cls.markers_screen_pos[str(cls.current_target_marker_id)]['reliability'])}
        except KeyError:
            mm: dict = {'Target id': cls.current_target_marker_id,
                        'Trust (%)': 'N/D'}
        return mm
