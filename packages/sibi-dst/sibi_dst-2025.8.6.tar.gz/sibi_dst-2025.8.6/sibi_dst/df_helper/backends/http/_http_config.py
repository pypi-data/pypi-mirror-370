from typing import Dict, Optional, Any

import dask.dataframe as dd
import httpx
import pandas as pd
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, SecretStr

from sibi_dst.utils import Logger


class HttpConfig(BaseModel):
    """
    Configuration for HTTP client operations, designed to manage and fetch data
    from HTTP endpoints asynchronously. This class serves as a centralized configuration
    and operation hub encapsulating settings such as base URL, query parameters, API keys,
    and logger support. It employs `httpx` for HTTP interactions and leverages Dask for the
    resulting data handling and transformation.

    :ivar base_url: The base URL for HTTP communication.
    :type base_url: HttpUrl
    :ivar params: Optional dictionary containing query parameters to be used with GET requests.
    :type params: Optional[Dict[str, Any]]
    :ivar logger: The logger instance for logging operations. If not provided, a default logger
        is initialized using the class name.
    :type logger: Optional[Logger]
    :ivar timeout: The timeout value in seconds for HTTP requests. Defaults to 300.
    :type timeout: Optional[int]
    :ivar api_key: The optional secret API key for authorization. If present, it will populate
        the Authorization header in HTTP requests.
    :type api_key: Optional[SecretStr]
    """
    base_url: HttpUrl
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    logger: Optional[Logger] = None
    timeout: Optional[int] = 300
    api_key: Optional[SecretStr] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, logger=None, **data):
        """
        Initializes the class with a logger and other data parameters.

        This constructor allows the option to provide a custom logger. If no logger
        is supplied during initialization, a default logger specific to the class
        is created using the Logger utility. It also initializes the instance
        with additional data passed as keyword arguments.

        :param logger: Optional logger instance. If not provided, a default
            logger is created using the class name as the logger name.
        :type logger: logging.Logger, optional
        :param data: Arbitrary keyword arguments containing data to initialize
            the class.
        :type data: dict
        """
        super().__init__(**data)
        # Initialize the logger if not provided
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)

    async def fetch_data(self, **options) -> dd.DataFrame:
        """
        Fetches data from a specified HTTP JSON source and returns it as a dask DataFrame.

        This asynchronous method constructs a request URL based on the provided options
        and sends an HTTP GET request. The fetched JSON data is normalized and
        converted to a dask DataFrame for further use. It handles request errors and
        JSON parsing errors effectively.

        :param options: Arbitrary keyword arguments representing dynamic path segments
            to be appended to the base URL.
        :type options: dict
        :return: A dask DataFrame containing the structured data retrieved
            from the HTTP JSON source.
        :rtype: dd.DataFrame
        :raises httpx.RequestError: If there is an issue with the HTTP request.
        :raises ValueError: If there is an error parsing JSON data.
        """
        try:
            # Build URL with options as path segments

            if options:
                formatted_url = str(self.base_url).rstrip("/")
                formatted_url += "/" + "/".join(str(value) for value in options.values()) + "/"
            else:
                formatted_url = str(self.base_url)
                # Set up headers with API key if provided
            headers = {"Authorization": f"Bearer {self.api_key.get_secret_value()}"} if self.api_key else {}

            self.logger.debug(f"Fetching data from {formatted_url} with params {self.params}")
            async with httpx.AsyncClient() as client:
                response = await client.get(formatted_url, params=self.params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                df = dd.from_pandas(pd.json_normalize(data), npartitions=1)
                self.logger.debug("Data successfully loaded from HTTP JSON source.")
                return df
        except httpx.RequestError as e:
            self.logger.debug(f"HTTP request error: {e}")
            raise
        except ValueError as e:
            self.logger.debug(f"Error parsing JSON data: {e}")
            raise
