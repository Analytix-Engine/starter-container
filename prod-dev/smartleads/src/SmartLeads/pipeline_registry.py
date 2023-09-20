# System imports
from typing import Dict

# Third-party imports
from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

# Local imports


"""
Project pipelines registration.
"""


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines = find_pipelines()
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines
