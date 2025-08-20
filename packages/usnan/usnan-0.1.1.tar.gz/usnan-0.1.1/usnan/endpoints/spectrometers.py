"""Spectrometers endpoint implementation"""

import time
from typing import List, Dict

from .base import BaseEndpoint
from ..models.spectrometers import Spectrometer


class SpectrometerEndpoint(BaseEndpoint):
    """Endpoint for managing spectrometers"""

    _spectrometers: List[Spectrometer]
    _spectrometers_map: Dict[str, Spectrometer]

    def __init__(self, client):
        super().__init__(client)
        self._spectrometers: List[Spectrometer] = []
        self._spectrometers_map: Dict[str, Spectrometer] = {}

    def list(self) -> List[Spectrometer]:
        """
        List all spectrometers
        
        Returns:
            List of Spectrometer objects
        """
        # Check if cache needs to be invalidated
        if self._spectrometers and self.client.cache_clear_time <= self._last_fetch_time:
            return self._spectrometers
        else:
            response = self._get('/nan/public/instruments')
            facilities = [Spectrometer.from_dict(self.client, item) for item in response]
            self._spectrometers_map = {_.identifier: _ for _ in facilities}
            self._spectrometers = facilities
            self._last_fetch_time = time.time()
            return facilities

    def get(self, spectrometer_id: str) -> Spectrometer:
        """
        Get a specific spectrometer by ID
        
        Args:
            spectrometer_id: The spectrometer ID
            
        Returns:
            Spectrometer object
        """
        self.list() # Ensure that the spectrometers are cached
        if spectrometer_id not in self._spectrometers_map:
            raise KeyError(f'Unknown spectrometer identifier: {spectrometer_id}')
        return self._spectrometers_map[spectrometer_id]
