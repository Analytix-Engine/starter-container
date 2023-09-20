import pkgutil

import streamlit as st

import SmartLeads.streamlit_app.assets as assets

CATEGORICAL_COLOUR_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#aec7e8",
    "#ffbb78",
]


def insert_css_theme():
    css = pkgutil.get_data(assets.__package__, "theme.css").decode("utf-8")
    st.markdown(
        """\
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com"
            crossorigin>
            <link
href="https://fonts.googleapis.com/css2?family=Lato:wght@900&display=swap"
rel="stylesheet">""",
        unsafe_allow_html=True,
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    hide_decoration_bar_style = """
        <style>
            header {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
