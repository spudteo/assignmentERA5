## Overview

The ingestion script (`script/ingestion.py`) is designed to download precipitation data from the ERA5 public dataset hosted on Google Cloud Storage. It leverages parallel processing to speed up downloads using multiple CPU cores and provides flexible configuration options for specifying date ranges.

## Command Line Arguments

The script accepts the following command line arguments:

| **Argument**      | **Required** | **Default** | **Description**                                                           |
|--------------------|--------------|-------------|---------------------------------------------------------------------------|
| `--raw-directory` | Yes          | -           | Path to the directory where downloaded files will be stored.              |
| `--start-date`    | Yes          | -           | Start date for data download in `YYYY-MM-DD` format.                      |
| `--end-date`      | Yes          | -           | End date for data download in `YYYY-MM-DD` format.                        |
| `--log-level`     | No           | `INFO`      | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.    |
| `--timer-verbose` | No           | `False`     | Enable detailed timing logs for monitoring performance.                   |
## Run example
```bash
python script/ingestion.py --raw-directory /path/to/output --start-date 2022-01-01 --end-date 2022-12-31
```

With uv 

```bash
uv run script/ingestion.py --raw-directory /path/to/output --start-date 2022-01-01 --end-date 2022-12-31
```