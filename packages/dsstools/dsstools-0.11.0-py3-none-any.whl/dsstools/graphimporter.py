# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Literal

import networkx as nx

from dsstools.log.logger import get_logger

logger = get_logger("WDCAPI")

from dsstools.wdc import WDC


class GraphImporter(WDC):
    """Class enabling graph imports from the WDC server.

    Args:
        identifier: Identifier of the network data. This is a numeric ID identifying
            the graph. Unintuitively, this differs from the corresponding text search
            data, if you need both data types.
        token: Token for authorization.
        api: API address to send request to. Leave this as is.
        insecure: Hide warning regarding missing https.
        timeout: Set the timeout to the server. Increase this if you request large
            networks.
        params: These are additional keyword arguments passed onto the API endpoint. See
            https://dss-wdc.wiso.uni-hamburg.de/#_complex_datatypes_for_the_api_requests
            for further assistance.
            """
    endpoint = "domaingraph"

    def __init__(self,
                 identifier: int | None = None,
                 *,
                 token: str | None = None,
                 api: str = "https://dss-wdc.wiso.uni-hamburg.de/api",
                 insecure: bool = False,
                 timeout: int = 60,
                 params: dict | None = None,
                 ):
        super().__init__(token=token, api=api, insecure=insecure, timeout=timeout, params=params)
        self.identifier = identifier

    def list_available_graphs(self) -> list[dict]:
        """List available graphs for the current token.

        Returns:
          : List of dicts containing the graphs with metadata.

        """
        results = []
        for page in self._get_results(self._construct_url_base() +  "/list"):
            results.extend(page["content"])
        return results

    def _get_graph_elements(self, element:Literal["nodes", "edges"]="nodes"):
        """Generic function providing graph elements from the API.

        Args:
          element: Literal["nodes","edges"]: Type of element to get. (Default value =
            "nodes")

        Returns:
          : List of graph elements, containing 3-tuples for edges of the structure (from,
            to, weight). For nodes, this is a 2-tuple of the structure (ID,
            {additional_data_dict}).

        """
        elements = []
        for page in self._get_results(self._construct_url_base() +  f"/{self.identifier}" + f"/{element}", params=self.params):
            for element_data in page["content"]:
                if element == "nodes":
                    id = element_data.pop("id")
                    elements.append((id, element_data))
                else:
                    elements.append(tuple(element_data.values()))
        return elements

    def get_nodes(self):
        """Get the nodes of the selected graph.

        Args:

        Returns:
          : List of nodes, containing a 2-tuple of the structure (ID,
          {additional_data_dict}).

        """
        return self._get_graph_elements(element="nodes")

    def get_edges(self):
        """Get the edges of the selected graph.

        Args:

        Returns:
          : List of edges, containing a 3-tuple of the structure (from,
          to, weight).

        """
        return self._get_graph_elements(element="edges")

    def get_graph(self, graph_type=nx.DiGraph):
        """Get the full graph containing nodes and edges.

        Args:
          graph_type: Type of graph to create. (Default value = nx.DiGraph)

        Returns:
          : Graph from API

        """
        graph = graph_type()
        nodes = self.get_nodes()
        edges = self.get_edges()
        graph.add_nodes_from(nodes)
        graph.add_weighted_edges_from(edges)
        return graph

def list_wdcapi_graphs(token:str, timeout: int=60):
    """List accessible graph identifiers for the given token.

    Comfort wrapper around the `GraphImporter().list_available_graphs()` object which
    should mirror the common structure of NetworkX.

    Args:
      token:str: Token to authenticate with.
      timeout: int:  Timeout in seconds after the request cancels. Leave at default.
        (Default value = 60)

    Returns:

    """
    gi = GraphImporter(
        token=token,
        timeout=timeout
    )
    return gi.list_available_graphs()


def read_wdcapi(identifier:str, token:str, timeout: int=60, graph_type=nx.DiGraph):
    """Import a graph from the WDC API.

    Use the identifier you select in `read_wdcapi()`.

    Comfort wrapper around the `GraphImporter().get_graph()` object which should mirror
    the common structure of NetworkX.

    Args:
      identifier: str: Identifier of the graph.
      token: str: Token to authenticate with.
      timeout: int: Timeout in seconds after the request cancels. For very large graphs
        this should be increased. (Default value = 60)
      graph_type: Type of graph to return. For crawled graphs nx.DiGraph is recommended.
        (Default value = nx.DiGraph)

    Returns:
      : The imported graph.

    """
    gi = GraphImporter(
        identifier=identifier,
        token=token,
        timeout=timeout
    )
    return gi.get_graph(graph_type=graph_type)
