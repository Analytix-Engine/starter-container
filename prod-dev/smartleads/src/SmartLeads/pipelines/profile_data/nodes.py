# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from datetime import datetime
from typing import Dict

import numpy as np
import streamlit as st
from pandas import DataFrame


def create_data_profile(df: DataFrame) -> Dict[str, Dict]:
    """Create a data profile for a given dataframe.

    Args:
        df (DataFrame): The dataframe to create a profile for.

    Returns:
        Dict(str, Dict): A dictionary containing the data profile.
    """
    with st.spinner("Creating data profiles"):
        d: Dict = {
            "analysis": {
                "title": "Analysis",
                "date_start": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            },
            "table": {},
            "alerts": {},
            "variables": {},
        }
        d["table"]["n"] = df.shape[0]
        d["table"]["n_var"] = df.shape[1]
        d["table"]["memory_size"] = df.memory_usage().sum() / 1024**2
        d["table"]["record_size"] = d["table"]["memory_size"] / d["table"]["n"]
        d["table"]["n_cells_missing"] = df.isna().sum().sum()
        d["table"]["n_vars_with_missing"] = df.isna().any().sum()
        d["table"]["p_cells_missing"] = d["table"]["n_cells_missing"] / (
            df.shape[0] * df.shape[1]
        )
        d["table"]["types"] = df.dtypes.to_dict()
        d["table"]["types"] = {k: v.name for k, v in d["table"]["types"].items()}
        d["alerts"] = []
        d["variables"] = {}
        progress = st.progress(0, "Creating data profiles")
        for c in df.columns.to_list():
            progress.progress(
                value=int(
                    (df.columns.to_list().index(c) + 1)
                    / len(df.columns.to_list())
                    * 100
                ),
                text=c,
            )
            r = {
                "n_distinct": df[c].nunique(),
                "p_distinct": df[c].nunique() / df.shape[0],
                "is_unique": df[c].nunique() == df.shape[0],
                "n_unique": df[c].nunique(),
                "type": df[c].dtype.name,
                "value_counts_without_nan": df[c].value_counts(dropna=False).to_dict(),
                "value_counts_index_sorted": df[c]
                .value_counts(dropna=False)
                .sort_index()
                .to_dict(),
                "ordering": "alphabetical"
                if df[c].dtype.name == "object"
                else "numeric",
                "n_missing": df[c].isna().sum(),
                "p_missing": df[c].isna().sum() / df.shape[0],
                "n": df.shape[0],
                "count": df[c].notnull().sum(),
                "memory_size": df[c].memory_usage() / 1024**2,
            }
            if r["type"] in ("object", "bool"):
                r["is_categorical"] = True
            else:
                r["is_categorical"] = False

            if r["is_categorical"]:
                r["mode"] = df[c].value_counts(dropna=True).iloc[0]
                # r['histogram'] = df[c].value_counts(dropna=True).to_dict()

            else:
                r["n_negative"] = (df[c] < 0).sum()
                r["n_positive"] = (df[c] > 0).sum()
                r["n_infinite"] = df[c].isna().sum()
                r["n_zeroes"] = (df[c] == 0).sum()
                r["mean"] = df[c].mean()
                r["std"] = df[c].std()
                r["variance"] = df[c].var()
                r["min"] = df[c].min()
                r["max"] = df[c].max()
                r["kurtosis"] = df[c].kurtosis()
                r["skewness"] = df[c].skew()
                r["sum"] = df[c].sum()
                r["mad"] = (df[c] - df[c].mean()).abs().mean()
                r["range"] = df[c].astype(float).max() - df[c].astype(float).min()
                r["5%"] = df[c].quantile(0.05)
                r["25%"] = df[c].quantile(0.25)
                r["50%"] = df[c].quantile(0.5)
                r["75%"] = df[c].quantile(0.75)
                r["95%"] = df[c].quantile(0.95)
                r["iqr"] = r["75%"] - r["25%"]
                r["cv"] = r["std"] / r["mean"] if r["mean"] else None
                r["n_zeros"] = (df[c] == 0).sum()
                r["p_zeros"] = r["n_zeros"] / r["n"] if r["n"] else None
                r["p_infinite"] = r["n_infinite"] / r["n"] if r["n"] else None

                counts, edges = np.histogram(df[c].dropna())

                r["histogram"] = {"counts": counts, "bin_edges": edges}

                r["mode"] = df[c].mode().to_list()

            d["variables"][c] = r

            d["analysis"]["date_end"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.success("Data profiles created successfully")
        return d
