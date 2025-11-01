import pytest
from google.cloud.storage import Client  # type: ignore

from src.etl.ingestion_layer import DataIngestionManager


def test_generate_paths():
    bucket_name = "test-bucket"
    base_path = "raw/date-variable-single_level/{date_str}/total_precipitation/surface.nc"
    storage_client = Client.create_anonymous_client()
    manager = DataIngestionManager(bucket_name, base_path, storage_client)

    # Generate paths for a 3-day interval
    paths = manager.generate_paths("2024-01-01", "2024-01-03")
    expected_paths = [
        "raw/date-variable-single_level/2024/01/01/total_precipitation/surface.nc",
        "raw/date-variable-single_level/2024/01/02/total_precipitation/surface.nc",
        "raw/date-variable-single_level/2024/01/03/total_precipitation/surface.nc",
    ]
    assert paths == expected_paths

    # Verify custom partition format
    custom_paths = manager.generate_paths("2024-01-01", "2024-01-01", partition_format="%Y-%m-%d")
    expected_custom_path = ["raw/date-variable-single_level/2024-01-01/total_precipitation/surface.nc"]
    assert custom_paths == expected_custom_path


def test_generate_paths_invalid_dates():
    bucket_name = "test-bucket"
    base_path = "raw/date-variable-single_level/{date_str}/total_precipitation/surface.nc"
    storage_client = Client.create_anonymous_client()
    manager = DataIngestionManager(bucket_name, base_path, storage_client)

    # End date earlier than start date
    with pytest.raises(ValueError) as exc_info:
        manager.generate_paths("2024-01-03", "2024-01-01")
    assert str(exc_info.value) == "End date (2024-01-01) cannot be earlier than start date (2024-01-03)."

    # Invalid date format
    with pytest.raises(ValueError):
        manager.generate_paths("2024/01/01", "2024-01-03")

    # Non-existent date
    with pytest.raises(ValueError):
        manager.generate_paths("2024-02-30", "2024-03-01")

    # Completely invalid date
    with pytest.raises(ValueError):
        manager.generate_paths("invalid_date", "2024-01-03")
