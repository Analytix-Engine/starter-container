import streamlit as st


def custom_markdown(
    font_family, color, font_size, text, bold=False, italic=False, help=None
):
    """
    Custom markdown function to allow for custom font family, color, font size, bold,
    and italic.

    Args:
        font_family (str): The font family to use
        color (str): The color to use
        font_size (int): The font size to use
        text (str): The text to display
        bold (bool): Whether to use bold formatting (default False)
        italic (bool): Whether to use italic formatting (default False)
    """
    # create a list of HTML tags to include based on the bold and italic parameters
    tags = []
    if bold:
        tags.append("b")
    if italic:
        tags.append("i")

    # create the HTML string with the appropriate tags
    html = (
        f'<h1 style="text-align:center; font-family:{font_family}; '
        f'color:{color}; font-size: {font_size}px;">'
    )
    for tag in tags:
        html += f"<{tag}>"
    html += text
    for tag in reversed(tags):
        html += f"</{tag}>"
    html += "</h2>"

    return st.markdown(html, unsafe_allow_html=True, help=help)


def info_header(header_markdown: str, info_text: str):
    cols = st.columns([9, 1])
    with cols[0]:
        st.markdown(header_markdown)
    with cols[1]:
        custom_markdown("Lato", "#000000", 40, "", bold=True, help=info_text)


def info_small(info_text: str):
    custom_markdown("Lato", "#000000", 40, "", bold=True, help=info_text)
