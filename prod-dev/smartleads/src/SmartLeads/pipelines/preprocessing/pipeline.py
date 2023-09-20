"""
This is a boilerplate pipeline 'profile_data'
generated using Kedro 0.18.12
"""

from kedro.pipeline import node, pipeline

from .nodes import preprocess_features


def create_pipeline(**kwargs):
    return pipeline(
        [
            node(func=lambda x: x, inputs="parms", outputs="parms_dummy"),
            node(
                func=preprocess_features,
                inputs=["customer_data"],
                outputs=["customer_data_preprocessed", "customer_data_pipe"],
                name="create_raw_data_profiler_output",
            ),
        ],
        inputs=kwargs.get("inputs"),
        outputs=kwargs.get("outputs"),
        tags="preprocess",
    )
