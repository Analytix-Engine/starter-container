# System imports

# Third-party imports
import streamlit as st

# Local imports
from SmartLeads.streamlit_app.util.page import Page

""""
The Introduction page of the Streamlit UI app.
"""


class IntroductionPage(Page):
    def __init__(self, menu_label, menu_icon):
        super().__init__(menu_label, menu_icon, catalog="DATA")

    def view_page(self):
        st.title("Introduction")
