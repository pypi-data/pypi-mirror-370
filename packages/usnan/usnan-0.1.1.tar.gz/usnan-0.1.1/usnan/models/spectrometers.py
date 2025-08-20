from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal

import usnan
from .probes import Probe


@dataclass
class SampleChanger:
    """Represents a sample changer on a spectrometer"""
    model: Optional[str] = None
    vendor: Optional[str] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    num_spinners: Optional[int] = None
    num_96_racks: Optional[int] = None

    def __str__(self) -> str:
        """Return a string representation of the sample changer"""
        parts = []

        if self.vendor and self.model:
            parts.append(f"{self.vendor} {self.model}")
        elif self.vendor:
            parts.append(self.vendor)
        elif self.model:
            parts.append(self.model)
        else:
            parts.append("Sample Changer")

        specs = []
        if self.num_spinners:
            specs.append(f"{self.num_spinners} spinners")
        if self.num_96_racks:
            specs.append(f"{self.num_96_racks} 96-well racks")
        if self.min_temp is not None or self.max_temp is not None:
            temp_range = "Temp: "
            if self.min_temp is not None:
                temp_range += f"{self.min_temp}°C"
            else:
                temp_range += "?"
            temp_range += " to "
            if self.max_temp is not None:
                temp_range += f"{self.max_temp}°C"
            else:
                temp_range += "?"
            specs.append(temp_range)

        if specs:
            parts.append(f"({', '.join(specs)})")

        return " ".join(parts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SampleChanger':
        if data is None:
            return None
        return cls(
            model=data.get('model'),
            vendor=data.get('vendor'),
            min_temp=data.get('min_temp'),
            max_temp=data.get('max_temp'),
            num_spinners=data.get('num_spinners'),
            num_96_racks=data.get('num_96_racks')
        )


@dataclass
class Feature:
    """Represents a software feature"""
    feature: str

    def __str__(self) -> str:
        """Return a string representation of the feature"""
        return self.feature

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feature':
        return cls(feature=data['feature'])


@dataclass
class SoftwareVersion:
    """Represents a software version with installed features"""
    version: str
    features: Optional[List[str]] = None

    def __str__(self) -> str:
        """Return a string representation of the software version"""
        if self.features:
            return f"Version {self.version} (Features: {', '.join(self.features)})"
        return f"Version {self.version}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SoftwareVersion':
        return cls(
            version=data['version'],
            features=[
                f for f in data.get('installed_software', [])
            ] if data.get('installed_software', []) else []
        )


@dataclass
class Software:
    """Represents software installed on a spectrometer"""
    software: str
    versions: Optional[List[SoftwareVersion]] = None

    def __str__(self) -> str:
        """Return a string representation of the software"""
        if self.versions:
            version_strs = [v.version for v in self.versions]
            return f"{self.software} (Versions: {', '.join(version_strs)})"
        return self.software

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Software':
        if data is None:
            return None
        return cls(
            software=data['software'],
            versions=[
                SoftwareVersion.from_dict(v) for v in data.get('versions', [])
            ]
        )


@dataclass
class InstallScheduleRecord:
    """Represents a scheduled probe installation"""
    probe: Optional[Probe] = None
    install_start: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the scheduled installation"""
        return (f"Probe: {self.probe.name}\n"
                f"Install start: {self.install_start}")

    @classmethod
    def from_dict(cls, client: 'usnan.USNANclient', data: Dict[str, Any]) -> 'InstallScheduleRecord':
        return cls(
            probe=Probe.from_identifier(client, data.get('identifier')),
            install_start=data.get('install_start')
        )


@dataclass
class FieldDrift:
    """Represents a field drift measurement"""
    rate: Optional[float] = None
    recorded: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the field drift"""
        parts = []

        if self.rate is not None:
            parts.append(f"Rate: {self.rate}")
        if self.recorded:
            parts.append(f"Recorded: {self.recorded}")

        return " | ".join(parts) if parts else "Field drift measurement"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldDrift':
        return cls(
            rate=data.get('rate'),
            recorded=data.get('recorded')
        )


@dataclass
class Spectrometer:
    """Represents a spectrometer in the system"""
    identifier: str
    name: str = None
    _initialized: bool = False
    _client: 'usnan.USNANClient' = None
    year_commissioned: Optional[int] = None
    status: Optional[Literal["Decommissioned", "Operational", "Under Repair"]] = None
    is_public: Optional[bool] = None
    rates_url: Optional[str] = None
    magnet_vendor: Optional[Literal["Agilent/Varian", "Bruker", "JEOL", "Q One", "Tech MAG"]] = None
    field_strength_mhz: Optional[float] = None
    bore_mm: Optional[float] = None
    is_pumped: Optional[bool] = None
    console_vendor: Optional[Literal["Agilent/Varian", "Bruker", "JEOL", "Q One", "Tech MAG"]] = None
    model: Optional[str] = None
    serial_no: Optional[str] = None
    year_configured: Optional[int] = None
    channel_count: Optional[int] = None
    receiver_count: Optional[int] = None
    operating_system: Optional[Literal["Windows", "RedHat", "CentOS", "Ubuntu", "Alma"]] = None
    version: Optional[str] = None
    sample_changer_id: Optional[int] = None
    facility: 'usnan.models.Facility' = None
    _facility_identifier: Optional[str] = None
    sample_changer: Optional[SampleChanger] = None
    sample_changer_default_temperature_control: Optional[Literal["Cooled", "Heated", "Room Temperature"]] = None
    software: Optional[Software] = None
    installed_probe: Optional[Probe] = None
    compatible_probes: Optional[List[Probe]] = None
    install_schedule: Optional[List[InstallScheduleRecord]] = None
    field_drifts: Optional[List[FieldDrift]] = None

    def __str__(self) -> str:
        """Return a string representation of the spectrometer"""
        lines = []

        # Basic info
        lines.append(f"Spectrometer: {self.name}")
        lines.append(f"Identifier: {self.identifier}")

        if self.status:
            lines.append(f"Status: {self.status}")
        if self.year_commissioned:
            lines.append(f"Commissioned: {self.year_commissioned}")

        # Magnet info
        if self.field_strength_mhz:
            lines.append(f"Field Strength: {self.field_strength_mhz} MHz")

        if self.bore_mm:
            lines.append(f"Bore: {self.bore_mm} mm")
        if self.is_pumped is not None:
            lines.append(f"Pumped: {'Yes' if self.is_pumped else 'No'}")

        # Console info
        if self.console_vendor or self.model:
            console_info = "Console: "
            if self.console_vendor and self.model:
                console_info += f"{self.console_vendor} {self.model}"
            elif self.console_vendor:
                console_info += self.console_vendor
            elif self.model:
                console_info += self.model
            if self.serial_no:
                console_info += f" (S/N: {self.serial_no})"
            lines.append(console_info)

        if self.year_configured:
            lines.append(f"Configured: {self.year_configured}")

        # Channel/receiver info
        if self.channel_count:
            lines.append(f"Channels: {self.channel_count}")
        if self.receiver_count:
            lines.append(f"Receivers: {self.receiver_count}")

        # Software info
        if self.operating_system:
            os_info = f"OS: {self.operating_system}"
            if self.version:
                os_info += f" {self.version}"
            lines.append(os_info)

        if self.software and self.software.software:
            lines.append(f"Software: {self.software.software}")
            if self.software.versions:
                for version in self.software.versions:
                    lines.append(f"  Version: {version.version}")

        # Sample changer
        if self.sample_changer:
            sc_info = "Sample Changer: "
            if self.sample_changer.vendor and self.sample_changer.model:
                sc_info += f"{self.sample_changer.vendor} {self.sample_changer.model}"
            elif self.sample_changer.vendor:
                sc_info += self.sample_changer.vendor
            elif self.sample_changer.model:
                sc_info += self.sample_changer.model
            else:
                sc_info += "Yes"

            if self.sample_changer.num_spinners:
                sc_info += f" ({self.sample_changer.num_spinners} spinners)"
            lines.append(sc_info)

        # Installed probe
        if self.installed_probe:
            probe_info = f"Installed Probe: {self.installed_probe.name}"
            lines.append(probe_info)

        # Compatible probes
        if self.compatible_probes:
            lines.append(f"Compatible Probes:")
            for probe in self.compatible_probes:
                probe_line = f"  {probe.name}"
                lines.append(probe_line)

        # Public access
        if self.is_public is not None:
            lines.append(f"Public Access: {'Yes' if self.is_public else 'No'}")
        if self.rates_url:
            lines.append(f"Rates: {self.rates_url}")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        """Return a concise representation of the spectrometer"""
        return f"Spectrometer('{self.identifier})"

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
            full_spectrometer = super().__getattribute__('_client').spectrometers.get(super().__getattribute__('identifier'))
            # Copy all the loaded data to this instance
            for key, value in full_spectrometer.__dict__.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
            super().__setattr__('_initialized', True)
        
        return super().__getattribute__(name)

    @classmethod
    def from_dict(cls, client: 'usnan.USNANClient', data: Dict[str, Any]) -> 'Spectrometer':
        """Create a Spectrometer instance from API response data"""
        return cls(
            identifier=data['identifier'],
            name=data['name'],
            year_commissioned=data.get('year_commissioned'),
            status=data.get('status'),
            is_public=data.get('is_public'),
            rates_url=data.get('rates_url'),
            magnet_vendor=data.get('magnet_vendor'),
            field_strength_mhz=data.get('field_strength_mhz'),
            bore_mm=data.get('bore_mm'),
            is_pumped=data.get('is_pumped'),
            console_vendor=data.get('console_vendor'),
            model=data.get('model'),
            serial_no=data.get('serial_no'),
            year_configured=data.get('year_configured'),
            channel_count=data.get('channel_count'),
            receiver_count=data.get('receiver_count'),
            operating_system=data.get('operating_system'),
            version=data.get('version'),
            sample_changer_id=data.get('sample_changer_id'),
            facility=usnan.models.Facility.from_identifier(client, data.get('facility_identifier')) if data.get('facility_identifier') else None,
            _facility_identifier=data.get('facility_identifier'),
            sample_changer=SampleChanger.from_dict(data.get('sample_changer')),
            sample_changer_default_temperature_control=data.get('sample_changer_default_temperature_control'),
            software=Software.from_dict(data.get('software')),
            installed_probe=Probe.from_identifier(client, data.get('installed_probe').get('identifier')) if data.get('installed_probe') else None,
            compatible_probes=[
                Probe.from_identifier(client, p.get('identifier')) for p in data.get('compatible_probes', []) if p.get('identifier')
            ],
            install_schedule=[
                InstallScheduleRecord.from_dict(client, i) for i in data.get('install_schedule', [])
            ],
            field_drifts=[
                FieldDrift.from_dict(f) for f in data.get('field_drifts', [])
            ],
            _initialized=True,
            _client=client
        )

    @classmethod
    def from_identifier(cls, client: 'usnan.USNANClient', identifier: str) -> 'Spectrometer':
        return cls(identifier=identifier, _initialized=False, _client=client)
