# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import networkx as nx
import pandas as pd

from dsstools.log.logger import get_logger
from dsstools.utils import ensure_file_format

logger = get_logger(__name__)


@dataclass
class GraphDescriptor:
    """This class provides a dataframe (~table) view of the given graph.

    Every metric you add is its own column and every node its own row. It allows you
    to add custom metrics for more detailed analysis and save the dataframe as either
    csv or xlsx document.

    The naming hierarchy is as follows:
        - if activated, default metrics are always set first
        - if a custom metric is equal to a default metric, the values will be replaced
        - if a node attribute name is equal to regular or custom metric in df, the node
          attribute will have the number of duplicates as suffix
        - if two nodes have the same attribute, the attribute will be considered equal
          and their individual values will be in the same column

    Args:
        graph (nx.Graph): The graph you want to save/analyse
        include_defaults (bool): The class adds betweenness, degree and centrality as
            default metrics for all nodes. You can deactivate this behaviour by setting
            this to False (default True)
        round_floats_to (int): The class rounds every float down to 4 decimal points by
            default. This guarantees that cells won't grow to big, making it hard to
            analyse the data. Increase this value for more details
        max_level (int | None): If your nodes hold some nested structure (dict of dicts)
            this value defines how 'deep' the level of unpacking goes. The unpacked
            values will become their own columns.
            If set to None, all values will be unpacked (default = None)

    """
    graph: nx.Graph
    include_defaults: bool = True
    round_floats_to: int = 4
    max_level: int = None

    dataframe: pd.DataFrame = field(init=False)

    custom_calculations: dict[str, pd.Series] = field(init=False, default_factory=dict)

    def __post_init__(self):
        # Calculate metrics after initialization
        self.default_metrics = {
            "Betweenness": nx.betweenness_centrality(self.graph),
            "Degree": dict(self.graph.degree()),
            "Centrality": nx.degree_centrality(self.graph)
        }

    def get_dataframe(self) -> pd.DataFrame:
        if not hasattr(self, "dataframe"):
            self.__create_dataframe()
        return self.dataframe

    def add_custom_metrics(self,
                           custom_metrics: dict[str, callable]) -> 'GraphDescriptor':
        """Allows you to add custom graph metrics by passing a dictionary
        of metric names and functions that operate on the graph.

        Custom metrics will override default metrics if they are named the same.

        Examples:
            ```python
            def calculate_clustering(graph):
                return nx.clustering(graph)

            # Note how some values must be wrapped in a dictionary first,
            # else pandas will read them as NaN
            def calculate_shortest_path_length(graph):
                return dict(nx.shortest_path_length(graph))

            custom_metrics = {
                'Clustering': calculate_clustering,
                'Shortest path length': calculate_shortest_path_length,
                'Closeness': lambda graph: nx.closeness_centrality(graph)
            }

            GraphDescriptor(graph=mygraph).add_custom_metrics(custom_metrics)
            ```

        Args:
            custom_metrics (dict[str, callable]): A dictionary where keys are metric
                names and values are functions accepting a NetworkX graph and return a
                dictionary of node-based metric values (otherwise values in dataframe
                might be NaN).

        Returns:
            self
        """
        for metric_name, metric_func in custom_metrics.items():
            try:
                # Execute the function and store the result
                metric_result = metric_func(self.graph)

                # Store the result in dictionary to add them later
                self.custom_calculations[metric_name] = pd.Series(metric_result)

            except Exception as e:
                print(f"Error calculating metric {metric_name}: {e}")

        # Always recalculate Dataframe, if new metrics are added
        self.__create_dataframe()

        return self

    def __flatten_dict(self, flat_data: dict, parent_key: str = '', sep: str = '.',
                       level: int = 0):
        """ Flattens a nested dictionary up to a specified max depth.

        If a dictionary is encountered at max depth, it is replaced with "PLACEHOLDER".

        Args:
            flat_data (dict): The dictionary to flatten.
            parent_key: The base key for nested keys.
            sep: Separator used for flattened keys.
            level: Current recursion depth.

        Returns:
            A flattened dictionary.
        """
        items = []
        for key, value in flat_data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            new_key = self.__ensure_uniqueness(new_key)
            if isinstance(value, dict):
                # max_level can be None, so check is necessary
                if self.max_level and level + 1 >= self.max_level:
                    items.append((new_key, "PLACEHOLDER"))
                else:
                    items.extend(
                        self.__flatten_dict(value, new_key, sep=sep, level=level + 1
                                            ).items())
            else:
                items.append((new_key, value))
        return dict(items)

    def __create_dataframe(self) -> None:
        """Creates a dataframe view of a graph.

        Every Node has its own row (index) and every attribute its own column.

        If not all Nodes have the same attributes, 'None' will be set as placeholder
        value.
        """
        # Collect all nodes and their attributes (row data)
        rows = []
        nodes = []
        for node, data in self.graph.nodes(data=True):
            # Flat/unpack values without changing them (if dict(dict(dict())))
            flat_data = self.__flatten_dict(data)
            rows.append(flat_data)
            nodes.append(node)

        # Create DataFrame directly from lists (no .loc or .at necessary, this lead to
        # problems with lists, sets etc. in the past) with nodes as index
        self.dataframe = pd.DataFrame(rows, index=nodes)

        # Adding fix calculated values (default metrics)
        if self.include_defaults:
            for metric_name, metric_result in self.default_metrics.items():
                self.dataframe[metric_name] = pd.Series(metric_result)

        # Adding custom values after defaults if available (custom metrics)
        if self.custom_calculations:
            for metric_name, metric_results in self.custom_calculations.items():
                self.dataframe[metric_name] = metric_results

        # Rounding float columns (if needed) to the specified decimal places
        self.dataframe = self.dataframe.map(
            lambda x: round(x, self.round_floats_to) if isinstance(x, float) else x
        )

    def __ensure_uniqueness(self, col_name: str) -> str:
        """Ensures that no node attribute overrides a metric column.

        Warns the user, if an attribute is named the same as a metric.

        Args:
            col_name: Essentially the node attribute that needs to be checked.

        Returns:
            A unique name for the attribute.
        """
        counter = 0
        new_name = col_name
        # Is there a case where this can be >1? customs override defaults and customs
        # are unique. If two nodes have the same attributes, their values should be part
        # of the same column.
        while (new_name in self.custom_calculations.keys() or
               (self.include_defaults and new_name in self.default_metrics.keys())):
            counter += 1
            new_name = f"{col_name}_{counter}"

        if counter > 0:
            logger.warning(f"Column '{col_name}' already exists. Using '{new_name}' instead.")
        return new_name

    def write_file(
        self,
        save_path: str | Path,
        *,
        excel_engine: Literal["openpyxl", "xlsxwriter"] = 'openpyxl',
    ) -> 'GraphDescriptor':
        """Saves the dataframe at the given location in the provided format.

        The saving format will be determined dynamically based on the path suffix

        Args:
            save_path (str | Path): the saving location (and format)
            excel_engine (str): the type of engine you want to use for saving the file
                in xlsx-format. Uses 'openpyxl' as default. 'openpyxl' must be installed
                in order to work correctly

        Returns:
            self
        """
        if not hasattr(self, "dataframe"):
            self.__create_dataframe()

        # Checking the saving data
        formats = {"csv", "xlsx"}
        save_path, saving_format = ensure_file_format(save_path, default_format=".csv",
                                                      format_filter=formats)

        # Saves the dataframe for the given type (could be match case for >= 3.10)
        if saving_format == "csv":
            self.dataframe.to_csv(save_path, na_rep="None")

        elif saving_format == "xlsx":
            self.dataframe.to_excel(save_path, na_rep="None", engine=excel_engine)

        return self
