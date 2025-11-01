from unittest.mock import Mock, patch

import numpy as np
import pytest
import xarray as xr

from src.etl.processing_layer import DataProcessor


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def processor(mock_client):
    return DataProcessor(base_path="/fake/path", client=mock_client)


@pytest.fixture
def sample_dataset():
    # Create a test dataset
    lat = np.array([45.0, 45.1], dtype=np.float32)
    lon = np.array([9.0, 9.1], dtype=np.float32)
    time = np.array(["2024-01-01", "2024-01-02"], dtype="datetime64[ns]")
    data = np.random.rand(2, 2, 2)  # (time, lat, lon)

    return xr.Dataset(
        data_vars={"tp": (["time", "latitude", "longitude"], data)},
        coords={
            "time": time,
            "latitude": lat,
            "longitude": lon,
        },
    )


@patch("xarray.open_mfdataset")
def test_read_data(mock_open_mfdataset, processor, sample_dataset):
    """Test data reading"""
    mock_open_mfdataset.return_value = sample_dataset
    result = processor.read_data()

    assert isinstance(result, xr.Dataset)
    mock_open_mfdataset.assert_called_once()


def test_calculate_h3_indices(processor):
    """Test H3 indices calculation"""
    lat = np.array([45.0], dtype=np.float32)
    lon = np.array([9.0], dtype=np.float32)
    resolution = 8

    result = processor._calculate_h3_indices(lat, lon, resolution)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 1)


def test_create_h3_array(processor):
    """Test H3 array creation"""
    lat = np.array([45.0], dtype=np.float32)
    lon = np.array([9.0], dtype=np.float32)
    resolution = 8

    index_name, h3_array = processor._create_h3_array(lat, lon, resolution)

    assert index_name == "h3_resolution_8"
    assert isinstance(h3_array, xr.DataArray)
    assert h3_array.shape == (1, 1)


def test_update_schema_with_h3_fields(processor):
    """Test schema update with H3 fields"""
    initial_field_count = len(processor.schema)
    desired_resolution = [4, 8]

    processor._update_schema_with_h3_fields(desired_resolution)

    assert len(processor.schema) == initial_field_count + 2
    assert "h3_resolution_4" in processor.schema.names
    assert "h3_resolution_8" in processor.schema.names


def test_transform_data(processor, sample_dataset):
    """Test della trasformazione dei dati"""
    processor.ds = sample_dataset
    desired_resolution = [8]

    result = processor.transform_data(desired_resolution)

    assert isinstance(result, xr.Dataset)
    assert "h3_resolution_8" in result.coords
