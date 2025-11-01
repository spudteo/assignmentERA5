from datetime import datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (DoubleType, StringType, StructField, StructType,
                               TimestampType)

from src.etl.query_layer import QueryExample


@pytest.fixture
def spark():
    return SparkSession.builder.appName("test").master("local[*]").getOrCreate()


@pytest.fixture
def mock_data(spark):
    # Define the schema
    schema = StructType(
        [
            StructField("h3_resolution_8", StringType(), True),
            StructField("h3_resolution_4", StringType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("time", TimestampType(), True),
            StructField("tp", DoubleType(), True),
        ]
    )

    # Create test data
    data = [
        ("883830333233", "843430333233", 90.0, 0.0, datetime(2022, 3, 31), 4.32),
        ("883830333233", "843430333233", 90.0, 0.0, datetime(2022, 4, 1), 5.1),
        ("883830333234", "843430333234", 89.0, 1.0, datetime(2022, 3, 31), 3.2),
        ("883830333234", "843430333234", 89.0, 1.0, datetime(2022, 4, 1), 2.8),
    ]

    return spark.createDataFrame(data, schema)


def test_analyze_h3_time_combined(spark, mock_data, tmp_path):
    temp_parquet = str(tmp_path / "test.parquet")
    mock_data.write.parquet(temp_parquet)

    # Initialize the class with mock DataFrame
    query_example = QueryExample(temp_parquet)

    # Execute the method to test
    result = query_example.analyze_h3_time_combined(resolution=8, start_date="2022-03-31", end_date="2022-04-01")

    # Verify the results
    result_rows = result.collect()

    # Test number of rows (2 h3 index * 2 date = 4 rows)
    assert len(result_rows) == 4

    # Test columns
    expected_columns = {"h3_resolution_8", "date", "tp_avg", "tp_max", "tp_min"}
    assert set(result.columns) == expected_columns
