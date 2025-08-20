"""
Test file for USNANClient datasets functionality.
"""

import pytest
import usnan


class TestDatasetRetrieval:
    """Tests for individual dataset retrieval"""

    def test_get_single_dataset(self):
        """Ensure we can get a single dataset by ID."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        d = client.datasets.get(363067)
        assert isinstance(d, usnan.models.Dataset)
        assert isinstance(d.facility, usnan.models.Facility)
        assert isinstance(d.spectrometer, usnan.models.Spectrometer)
        assert isinstance(d.spectrometer.installed_probe, usnan.models.Probe) or d.spectrometer.installed_probe is None

    def test_get_dataset_with_string_id(self):
        """Test that string IDs are handled correctly."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        with pytest.raises(TypeError):
            client.datasets.get("363067")

    def test_get_nonexistent_dataset(self):
        """Test that requesting a non-existent dataset raises appropriate error.
        301 is known not to exist. """
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        with pytest.raises(KeyError):
            client.datasets.get(301)

    def test_dataset_lazy_loading(self):
        """Test that datasets can be created with minimal data and load on access."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        # Create a dataset with just an ID (not initialized)
        d = usnan.models.Dataset.from_identifier(client, 363067)
        assert d.id == 363067
        assert not d._initialized
        
        # Accessing a property should trigger initialization
        assert d.title is not None
        assert d._initialized


class TestDatasetSearch:
    """Tests for dataset searching functionality"""

    def test_basic_search(self):
        """Ensure that getting datasets via search works."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        search_config = usnan.models.SearchConfig().add_filter('is_knowledgebase', value=True, match_mode='equals')
        results = client.datasets.search(search_config)

        count = 0
        for dataset in results:
            assert isinstance(dataset, usnan.models.Dataset)
            count += 1
            if count + 1 == search_config.records: # Don't fetch a new batch
                break

        assert count > 0

    def test_search_pagination(self):
        """Test that search handles pagination correctly."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        search_config = usnan.models.SearchConfig(records=49).add_filter('is_knowledgebase', value=True, match_mode='equals')
        results = client.datasets.search(search_config)

        # Test that we can get more than the initial batch size
        count = 0
        for dataset in results:
            count += 1
            if count >= 50:  # Test pagination by going beyond initial batch
                break

        assert count >= 50

        # Ensure that the fetcher is fetching more records after exhausting the initial batch
        assert search_config.records > 25

    def test_search_with_multiple_filters(self):
        """Test search with multiple filters."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        search_config = (usnan.models.SearchConfig(records=1)
                         .add_filter('is_knowledgebase', value=True, match_mode='equals')
                         .add_filter('num_dimension', value=2, match_mode='equals'))
        
        results = client.datasets.search(search_config)
        
        # Verify we get results and they match our criteria
        found_results = False
        for dataset in results:
            found_results = True
            assert dataset.is_knowledgebase is True
            assert dataset.num_dimension == 2
            break  # Just check first result for performance
        
        # We should find at least some results
        assert found_results

    def test_search_empty_results(self):
        """Test search that returns no results."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        # Use a filter that should return no results
        search_config = usnan.models.SearchConfig().add_filter('dataset_name', value='nonexistent_dataset_12345', match_mode='equals')
        results = client.datasets.search(search_config)

        count = 0
        for dataset in results:
            count += 1

        assert count == 0

    def test_search_generator_behavior(self):
        """Test that search returns a proper generator."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        search_config = usnan.models.SearchConfig(records=1).add_filter('is_knowledgebase', value=True, match_mode='equals')
        results = client.datasets.search(search_config)

        # Should be a generator
        assert hasattr(results, '__iter__')
        assert hasattr(results, '__next__')

        # Should be able to iterate multiple times by creating new searches
        first_result = next(results)
        assert isinstance(first_result, usnan.models.Dataset)


class TestDatasetModel:
    """Tests for Dataset model functionality"""

    def test_dataset_attributes(self):
        """Test that dataset has expected attributes."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        d = client.datasets.get(363067)
        
        # Test that basic attributes exist
        assert hasattr(d, 'id')
        assert hasattr(d, 'dataset_name')
        assert hasattr(d, 'experiment_name')
        assert hasattr(d, 'facility')
        assert hasattr(d, 'spectrometer')
        
        # Test that ID is set correctly
        assert d.id == 363067

    def test_dataset_dimensions(self):
        """Test dataset dimensions functionality."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        d = client.datasets.get(363067)
        
        if d.dimensions:
            for dim in d.dimensions:
                assert isinstance(dim, usnan.models.datasets.Dimension)
                assert hasattr(dim, 'dimension')
                assert hasattr(dim, 'nucleus')
                assert hasattr(dim, 'is_direct')

    def test_dataset_versions(self):
        """Test dataset versions functionality."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        d = client.datasets.get(363067)
        
        if d.versions:
            for version in d.versions:
                assert isinstance(version, usnan.models.datasets.DatasetVersion)
                assert isinstance(version.dataset, usnan.models.Dataset)
                assert version.dataset._initialized is False
                assert hasattr(version, 'id')


class TestErrorHandling:
    """Tests for error handling in dataset operations"""

    def test_invalid_search_filter(self):
        """Test that invalid filter names raise RuntimeError."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')

        with pytest.raises(ValueError):
            usnan.models.SearchConfig().add_filter('is_knowlsedgebase', value=True, match_mode='equals')

    def test_mismatched_filter_operators(self):
        """Test that mismatched filters cannot be applied."""
        with pytest.raises(ValueError):
            usnan.models.SearchConfig().add_filter('test', value=True, operator='OR').add_filter('test', value=True, operator='AND')

    def test_invalid_dataset_id_type(self):
        """Test handling of invalid dataset ID types."""
        client = usnan.USNANClient('https://dev.api.nmrhub.org')
        
        with pytest.raises(TypeError):
            client.datasets.get(None)


class TestSearchConfiguration:
    """Tests for search configuration functionality"""

    def test_search_config_cloning(self):
        """Test that search config can be cloned properly."""
        original = usnan.models.SearchConfig().add_filter('is_knowledgebase', value=True, match_mode='equals')
        cloned = original.clone()
        
        # Should be different objects
        assert original is not cloned
        
        # But should have same configuration
        assert original.build() == cloned.build()

    def test_search_config_offset_and_records(self):
        """Test search config offset and records parameters."""
        config = usnan.models.SearchConfig()
        
        # Test default values
        built_config = config.build()
        assert 'offset' in built_config and 'records' in built_config
        
        # Test that offset can be modified
        config.offset = 10
        config.records = 50
        built_config = config.build()
        
        # The exact parameter names might vary, but the values should be set
        assert config.offset == 10
        assert config.records == 50

