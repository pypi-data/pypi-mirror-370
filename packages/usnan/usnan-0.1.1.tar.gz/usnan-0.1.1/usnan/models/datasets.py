from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal, Union

import usnan


@dataclass
class Dimension:
    """Represents a dimension in a dataset"""
    dimension: int
    nucleus: str
    is_direct: bool
    spectral_width_ppm: Optional[float] = None
    maximum_evolution_time: Optional[float] = None
    num_points: Optional[int] = None

    def __str__(self) -> str:
        """Return a string representation of the dimension"""
        parts = [f"Dimension {self.dimension}: {self.nucleus}"]

        if self.is_direct:
            parts.append("(direct)")
        else:
            parts.append("(indirect)")

        specs = []
        if self.spectral_width_ppm:
            specs.append(f"SW: {self.spectral_width_ppm} Hz")
        if self.num_points:
            specs.append(f"Points: {self.num_points}")
        if self.maximum_evolution_time:
            specs.append(f"Max evolution: {self.maximum_evolution_time} s")

        if specs:
            parts.append(f"[{', '.join(specs)}]")

        return " ".join(parts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dimension':
        return cls(
            dimension=data['dimension'],
            nucleus=data['nucleus'],
            is_direct=data['is_direct'],
            spectral_width_ppm=data.get('spectral_width_ppm'),
            maximum_evolution_time=data.get('maximum_evolution_time'),
            num_points=data.get('num_points')
        )


@dataclass
class DatasetVersion:
    """Represents a version of an experiment"""
    dataset: 'Dataset' = None
    version: int = None

    @classmethod
    def from_dict(cls, client: 'usnan.USNANClient', data: Dict[str, Any]) -> 'DatasetVersion':
        return cls(
            dataset=usnan.models.Dataset.from_identifier(client=client, identifier=data['id']),
            version=data.get('version'),
        )


@dataclass
class Dataset:
    """Represents a dataset in the system"""

    id: int
    _initialized: bool = False
    _client: 'usnan.USNANClient' = None
    classification: Optional[Literal["Calibration experiment", "Failed-sample related", "Failed-instrument related", "Failed-setup related", "Successful experiment", "Test experiment"]] = None
    dataset_name: Optional[str] = None
    decoupling_sequence: Optional[str] = None
    experiment_end_time: Optional[str] = None
    experiment_name: Optional[str] = None
    experiment_start_time: Optional[str] = None
    facility_identifier: Optional[str] = None
    identifier: Optional[str] = None
    is_knowledgebase: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_multi_receiver: Optional[bool] = None
    is_non_uniform: Optional[bool] = None
    mas_rate: Optional[float] = None
    mixing_sequence: Optional[str] = None
    mixing_time: Optional[float] = None
    notes: Optional[str] = None
    num_dimension: Optional[int] = None
    num_dimension_collected: Optional[int] = None
    number_in_set: Optional[int] = None
    pi_name: Optional[str] = None
    preferred: Optional[bool] = None
    public_time: Optional[str] = None
    published_time: Optional[str] = None
    pulse_sequence: Optional[str] = None
    sample_id: Optional[int] = None
    sample_sparsity: Optional[float] = None
    session_id: Optional[int] = None
    solvent: Optional[str] = None
    source: Optional[Literal['NDTS-auto', 'NDTS-manual', 'NAN-arbitrary']] = None
    spectrometer_identifier: Optional[str] = None
    state: Optional[str] = None
    tags: Optional[List[str]] = None
    temperature_k: Optional[float] = None
    time_shared: Optional[bool] = None
    title: Optional[str] = None
    version: Optional[int] = None
    z0_drift_correction: Optional[bool] = None

    # Related objects
    spectrometer: 'usnan.models.Spectrometer' = None
    facility: 'usnan.models.Facility' = None
    dimensions: Optional[List[Dimension]] = None
    versions: Optional[List[DatasetVersion]] = None

    @classmethod
    def from_dict(cls, client: 'usnan.USNANClient', data: Dict[str, Any]) -> 'Dataset':
        """Create a Dataset instance from API response data"""
        return cls(
            id=data['id'],
            _client=client,
            _initialized=True,
            classification=data.get('classification'),
            dataset_name=data.get('dataset_name'),
            decoupling_sequence=data.get('decoupling_sequence'),
            experiment_end_time=data.get('experiment_end_time'),
            experiment_name=data.get('experiment_name'),
            experiment_start_time=data.get('experiment_start_time'),
            facility_identifier=data.get('facility_identifier'),
            identifier=data.get('identifier'),
            is_knowledgebase=data.get('is_knowledgebase'),
            is_locked=data.get('is_locked'),
            is_multi_receiver=data.get('is_multi_receiver'),
            is_non_uniform=data.get('is_non_uniform'),
            mas_rate=data.get('mas_rate'),
            mixing_sequence=data.get('mixing_sequence'),
            mixing_time=data.get('mixing_time'),
            notes=data.get('notes'),
            num_dimension=data.get('num_dimension'),
            num_dimension_collected=data.get('num_dimension_collected'),
            number_in_set=data.get('number_in_set'),
            pi_name=data.get('pi_name'),
            preferred=data.get('preferred'),
            public_time=data.get('public_time'),
            published_time=data.get('published_time'),
            pulse_sequence=data.get('pulse_sequence'),
            sample_id=data.get('sample_id'),
            sample_sparsity=data.get('sample_sparsity'),
            session_id=data.get('session_id'),
            solvent=data.get('solvent'),
            source=data.get('source'),
            spectrometer_identifier=data.get('spectrometer_identifier'),
            state=data.get('state'),
            tags=data.get('tags'),
            temperature_k=data.get('temperature_k'),
            time_shared=data.get('time_shared'),
            title=data.get('title'),
            version=data.get('version'),
            z0_drift_correction=data.get('z0_drift_correction'),
            # Complex objects
            dimensions=[Dimension.from_dict(d) for d in data.get('dimensions', [])] if data.get("dimensions") else None,
            versions=[DatasetVersion.from_dict(client, v) for v in data.get('versions', [])] if data.get("versions") else None,
            # References to other objects
            spectrometer=usnan.models.Spectrometer.from_identifier(client, data.get('spectrometer_identifier')),
            facility=usnan.models.Facility.from_identifier(client, data.get('facility_identifier')),
        )

    @classmethod
    def from_identifier(cls, client: 'usnan.USNANClient', identifier: int) -> 'Dataset':
        return cls(id=identifier, _initialized=False, _client=client)


    def __getattribute__(self, name):
        # Always allow access to private attributes and methods to avoid infinite recursion
        if name.startswith('_'):
            return super().__getattribute__(name)
        # We don't need to initialize to get the ID
        if name == 'id':
            return super().__getattribute__(name)

        # Auto-initialize if not already initialized
        if not super().__getattribute__('_initialized'):
            # Load the full data from the API
            full_spectrometer = super().__getattribute__('_client').datasets.get(super().__getattribute__('id'))
            # Copy all the loaded data to this instance
            for key, value in full_spectrometer.__dict__.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
            super().__setattr__('_initialized', True)

        return super().__getattribute__(name)

    def __repr__(self) -> str:
        """Return a concise representation of the dataset"""
        return f"Dataset('{self.id}')"

    def __str__(self) -> str:
        """Return a detailed string representation of the dataset"""
        parts = []
        
        # Dataset name
        if self.dataset_name:
            parts.append(self.dataset_name)
        
        # Title (if different from dataset_name)
        if self.title and self.title != self.dataset_name:
            parts.append(f"'{self.title}'")
        
        # Time range
        if self.experiment_start_time and self.experiment_end_time:
            parts.append(f"({self.experiment_start_time} - {self.experiment_end_time})")
        elif self.experiment_start_time:
            parts.append(f"(started: {self.experiment_start_time})")
        elif self.experiment_end_time:
            parts.append(f"(ended: {self.experiment_end_time})")
        
        # Version
        if self.version is not None:
            parts.append(f"v{self.version}")
        
        # Publication info
        if self.published_time:
            parts.append(f"published: {self.published_time}")
        
        return " ".join(parts) if parts else f"Dataset {self.id}"

    def save_data(self, location: Union[str,Path]):
        """ Downloads all dataset files (including supplemental data) and saves them to the specified folder.
        The specified folder should either not yet exist or be empty."""

        r = self._client.datasets.download([self.id], location)
