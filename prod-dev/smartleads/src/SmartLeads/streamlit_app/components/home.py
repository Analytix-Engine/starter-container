# System imports
import pkgutil
import base64
import os

# Third-party imports
import streamlit as st

# Local imports
from SmartLeads.streamlit_app.util.page import Page
import SmartLeads.streamlit_app.assets as assets


class HomePage(Page):
    def __init__(self, menu_label, menu_icon):
        super().__init__(menu_label, menu_icon, catalog="DATA")

    def view_page(self):
        banner_data = pkgutil.get_data(
            assets.__package__, "Linkedin_Banner.jpg"
        )

        banner_html = f"""
            <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-repeat: no-repeat;
            background-size: cover;
            margin: 0;
            padding: 0;">
                <img src="data:image/png;base64,{
                    base64.b64encode(banner_data).decode()
                }">
            </div>
        """

        st.markdown(banner_html, unsafe_allow_html=True)

        # Edit the body of the page
        st.markdown('''<style>
        .css-fg4pbf {
            position: absolute;
            background:  #011E45;
            color: rgb(255, 255, 255);
            inset: 0px;
            overflow: hidden;
        }
        </style>''', unsafe_allow_html=True)
        
        #Edit header of the page
        st.markdown('''<style>
        .css-18ni7ap {
        position: fixed;
        top: 0px;
        left: 0px;
        right: 0px;
        height: 2.875rem;
        background: #011E45;
        outline: none;
        z-index: 999990;
        display: block;
        }
        <style>''', unsafe_allow_html=True)

        st.markdown(
            f"<h2 style='text-align: center;color: white;'>{self.menu_label}</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h4 style='text-align: center;color: white;'>Please select a page</h4>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    HomePage("Home", "🏠").view_page()