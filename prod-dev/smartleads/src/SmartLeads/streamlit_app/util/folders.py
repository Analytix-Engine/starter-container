import os
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

WORKSPACE_FOLDERS = {
    "CONF": ["conf"],
    "CATALOG": ["conf", "catalog"],
    "DATA": ["data"],
    "LICENSE": ["license"],
}


def get_documents_folder():
    if os.name == "posix":  # macOS (posix) path
        return str(Path.home() / "Documents")
    elif os.name == "nt":  # Windows (nt) path
        return str(Path.home() / "Documents")
    else:
        raise OSError("Unsupported operating system")


def get_workspace_folder(tool_name: str) -> str:
    """Returns the home folder for the user.

    Args:
        tool_name (str): The name of the tool.
    Returns:
        str: Path to the home folder.
    """
    # For MacOs and Linux
    if os.name == "posix":
        return os.path.join(os.path.expanduser("~"), f".{tool_name}")
    elif os.name == "nt":
        return os.path.join(os.path.expandvars("%userprofile%"), f".{tool_name}")
    else:
        raise OSError("Unsupported operating system")


def get_workspace_folders(tool_name: str) -> Dict:
    """Gets a dictionary of the workspace folders used by the tool.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        Dict: A dictionary of the workspace folders used by the tool.
    """
    result = {}
    for key, value in WORKSPACE_FOLDERS.items():
        result[key] = os.path.join(get_workspace_folder(tool_name), *value)
    return result


def create_workspace_structure(tool_name: str):
    """Creates the folder structures in the workspace folder.

    Args:
        tool_name (str): The name of the tool.

    Return:
        None
    """
    documents_folder = get_documents_folder()
    if not os.path.exists(documents_folder):
        os.makedirs(documents_folder, exist_ok=True)
    for _, value in WORKSPACE_FOLDERS.items():
        folder_path = os.path.join(get_workspace_folder(tool_name), *value)
        os.makedirs(folder_path, exist_ok=True)


def local_path_explorer(
    allowed_file_extentions: List[str] = None, is_folder=False
) -> str:
    """Using Streamlit, explore the local path to specify the
    ocation of a file."""
    st.markdown("---")
    # First check if the active path is in the session state. If not,
    # set it to the current working directory.
    if "local_path_explorer_active_path" not in st.session_state:
        st.session_state["local_path_explorer_active_path"] = get_documents_folder()
        active_path = get_documents_folder()
    else:
        active_path = st.session_state["local_path_explorer_active_path"]

    # Split the active path into a list of folders
    active_path_list = active_path.split(os.sep)
    # join the active path list to create a string, windows uses \ and unix uses /
    # check if selected_file variable is available
    if "selected_file" in locals():
        display_path = os.sep.join(active_path_list)
        st.success(f" Selection: `{display_path}`")

    # Creating three columns.

    # # The first will contain the active path and allows people to go
    # back to a previous folder.

    # # The second will contain a list of folders in the active path.

    # # The third will contain a list of files in the active path.
    active_path_column, folder_column, file_column = st.columns([4, 2, 2])

    # Working in the active path column
    with active_path_column:
        # Looping though each item in the active path
        navigate_active_path = st.radio(
            "# 1️⃣ Path",
            active_path_list,
            index=len(active_path_list) - 1,
            key="active_path_radio_button",
            help="Select input path to explore folders",
        )

        if navigate_active_path is not None:
            active_path = os.sep.join(
                active_path_list[: active_path_list.index(navigate_active_path) + 1]
            )
            if active_path != st.session_state["local_path_explorer_active_path"]:
                st.session_state["local_path_explorer_active_path"] = active_path

                st.experimental_rerun()

    # Get a list of folders in the active_path
    contents = sorted(os.listdir(active_path))

    with folder_column:
        # Create a list of buttons for each file in the active path
        folders = [
            c
            for c in contents
            if os.path.isdir(os.path.join(active_path, c)) and not c.startswith(".")
        ]

        folders = [f"📁 {f}" for f in folders]

        # navigate_folder = st.radio(
        #     "# 2️⃣ Folder", [""] + folders,
        #     key="folder_radio_button",
        #     help = "Select input folder to explore files"
        # )
        navigate_folder = st.selectbox(
            "# 2️⃣ Folder",
            [""] + folders,
            key="folder_select",
            help="Select input folder to explore files",
        )

        if navigate_folder:
            navigate_folder = navigate_folder.replace("📁 ", "")
            active_path = os.path.join(active_path, navigate_folder)
            if active_path != st.session_state["local_path_explorer_active_path"]:
                st.session_state["local_path_explorer_active_path"] = active_path
                st.experimental_rerun()

    if is_folder is False:
        with file_column:
            files = [
                c for c in contents if os.path.isfile(os.path.join(active_path, c))
            ]

            files = [f"🗳️ {f}" for f in files]

            # Filters out allowed file extentions
            if allowed_file_extentions is not None:
                files = [
                    f for f in files if f.split(".")[-1] in allowed_file_extentions
                ]

            # selected_file = st.radio(
            #     "# 3️⃣ File",
            #     files,
            #     key="selected_file_radio_button",
            #     help="Select input file to load"
            # )
            selected_file = st.selectbox(
                "# 3️⃣ File",
                files,
                key="selected_file_select",
                help="Select input file to load",
            )
        if selected_file is not None:
            selected_file = selected_file.replace("🗳️ ", "")
            # st.success(f"Selected file: {selected_file}")
            display_path = os.sep.join(active_path_list + [selected_file])
            st.success(f" Selection: `{display_path}`")
            st.markdown("---")
            return os.path.join(active_path, selected_file)
    else:
        st.markdown("---")
        return active_path
    return None
