# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for drawing network images through method chaining."""

import json
import math
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.axes._base import _AxesBase
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from networkx.classes.reportviews import NodeDataView, OutEdgeDataView

from dsstools.log.logger import get_logger
from dsstools.mapping import comfort_fixed, comfort_numeric_fixed, comfort_str_fixed
from .layouter import Layouter
from .mapping import GenericMapping, Sequential, Qualitative, fixed
from .utils import NumpyEncoder

logger = get_logger(__name__)

# TODO Upstream this
# The following function is distributed through NetworkX and contains
# adaptions by the following developers:
# David Seseke <david.seseke@uni-hamburg.de>
# Katherine Shay < katherine.shay@studium.uni-hamburg.de>
#
# The following license applies to this function:
# Copyright (C) 2004-2025, NetworkX Developers
# Aric Hagberg <hagberg@lanl.gov>
# Dan Schult <dschult@colgate.edu>
# Pieter Swart <swart@lanl.gov>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.

#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.

#   * Neither the name of the NetworkX Developers nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.


# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

NOT_IMPLEMENTED = NotImplementedError("This feature is yet to be implemented.")


def _draw_networkx_multiple_labels(
    G,
    pos,
    labels: dict,
    font_size=12,
    font_color="k",
    font_family="sans-serif",
    font_weight="normal",
    alpha=None,
    bbox=None,
    horizontalalignment="center",
    verticalalignment="center",
    ax=None,
    clip_on=True,
    hide_ticks=True,
):
    """Draw node labels on the graph G.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary
        A dictionary with nodes as keys and positions as values.
        Positions should be sequences of length 2.

    labels (dict): Node labels in a dictionary of text labels keyed by node.
        Node-keys in labels should appear as keys in `pos`.
        If needed use: `{n:lab for n,lab in labels.items() if n in pos}`

    font_size : int or array of ints (default=12)
        Font size for text labels

    font_color : color or array of colors (default='k' black)
        Font color string. Color can be string or rgb (or rgba) tuple of
        floats from 0-1.

    font_weight : string or array of strings (default='normal')
        Font weight

    font_family : string or array of strings (default='sans-serif')
        Font family

    alpha : float or array of floats or None (default=None)
        The text transparency

    bbox : Matplotlib bbox, (default is Matplotlib's ax.text default)
        Specify text box properties (e.g. shape, color etc.) for node labels.

    horizontalalignment : string (default='center')
        Horizontal alignment {'center', 'right', 'left'}

    verticalalignment : string (default='center')
        Vertical alignment {'center', 'top', 'bottom', 'baseline', 'center_baseline'}

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    clip_on : bool (default=True)
        Turn on clipping of node labels at axis boundaries

    Returns
    -------
    dict
        `dict` of labels keyed on the nodes

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> labels = nx.draw_networkx_labels(G, pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    draw
    draw_networkx
    draw_networkx_nodes
    draw_networkx_edges
    draw_networkx_edge_labels
    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    text_items = {}  # there is no text collection so we'll fake one
    for n, label in labels.items():
        (x, y) = pos[n]
        if not isinstance(label, str):
            label = str(label)  # this makes "1" and 1 labeled the same
        t = ax.text(
            x,
            y,
            label,
            size=font_size[n],
            color=font_color[n],
            family=font_family[n],
            # TODO Make font_weight selectable
            weight=font_weight,
            alpha=alpha[n],
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            transform=ax.transData,
            bbox=bbox,
            clip_on=clip_on,
        )
        text_items[n] = t

    if hide_ticks:
        ax.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )

    return text_items


class GraphElement:
    def set_colors(self, arg: GenericMapping | str):
        """Set the colors of the displayed nodes.

        Args:
          arg: Colors to set. String values will be mapped onto all nodes.

        Returns:
          self
        """
        self.colors = comfort_fixed(arg)
        return self

    def set_sizes(self, arg: GenericMapping | int | float):
        """Set size of labels for nodes as pt sizes.

        Args:
            arg: Font size for text labels
        Returns:
            self
        """

        self.sizes = comfort_numeric_fixed(arg)

        return self

    def set_alphas(self, arg: GenericMapping | float):
        """Set alpha based on argument.

        Args:
            arg: The text transparency as mapping between 0 and 1.
        Returns:
            self
        """
        self.alphas = comfort_fixed(arg)
        return self

    def set_transparency(self, arg: GenericMapping | float):
        """Set transparency based on argument.

        This is the same as `set_alphas()`. Alpha is the value for the transparency of a
        color.

        Args:
            arg: The text transparency as mapping between 0 and 1.
        Returns:
            self
        """
        return self.set_alphas(arg)


class Labels(GraphElement):
    def __init__(self):
        self.show_labels = False
        self.labels = []
        self.sizes = None
        self.colors = None
        self.alphas = None
        self.font_families = None

    def set_labels(self, arg: dict[int, str] | dict[int, int]):
        """Set labels for nodes based on arguments.

        Args:
           arg (dict): node identifier as the integer and the label as the string
        """
        self.show_labels = True
        self.labels = arg
        return self

    def set_font_families(self, arg: GenericMapping | str):
        """Set font family for all labels if single font is passed,.

        Allows for multiple fonts to be set if an array of fonts is passed,
        allows for fonts to be individually set for labels based on the given
        node if a dictionary is passed.

        Args:
            arg: Font family
        """
        if isinstance(arg, str):
            if mpl.font_manager.findfont(arg, fallback_to_default=False) is None:
                value_error = ValueError("Font family not supported.")
                logger.error(value_error)
                raise value_error

        self.font_families = comfort_str_fixed(arg)
        return self


class Nodes(GraphElement):
    def __init__(self, labels=None):

        self.labels = labels

        self.positions = None
        self.sizes = fixed(50)
        self.colors = fixed("lightgrey")
        self.alphas = fixed(1)

        self.contour_colors = fixed("white")
        self.contour_sizes = fixed(0.5)

    def set_positions(self, pos: dict | list | Path | str):
        """Set the node positions as a dict or list.

        When using a file, use `set_position_file()` instead.

        Args:
          pos: dict | list: Array of positions. Dicts should be keyed by node ID.

        Returns:
          self
        """
        if isinstance(pos, (Path, str)):
            filep = Path(pos)
            if filep.exists():
                self.positions = Layouter().read_from_file(pos)
                return self
            file_not_found = FileNotFoundError(
                "Position file was not found under the given path."
            )
            logger.error(file_not_found)
            raise file_not_found
        self.positions = pos
        return self

    def set_sizes(self, arg: GenericMapping | float | int):
        """Set the sizes of the displayed nodes.

        Args:
          arg: Sizes to set. Scalar values will be mapped onto all nodes. String values
          will get mapped onto the corresponding data arrays or closeness values per
          node.

        Returns:
          self
        """
        argument = comfort_numeric_fixed(arg)
        if isinstance(argument, Sequential):
            self.sizes = argument.also(lambda x: math.sqrt(x))
        else:
            self.sizes = argument
        return self

    def set_contour_colors(self, arg: GenericMapping | str):
        """Set the contour color of the displayed nodes.

        Contour means the outer border of a node.

        Args:
          arg: Colors to set. String values will be mapped onto all node contours.
            Additional options contain "node" and "edge" to automatically select the
            corresponding color.

        Returns:
          self
        """
        self.contour_colors = comfort_fixed(arg)
        return self

    def set_contour_sizes(self, arg: GenericMapping | float | int):
        """Set the contour sizes of the displayed nodes.

        Contour means the outer border of a node.

        Args:
          arg: Sizes to set. Integer values will be mapped onto all node contours.
            String values will get mapped onto the corresponding data arrays or closeness
            values per node.

        Returns:
          self
        """
        self.contour_sizes = comfort_numeric_fixed(arg)
        return self


class Edges(GraphElement):
    def __init__(self, labels=None):
        self.labels = labels

        self.sizes = fixed(0.5)
        self.colors = fixed("lightgrey")
        self.arrow_size = 2
        self.alphas = fixed(1)


class Description:
    """Class containing description drawing preferences."""

    def __init__(self):
        self.text = ""
        self.alpha = 0.5
        self.size = 8

    def set_text(self, text: str):
        """Set the description setting.

        Args:
          text: Text to set as description
        """
        self.text = text
        return self


class GraphKey:
    """Class to create graph key objects like colorbars or legends."""

    def __init__(
        self,
        mapping: Sequential | Qualitative | dict,
        label: str = None,
        graph_element: OutEdgeDataView | NodeDataView = None,
    ):
        self.mapping = mapping
        self.label = label
        self._graph_element = graph_element
        self.shape = None
        self._ax = None

    def create_legend(self):
        legend_elements: list = []
        # TODO update implementation after large refactor to use consistent node/edge attributes from IG
        graph_element_msg: str = ""
        if self._graph_element is None:
            graph_element_msg = graph_element_msg + "No value for _graph_element set, "
            if self.shape is not None:
                graph_element_msg = (
                    graph_element_msg
                    + "desired shape of legend keys cannot be determined. Shap has be"
                )
                self.shape = None

            self._graph_element = NodeDataView()

        color = "black"
        size = 30

        if isinstance(self.mapping, dict):
            mapping = self.mapping

        elif hasattr(self.mapping, "mapping"):
            mapping = self.mapping.mapping

        if isinstance(list(mapping.values())[0], int) or isinstance(
            list(mapping.values())[0], float
        ):
            fallback = mapping[None]

            del mapping[None]

            max_key = max(mapping, key=mapping.get)
            min_key = min(mapping, key=mapping.get)

            size_mapping = {
                max_key: mapping[max_key],
                min_key: mapping[min_key],
                "fallback": fallback,
            }
            mapping = size_mapping

        elif None in mapping.keys():
            fallback = mapping[None]
            del mapping[None]
            mapping["fallback"] = fallback

        for i, k in mapping.items():

            if isinstance(k, str):
                color = k
            elif isinstance(k, int) or isinstance(k, float):
                size = k

            if isinstance(self._graph_element, NodeDataView):
                if self.shape is None:
                    self.shape = "o"
                    if len(graph_element_msg) == 0:
                        logger.info(
                            "No value for shape set. Default shape 'o' for Nodes is used."
                        )
                    elif len(graph_element_msg) > 0:
                        logger.warning(
                            graph_element_msg
                            + "No value for shape set. Default shape 'o' for Nodes is used."
                        )

                legend_element = plt.scatter(
                    [0], [0], marker=self.shape, color=color, label=i, s=size
                )
                legend_elements.append(legend_element)

            if isinstance(self._graph_element, OutEdgeDataView):
                if self.shape is None:
                    self.shape = "solid"
                    logger.info(
                        "No value for shape set. Default shape 'solid' for Edges is used."
                    )
                legend_element = Line2D(
                    [0], [0], linestyle=self.shape, color=color, label=i, linewidth=size
                )
                legend_elements.append(legend_element)

        return legend_elements


class GraphKeyGenerator:
    """Base class for generating graph keys.

    Graph keys contain both colorbars and legends as a MatplotLib figure.
    """

    def __init__(self):
        self._fig = None
        self.colorbars: list = []
        self.legends: list = []
        self.keys: list = []

    def add_graph_key(self, graph_key: GraphKey):
        self.keys.append(graph_key)

    def place_legend(self, legend: GraphKey, ax: _AxesBase, index: int):
        """Places legend on the given axis based on the index. Limit of 3
        legends per axis, fills axis from top to bottom.

        Args:
            legend: Legend to be placed
            ax: column axis in which to place the legend
            index: index of the legend for determining placement within the given ax
        """
        ax.set_axis_off()
        legend_elements = legend.create_legend()

        def set_legend(location: str, ax: _AxesBase):
            ax.legend(
                handles=legend_elements,
                loc=location,
                title=legend.label,
                title_fontproperties=FontProperties(weight="semibold", size="medium"),
                scatterpoints=1,
                edgecolor="#d3d3d3",
            )

        placement = index % 3
        if placement == 0:
            location = "upper center"
            set_legend(location, ax)
        elif placement == 1:
            ax2 = ax.twiny()
            location = "center"
            set_legend(location, ax2)
            ax2.set_axis_off()

        elif placement == 2:
            ax2 = ax.twiny()
            ax2.set_axis_off()
            ax3 = ax2.twiny()
            location = "lower center"
            set_legend(location, ax3)
            ax3.set_axis_off()

    def place_colorbar(self, colorbar: GraphKey, ax: _AxesBase):
        """Generates then places the given colorbar on the given axis.

        The colorbar is
        generated based on its mapping and the fallback is appended to the bottom of the
        generated colorbar axis.

        Args:
            colorbar: colorbar to be placed
            ax: column axis in which to place the legend
        """
        cmap = mpl.colors.ListedColormap(
            colorbar.mapping.colormap(
                np.linspace(
                    colorbar.mapping.out_range[0], colorbar.mapping.out_range[1], 128
                )
            )
        )

        cbar = self._fig.colorbar(
            mpl.cm.ScalarMappable(
                cmap=cmap,
                norm=mpl.colors.Normalize(
                    vmin=colorbar.mapping.in_range[0], vmax=colorbar.mapping.in_range[1]
                ),
            ),
            cax=ax,
            orientation="vertical",
        )
        cbar.set_label(label=colorbar.label, weight="semibold")

        # Fallback implementation
        fallback_cmap = mpl.cm.ScalarMappable(
            cmap=mpl.colors.ListedColormap(
                [mpl.colors.to_rgb(colorbar.mapping.fallback)]
            )
        )

        divider = make_axes_locatable(cbar.ax)
        fallback_ax = divider.append_axes("bottom", size="5%", aspect=1, anchor="C")
        self._fig.add_axes(cbar.ax, label=4, aspect=1, position="bottom")
        fallback_cbar = self._fig.colorbar(
            cax=fallback_ax, mappable=fallback_cmap, orientation="vertical"
        )
        fallback_cbar.set_ticks(ticks=[0.5], labels=["fallback"])
        fallback_cbar.ax.tick_params(length=0)

    def sort_keys(self):
        """Add the graph keys to either self.colorbars or self.legends based on
        the attributes of the graph keys."""
        for index, key in enumerate(self.keys):
            if hasattr(key.mapping, "colormap") and key.mapping.colormap is not None:
                self.colorbars.append(key)
            else:
                self.legends.append(key)

            if key.label is None:
                logger.debug(
                    f'Label parameter for graph key with mapping "{key.mapping}" at index {index} in self.keys is None. Graph key will be displayed without label.',
                    stacklevel=4,
                )

    def draw_keys(self):
        """Determine the figure axis and draw the graph keys.

        Colorbars have their own axis while 3 legends are drawn on 1
        axis.
        """
        self.sort_keys()

        legend_cols: int = math.ceil(len(self.legends) / 3)
        key_cols: int = len(self.colorbars) + legend_cols

        if key_cols <= 1:
            self._fig, axs = plt.subplots(1, 2)
            plt.axis("off")

        else:
            self._fig, axs = plt.subplots(1, key_cols)

        for index, colorbar in enumerate(self.colorbars):
            # row 1 is always for the colorbar, fallback is appended directly to the cbar axis
            ax = axs[index]

            self.place_colorbar(colorbar, ax)
            self._fig.tight_layout()

        for index, legend in enumerate(self.legends):

            ax_label = len(self.colorbars) + math.floor(index / 3)
            ax = axs[ax_label]

            self.place_legend(legend, ax, index)
            self._fig.tight_layout()


class ImageGenerator:
    """Base class for setting up image generation."""

    # NOTE Proposal: Move all the default settings from settings.py to this init
    def __init__(self, graph):
        self.graph = graph
        self.axis = None
        self._fig = None
        self.img_dir = Path(".")
        self.continous_cmap = mpl.colormaps["viridis"]
        self.qualitative_cmap = mpl.colormaps["tab10"]

        self.description = Description()

        self.nodes = Nodes(Labels())
        self.edges = Edges()

        # GraphKey/other
        self.graph_keys = GraphKeyGenerator()
        self._fig_graph_keys = None

        # Canvas
        self.dpi = 200
        self.canvas_height = 10
        self.canvas_width = 10
        self.axlimit = 1.05
        self.canvas_right = None

    def _check_positions(self):
        if self.nodes.positions is not None:
            return self.nodes.positions

        value_error = ValueError(
            "Node(s) have no position data. Try setting positions using nodes.set_positions() or use layouter.Layouter to create a graph"
        )
        logger.error(value_error)
        raise value_error

    def change_graph(self, graph):
        """Set the graph attribute.

        Args:
          graph: A NetworkX graph object.

        Returns:
          self
        """
        self.graph = graph
        return self

    def set_graph_keys(self, graph_keys: GraphKeyGenerator):
        """Set the graph_keys setting.

        Graph keys consist of legends and colorbars.

        Args:
          graph_keys: GraphKeyGenerator object which contains all legends and/or colorbars to be drawn

        Returns:
          self
        """
        self.graph_keys = graph_keys
        return self

    def set_graph_key(
        self,
        mapping: Sequential | Qualitative,
        graph_element: Literal["edges", "nodes", None] = None,
        label: str | None = None,
    ):
        """Set a graph key.

        Graph keys consist of legends and colorbars.

        Args:
            mapping: mapping strategy for the basis of the graph key
            graph_element: the graph element to be modeled, necessary for generating text box legends.
            label: optional label to be applied to the graph key

        Returns:
            self

        """

        if not (hasattr(mapping, "colormap")) or mapping.colormap is None:

            if graph_element == "nodes" or graph_element is None:
                graph_element = self.graph.nodes(data=True)
            if graph_element == "edges":
                graph_element = self.graph.edges(data=True)

            graph_attributes = mapping.supplier._get_values(graph_element, self.graph)
            visual_values = mapping.get(graph_element, self.graph)
            legend = {}

            for ge, value in graph_attributes.items():
                legend[value] = visual_values[ge]
            if None not in legend.keys():
                legend[None] = mapping.fallback
            mapping = legend

        graph_key = GraphKey(mapping, graph_element=graph_element, label=label)

        self.graph_keys.add_graph_key(graph_key)

        return self

    def set_axis(self, axis):
        """Set an existing matplotlib axis object as ImageGenerator object.

        Args:
          axis: Matplotlib axis

        Returns:
          self
        """
        self.axis = axis
        return self

    def _setup_canvas(self):
        """Prepare the correct canvas and set to attributes."""
        if not self.axis:
            self._fig, self.axis = plt.subplots(
                1, 1, figsize=(self.canvas_width, self.canvas_height)
            )
            self._fig.subplots_adjust(
                left=0, bottom=0, right=1, top=1, wspace=0, hspace=0
            )
            # Use slightly increased limits to prevent clipping
            self.axis.set_xlim([-self.axlimit, self.axlimit])
            self.axis.set_ylim([-self.axlimit, self.axlimit])
            self.axis.axis("off")
        elif not self._fig:
            self._fig = self.axis.get_figure()

    def draw_nodes(self):
        """Draw nodes according to the settings."""
        self._check_setup()
        self._setup_canvas()
        node_positions = self._check_positions()

        node_sizes = self.nodes.sizes.get(self.graph.nodes(data=True), self.graph)
        node_colors = self.nodes.colors.get(self.graph.nodes(data=True), self.graph)
        node_contour_sizes = self.nodes.contour_sizes.get(
            self.graph.nodes(data=True), self.graph
        )
        node_alphas = self.nodes.alphas.get(self.graph.nodes(data=True), self.graph)
        node_contour_colors = self.nodes.contour_colors.get(
            self.graph.nodes(data=True), self.graph
        )

        nx.draw_networkx_nodes(
            self.graph,
            pos=node_positions,
            node_size=list(node_sizes.values()),  # type: ignore
            node_color=list(node_colors.values()),  # type: ignore
            linewidths=list(node_contour_sizes.values()),
            edgecolors=list(node_contour_colors.values()),
            alpha=list(node_alphas.values()),
            ax=self.axis,
        )
        return self

    def draw_edges(self):
        """Draw edges according to the settings."""
        self._check_setup()
        self._setup_canvas()

        node_positions = self._check_positions()

        node_sizes = self.nodes.sizes.get(self.graph.nodes(data=True), self.graph)
        edge_colors = self.edges.colors.get(self.graph.edges(data=True), self.graph)
        edge_sizes = self.edges.sizes.get(self.graph.edges(data=True), self.graph)
        edge_alphas = self.edges.alphas.get(self.graph.edges(data=True), self.graph)

        nx.draw_networkx_edges(
            self.graph,
            pos=node_positions,
            edge_color=list(edge_colors.values()),
            width=list(edge_sizes.values()),
            arrows=self.edges.arrow_size > 0,
            arrowsize=self.edges.arrow_size,
            ax=self.axis,
            node_size=list(node_sizes.values()),
            alpha=list(edge_alphas.values()),
        )
        return self

    def draw_labels(self):
        """Draw labels based on values."""
        self._check_setup()
        self._setup_canvas()

        if (
            self.nodes.labels.show_labels
            or self.nodes.labels.sizes is not None
            or self.nodes.labels.colors is not None
            or self.nodes.labels.alphas is not None
            or self.nodes.labels.font_families is not None
        ):

            if not self.nodes.labels.labels:
                labels = {n: n for n in self.graph.nodes}
                self.nodes.labels.set_labels(labels)

            if self.nodes.labels.sizes is None:
                self.nodes.labels.sizes = fixed(12)

            if self.nodes.labels.colors is None:
                self.nodes.labels.colors = fixed("black")

            if self.nodes.labels.alphas is None:
                self.nodes.labels.alphas = fixed(1.0)

            if self.nodes.labels.font_families is None:
                self.nodes.labels.font_families = fixed("DejaVu Sans")

            node_positions = self._check_positions()

            labels_size = self.nodes.labels.sizes.get(
                self.graph.nodes(data=True), self.graph
            )
            labels_color = self.nodes.labels.colors.get(
                self.graph.nodes(data=True), self.graph
            )
            labels_font_family = self.nodes.labels.font_families.get(
                self.graph.nodes(data=True), self.graph
            )
            labels_alpha = self.nodes.labels.alphas.get(
                self.graph.nodes(data=True), self.graph
            )

            _draw_networkx_multiple_labels(
                self.graph,
                labels=self.nodes.labels.labels,
                pos=node_positions,
                font_size=labels_size,
                font_color=labels_color,
                font_family=labels_font_family,
                alpha=labels_alpha,
                ax=self.axis,
            )

        return self

    def draw_description(self):
        """Draw description below the image according to the settings."""
        self._check_setup()
        self._setup_canvas()
        if self.description.text and self.axis is not None:
            self.axis.text(
                0.95,
                0.1,
                self.description.text,
                size=self.description.size,
                ha="right",
                transform=self.axis.transAxes,
                alpha=self.description.alpha,
            )
        return self

    def _draw_graph_keys(self):
        """Draw the graph keys in a separate figure.

        Uses the settings done in the GraphKeyGenerator.
        """
        if len(self.graph_keys.keys) > 0:
            self.graph_keys.draw_keys()
            self._fig_graph_keys = self.graph_keys._fig
        else:
            logger.warning(
                "No graph_keys were set, so no graph key will be displayed",
                stacklevel=4,
            )
        return self

    def draw(self):
        self.draw_edges().draw_nodes()
        self.draw_labels()
        if self.description.text:
            self.draw_description()
        self._draw_graph_keys()
        return self

    def write_file(self, path: str | Path):
        """Write file to disk on the given path.

        Will also close the internal figure object.

        Args:
          path: str | Path: Path to write the file to.

        Returns:
          self
        """
        path = Path(path)
        filepath, file_format = ensure_file_format(
            path, path.suffix, default_format=".svg"
        )

        self._fig.savefig(filepath, format=file_format, dpi=self.dpi)
        logger.info(f"Written graph image to {filepath}.")
        plt.close(self._fig)

        if self._fig_graph_keys is not None:

            graph_keys_filepath = Path(
                str(filepath.with_suffix("")) + "_graphkey" + str(filepath.suffix)
            )
            self._fig_graph_keys.savefig(
                graph_keys_filepath, format=file_format, dpi=self.dpi
            )
            logger.info(f"Written graph key image to {graph_keys_filepath}.")
            plt.close(self._fig_graph_keys)

        return self

    def deepcopy(self):
        """Create deep copy of the object.

        This is the same as calling copy.deepcopy() on the object
        """
        return deepcopy(self)

    def _check_setup(self):
        """Check if the setup is sufficient for drawing."""
        errors = []
        if self.graph is None:
            errors.append("Please set a graph.")
        # TODO maybe call self.check_positions() instead of in draw calls

        if not (self.nodes.positions):
            errors.append("Positions are not set.")
        elif set(self.graph.nodes) - set(self.nodes.positions.keys()):
            errors.append(
                """
            Position values and node IDs are not fully overlapping.
            This might be happening due to an obsoleted position file.
            """
            )

        if len(errors) > 0:
            [logger.error(e) for e in errors]
            raise ValueError("Your draw setup contains errors.")

    def write_json(self, path: str | Path) -> "ImageGenerator":
        """Write the graph data to a json file.

        This is following nx.node_link_data format as shown here:
        https://networkx.org/documentation/stable/reference/readwrite/generated/networkx.readwrite.json_graph.node_link_data.html

        Args:
            path: saving location and name for the json-file

        Returns:
            self
        """
        # TODO: Validate path with new helper method

        # Validates that a position attribute is set or raises an error
        node_positions = self._check_positions()
        # Ensure we do not change the original graph with our new attributes
        export_graph = deepcopy(self.graph)

        # Adding 'x' and 'y' as attributes for nodes
        node_sizes = self.nodes.sizes.get(export_graph.nodes(data=True), export_graph)
        node_colors = self.nodes.colors.get(export_graph.nodes(data=True), export_graph)
        # NOTE Edges are currently not exported. See FIXME below.
        # edge_colors = self.edges.colors.get(export_graph.edges(data=True), export_graph)
        # edge_sizes = self.edges.sizes.get(export_graph.edges(data=True), export_graph)

        # Sets the attributes explicitly as x and y coordinates for all nodes
        for node in export_graph.nodes:
            n = export_graph.nodes[node]
            n["x"] = node_positions[node][0]
            n["y"] = node_positions[node][1]
            n["nodeColor"] = node_colors[node]
            n["nodeSize"] = node_sizes[node]
        # # FIXME This is breaking due to an incorrect get function.
        # for edge in export_graph.edges:
        #     e = export_graph.edges[edge]
        #     e["edgeColor"] = edge_colors[edge]
        #     e["edgeSize"] = edge_sizes[edge]

        # Output to JSON format
        data = nx.node_link_data(export_graph)
        with open(path, "w") as file:
            # The Encoder ensure that np.ndarrays can be saved (as lists)
            json.dump(data, file, indent=4, cls=NumpyEncoder)

        return self


def ensure_file_format(
    path: str | Path, user_saving_format: str | None, *, default_format: str
) -> tuple[Path, str]:
    """Ensure the provided path has a saving format.

    Args:
        path: the path that needs to be validated
        user_saving_format: the saving format provided by the user
        default_format: the format a programmer can set that will be used as default, if
            no format was provided at all

    Returns:
        the filepath and format (without leading dot) as an 2-Tuple
    """
    # Ensures Path-operations
    if isinstance(path, str):
        path = Path(path)

    # If no format was specified
    if not path.suffix and not user_saving_format:
        logger.warning(
            f"No saving format was provided in the 'save_path' or directly "
            f"via 'saving_format'. '{default_format}' was used as default",
            stacklevel=4,
        )
        user_saving_format = default_format

    # 'user_saving_format' is always valued higher than path suffix
    if user_saving_format:
        # If user forgot the leading dot
        if not user_saving_format.startswith("."):
            user_saving_format = "." + user_saving_format
        path = path.with_suffix(user_saving_format)

    cleaned_suffix = path.suffix.strip(".")
    return path, cleaned_suffix
