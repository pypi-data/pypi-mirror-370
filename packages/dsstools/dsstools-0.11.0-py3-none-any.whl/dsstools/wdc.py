# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import requests

from dsstools.log.logger import get_logger

logger = get_logger("WDCAPI")

class WDC:
    endpoint = "UNSET"

    def __init__(
        self,
        *,
        token: str | None = None,
        api: str = "https://dss-wdc.wiso.uni-hamburg.de/api",
        insecure: bool = False,
        timeout: int = 120,
        params: dict | None = None,
    ):
        """Internal class for interacting with the WDC API.

        Args:
          token: Token for authorization.
          api: API address to send request to. Leave this as is.
          insecure: Hide warning regarding missing https.
          timeout: Set the timeout to the server. Increase this if you request large
            networks.
          params: These are additional keyword arguments passed onto the API endpoint. See
            https://dss-wdc.wiso.uni-hamburg.de/#_complex_datatypes_for_the_api_requests
            for further assistance.
        """

        if not insecure and not api.startswith("https://"):
            logger.warning(
                "Not using HTTPS for your request to the Solr server. Consider using encryption."
            )
        self.api = api[:-1] if api.endswith("/") else api
        self.identifier = None
        self.session = requests.Session()
        self.timeout = timeout
        self.params = params if params else {}
        if token:
            self.token = token

    @property
    def token(self):
        """Get the password token."""
        return self.session.headers.get("Token")

    @token.setter
    def token(self, value):
        """Set the password token.

        Args:
          value: Token
        """
        if self.session.headers.get("Token") != value:
            self.session.headers.update({"Token": f"{value}"})

    def _get_results(self, url, params: dict | None = None):
        """Handle pagination of json responses for the given URL.

        Args:
          url: URL to query for.
          params: dict | None:  (Default value = None)

        Returns:
          Iterator of the results.

        """
        if not params:
            params = {}

        if self.token is None:
            logger.error("Missing WDC api token.")
            raise ValueError("Set a token before accessing the WDC api.")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.ReadTimeout as e:
            errmsg = "Try increasing the timeout value for load-intensive queries for the TextSearch instance."
            e.args += (errmsg,)
            raise e


        try:
            response.raise_for_status()
        except requests.HTTPError:
            invalid_request_reason = response.json()["responseHeader"]["msg"]
            logger.error(f"Invalid request: {invalid_request_reason}")
            raise requests.HTTPError(f"Your request has failed because: {invalid_request_reason}")

        first_page = response.json()
        yield first_page
        num_pages = first_page["page"]["totalPages"]

        for page in range(1, num_pages):
            response = self.session.get(url, params={"page": page})
            response.raise_for_status()
            yield response.json()

    def _construct_url_base(self) -> str:
        """Construct the url from API and endpoint."""
        return f"{self.api}/{self.endpoint}"


class WDCGeneric(WDC):
    def __init__(self,
                 identifier: str | int = None,
                 *,
                 token: str | None = None,
                 api: str = "https://dss-wdc.wiso.uni-hamburg.de/api",
                 insecure: bool = False,
                 timeout: int = 60,
                 params: dict | None = None,
                 ):
        """Public class for calling WDC-API directly.

        If you want to interact with WDC directly, you need to use this WDCGeneric class
        since it allows you to parse an identifier for snapshots (or use subclasses of
        WDC such as TextSearch or GraphImporter directly). This is for advanced users
        only.

        Note: WDCGeneric was split up with v0.10.0 into WDC and WDCGeneric
        This exists to ensure compatibility with older versions. This also helps with
        type hinting across different versions.

        Args:
          identifier: Identifier of the network data.
          token: Token for authorization.
          api: API address to send request to. Leave this as is.
          insecure: Hide warning regarding missing https.
          timeout: Set the timeout to the server. Increase this if you request large
            networks.
          params: These are additional keyword arguments passed onto the API endpoint. See
            https://dss-wdc.wiso.uni-hamburg.de/#_complex_datatypes_for_the_api_requests
            for further assistance.
          """
        super().__init__(token=token, api=api, insecure=insecure, timeout=timeout, params=params)
        self.identifier = identifier
