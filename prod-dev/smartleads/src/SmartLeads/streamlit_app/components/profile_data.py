# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from SmartLeads.pipelines.profile_data.pipeline import create_pipeline
from SmartLeads.streamlit_app.util.catalogs import (
    create_catalog_safe_name,
    get_select_labels_from_catalog,
    load_catalog,
)
from SmartLeads.streamlit_app.util.formatting import int_space
from SmartLeads.streamlit_app.util.page import Page
from SmartLeads.streamlit_app.util.runner import run_pipeline


class ProfileDataPage(Page):
    def __init__(self, menu_label: str, menu_icon: str, input_catalog: str):
        super().__init__(menu_label, menu_icon, catalog="DATA")
        self.outputs = ["data_profile"]
        self.output_catalog = menu_label
        self.input_catalog = input_catalog
        self.introduction_markdown = """\
        # Create Data Profile\n
        In the previous step we added our dataset to the project.

        When doing any kind of data analysis, it always pays to have a look
        at the data first. This step creates the data profile for the dataset.

        This not only allows us to check that our data is being processed in the
        right way but also allows the tool to take a (very educated) guess at the
        data types of the columns in the dataset."""

    def plot_histograms(self, h):
        fig = go.Figure()
        x_values = h["bin_edges"]
        y_values = h["counts"]
        padding = 0.01 * np.mean(h["bin_edges"])
        for x_start, x_end, y in zip(x_values[:-1], x_values[1:], y_values):
            fig.add_trace(
                go.Scatter(
                    x=[
                        x_start + padding,
                        x_start + padding,
                        x_end - padding,
                        x_end - padding,
                    ],
                    y=[0, y, y, 0],
                    fill="toself",
                    fillcolor="dodgerblue",
                    line_color="dodgerblue",
                    mode="lines",
                )
            )

        # Remove the legend
        fig.update_layout(showlegend=False)

        return fig

    def show_global_stats(self, data_profile_obj):
        st.markdown("---")
        st.markdown("## Global Statistics")
        st.markdown(
            "Here we can see some global statistics for the dataset."
            "These are statistics that do not change per column and gives us a "
            "good overview of the dataset."
        )
        tabs = st.tabs(["Analysis", "Summary", "Alerts", "Variables"])
        with tabs[0]:
            st.markdown("This tab allows us to see when the analysis was run.")
            analysis_header_columns = st.columns(3)
            with analysis_header_columns[0]:
                st.caption(f'Title: `{data_profile_obj["analysis"]["title"]}`')
            with analysis_header_columns[1]:
                st.caption(f'Created: `{data_profile_obj["analysis"]["date_start"]}`')
            with analysis_header_columns[2]:
                st.caption(f'Finished: `{data_profile_obj["analysis"]["date_end"]}`')

        with tabs[1]:
            st.markdown(
                "This tab allows us to see some summary statistics for the " "dataset."
            )
            dataset_header_columns = st.columns(3)
            with dataset_header_columns[0]:
                st.markdown("### Size")
                n = int_space(data_profile_obj["table"]["n"])
                st.write(f"Number of records in dataset: `{n}`")
                n_var = int_space(data_profile_obj["table"]["n_var"])
                st.write(f"Number of variables in dataset: `{n_var}`")
                memory_size = int_space(data_profile_obj["table"]["memory_size"])
                st.write(f"Size in memory: `{memory_size}`")
                record_size = int_space(data_profile_obj["table"]["record_size"])
                st.write(f"Size of one row in memory: `{record_size}`")

            with dataset_header_columns[1]:
                st.markdown("### Missing")
                n_cells_missing = int_space(
                    data_profile_obj["table"]["n_cells_missing"]
                )  # noqa: E501
                st.write(f"Number of cells missing: `{n_cells_missing}`")
                n_vars_with_missing = int_space(
                    data_profile_obj["table"]["n_vars_with_missing"]
                )
                n_vars_label = "Number of variables with missing values:"
                st.write(f"{n_vars_label} `{n_vars_with_missing}`")
                p_cells_missing = data_profile_obj["table"]["p_cells_missing"]
                st.write(f"Percentage of cells missing: `{p_cells_missing:.2%}`")

            with dataset_header_columns[2]:
                st.markdown("### Types")
                for key, value in data_profile_obj["table"]["types"].items():
                    st.write(f"{key}: `{value}`")

        with tabs[2]:
            st.markdown("Coming soon: Auomated alerts for the dataset.")
            alert_columns = st.columns(3)
            for i, alert in enumerate(data_profile_obj["alerts"]):
                with alert_columns[i % 3]:
                    alert = (
                        alert.replace("[", "`")
                        .replace("]", "`")
                        .replace("(", "`")
                        .replace(")", "`")
                    )
                    st.write(alert)

        with tabs[3]:
            st.markdown("This tab allows us to see the variables in the dataset.")
            variable_columns = st.columns(9)
            for i, variable in enumerate(data_profile_obj["variables"]):
                with variable_columns[i % 9]:
                    st.write(variable)
            st.markdown("---")

    def show_column_stats(self, data_profile_obj):
        """Shows the statistics for the columns in the data profile.

        Args:
            data_profile (dict): The data profile to show.

        Returns:
            None
        """
        st.markdown("---")
        st.markdown("## Variable Statistics")
        st.markdown(
            "Here we can see the statistics for each of the columns in the "
            "dataset. This allows us to see the statistics for each column and "
            "gives us a good idea of what is included in the dataset."
            "Please select the column for which you would like to view the data."
        )

        columns = list(data_profile_obj["variables"].keys())

        selected_column = st.selectbox("Choose column to view", columns, index=0)

        keys = {
            "n_distinct": "Number of distinct values",
            "p_distinct": "Percentage of distinct values",
            "is_unique": "Is unique",
            "n_unique": "Number of unique values",
            "p_unique": "Percentage of unique values",
            "type": "Type",
            "value_counts_without_nan": "Value counts without NaN",
            "value_counts_index_sorted": "Value counts index sorted",
            "ordering": "Ordering",
            "n_missing": "Number of missing values",
            "n": "Number of values",
            "p_missing": "Percentage of missing values",
            "count": "Count",
            "memory_size": "Memory size",
            "n_negative": "Number of negative values",
            "p_negative": "Percentage of negative values",
            "n_infinite": "Number of infinite values",
            "n_zeros": "Number of zeros",
            "mean": "Mean",
            "std": "Standard deviation",
            "variance": "Variance",
            "min": "Minimum",
            "max": "Maximum",
            "kurtosis": "Kurtosis",
            "skewness": "Skewness",
            "sum": "Sum",
            "mad": "Mean absolute deviation",
            "range": "Range",
            "5%": "5th percentile",
            "25%": "25th percentile",
            "50%": "50th percentile",
            "75%": "75th percentile",
            "95%": "95th percentile",
            "iqr": "Interquartile range",
            "cv": "Coefficient of variation",
            "p_zeros": "Percentage of zeros",
            "p_infinite": "Percentage of infinite values",
            "monotonic": "Monotonic",
            "histogram": "Histogram",
        }

        not_default_display = [
            "histogram",
            "value_counts_without_nan",
            "value_counts_index_sorted",
        ]

        tabs_keys = {
            "n_distinct": "Summary",
            "mean": "Statistics",
            "range": "Percentiles",
            "cv": "Other",
        }

        if selected_column is not None:
            tab_list = [v for k, v in tabs_keys.items()]
            tab_list.append("Histogram")
            tab_list.append("Data")
            tabs = st.tabs(tab_list)

        tab_key = "Summary"
        for key, description in keys.items():
            if key in not_default_display:
                continue
            if key in tabs_keys.keys():
                tab_key = tabs_keys[key]
                continue
            if key in data_profile_obj["variables"][selected_column]:
                tab_key_index = list(tabs_keys.values()).index(tab_key)
                with tabs[tab_key_index]:
                    st.write(
                        f"{description}: "
                        f'`{data_profile_obj["variables"][selected_column][key]}`'
                    )

        with tabs[len(tab_list) - 2]:
            if "histogram" in data_profile_obj["variables"][selected_column]:
                st.plotly_chart(
                    self.plot_histograms(
                        data_profile_obj["variables"][selected_column]["histogram"]
                    )
                )

        data = data_profile_obj["variables"][selected_column]
        with tabs[len(tab_list) - 1]:
            value_counts_without_nan = data["value_counts_without_nan"]
            df_data = [[k, v] for k, v in value_counts_without_nan.items()]
            df = pd.DataFrame(df_data, columns=["Value", "Count"])
            df = df.sort_values(by=["Count"], ascending=False)
            st.write(df)

    def view_data_profile(self):
        st.markdown("# View Data Profile")
        st.markdown(
            "In the previous step we created the data profile for our dataset. "
            "Here we can view the data profile. This can already start to give "
            "us some insights into the data and our customers' behaviour."
        )
        st.markdown("---")
        st.markdown("# Select a data profile to view.")
        catalog = load_catalog(self.catalog)
        labels = get_select_labels_from_catalog(self.output_catalog)

        data_profile_name = st.selectbox("Data Profile", labels, index=len(labels) - 1)

        if data_profile_name is not None:
            data_profile_name = create_catalog_safe_name(
                self.output_catalog, data_profile_name, "data_profile"
            )
            data_profile = catalog.load(data_profile_name)
            self.show_global_stats(data_profile)
            self.show_column_stats(data_profile)

    def run(self, raw_data_source: str, raw_data_profile: str):
        raw_data_source = create_catalog_safe_name(
            self.input_catalog, raw_data_source, "data"
        )

        run_pipeline(
            inputs={"data": raw_data_source},
            outputs={o: raw_data_profile for o in self.outputs},
            create_pipeline_function=create_pipeline,
            output_catalog_str=self.output_catalog,
            dataset_name=raw_data_profile,
            parameters={
                "catalog": self.output_catalog,
                "input_data": raw_data_profile,
                "output_data": raw_data_profile,
            },
        )

    def view_page(self):
        st.markdown(self.introduction_markdown)

        columns = st.columns(3)
        with columns[0]:
            st.markdown("## Select input dataset")
        with columns[1]:
            st.markdown("## Specify output dataset name")
        with columns[2]:
            st.markdown("## Run")

        columns = st.columns(3)
        with columns[0]:
            st.markdown(
                "Here we select the dataset that we want to create the data "
                "profile for."
            )
        with columns[1]:
            st.markdown(
                "It is easier here to stick to the default name. However, "
                "if you want to change it, you can do so here."
            )
        with columns[2]:
            st.markdown(
                "Once you have selected the input dataset and specified the "
                "output dataset name, you can run the pipeline."
            )

        columns = st.columns(3)

        with columns[0]:
            labels = get_select_labels_from_catalog(self.input_catalog)
            raw_data_source = st.selectbox(
                "Select dataset",
                labels,
                index=(len(labels) - 1),
                label_visibility="collapsed",
            )
        with columns[1]:
            raw_data_profile = st.text_input(
                "Output dataset name",
                value=f"{raw_data_source}",
                label_visibility="collapsed",
            )
        with columns[2]:
            create_data_profile_button = st.button(
                "Create Data Profile", use_container_width=True
            )

        if create_data_profile_button:
            self.run(
                raw_data_source=raw_data_source,
                raw_data_profile=raw_data_profile,
            )

        self.view_data_profile()
