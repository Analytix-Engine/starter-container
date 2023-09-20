"""
This is a boilerplate pipeline 'profile_data'
generated using Kedro 0.18.12
"""

from kedro.pipeline import node, pipeline

from .nodes import create_data_profile


def create_pipeline(**kwargs):
    return pipeline(
        [
            node(func=lambda x: x, inputs="parms", outputs="parms_dummy"),
            node(
                func=create_data_profile,
                inputs=["data"],
                outputs="data_profile",
                name="create_raw_data_profiler_output",
            ),
        ],
        inputs=kwargs.get("inputs"),
        outputs=kwargs.get("outputs"),
        tags="create_data_profile",
    )
