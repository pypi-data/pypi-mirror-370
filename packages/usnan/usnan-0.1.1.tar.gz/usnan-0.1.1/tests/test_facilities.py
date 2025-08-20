"""
Test file for USNANClient facility functionality.
"""

import usnan


def test_get_facilities():
    """Test that get_facilities returns expected values. """

    client = usnan.USNANClient('https://dev.api.nmrhub.org')
    facilities = client.facilities.list()

    # Assert we got a list with at least one facility
    assert isinstance(facilities, list)
    assert len(facilities) >= 1
    assert all([_._initialized == True for _ in facilities])
    assert isinstance(facilities[0], usnan.models.Facility)

    # Ensure that we can get a facility by ID
    first_facility = facilities[0]
    assert client.facilities.get(first_facility.identifier) == first_facility

    # Ensure that we can look up spectrometers for the facility
    uconn = client.facilities.get('UCHC-Mullen')
    assert len(uconn.spectrometers) > 0

    assert(uconn.spectrometers[0].name is not None)
