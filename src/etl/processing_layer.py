import glob
import logging
import os
import time
from typing import Any

import h3  # type: ignore
import numpy as np
import numpy.typing as npt
import pyarrow as pa  # type: ignore
import xarray as xr
from dask.distributed import Client

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, base_path: str, client: Client) -> None:
        self.base_path = base_path
        self.client = client

        # Base schema
        self.schema = pa.schema(
            [
                ("latitude", pa.float32()),
                ("longitude", pa.float32()),
                ("time", pa.timestamp("ms")),
                ("tp", pa.float64()),
            ]
        )
        logger.debug("Base schema initialized")

    def read_data(self) -> xr.Dataset:
        """Reads NetCDF files and returns an xarray dataset"""
        logger.info("Starting NetCDF files reading")
        files = glob.glob(os.path.join(self.base_path, "**/*.nc"), recursive=True)
        logger.debug(f"Found {len(files)} files to process")

        self.ds = xr.open_mfdataset(files, engine="netcdf4", parallel=True, combine="by_coords")
        logger.info("NetCDF files reading completed")
        return self.ds

    def _calculate_h3_indices(
        self,
        latitude: npt.NDArray[np.float32],
        longitude: npt.NDArray[np.float32],
        resolution: int,
    ) -> npt.NDArray[Any]:
        """Calculate H3 indices for given coordinates"""
        h3_indices = np.zeros((len(latitude), len(longitude)), dtype=object)

        for i, lat in enumerate(latitude):
            for j, lon in enumerate(longitude):
                h3_indices[i, j] = h3.latlng_to_cell(lat, lon, resolution)

        return h3_indices

    def _create_h3_array(
        self,
        latitude: npt.NDArray[np.float32],
        longitude: npt.NDArray[np.float32],
        resolution: int,
    ) -> tuple[str, xr.DataArray]:
        """Create xarray DataArray with H3 indices for a given resolution

        Args:
            latitude (array): Latitude array
            longitude (array): Longitude array
            resolution (int): H3 resolution to apply

        Returns:
            tuple: (index name, xarray DataArray with H3 indices)
        """
        h3_indices = self._calculate_h3_indices(latitude, longitude, resolution)
        index_name = f"h3_resolution_{resolution}"

        h3_array = xr.DataArray(h3_indices, coords=[latitude, longitude], dims=["latitude", "longitude"])
        h3_array = h3_array.persist()

        return index_name, h3_array

    def _update_schema_with_h3_fields(self, desired_resolution: list[int]) -> None:
        """Update schema with H3 fields for specified resolutions

        Args:
            desired_resolution (list): List of H3 resolutions to add to the schema
        """
        fields = list(self.schema)
        for resolution in desired_resolution:
            index_name = f"h3_resolution_{resolution}"
            fields.insert(0, pa.field(index_name, pa.binary(15)))
        self.schema = pa.schema(fields)

    def transform_data(self, desired_resolution: list[int]) -> xr.Dataset:
        """Applies H3 transformation to data for multiple resolutions"""
        logger.info(f"Starting data transformation for resolutions: {desired_resolution}")
        longitude = self.ds.longitude
        latitude = self.ds.latitude

        logger.debug("Computing H3 indices")
        h3_coords = dict(
            (index_name, h3_array)
            for index_name, h3_array in (
                self._create_h3_array(latitude, longitude, resolution) for resolution in desired_resolution
            )
        )

        self._update_schema_with_h3_fields(desired_resolution)
        logger.debug("Schema updated with new H3 fields")

        self.transformed_data = self.ds.assign_coords(h3_coords)
        logger.info("Data transformation completed")
        return self.transformed_data

    def write_data(
        self,
        output_path: str,
        partition_cols: list[str] | None = None,
        overwrite: bool = False,
        compression: str = "snappy",
    ) -> None:
        """Writes data in Parquet format

        Args:
            output_path (str): Output path for Parquet files
            partition_cols (list[str], optional): Columns to use for partitioning. Defaults to None
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False
            compression (str, optional): Compression algorithm to use. Defaults to "snappy"
        """
        logger.info(f"Starting data writing to: {output_path}")
        dd = self.transformed_data.to_dask_dataframe(["time", "latitude", "longitude"])

        start_time = time.time()
        dd.to_parquet(
            path=output_path,
            engine="pyarrow",
            compression=compression,
            schema=self.schema,
            write_index=False,
            write_metadata_file=True,
            partition_on=partition_cols,
            overwrite=overwrite,
            coerce_timestamps="ms",
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Writing completed in {elapsed_time:.2f} seconds")
