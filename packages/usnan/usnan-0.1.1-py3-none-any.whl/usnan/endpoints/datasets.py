"""Datasets endpoint implementation"""
import concurrent.futures
import tempfile
import zipfile
from pathlib import Path
from typing import Generator, List, Union

from .base import BaseEndpoint
from ..models.datasets import Dataset
from ..models.search import SearchConfig


class DatasetsEndpoint(BaseEndpoint):
    """Endpoint for managing datasets"""

    def search(self, search_config: SearchConfig) -> Generator[Dataset, None, None]:
        """
        Search datasets according to parameters in the search_config object.
        
        Args:
            search_config: Search configuration object
            
        Returns:
            Generator of Dataset objects
        """

        config_copy: SearchConfig = search_config.clone()
        next_batch_future = None
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        def fetch_batch(config):
            """Helper function to fetch a batch of data"""
            return self._get('/nan/public/datasets/search', params=config.build())

        try:
            while True:
                # Get current batch (either first request or from prefetched future)
                if next_batch_future is None:
                    response = fetch_batch(config_copy)
                else:
                    response = next_batch_future.result()
                
                # Prepare next batch config before yielding current results
                next_config = config_copy.clone()
                next_config.offset += next_config.records
                
                # Double the amount of records fetched at a time each time they are exhausted, but don't
                #  fetch more than 1000 at a time.
                if next_config.records < 1000:
                    new_records = int(next_config.records * 2)
                    next_config.records = new_records
                    if new_records > 1000:
                        next_config.records = 1000

                # Start prefetching next batch if not on last page
                if not response.get('last_page'):
                    next_batch_future = executor.submit(fetch_batch, next_config)
                else:
                    next_batch_future = None

                # Yield current batch results
                for item in response.get('experiments', []):
                    yield Dataset.from_dict(self.client, item)
                
                if response.get('last_page'):
                    return
                
                config_copy = next_config
        finally:
            executor.shutdown(wait=False)
    
    def get(self, dataset_id: int) -> Dataset:
        """
        Get a specific dataset by ID

        Args:
            dataset_id: The dataset ID

        Returns:
            Dataset object
        """
        if not isinstance(dataset_id, int):
            raise TypeError('dataset_id must be an integer.')

        experiment = self._get(f'/nan/public/datasets/{dataset_id}')
        return Dataset.from_dict(self.client, experiment)

    def download(self, dataset_ids: List[int], location: Union[str, Path]):
        """ Downloads the data for the specified dataset ids. """

        # Convert location to Path object for easier handling
        location_path = Path(location)

        # Check if target directory exists and is empty
        if location_path.exists():
            if not location_path.is_dir():
                raise ValueError(f"Target location '{location_path}' exists but is not a directory")
            if any(location_path.iterdir()):
                raise ValueError(f"Target directory '{location_path}' is not empty")
        else:
            # Create the target directory
            location_path.mkdir(parents=True, exist_ok=True)

        json = self._post('/nan/data-browser/experiment-download', json={'ids': dataset_ids})

        # Get the file response directly from the client
        response = self.client._make_request('GET', '/nan/data-browser/experiment-download',
                                             params={'resume_id': json['data']['resume_id']})

        # Create a temporary file to save the ZIP
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_zip_path = Path(temp_file.name)
            temp_file.write(response.content)

            # Extract the ZIP file to the target location
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(location_path)
