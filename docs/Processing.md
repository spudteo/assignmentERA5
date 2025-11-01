## Overview

The processing script (`script/processing.py`) processes the downloaded meteorological data by applying H3 indexing and converting files from NetCDF format to Parquet. This script leverage Dask.

## Command Line Arguments

The script supports the following command line arguments:

| **Argument**         | **Required** | **Default** | **Description**                                                          |
|-----------------------|--------------|-------------|---------------------------------------------------------------------------|
| `--raw-directory`    | Yes          | -           | Path to the directory containing input NetCDF files.                     |
| `--output-directory` | Yes          | -           | Path to the directory where output Parquet files will be saved.          |
| `--h3-resolutions`   | Yes          | -           | Comma-separated H3 resolution levels (e.g., `4,8`).                      |
| `--compression`      | No           | `snappy`    | Compression algorithm to use for Parquet files.                          |
| `--partition-cols`   | No           | `None`      | Columns to partition by (e.g., `time,h3_res_4`).                         |
| `--overwrite`        | No           | `False`     | Overwrite existing output files if set to `True`.                        |
| `--n-workers`        | No           | `1`         | Number of Dask workers to use for parallel processing.                   |
| `--threads-per-worker`| No          | `2`         | Number of threads per Dask worker.                                       |
| `--memory-limit`     | No           | `16GB`      | Memory limit for each Dask worker.                                       |
| `--log-level`        | No           | `INFO`      | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.   |
## Run example
```bash
python script/processing.py \
    --raw-directory /path/to/input \
    --output-directory /path/to/output \
    --h3-resolutions "4,8" \
    --n-workers 4
```
