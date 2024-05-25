from base_details_window import BaseDetailsWindow
from content import contents_declarative_details
from PyQt6.QtWidgets import *
from function import add_excluded_attribute, remove_excluded_attribute


class DetailsDeclarativeWindow(BaseDetailsWindow):
    def __init__(self, switch_view_callback, color_map):
        super().__init__("declarative", switch_view_callback, contents_declarative_details, color_map)
        # todo: to improve