# System imports

# Third party imports
import uuid

import pytest
from kedro.framework.hooks.manager import _create_hook_manager, _register_hooks
from kedro.io import DataCatalog
from kedro.runner import SequentialRunner

# Local imports
from SmartLeads.settings import HOOKS

"""
The generic pipeline test helpers.
"""


@pytest.fixture
def get_pipeline_session_id():
    """
    A Pytest helper to generate a unique pipeline instance session identifier.
    """
    session_id = uuid.uuid4()
    yield session_id.hex


@pytest.fixture
def get_seq_runner():
    """
    A Pytest helper to create a Pipeline runner instance.
    """
    return SequentialRunner()


@pytest.fixture
def get_catalog():
    """
    A Pytest helper to create a Pipeline Data Catalog instance.
    """
    return DataCatalog()


@pytest.fixture
def get_hook_manager():
    """
    A Pytest helper to create a Pipeline Hook Manager instance.
    """
    _hook_manager = _create_hook_manager()
    _hooks = HOOKS
    _register_hooks(hook_manager=_hook_manager, hooks=_hooks)

    return _hook_manager
