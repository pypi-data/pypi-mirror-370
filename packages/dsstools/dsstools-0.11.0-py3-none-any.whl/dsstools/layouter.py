# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
""""""

import json
import random
from pathlib import Path
from typing import Optional, Union

import networkx as nx
import numpy as np

from dsstools.log.logger import get_logger

from .utils import NumpyEncoder, PositionKeyCoder

logger = get_logger(__name__)


class Layouter:
    @staticmethod
    def name() -> str:
        return "spring"

    def __str__(self):
        return self.name()

    def create_layout(
        self,
        graph: nx.Graph,
        seed: Optional[int] = None,
        pos: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """Create position dictionary according to set layout engine. Default
        layout is Spring.

        Args:
           graph:  Graph object
           seed: Set a default seed (default None)
           pos: Pre-populated positions


        Returns:
            Dictionary of node and positions.
        """
        if seed is None:
            random.seed()
            seed = random.randrange(100000)

        logger.info(f"Using seed {seed} for generating positions.")

        # This produces ndarrays which are not JSON serializable so we convert them to lists
        return nx.spring_layout(graph, pos=pos, seed=seed, **kwargs)

    def read_or_create_layout(
        self,
        filepath: Union[str, Path],
        graph: nx.Graph,
        seed: Optional[int] = None,
        overwrite: bool = False,
        **kwargs,
    ) -> dict:
        """Read positions from file. If non-existant create pos and write to
        file.

        Args:
            filepath: Filename to read positions from
            graph: Graph object to update
            seed: Seed to use for the layout.
            overwrite: Overwrite existing file (default False)

        Returns:
            Dictionary of positions per Node. Will return an empty dict if creation
            failed.
        """

        path = Path(filepath)
        if path.is_file() and not overwrite:
            return self.read_from_file(filepath)
        if path.is_dir():
            invalid_path = ValueError("Provide a path for a filename, not a directory.")
            logger.error(invalid_path)
            raise invalid_path
        positions = self.create_layout(graph, seed=seed, **kwargs)
        self.write_to_file(positions, filepath)
        return positions if positions is not None else dict()

    def write_to_file(self, positions, path):
        with open(path, "w", encoding="UTF-8") as file:
            logger.info(f"Writing positions to '{path}'.")
            data_ready_for_json = PositionKeyCoder().encode_typed_keys(positions)
            file.write(json.dumps(data_ready_for_json, cls=NumpyEncoder, indent=4))

    def read_from_graph(self, graph: nx.Graph, pos_name: tuple[str, str] = ("x", "y")) -> dict:
        """Read positions from node attributes in the graph.

        This is relevant when importing from Pajek or GEXF files where the positions are
        already set with another tool. Imported values are normalized onto [-1,1] in all
        directions.

        Args:
            graph (nx.Graph): Graph object including the node attributes.
            pos_name (tuple): Node attribute names to look for. These depend on the
                              imported file format.

        Returns:
            Dictionary of positions per Node.
        """
        nodes_x = nx.get_node_attributes(graph, pos_name[0])
        nodes_y = nx.get_node_attributes(graph, pos_name[1])
        positions = {}

        # I am really sorry for this
        for (node, x), y in zip(nodes_x.items(), nodes_y.values()):
            positions[node] = [x, y]

        return {
            key: tuple(value)
            for key, value in nx.rescale_layout_dict(positions).items()
        }

    def read_from_file(self, filename: Union[str, Path], **kwargs) -> dict:
        """Reads position from JSON file under filepath.

        The following structure for the JSON is expected, where each key contains an
        array of length 2 containing the coordinates. Coordinates should be in the range
        [-1,1]:

        ```json
        {
            "domain1": [-0.1467271130230262, 0.25512246449304427],
            "domain2": [-0.3683594304205127, 0.34942480334119136],
        }
        ```

        This structure is generated through `dsstools.Layouter().write_to_file()`.

        Args:
           filename (Union[str.Path]): Path to file to be read.
           **kwargs:

        Returns:
            Dictionary of nodes and positions.
        """
        path = Path(filename)
        if path.is_file():
            logger.info(f"Read positions from '{path}'.")
            with open(path, "r", encoding="UTF-8") as file:
                pos = json.load(file, object_hook=PositionKeyCoder().decode_typed_keys)
            # We need to convert back from lists to ndarray to maintain
            # compatibility with classic networkx
            ndarray_pos = {}
            for key in pos.keys():
                ndarray_pos[key] = np.asarray(pos[key])
            return ndarray_pos

        file_not_found = FileNotFoundError(
            f"Given file under {filename} does not exist."
        )
        logger.error(file_not_found)
        raise file_not_found

    # NX kwargs -> pos for initial positions


class GraphvizLayouter(Layouter):
    """Create layouts using graphviz as backend.

    This is rather complicated to install the proper dependencies for. Not for the faint
    of heart.
    """

    @staticmethod
    def name() -> str:
        return "graphviz"

    def create_layout(
        self,
        graph: nx.Graph,
        seed: Optional[int] = None,
        pos: Optional[dict] = None,
        prog="fdp",
        additional_args="",
        **kwargs,
    ) -> dict:
        if seed is None:
            random.seed()
            seed = random.randrange(100000)

        logger.info(f"Using seed {seed} for generating positions.")
        dot_args = f"-Gstart={seed} -Nshape=circle " + additional_args

        positions = nx.nx_agraph.graphviz_layout(graph, prog=prog, args=dot_args)
        return nx.rescale_layout_dict(positions)


class KamadaKawaiLayouter(Layouter):
    """Create layouts using Kamada-Kawai as backend."""

    @staticmethod
    def name() -> str:
        return "kamada-kawai"

    def create_layout(
        self,
        graph: nx.Graph,
        seed: Optional[int] = None,
        pos: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        logger.info("No seed for generating positions, so always save your layout.")
        if seed is not None:
            logger.info("Seed value for Kamada-Kawai layout is ignored.")

        return nx.kamada_kawai_layout(graph, pos=pos, **kwargs)


class ForceAtlas2Layouter(Layouter):
    """Create layouts using ForceAtlas 2 as backend.

    Note: This layouter engine is quite peculiar to create good results with. Please
    ensure you at least read the corresponding entry in the NetworkX documentation:
    https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.forceatlas2_layout.html
    """

    @staticmethod
    def name() -> str:
        return "forceatlas2"

    def create_layout(
        self,
        graph: nx.Graph,
        seed: Optional[int] = None,
        pos: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        positions = nx.forceatlas2_layout(graph, pos=pos, seed=seed, **kwargs)
        return nx.rescale_layout_dict(positions)
