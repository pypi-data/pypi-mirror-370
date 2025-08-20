"""
Test file for USNANClient probes functionality.
"""

import usnan


def test_get_probes():
    """Test that get_probes returns expected values. """

    client = usnan.USNANClient('https://dev.api.nmrhub.org')
    probes = client.probes.list()

    # Assert we got a list with at least one probe
    assert isinstance(probes, list)
    assert len(probes) >= 1
    assert all([_._initialized == True for _ in probes])
    assert isinstance(probes[0], usnan.models.Probe)

    # Ensure that we can get a probe by ID
    first_probe = probes[0]
    assert client.probes.get(first_probe.identifier) == first_probe

    # Ensure that we can look up the spectrometer for the probe
    for probe in probes:
        if probe.installed_on_spectrometer_since is not None:
            assert isinstance(probe.installed_on_spectrometer, usnan.models.Spectrometer)

