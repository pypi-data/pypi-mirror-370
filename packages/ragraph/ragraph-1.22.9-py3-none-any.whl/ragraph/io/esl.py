"""# Elephant Specification Language format support"""

from pathlib import Path
from typing import Union

try:
    from raesl.compile import to_graph
except ImportError:
    raise ImportError("This functionality requires the 'raesl' library to be installed.")

from ragraph.graph import Graph


def from_esl(
    *paths: Union[str, Path],
) -> Graph:
    """Convert ESL file(s) into a :obj:`ragraph.graph.Graph`.

    Arguments:
        paths: Paths to resolve into ESL files. May be any number of files and
            directories to scan.

    Returns:
        Instantiated graph.
    """
    return to_graph(*paths, output=None, force=False)
