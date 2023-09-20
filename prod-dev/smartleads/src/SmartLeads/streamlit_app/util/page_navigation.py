import pkgutil
from typing import List

import streamlit as st
from streamlit_option_menu import option_menu

import SmartLeads.streamlit_app.assets as assets
from SmartLeads.streamlit_app.util.page import Page

_STYLES = {
    "container": {
        "padding": "0!important",
        "background-color": "#111827",
        "border-radius": "0",
    },
    "icon": {"color": "#38A1FF", "font-size": "16px"},
    "nav-link": {
        "font-size": "16px",
        "text-align": "left",
        "margin": "0",
        "color": "#D1D5DB",
        "--hover-color": "#FFFFFFF14",
    },
    "nav-link-selected": {
        "background-color": "#FFFFFF14",
        "color": "#38A1FF",
    },
}


class PageNavigation:
    def __init__(self, pages: List[Page]):
        self.pages = pages
        self.current_page = None

    def create_option_menu(self):
        menu_labels = [page.menu_label for page in self.pages]
        menu_icons = [page.menu_icon for page in self.pages]
        with st.sidebar:
            self.add_logo()
            selected = option_menu(
                None,
                menu_labels,
                icons=menu_icons,
                menu_icon="cast",
                default_index=0,
                styles=_STYLES,
            )
        self.change_page(selected)

    def change_page(self, menu_label):
        self.current_page = self.get_page(menu_label)
        self.current_page.view_page()

    def get_page(self, menu_label):
        return next(
            (page for page in self.pages if page.menu_label == menu_label),
            None,
        )

    def add_logo(self):
        logo_html = pkgutil.get_data(assets.__package__, "logo.html").decode("utf-8")
        st.write(logo_html, unsafe_allow_html=True)
