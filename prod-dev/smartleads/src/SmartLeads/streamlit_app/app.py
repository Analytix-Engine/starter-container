# System imports

# Third-party imports
import streamlit as st

# Local imports
from SmartLeads.streamlit_app.components.home import HomePage
from SmartLeads.streamlit_app.components.manage_data_catalog import ManageDataCatalogPage
from SmartLeads.streamlit_app.util.folders import create_workspace_structure
from SmartLeads.streamlit_app.util.license_activation import (
    activate_license_key,
    is_offline_license_file_valid,
    load_license_config,
)
from SmartLeads.streamlit_app.util.page_navigation import PageNavigation
from SmartLeads.streamlit_app.util.theme import insert_css_theme

STREAMLIT_PAGES = [
    HomePage(menu_label="Home", menu_icon="house"),
    ManageDataCatalogPage(menu_label="Manage Data Catalog", menu_icon="database"),
]


if __name__ == "__main__":
    create_workspace_structure(tool_name="SmartLeads")
    st.set_page_config(
        "SmartLeads",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    insert_css_theme()
    # load_license_config()

    # if "is_license_valid" not in st.session_state:
    #   st.session_state.is_license_valid = False
    #   is_offline_license_file_valid()

    # if not st.session_state.is_license_valid:
    #     activate_license_key()
    # else:
    if True:
        PageNavigation(STREAMLIT_PAGES).create_option_menu()
