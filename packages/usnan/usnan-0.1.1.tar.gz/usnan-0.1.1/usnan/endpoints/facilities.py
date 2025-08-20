"""Facilities endpoint implementation"""
import time
from typing import List, Dict

from .base import BaseEndpoint
from ..models.facilities import Facility


class FacilitiesEndpoint(BaseEndpoint):
    """Endpoint for managing facilities"""

    _facilities: List[Facility]
    _facilities_map: Dict[str, Facility]

    def __init__(self, client):
        super().__init__(client)
        self._facilities: List[Facility] = []
        self._facilities_map: Dict[str, Facility] = {}

    def list(self) -> List[Facility]:
        """
        List all facilities
        
        Returns:
            List of Facility objects
        """
        # Check if cache needs to be invalidated
        if self._facilities and self.client.cache_clear_time <= self._last_fetch_time:
            return self._facilities
        else:
            response = self._get('/nan/public/facilities')
            facilities = [Facility.from_dict(self.client, item) for item in response]
            self._facilities_map = {_.identifier: _ for _ in facilities}
            self._facilities = facilities
            self._last_fetch_time = time.time()
            return facilities

    def get(self, facility_id: str) -> Facility:
        """
        Get a specific facility by ID
        
        Args:
            facility_id: The facility ID
            
        Returns:
            Facility object
        """
        self.list() # Ensure that the facilities are cached
        if facility_id not in self._facilities_map:
            raise KeyError(f'Unknown facility ID: {facility_id}')
        return self._facilities_map[facility_id]
