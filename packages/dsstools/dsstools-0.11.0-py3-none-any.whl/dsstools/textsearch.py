# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""This module allows for text search in graph nodes. """

from functools import singledispatchmethod
from typing import Iterable, List, Union

import networkx as nx
import pandas as pd

from dsstools.log.logger import get_logger
from dsstools.wdc import WDC

from .attrs import Category, Code
from .utils import _deprecate

logger = get_logger("WDCAPI")


class TextSearch(WDC):
    """Class allowing to search for keywords in the WDC API.

    Args:
      identifier: Identifier of the network data. For the text search this is
        normally in the form `20121227_intermediaries` (a date string with a short
        text appended).
      token: Token for authorization.
      api: API address to send request to. Leave this as is.
      insecure: Hide warning regarding missing https.
      timeout: Set the timeout to the server. Increase this if you request large
        networks.

    Returns:
      Instance of TextSearch

    """

    endpoint = "snapshot"
    def __init__(self,
                 identifier: str | None = None,
                 *,
                 token: str | None = None,
                 api: str = "https://dss-wdc.wiso.uni-hamburg.de/api",
                 insecure: bool = False,
                 timeout: int = 60,
                 params: dict | None = None,
                 ):
        super().__init__(token=token, api=api, insecure=insecure, timeout=timeout, params=params)
        self.identifier = identifier

    @staticmethod
    def _handle_grafted_terms(fun):
        def wrapper(*args, **kwargs):
            domain, terms = args
            # Flatten list internally
            if all(isinstance(term, list) for term in terms):
                response = fun(domain, [t for te in terms for t in te], **kwargs)
                if response is not None:
                    return {
                        term_group[0]: sum(response.get(term) for term in term_group)
                        for term_group in terms
                    }
                else:
                    return response
            elif any(isinstance(term, list) for term in terms):
                logger.error("Passed list must be exclusively a list of strings or a list of lists")
                raise ValueError(
                    "The passed term list does not exclusively contain either strings or lists."
                )
            else:
                return fun(domain, terms, **kwargs)

        return wrapper

    def _construct_url(self) -> str:
        """Construct a url from API, endpoint and identifier."""
        if self.identifier:
            return f"{self.api}/{self.endpoint}/{self.identifier}/"
        else:
            logger.error("An identifier must be set.")
            raise ValueError("Please set a snapshot identifier to the TextSearch object first.")

    def get_missing(self, domains: Iterable) -> set:
        """Compare given domains and hits on the API and return the difference.

        Args:
          domains: Domains to compare against
          domains: Iterable: 

        Returns:
          : Difference of domains

        """
        domain_hits = set()
        for page in self._get_results(self._construct_url() + "domains"):
            for data in page["content"]:
                domain_hits.add(data["domainName"])
        return set(domains) - domain_hits

    def get_snapshots(self, name_tag="") -> set:
        """List available snapshots by name.

        Args:
          name_tag: Filter for name tag. (Default value = "")

        Returns:
          Available snapshot ids.

        """
        snapshots = set()
        for page in self._get_results(self._construct_url_base() + "/list"):
            for data in page["content"]:
                if name_tag in data["name"]:
                    snapshots.add(data["name"])
        return snapshots

    def __query_domains(
            self, domains, query_term, missing_domains=None, key=None
    ) -> dict:
        if key is None:
            key = query_term

        domain_hits = {}
        # The argument query_term overwrites any passed "query" key.
        params = self.params | {"query": query_term}
        for page in self._get_results(self._construct_url() + "searchDomains", params):
            for data in page["content"]:
                domain_hits[data["domainName"]] = data["hits"]
        single_term_hits = {}
        for domain in domains:
            if domain in missing_domains:
                # Make missing domains a None for visualization purposes.
                single_term_hits[domain] = None
            else:
                # Make zero hits an actual zero (and not None).
                single_term_hits[domain] = domain_hits.get(domain, 0)
        return single_term_hits

    @singledispatchmethod
    def search(self, domains: nx.Graph|List , terms: List[str] | List[List[str]] | dict[str, str] | dict[str, List[str]] | pd.Series | pd.DataFrame):
        """Searches the given keywords across a Graph or iterator.
        
        For using a complex, already existing Solr query it is recommended to use the following structure:
        {"some-key": "your-query OR some-other-query"} (see the docstring for the `terms` parameter).

        Args:
          domains: Set of identifiers to search in. Both graphs and
            lists are allowed.
          terms: Terms to search for. Various structures are allowed. Lists of lists
            combine all response values into one response, e.g. [[A,B],[C,D]] means A and
            B counts will be combined into one value. This is helpful for using synonyms.
            In legends the first value in the inner list sets the "key". dict[str,
            List[str]] follow the same structure of combining the values in the list but
            give the result the selected key.

        Returns:
          Updated graph or dict containing the responses.

        """
        not_implemented = NotImplementedError("Can only search on domain lists or graphs.")
        logger.error(not_implemented)
        raise not_implemented

    # TODO How to handle literal terms?
    @search.register
    def _(
        self,
        domains: list,
        terms: List[str] | List[List[str]] | dict[str, str] | dict[str, List[str]] | pd.Series | pd.DataFrame
    ) -> dict:

        term_hits = {}
        missing_domains = self.get_missing(domains)
        logger.info(f"The following terms are set for the query: {terms}")
        if isinstance(terms, list):
            terms_iter = terms
        else:
            terms_iter = terms.items()

        for term in terms_iter:
            if isinstance(terms, (dict, pd.Series)):
                key, term = term
            elif isinstance(terms, pd.DataFrame):
                key, column = term
                term = column.to_list()
            elif isinstance(terms, list) and isinstance(term, list):
                key = term[0]
            else:
                key = term

            query_term = " OR ".join(term) if isinstance(term, list) else term
            logger.info(f"Querying API for {term}...")
            term_hits[key] = self.__query_domains(
                domains, query_term, missing_domains, key=key
            )

        # Transpose dict of dict (nested dict). We first get the keys from the first
        # entry and then construct the resulting new dictionary. See for an explanation
        # here:
        # https://stackoverflow.com/questions/33425871/rearranging-levels-of-a-nested-dictionary-in-python
        # This could also be done by converting to a Pandas DataFrame as a dict of dict
        # is equivalent to a 2D matrix:
        # df = pd.DataFrame.from_dict(term_hits).T
        keys = term_hits[next(iter(term_hits.keys()))].keys()
        return {
            key: {k: term_hits[k][key] for k in term_hits if key in term_hits[k]}
            for key in keys
        }

    @_deprecate("Beware, this method will be changed in future versions.", "v0.12.0")
    @search.register
    def _(
        self,
        domains: nx.Graph,
        terms: List[str] | List[List[str]] | dict[str, str] | dict[str, List[str]] | pd.Series | pd.DataFrame
    ) -> nx.Graph:
        domain_hits = self.search(list(domains.nodes), terms)
        for node_id, values in domain_hits.items():
            node = domains.nodes[node_id]
            for key, value in values.items():
                if value is not None:
                    node[str(Code(key, Category.TEXT))] = value
        return domains
