from dataclasses import dataclass
from functools import cached_property
from typing import Optional, List, Dict, Any, Union, Literal

import usnan
import usnan.models

@dataclass
class Channel:
    """Represents a channel on a probe"""
    ch_number: int
    amplifier_cooled: Optional[bool] = None
    inner_coil: Optional[str] = None
    outer_coil: Optional[str] = None
    min_frequency_nucleus: Optional[float] = None
    max_frequency_nucleus: Optional[float] = None
    broadband: Optional[bool] = None
    nuclei: Optional[List['Nucleus']] = None

    def __str__(self) -> str:
        """Return a string representation of the channel"""
        parts = [f"Channel {self.ch_number}"]

        coils = []
        if self.inner_coil:
            coils.append(f"Inner: {self.inner_coil}")
        if self.outer_coil:
            coils.append(f"Outer: {self.outer_coil}")
        if coils:
            parts.append(f"({', '.join(coils)})")

        if self.broadband:
            parts.append("[Broadband]")

        if self.nuclei:
            nuclei_names = [n.nucleus for n in self.nuclei]
            parts.append(f"Nuclei: {', '.join(nuclei_names)}")

        return " ".join(parts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Channel':
        return cls(
            ch_number=data['ch_number'],
            amplifier_cooled=data.get('amplifier_cooled'),
            inner_coil=data.get('inner_coil'),
            outer_coil=data.get('outer_coil'),
            min_frequency_nucleus=data.get('min_frequency_nucleus'),
            max_frequency_nucleus=data.get('max_frequency_nucleus'),
            broadband=data.get('broadband'),
            nuclei=[Nucleus.from_dict(n) for n in data.get('nuclei', [])] if data.get('nuclei') else []
        )


@dataclass
class Probe:
    """Represents a probe in the system"""
    identifier: str = None
    _initialized: bool = False
    _client: 'usnan.USNANClient' = None
    status: Optional[Literal["Decommissioned", "Operational", "Under Repair"]] = None
    status_detail: Optional[Literal["Solid State", "Solution"]] = None
    kind: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    cooling: Optional[Literal["Helium", "Nitrogen", "Room Temp"]] = None
    sample_diameter: Optional[float] = None
    max_spinning_rate: Optional[float] = None
    gradient: Optional[bool] = None
    x_gradient_field_strength: Optional[float] = None
    y_gradient_field_strength: Optional[float] = None
    z_gradient_field_strength: Optional[float] = None
    h1_fieldstrength_mhz: Optional[float] = None
    min_temperature_c: Optional[float] = None
    max_temperature_c: Optional[float] = None
    facility_identifier: Optional[str] = None
    facility_short_name: Optional[str] = None
    facility_long_name: Optional[str] = None
    channels: Optional[List[Channel]] = None

    installed_on_spectrometer: Optional['usnan.models.Spectrometer'] = None
    installed_on_spectrometer_since: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the probe"""
        lines = []

        # Basic info
        lines.append(f"Probe: {self.name}")
        lines.append(f"Identifier: {self.identifier}")
        if self.vendor and self.model:
            lines.append(f"Model: {self.vendor} {self.model}")
        elif self.vendor:
            lines.append(f"Vendor: {self.vendor}")
        elif self.model:
            lines.append(f"Model: {self.model}")

        if self.serial_number:
            lines.append(f"Serial: {self.serial_number}")
        if self.status:
            lines.append(f"Status: {self.status}")
        if self.status_detail:
            lines.append(f"Status Detail: {self.status_detail}")
        if self.kind:
            lines.append(f"Type: {self.kind}")

        # Technical specs
        if self.sample_diameter:
            lines.append(f"Sample Diameter: {self.sample_diameter} mm")
        if self.cooling:
            lines.append(f"Cooling: {self.cooling}")
        if self.max_spinning_rate:
            lines.append(f"Max Spinning Rate: {self.max_spinning_rate} Hz")
        if self.h1_fieldstrength_mhz:
            lines.append(f"1H Field Strength: {self.h1_fieldstrength_mhz} MHz")

        # Temperature range
        if self.min_temperature_c is not None or self.max_temperature_c is not None:
            temp_range = "Temperature Range: "
            if self.min_temperature_c is not None:
                temp_range += f"{self.min_temperature_c}°C"
            else:
                temp_range += "?"
            temp_range += " to "
            if self.max_temperature_c is not None:
                temp_range += f"{self.max_temperature_c}°C"
            else:
                temp_range += "?"
            lines.append(temp_range)

        # Gradient info
        if self.gradient:
            grad_info = "Gradient: Yes"
            grad_strengths = []
            if self.x_gradient_field_strength:
                grad_strengths.append(f"X: {self.x_gradient_field_strength}")
            if self.y_gradient_field_strength:
                grad_strengths.append(f"Y: {self.y_gradient_field_strength}")
            if self.z_gradient_field_strength:
                grad_strengths.append(f"Z: {self.z_gradient_field_strength}")
            if grad_strengths:
                grad_info += f" ({', '.join(grad_strengths)})"
            lines.append(grad_info)

        # Facility info
        if self.facility_short_name or self.facility_long_name:
            facility_name = self.facility_short_name or self.facility_long_name
            lines.append(f"Facility: {facility_name}")

        # Installation info
        if self.installed_on_spectrometer:
            install_info = f"Installed on: {self.installed_on_spectrometer.name}"
            if self.installed_on_spectrometer_since:
                install_info += f" since {self.installed_on_spectrometer_since}"
            lines.append(install_info)

        # Channels
        if self.channels:
            lines.append(f"Channels ({len(self.channels)}):")
            for channel in self.channels:
                ch_line = f"  Ch {channel.ch_number}"
                if channel.inner_coil or channel.outer_coil:
                    coils = []
                    if channel.inner_coil:
                        coils.append(f"Inner: {channel.inner_coil}")
                    if channel.outer_coil:
                        coils.append(f"Outer: {channel.outer_coil}")
                    ch_line += f" ({', '.join(coils)})"
                if channel.broadband:
                    ch_line += " [Broadband]"
                lines.append(ch_line)

                # Show nuclei for this channel
                if channel.nuclei:
                    for nucleus in channel.nuclei:
                        lines.append(f"    {nucleus.nucleus}")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        """Return a concise representation of the probe using naming logic"""
        return f"Probe('{self.identifier}')"

    @cached_property
    def name(self) -> str:
        """Return a concise representation of the probe using naming logic"""
        def get_nuclei_from_channels(channels):
            """Get nuclei string from channels"""
            if not channels:
                return ''
            
            response = ''
            for channel in channels:
                if channel.broadband:
                    response += 'BB'
                else:
                    if channel.nuclei and len(channel.nuclei) > 2:
                        response += 'BB'
                    else:
                        if channel.nuclei:
                            nuclei_names = [nucleus.nucleus for nucleus in channel.nuclei]
                            response += '/'.join(nuclei_names)
                response += '|'
            
            # Remove trailing '|'
            if response.endswith('|'):
                response = response[:-1]
            return response

        # Determine cryo type
        cryo = ' cryoprobe ' if self.cooling and self.cooling.lower() in ['helium', 'nitrogen'] else ' '
        
        # Get nuclei from inner and outer coils
        inner_channels = [ch for ch in (self.channels or []) if ch.inner_coil]
        outer_channels = [ch for ch in (self.channels or []) if ch.outer_coil]
        
        inner_nuclei = get_nuclei_from_channels(inner_channels)
        outer_nuclei = get_nuclei_from_channels(outer_channels)
        
        if outer_nuclei:
            outer_nuclei = f'({outer_nuclei})'
        
        # Build the name
        sample_diameter = self.sample_diameter or '?'
        model = self.model or ''
        name = f"{sample_diameter}mm{cryo}{model} {inner_nuclei}{outer_nuclei}"
        
        if self.gradient and str(self.gradient).lower() not in ['none', 'false']:
            name += f' {self.gradient}'
        
        return name.strip()

    def __getattribute__(self, name):
        # Always allow access to private attributes and methods to avoid infinite recursion
        if name.startswith('_'):
            return super().__getattribute__(name)
        # We don't need to initialize to get the identifier
        if name == 'identifier':
            return super().__getattribute__(name)
        
        # Auto-initialize if not already initialized
        if not super().__getattribute__('_initialized'):
            # Load the full data from the API
            full_probe = super().__getattribute__('_client').probes.get(super().__getattribute__('identifier'))
            # Copy all the loaded data to this instance
            for key, value in full_probe.__dict__.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
            super().__setattr__('_initialized', True)
        
        return super().__getattribute__(name)

    @classmethod
    def from_dict(cls, client: 'usnan.USNANClient', data: Dict[str, Any]) -> 'Probe':
        """Create a Probe instance from API response data"""
        return cls(
            identifier=data['identifier'],
            status=data.get('status'),
            status_detail=data.get('status_detail'),
            kind=data.get('kind'),
            vendor=data.get('vendor'),
            model=data.get('model'),
            serial_number=data.get('serial_number'),
            cooling=data.get('cooling'),
            sample_diameter=data.get('sample_diameter'),
            max_spinning_rate=data.get('max_spinning_rate'),
            gradient=data.get('gradient'),
            x_gradient_field_strength=data.get('x_gradient_field_strength'),
            y_gradient_field_strength=data.get('y_gradient_field_strength'),
            z_gradient_field_strength=data.get('z_gradient_field_strength'),
            h1_fieldstrength_mhz=data.get('h1_fieldstrength_mhz'),
            min_temperature_c=data.get('min_temperature_c'),
            max_temperature_c=data.get('max_temperature_c'),
            facility_identifier=data.get('facility_identifier'),
            facility_short_name=data.get('facility_short_name'),
            facility_long_name=data.get('facility_long_name'),
            installed_on_spectrometer=usnan.models.Spectrometer.from_identifier(identifier=data.get('installed_on').get('spectrometer_identifier'), client=client) if data.get('installed_on').get('spectrometer_identifier') else None,
            installed_on_spectrometer_since=data.get('installed_on').get('install_start'),
            channels=[Channel.from_dict(c) for c in data.get('channels', [])] if data.get('channels') else [],
            _initialized=True,
            _client=client
        )

    @classmethod
    def from_identifier(cls, client: 'usnan.USNANClient', identifier: str) -> 'Probe':
        probe = cls(identifier=identifier, _initialized=False, _client=client)
        return probe


@dataclass
class Nucleus:
    """Represents a nucleus with sensitivity measurements"""
    nucleus: str
    sensitivity_measurements: Optional[List['usnan.models.SensitivityMeasurement']] = None

    def __str__(self) -> str:
        """Return a string representation of the nucleus"""
        if self.sensitivity_measurements:
            return f"{self.nucleus} ({len(self.sensitivity_measurements)} measurements)"
        return self.nucleus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Nucleus':
        return cls(
            nucleus=data['nucleus'],
            sensitivity_measurements=[
                SensitivityMeasurement.from_dict(sm)
                for sm in data.get('sensitivity_measurements', [])
            ] if data.get('sensitivity_measurements') else []
        )

@dataclass
class SensitivityMeasurement:
    """Represents a sensitivity measurement for a nucleus"""
    is_user: Optional[bool] = None
    sensitivity: Optional[float] = None
    measurement_date: Optional[str] = None
    name: Optional[str] = None
    composition: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the sensitivity measurement"""
        parts = []

        if self.sensitivity is not None:
            parts.append(f"Sensitivity: {self.sensitivity}")
        if self.measurement_date:
            parts.append(f"Date: {self.measurement_date}")
        if self.name:
            parts.append(f"Sample: {self.name}")
        if self.is_user is not None:
            parts.append(f"User measurement: {'Yes' if self.is_user else 'No'}")

        return " | ".join(parts) if parts else "Sensitivity measurement"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensitivityMeasurement':
        return cls(
            is_user=data.get('is_user'),
            sensitivity=data.get('sensitivity'),
            measurement_date=data.get('measurement_date'),
            name=data.get('name'),
            composition=data.get('composition')
        )
