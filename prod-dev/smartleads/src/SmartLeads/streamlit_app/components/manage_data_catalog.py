# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pandas as pd
import streamlit as st
from kedro_datasets.pandas import CSVDataSet, ExcelDataSet

from SmartLeads.streamlit_app.util.catalogs import (
    add_pickle_to_catalog,
    create_catalog_safe_name,
    load_catalog,
    save_catalog,
)
from SmartLeads.streamlit_app.util.folders import local_path_explorer
from SmartLeads.streamlit_app.util.page import Page
from SmartLeads.streamlit_app.util.ui import custom_markdown


class ManageDataCatalogPage(Page):
    def __init__(self, menu_label, menu_icon):
        super().__init__(menu_label, menu_icon, catalog="DATA")
        self.input_catalogs = None
        self.output_catalog = menu_label
        self.csv_delimeter_map = {",": ",", ";": ";", "|": "|", "tab": "\t"}

    def add_csv_dataset(self):
        """Adds a csv dataset to the data_catalog."""

        catalog = load_catalog(self.catalog)
        file = local_path_explorer(["csv", "txt", "tab"])
        added = False
        columns = st.columns([2, 2, 2, 2])
        if file is not None:
            with columns[1]:
                delimiter = st.selectbox(
                    "# 4️⃣ Select Delimiter*",
                    self.csv_delimeter_map.keys(),
                    help="What delimiter is used in the csv file?",
                    index=0,
                    label_visibility="visible",
                )  # noqa: E501

            with columns[2]:
                dataset_name = st.text_input(
                    "# 5️⃣ Reference*",
                    label_visibility="visible",
                    help=(
                        "Dataset name. This will be used to refer to"
                        " the dataset throughout."
                    ),
                )

        if file is not None and dataset_name != "":
            # Get the full path to the file that is specified in the
            # file_uploader.

            file_path = file
            st.markdown("---")
            csv_columns = st.columns([2, 4, 2])
            with csv_columns[1]:
                if st.button(
                    "➕ Add dataset",
                    use_container_width=True,
                    type="primary",
                    help="Add the dataset to the data catalog.",
                ):
                    identifier = create_catalog_safe_name(
                        self.output_catalog, dataset_name, "data"
                    )
                    catalog.add(
                        identifier,
                        CSVDataSet(
                            file_path,
                            load_args={"sep": self.csv_delimeter_map[delimiter]},
                            save_args={"sep": self.csv_delimeter_map[delimiter]},
                        ),
                        replace=True,
                    )
                    identifier = create_catalog_safe_name(
                        self.output_catalog, dataset_name, "parms"
                    )
                    parameters = {dataset_name: identifier}
                    catalog = add_pickle_to_catalog(
                        data_path=self.output_catalog,
                        data_catalog=catalog,
                        data_catalog_identifier=self.catalog,
                        dataset_name=identifier,
                    )
                    catalog.save(identifier, parameters)
                    save_catalog(catalog, self.catalog)
                    added = True
                if added:
                    st.success("Dataset sucessfully added.")
        else:
            # give info to user
            st.info(
                "Please select the appropriate delimiter and enter a "
                "reference name for the dataset."
            )

    def add_excel_dataset(self):
        """Adds an excel dataset to the data_catalog."""

        catalog = load_catalog(self.catalog)

        file = local_path_explorer(["xlsx", "xls"])

        columns = st.columns([2, 2, 2, 2])

        added = False
        if file is not None:  # and dataset_name is not None:
            # Get the full path to the file that is specified in the file_uploader
            file_path = file
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            with columns[1]:
                sheet_name = st.selectbox(
                    "4️⃣ Sheet Name*",
                    [""] + sheet_names,
                    index=0,
                    label_visibility="visible",
                    help="Select the sheet name from the excel file.",
                )
            with columns[2]:
                dataset_name = st.text_input(
                    " 5️⃣ Reference*",
                    label_visibility="visible",
                    help=(
                        "Name data by typing in the cell below. This will be used "
                        "to refer to the dataset throughout."
                    ),
                )
        if file is not None and dataset_name != "" and sheet_name != "":
            print(f"dataset_name--{dataset_name}--")
            print(f"sheet_name--{sheet_name}--")
            file_path = file
            st.markdown("---")
            excel_columns = st.columns([2, 4, 2])
            with excel_columns[1]:
                if st.button("➕ Add dataset", use_container_width=True, type="primary"):
                    # with columns[2]:
                    #     if (sheet_name is not None) and st.button(
                    #         "Add dataset", use_container_width=True,
                    #         help="Add the dataset to the data catalog."
                    #     ):
                    identifier = create_catalog_safe_name(
                        self.output_catalog, dataset_name, "data"
                    )
                    catalog.add(
                        identifier,
                        ExcelDataSet(
                            file_path,
                            load_args={"sheet_name": sheet_name},
                            save_args={"sheet_name": sheet_name},
                        ),
                        replace=True,
                    )
                    identifier = create_catalog_safe_name(
                        self.output_catalog, dataset_name, "parms"
                    )
                    parameters = {dataset_name: identifier}
                    catalog = add_pickle_to_catalog(
                        data_path=self.output_catalog,
                        data_catalog=catalog,
                        data_catalog_identifier=self.catalog,
                        dataset_name=identifier,
                    )
                    catalog.save(identifier, parameters)
                    save_catalog(catalog, self.catalog)
                    added = True
                if added:
                    st.success("Dataset sucessfully added. Go to OneClickRun tab.")
        else:
            # give info to user
            st.info(
                "Please select a sheet name and enter a reference name for the dataset."
            )

    def add_dataset(self):
        """Adds a dataset to the Data Catalog."""

        # Allow the user to specify the type of dataset.

        st.markdown("")

        # with st.expander(" Add `.csv` or `.xlsx` files to Data Catalog"):
        columns = st.columns([3, 2, 3])
        with columns[1]:
            dataset_type = st.selectbox(
                "Specify the data type",
                ["", "CSV Format", "Excel File"],
                index=0,
                label_visibility="collapsed",
                help="Specify the file type",
            )  # noqa: E501

        # If the user selects CSVDataSet, then call the add_csv_dataset functi      on.
        # with st.expander(" Specify the path to the file"):
        if dataset_type == "CSV Format":
            self.add_csv_dataset()
        elif dataset_type == "Excel File":
            self.add_excel_dataset()

    def view_page(self):
        """Allows the user to add, edit and remove dataset entries from the data
        catalog.
        """
        custom_markdown("Lato", "#000000", 40, "Upload data", bold=True)

        # Write the streamlit user interface to allow the user to select whether
        # they want to add, edit or remove a dataset.

        st.header("", divider="blue")

        data_type = st.radio(
            "Select Data Type To Upload",
            ["Customer Data", "Product Data"]
        )

        self.add_dataset()
