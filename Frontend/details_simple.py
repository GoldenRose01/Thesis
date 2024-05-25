from base_details_window import BaseDetailsWindow
from content import contents_simple_details

class DetailsSimpleWindow(BaseDetailsWindow):
    def __init__(self, switch_view_callback, color_map):
        super().__init__("simple", switch_view_callback, contents_simple_details, color_map)
