"""Probes endpoint implementation"""

import time
from typing import List, Dict

from .base import BaseEndpoint
from ..models.probes import Probe


class ProbesEndpoint(BaseEndpoint):
    """Endpoint for managing probes"""

    _probes: List[Probe]
    _probes_map: Dict[str, Probe]

    def __init__(self, client):
        super().__init__(client)
        self._probes: List[Probe] = []
        self._probes_map: Dict[str, Probe] = {}

    def list(self) -> List[Probe]:
        """
        List all probes
        
        Returns:
            List of Probe objects
        """
        # Check if cache needs to be invalidated
        if self._probes and self.client.cache_clear_time <= self._last_fetch_time:
            return self._probes
        else:
            response = self._get('/nan/public/probes')
            probes = [Probe.from_dict(self.client, item) for item in response]
            self._probes_map = {_.identifier: _ for _ in probes}
            self._probes = probes
            self._last_fetch_time = time.time()
            return probes
    
    def get(self, probe_id: str) -> Probe:
        """
        Get a specific probe by ID
        
        Args:
            probe_id: The probe ID
            
        Returns:
            Probe object
        """
        self.list() # Ensure that the probes are cached
        if probe_id not in self._probes_map:
            raise KeyError(f'Unknown probe identifier: {probe_id}')
        return self._probes_map[probe_id]
