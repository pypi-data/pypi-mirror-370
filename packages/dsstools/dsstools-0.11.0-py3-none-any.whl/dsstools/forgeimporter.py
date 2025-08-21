# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
"""
import datetime
import os
import pickle
from pathlib import Path
from tempfile import gettempdir
from typing import Callable, Iterable, Union

import networkx as nx
import numpy as np
import pandas as pd
import requests

from dsstools.attrs import Category, Code
from dsstools.log.logger import get_logger

logger = get_logger(__name__)

def clean_graph_data_attributes(graph: nx.DiGraph) -> nx.DiGraph:
    """Replace empty strings in data attributes with np.nan."""
    for node in graph.nodes(data=True):
        for k,val in node[1].items():
            if val == "":
                node[1][k] = np.nan
    return graph


def import_from_data_forge(
    slug: str,
    snapshot: str,
    token: str,
    domain: str = "dss-graph.wiso.uni-hamburg.de",
    cache: Union[bool, Path, str] = True,
    remove_selfloops: bool = True,
    contract_redirects: bool = False,
    explicit_include: bool = False
) -> nx.DiGraph:
    """Import Graph object from dssCode.

    Args:
       slug (str): Name slug of the project (see dssCode-Interface)
       snapshot (str): Snapshot hash
       domain (str): The domain for the API call
       cache (bool,Path,str): Pass the cache directory. Defaults to temporary dir.
       remove_selfloops (bool): Remove edge selfloops.
       contract_redirects (bool): Contract redirecting nodes into one.
       explicit_include (bool): Include only explicitely marked nodes into graph
       (redirecting nodes need to be marked as well).

    Returns:
        nx.DiGraph: Graph with the imported data.
    """
    headers = {"Authorization": f"Token {token}"}

    node_url = f"https://{domain}/api/snapshots/{slug}/{snapshot}/node"
    edge_url = f"https://{domain}/api/snapshots/{slug}/{snapshot}/edge"
    property_url = (
        f"https://{domain}/api/snapshots/{slug}/{snapshot}/property"
    )
    # Parse nodes
    graph = _parse_json_response(
        nx.DiGraph(),
        node_url,
        headers,
        _json_node_parser,
        explicit_include=explicit_include,
    )
    # Parse edges
    graph = _parse_json_response(
        graph,
        edge_url,
        headers,
        _json_edge_parser,
    )
    # Parse properties
    graph = _parse_json_response(
        graph,
        property_url,
        headers,
        _json_property_parser,
    )

    if graph.graph["none_edge_count"] > 0:
        logger.warning(
            f"Skipped {graph.graph['none_edge_count']} Edge(s) without any corresponding nodes."
        )
    if graph.graph["orphan_edge_count"] > 0:
        logger.warning(
            f"Skipped {graph.graph['orphan_edge_count']} Edge(s) for finding one of their nodes."
        )
    graph.graph.pop("none_edge_count")
    graph.graph.pop("orphan_edge_count")

    if contract_redirects and graph.graph["redirects"]:
        for from_node, to_node in graph.graph["redirects"].items():
            # NOTE: Selfloops should be handled by the other option remove_selfloops
            graph = nx.contracted_nodes(graph, to_node, from_node)
    if remove_selfloops:
        graph.remove_edges_from(nx.selfloop_edges(graph))

    logger.info(f"Pulled {len(graph.nodes)} nodes and {len(graph.edges)} edges.")
    graph = clean_graph_data_attributes(graph)

    # TODO Make this an explicit intermediary save for writing to disk. This
    # should be able to be passed around between members.
    fnm = f"dsstools-{int(datetime.datetime.now().timestamp())}"
    if cache:
        if isinstance(cache, str):
            cache = Path(cache).absolute()
            cache.mkdir(parents=True, exist_ok=True)
            pth = cache / fnm
        elif isinstance(cache, Path):
            cache.mkdir(parents=True, exist_ok=True)
            pth = cache / fnm
        else:
            pth = Path(gettempdir()) / fnm
        with open(pth, "wb") as file:
            pickle.dump(graph, file)

    return graph



def _handle_json_response(json_response) -> list:
    """Try to properly set up paginated and non-paginated json data streams."""
    if isinstance(json_response, dict):
        if responses := json_response.get("results"):
            return responses
    elif isinstance(json_response, list):
        return json_response

    improper_json_response = ValueError("Unable to handle json response properly.")
    logger.error(improper_json_response)
    raise improper_json_response


def _json_node_parser(graph: nx.Graph, json_response, **kwargs) -> nx.DiGraph:
    # Ensure graph attributes are initialized
    if not graph.graph.get("uuid_map"):
        graph.graph["uuid_map"] = {}
    if not graph.graph.get("attributes"):
        graph.graph["attributes"] = {}
    if not graph.graph.get("redirects"):
        graph.graph["redirects"] = {}

    for json_node in _handle_json_response(json_response):
        include_condition = (
            json_node.get("status") == "IN" if kwargs.get("explicit_include") else True
        )
        if json_node.get("url") == "":
            logger.warning("Found node empty url attribute, skipping.")
        elif json_node.get("status") == "IG":
            logger.debug(f"Excluded node {json_node.get('url')}.")
        elif json_node.get("redirect") and include_condition:
            data = { str(Code(i, Category.MANUAL)): k for i,k in json_node["data"].items() }
            graph.add_node(json_node["url"], **data)
            graph.graph["uuid_map"][json_node["id"]] = json_node["url"]
            logger.debug(
                f"Found a redirecting node: {json_node['url']} -> {json_node.get('redirect')}"
            )
            graph.graph["redirects"][json_node["url"]] = json_node["redirect"]
        elif include_condition:
            graph.add_node(json_node["url"], **json_node["data"])
            graph.graph["uuid_map"][json_node["id"]] = json_node["url"]
    return graph



def _json_edge_parser(graph: nx.Graph, json_response, **kwargs): # type: ignore
    if not graph.graph.get("none_edge_count"):
        graph.graph["none_edge_count"] = 0
    if not graph.graph.get("orphan_edge_count"):
        graph.graph["orphan_edge_count"] = 0

    for json_edge in _handle_json_response(json_response):
        from_node = graph.graph["uuid_map"].get(json_edge.get("from_node"))
        to_node = graph.graph["uuid_map"].get(json_edge.get("to_node"))
        if from_node and to_node:
            graph.add_edge(from_node, to_node, weight=float(json_edge.get("weight")))
        else:
            if not from_node and not to_node:
                graph.graph["none_edge_count"] += 1
            else:
                graph.graph["orphan_edge_count"] += 1
            logger.debug(
                f"Missing node {json_edge.get('from_node') if not from_node else 'None'}"
                + f"{json_edge.get('to_node') if not from_node else 'None'}"
            )
    return graph


def _json_property_parser(graph: nx.Graph, json_response, **kwargs): # type: ignore
    if not graph.graph.get("properties"):
        graph.graph["properties"] = {}

    types = ["categorical", "numeric", "string", "boolean"]
    for typ in types:
        if cats := json_response.get(typ):
            for cat in cats:
                graph.graph["properties"][cat["name"]] = (
                    cat["choices"] if cat.get("choices") else []
                )

    return graph


def _parse_json_response(graph, url, headers, parser, **kwargs):
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        logger.error(f"Unsuccessful response from API: HTTP {resp.status_code}")
        logger.error(f"URL: {url}")
        raise ValueError(
            "Did not receive results."
            + " Please check your domain settings, slug and token and the endpoint."
        )
    graph = parser(
        graph, resp.json(), headers=headers, parser=parser, **kwargs
    )
    return graph


def read_from_pickle(folder:Union[str,Path]="", timestamp:str="") -> nx.DiGraph:
    """Read cached graph from directory.

    Automatically selects the newest instance, except a timestamp is given.

    Args:
       dir (str, Path): Path to directory to search for pickles. If empty, default to temp dir.
       timestamp (str): timestamp to explicitely select for.

    Returns:
        nx.DiGraph: Graph with the imported data.
    """
    newest_file = ""
    newest = 0
    if folder == "":
        folder = Path(gettempdir())
    elif isinstance(folder, str):
        folder = Path(folder)
    for file in os.listdir(folder):
        if file.startswith("dsstools-") and len(file.split("-")[-1]) == 10:
            time = int(file.split("-")[-1])
            if timestamp and timestamp == time:
                newest_file = file
            elif time > newest:
                newest = time
                newest_file = file

    pth = Path(folder, newest_file)
    # If no file is found file is ""
    if pth.is_dir():
        file_not_found = FileNotFoundError(f"Unable to find the cached file in the directory {folder}.")
        logger.error(file_not_found)
        raise file_not_found

    with open(pth, 'rb') as file:
        graph = pickle.load(file)
    graph = clean_graph_data_attributes(graph)
    return graph
