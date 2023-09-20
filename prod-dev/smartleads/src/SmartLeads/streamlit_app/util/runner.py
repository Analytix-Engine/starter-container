import os
import time
from typing import Any, Callable, Dict, Optional

import streamlit as st
from kedro.runner import SequentialRunner

from SmartLeads.streamlit_app.util.catalogs import (
    add_pickle_to_catalog,
    create_catalog_safe_name,
    load_catalog,
    save_catalog,
)

CATALOG = "DATA"


def run_pipeline(
    inputs: Dict[str, str],
    outputs: Dict[str, str],
    create_pipeline_function: Callable,
    output_catalog_str: str,
    dataset_name: str = "",
    parameters: Optional[Dict[str, Any]] = None,
):
    """Run a pipeline using the SequentialRunner.

    Args:
        pipe (Pipeline): Pipeline to run.
        catalog (DataCatalog): Catalog containing all of the elements.

    Returns:
        None
    """
    runner = SequentialRunner()
    catalog = load_catalog(CATALOG)
    with st.spinner("Running..."):
        parms_identifier = create_catalog_safe_name(
            catalog_name=output_catalog_str,
            dataset_name=dataset_name,
            component="parms",
        )
        add_pickle_to_catalog(
            data_path=output_catalog_str,
            data_catalog=catalog,
            data_catalog_identifier=CATALOG,
            dataset_name=parms_identifier,
        )

        catalog.save(parms_identifier, parameters)
        inputs["parms"] = parms_identifier

        for key, _ in outputs.items():
            identifier = create_catalog_safe_name(
                catalog_name=output_catalog_str,
                dataset_name=dataset_name,
                component=key,
            )
            catalog = add_pickle_to_catalog(
                data_path=output_catalog_str,
                data_catalog=catalog,
                data_catalog_identifier=CATALOG,
                dataset_name=identifier,
            )

        save_catalog(catalog, CATALOG)

        for key, value in outputs.items():
            identifier = create_catalog_safe_name(
                catalog_name=output_catalog_str,
                dataset_name=value,
                component=key,
            )
            outputs[key] = identifier

        pipe = create_pipeline_function(
            inputs=inputs,
            outputs=outputs,
            catalog=catalog,
        )

        start_time = time.time()
        import warnings

        warnings.simplefilter("ignore")
        os.environ["PYTHONWARNINGS"] = "ignore"
        runner.run(pipe, catalog)
        end_time = time.time()
        t = round(end_time - start_time, 2)
        st.success(f"Pipeline successfully run in {t} seconds!")
