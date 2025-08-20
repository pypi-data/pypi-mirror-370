from typing import Optional

import dask.dataframe as dd
import httpx
import pandas as pd


class DataFromHttpSource:
    def __init__(self, base_url: str, cube_name: str, api_key: Optional[str] = None, **kwargs):
        # Ensure 'params' exists before updating
        params = kwargs.pop('params', {})
        params.setdefault('cube', cube_name)

        self.config = {
            'base_url': base_url,
            'timeout': kwargs.get('timeout', 60),
            'npartitions': kwargs.get('npartitions', 1),
            'params': params,
            'headers': kwargs.get('headers', {})  # Allow custom headers
        }
        self.config.update(kwargs)

        # Add API key to headers if provided
        if api_key:
            self.config['headers']['Authorization'] = f"Bearer {api_key}"

        self.formatted_url = f"{str(self.config.get('base_url', '')).rstrip('/')}/"

    def load(self, **kwargs) -> dd.DataFrame:
        """Loads data from HTTP source into a Dask DataFrame."""
        params = {**self.config.get('params', {}), 'load_params': kwargs}

        try:
            response = httpx.post(
                self.formatted_url,
                json=params,
                timeout=self.config['timeout'],
                headers=self.config['headers']
            )
            response.raise_for_status()  # Raises an HTTPError for 4xx/5xx responses
            result = response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error: {e.response.status_code}, {e.response.text}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error: {str(e)}") from e
        except ValueError:
            raise RuntimeError("Failed to parse JSON response")

        return dd.from_pandas(pd.DataFrame(result.get('data', [])), npartitions=self.config['npartitions'])
