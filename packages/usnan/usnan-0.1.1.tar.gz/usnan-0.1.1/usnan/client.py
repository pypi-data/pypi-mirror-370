"""Main client for USNAN API"""

import logging
import time

import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from .endpoints import DatasetsEndpoint, FacilitiesEndpoint, SpectrometerEndpoint, ProbesEndpoint

# Set up logger for this module
logger = logging.getLogger(__name__)


class USNANClient:
    """Main client for interacting with the USNAN API
    
    Attributes:
        facilities: Access to facilities endpoint for querying facility information
        spectrometers: Access to spectrometers endpoint for querying spectrometer data
        datasets: Access to datasets endpoint for querying dataset information
        probes: Access to probes endpoint for querying probe data
    """

    def __init__(self, base_url: str="https://dev.api.nmrhub.org", timeout: int = 30, num_retries: int = 3):
        """
        Initialize the USNAN client
        
        Args:
            base_url: Base URL for the USNAN API
            timeout: Request timeout in seconds
            num_retries: Number of retries for failed requests (only for 500 errors or connectivity issues)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.num_retries = num_retries
        self._cache_clear_time = time.time()
        
        # Initialize session
        self.session = requests.Session()
        
        # Initialize endpoints
        self.datasets = DatasetsEndpoint(self)
        self.facilities = FacilitiesEndpoint(self)
        self.spectrometers = SpectrometerEndpoint(self)
        self.probes = ProbesEndpoint(self)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault('timeout', self.timeout)
        
        last_exception = None
        
        for attempt in range(self.num_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except (ConnectionError, Timeout) as e:
                # Network connectivity issues - retry
                last_exception = e
                if attempt < self.num_retries:
                    logger.info(f"Request to {url} failed due to connectivity issue, retrying in {2 ** attempt} seconds (attempt {attempt + 1}/{self.num_retries + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except requests.HTTPError as e:
                # Only retry on 500 status codes
                if e.response.status_code == 500:
                    last_exception = e
                    if attempt < self.num_retries:
                        logger.info(f"Request to {url} failed with HTTP 500, retrying in {2 ** attempt} seconds (attempt {attempt + 1}/{self.num_retries + 1})")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                if e.response.status_code == 400:
                    raise RuntimeError(f"NMRhub server indicated your request was invalid: {e.response.json()['message']}")
                if e.response.status_code == 404:
                    raise KeyError(f"NMRhub server indicated no results: {e.response.json()['message']}")
                raise
            except RequestException:
                # Other request exceptions - don't retry
                raise
        
        # If we get here, all retries failed
        raise last_exception

    def clear_cache(self) -> None:
        self._cache_clear_time = time.time()

    @property
    def cache_clear_time(self):
        return self._cache_clear_time
