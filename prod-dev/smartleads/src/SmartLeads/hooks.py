# System imports
import logging
import pdb
import sys
import traceback

# Third-party imports
from kedro.framework.hooks import hook_impl

# Local imports

"""
The main module for Kedro hook definitions.
"""


log = logging.getLogger(__name__)


class PDBNodeDebugHook:
    """A hook class for creating a post mortem debugging with the PDB debugger
    whenever an error is triggered within a node. The local scope from when the
    exception occured is available within this debugging session.
    """

    @hook_impl
    def on_node_error(self):
        _, _, traceback_object = sys.exc_info()

        #  Print the traceback information for debugging ease
        traceback.print_tb(traceback_object)

        # Drop you into a post mortem debugging session
        pdb.post_mortem(traceback_object)


class PDBPipelineDebugHook:
    """A hook class for creating a post mortem debugging with the PDB debugger
    whenever an error is triggered within a pipeline. The local scope from when the
    exception occured is available within this debugging session.
    """

    @hook_impl
    def on_pipeline_error(self):
        # We don't need the actual exception since it is within this stack frame
        _, _, traceback_object = sys.exc_info()

        #  Print the traceback information for debugging ease
        traceback.print_tb(traceback_object)

        # Drop you into a post mortem debugging session
        pdb.post_mortem(traceback_object)
