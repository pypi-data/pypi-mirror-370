import atexit
import json
import os
import sys

from validio_sdk.code.settings import dump_graph_var, graph_preamble_var
from validio_sdk.resource._resource import ResourceGraph
from validio_sdk.resource._serde import custom_resource_graph_encoder

"""
This holds a 'global' instance of a resource graph. This is the graph
that represents the code configuration. It is automatically populated
as the code declares resources.
Upon exit of the program, we serialize this instance to the parent process.
"""
RESOURCE_GRAPH: ResourceGraph = ResourceGraph()


def _dump_graph() -> None:
    # Since we piggyback on stdout, we prefix the graph with a
    # preamble to identify the start of the relevant info in the stream.
    if dump_graph_var in os.environ:
        try:
            print(graph_preamble_var)
            print(
                json.dumps(
                    RESOURCE_GRAPH, default=custom_resource_graph_encoder, indent=2
                )
            )
        except Exception as e:
            # If we fail to parse the graph, write the error out to stderr
            # since Python won't let us easily exit with an error from here.
            # The parent process is set up to check stderr since we don't
            # have a graph, so it will exit with the error instead.
            print(e, file=sys.stderr)


atexit.register(_dump_graph)
