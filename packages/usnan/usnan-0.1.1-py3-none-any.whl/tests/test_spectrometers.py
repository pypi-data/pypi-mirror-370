"""
Test file for USNANClient spectrometers functionality.
"""

import usnan


def test_get_spectrometers():
    """Test that get_spectrometers returns expected values. """

    client = usnan.USNANClient('https://dev.api.nmrhub.org')
    spectrometers = client.spectrometers.list()

    # Assert we got a list with at least one spectrometer
    assert isinstance(spectrometers, list)
    assert len(spectrometers) >= 1
    assert all([_._initialized == True for _ in spectrometers])
    assert isinstance(spectrometers[0], usnan.models.Spectrometer)

    # Ensure that we can get a spectrometer by ID
    first_spectrometer = spectrometers[0]
    assert client.spectrometers.get(first_spectrometer.identifier) == first_spectrometer

    # Ensure that we can look up spectrometers for the spectrometer
    test = client.spectrometers.get(spectrometers[0].identifier)
    assert isinstance(test, usnan.models.Spectrometer)

