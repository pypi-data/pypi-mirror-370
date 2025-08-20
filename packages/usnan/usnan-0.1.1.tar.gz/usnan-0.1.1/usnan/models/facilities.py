import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Literal

import usnan


def _format_roles_responsibilities(roles: List[str]) -> str:
    """Convert CamelCase string to space-separated words"""

    # Insert space before uppercase letters that follow lowercase letters or digits
    return ", ".join([re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', role) for role in roles])


@dataclass
class Service:
    """Represents a service offered by a facility"""
    service: Literal["Analysis", "Data Processing", "Experiment Setup", "Remote Access", "Rotor Packing", "Sample Preparation", "Self Service", "Shipping and Handling", "Consultation", "Training"]
    description: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the service"""
        if self.description:
            return f"{self.service}: {self.description}"
        return self.service


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Service':
        return cls(
            service=data['service'],
            description=data.get('description')
        )


@dataclass
class Webpage:
    """Represents a webpage associated with a facility"""
    urltype: Literal["Contact", "Facility Access", "Overview", "Policy", "Rates", "Research", "Service", "Spectrometers"]
    url: str

    def __str__(self) -> str:
        """Return a string representation of the webpage"""
        return f"{self.urltype}: {self.url}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Webpage':
        return cls(
            urltype=data['urltype'],
            url=data['url']
        )


@dataclass
class Staff:
    """Represents a staff member at a facility"""
    first_name: str
    last_name: str
    middle_initial: Optional[str] = None
    work_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    email: Optional[str] = None
    roles: Optional[List[Literal["Administrator", "Director", "Engineer", "FacilityManager", "Researcher", "Technician", "Approver"]]] = None
    responsibilities: Optional[List[Literal["Administrator", "Director", "Engineer", "FacilityManager", "Researcher", "Technician", "Approver"]]] = None
    expertise: Optional[List[Literal["Bruker", "DNA/RNA", "Material", "Metabolomics", "Protein", "Pulse Sequence Programming", "Rotor Packing", "Small Molecule", "Solid State", "Solution", "Varian", "Carbohydrates"]]] = None

    def __str__(self) -> str:
        """Return a string representation of the staff member"""
        name = f"{self.first_name} {self.last_name}"
        if self.middle_initial:
            name = f"{self.first_name} {self.middle_initial}. {self.last_name}"

        details = []
        if self.email:
            details.append(f"Email: {self.email}")
        if self.roles:
            details.append(f"Roles: {_format_roles_responsibilities(self.roles)}")
        if self.responsibilities:
            details.append(f"Responsibilities: {_format_roles_responsibilities(self.responsibilities)}")
        if self.work_phone:
            details.append(f"Phone: {self.work_phone}")

        if details:
            return f"{name} ({' | '.join(details)})"
        return name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Staff':
        return cls(
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_initial=data.get('middle_initial'),
            work_phone=data.get('work_phone'),
            mobile_phone=data.get('mobile_phone'),
            email=data.get('email'),
            roles=data.get('roles'),
            responsibilities=data.get('responsibilities'),
            expertise=data.get('expertise')
        )


@dataclass
class Contact:
    """Represents a contact for a facility"""
    name: str
    work_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    email: Optional[str] = None
    details: Optional[str] = None
    responsibilities: Optional[List[Literal["Administrative Services", "Equipment Maintenance", "Experiment Support", "Sample Shipping and Handling", "Scheduling"]]] = None

    def __str__(self) -> str:
        """Return a string representation of the contact"""
        contact_info = []

        if self.email:
            contact_info.append(f"Email: {self.email}")
        if self.work_phone:
            contact_info.append(f"Phone: {self.work_phone}")
        if self.responsibilities:
            contact_info.append(f"Responsibilities: {_format_roles_responsibilities(self.responsibilities)}")

        return f"{self.name} ({' | '.join(contact_info)})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        return cls(
            name=data['name'],
            work_phone=data.get('work_phone'),
            mobile_phone=data.get('mobile_phone'),
            email=data.get('email'),
            details=data.get('details'),
            responsibilities=data.get('responsibilities')
        )


@dataclass
class Address:
    """Represents an address for a facility"""
    address_type: List[Literal["Physical", "Mailing", "Shipping"]]
    address1: str
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    zipcode_ext: Optional[str] = None
    country: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the address"""
        parts = [self.address1]
        if self.address2:
            parts.append(self.address2)
        if self.address3:
            parts.append(self.address3)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zipcode:
            zipcode_str = self.zipcode
            if self.zipcode_ext:
                zipcode_str += f"-{self.zipcode_ext}"
            parts.append(zipcode_str)
        if self.country:
            parts.append(self.country)

        return f"{', '.join(self.address_type)}: {', '.join(parts)}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        return cls(
            address_type=data['address_type'],
            address1=data['address1'],
            address2=data.get('address2'),
            address3=data.get('address3'),
            city=data.get('city'),
            state=data.get('state'),
            zipcode=data.get('zipcode'),
            zipcode_ext=data.get('zipcode_ext'),
            country=data.get('country')
        )


@dataclass
class Facility:
    """Represents a facility in the system"""
    identifier: str
    long_name: str
    _initialized: bool = False
    _client: 'usnan.USNANClient' = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    institution: Optional[str] = None
    url: Optional[str] = None
    color: Optional[str] = None
    logo: Optional[str] = None
    services: Optional[List[Service]] = None
    webpages: Optional[List[Webpage]] = None
    staff: Optional[List[Staff]] = None
    contacts: Optional[List[Contact]] = None
    addresses: Optional[List[Address]] = None
    spectrometers: List['usnan.models.Spectrometer'] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the facility"""
        lines = []

        # Basic info
        lines.append(f"Facility: {self.long_name}")
        if self.short_name:
            lines.append(f"Short Name: {self.short_name}")
        if self.identifier:
            lines.append(f"Identifier: {self.identifier}")
        if self.institution:
            lines.append(f"Institution: {self.institution}")
        if self.url:
            lines.append(f"URL: {self.url}")
        if self.description:
            lines.append(f"Description: {self.description}")

        # Services
        if self.services:
            lines.append(f"Services:")
            for service in self.services:
                lines.append(f"  {service}")

        # Addresses
        if self.addresses:
            lines.append(f"Addresses:")
            for addr in self.addresses:
                lines.append(f"  {addr}")

        # Contacts
        if self.contacts:
            lines.append(f"Contacts:")
            for contact in self.contacts:
                lines.append(f"  {str(contact)}")

        # Staff
        if self.staff:
            lines.append(f"Staff:")
            for staff_member in self.staff:
                lines.append(f"  {str(staff_member)}")

        # Webpages
        if self.webpages:
            lines.append(f"Webpages:")
            for webpage in self.webpages:
                lines.append(f"  {webpage}")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        """Return a concise representation of the facility"""
        return f"Facility('{self.identifier}')"

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
            full_facility = super().__getattribute__('_client').facilities.get(super().__getattribute__('identifier'))
            # Copy all the loaded data to this instance
            for key, value in full_facility.__dict__.items():
                if not key.startswith('_'):
                    setattr(self, key, value)
            super().__setattr__('_initialized', True)
        
        return super().__getattribute__(name)

    @classmethod
    def from_dict(cls, client: 'usnan.USNANClient', data: Dict[str, Any]) -> 'Facility':
        """Create a Facility instance from API response data"""
        return cls(
            identifier=data['identifier'],
            long_name=data['long_name'],
            short_name=data.get('short_name'),
            description=data.get('description'),
            institution=data.get('institution'),
            url=data.get('url'),
            color=data.get('color'),
            logo=data.get('logo'),
            services=[Service.from_dict(s) for s in data.get('services', [])],
            webpages=[Webpage.from_dict(w) for w in data.get('webpages', [])],
            staff=[Staff.from_dict(s) for s in data.get('staff', [])],
            contacts=[Contact.from_dict(c) for c in data.get('contacts', [])],
            addresses=[Address.from_dict(a) for a in data.get('addresses', [])],
            spectrometers=[s for s in client.spectrometers.list() if s._facility_identifier == data['identifier']],
            _initialized=True,
            _client=client
        )

    @classmethod
    def from_identifier(cls, client: 'usnan.USNANClient', identifier: str) -> 'Facility':
        return cls(identifier=identifier, long_name='', _initialized=False, _client=client)
