# System imports
import json
import os
import pkgutil

# Third-party imports
import streamlit as st

# Local imports
import SmartLeads
from SmartLeads.license import License
from SmartLeads.streamlit_app.util.folders import get_workspace_folders

_WORKSPACE_FOLDERS = get_workspace_folders(tool_name="SmartLeads")
_LICENSE_KEY_FILE_PATH = os.path.join(_WORKSPACE_FOLDERS["LICENSE"], "license.skm")


def load_license_config():
    license_config_json = pkgutil.get_data(
        SmartLeads.__package__, "license.json"
    ).decode("utf-8")
    st.session_state.license_config = json.loads(license_config_json)


def activate_license_key():
    license_key = st.text_input("Please enter your license key:")
    st.session_state.license = License.from_key(
        rsa_public_key=st.session_state.license_config["rsaPubKey"],
        activation_token=st.session_state.license_config["activationToken"],
        product_id=st.session_state.license_config["productId"],
        key=license_key,
    )
    if st.button("Activate License"):
        (
            st.session_state.is_license_valid,
            license_message,
        ) = st.session_state.license.is_license_valid()
        if not st.session_state.is_license_valid:
            st.error(license_message)
        else:
            show_license_expiration_warning()
            st.session_state.license.save_license(file_path=_LICENSE_KEY_FILE_PATH)
            st.success("License activated successfully.")
            st.experimental_rerun()


def is_offline_license_file_valid():
    if os.path.exists(_LICENSE_KEY_FILE_PATH):
        st.session_state.license = License.from_file(
            rsa_public_key=st.session_state.license_config["rsaPubKey"],
            key_file_path=_LICENSE_KEY_FILE_PATH,
        )
        (
            st.session_state.is_license_valid,
            _,
        ) = st.session_state.license.is_license_valid()
        show_license_expiration_warning()


def show_license_expiration_warning():
    if st.session_state.license.get_days_until_expiration() < 30:
        st.toast(
            f"The license expires in {st.session_state.license.get_days_until_expiration()} days. Please contact support to renew your license.",
            icon="⚠️",
        )
