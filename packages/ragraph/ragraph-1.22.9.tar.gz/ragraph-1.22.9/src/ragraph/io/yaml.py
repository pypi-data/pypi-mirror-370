"""# YAML format support"""

from pathlib import Path
from typing import Optional, Union

from ragraph.graph import Graph
from ragraph.io.json import graph_from_json_dict

try:
    from ruamel_yaml import YAML
except ImportError:
    from ruamel.yaml import YAML

yaml = YAML(typ="safe")


def from_yaml(path: Optional[Union[str, Path]] = None, enc: Optional[str] = None) -> Graph:
    """Decode YAML file or string into a Graph.

    Arguments:
        path: YAML file path.
        enc: YAML encoded string.

    Returns:
        Graph object.
    """
    if path is None and enc is None:
        raise ValueError("`path` and `enc` arguments cannot both be `None`.")
    if path is not None and enc is not None:
        raise ValueError("`path` and `enc` arguments cannot both be set.")

    if path:
        json_dict = yaml.load(Path(path))
    else:
        json_dict = yaml.load(enc)

    return graph_from_json_dict(json_dict)


def to_yaml(graph: Graph, path: Optional[Union[str, Path]] = None) -> Optional[str]:
    """Encode Graph to YAML file or string.

    Arguments:
        path: Optional file path to write YAML to.

    Returns:
        YAML string.
    """
    stream = Path(path) if path else None
    return yaml.dump(graph.json_dict, stream=stream)
