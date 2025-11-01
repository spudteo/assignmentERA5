## Overview

The query script (`script/query_example.py`) enables querying meteorological data stored in Parquet format. It supports various analysis modes, including temporal and spatial queries using the H3 index. It leverage Spark for performing the query.

## Command Line Arguments

The script accepts the following command line arguments:

| **Argument**        | **Required** | **Default** | **Description**                                                         |
|----------------------|--------------|-------------|---------------------------------------------------------------------------|
| `--parquet_path`    | Yes          | -           | Path to the Parquet files to query.                                      |
| `--query_type`      | Yes          | -           | Type of query to execute (see query types below).                        |
| `--start_date`      | No           | -           | Start date for temporal analysis (format: `YYYY-MM-DD`).                 |
| `--end_date`        | No           | -           | End date for temporal analysis (format: `YYYY-MM-DD`).                   |
| `--h3_resolution`   | No           | -           | H3 resolution level for spatial analysis.                                |
| `--sql_query`       | No           | -           | Custom SQL query for advanced analysis.                                  |
| `--log-level`       | No           | `INFO`      | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.   |
| `--no-compute`      | No           | `False`     | Displays the query plan instead of executing it.                         |

> **Note:** The required arguments may vary depending on the specified query type.

## Query Types

1. **march_30**  
   Filters data for March 30th.  
   *No additional parameters required.*

2. **daily_sum**  
   Calculates the daily sum of precipitation.  
   *No additional parameters required.*

3. **time_stats**  
   Performs statistical analysis over a specified time range.  
   *Requires:* `--start_date`, `--end_date`

4. **h3_analysis**  
   Performs spatial analysis using the H3 index.  
   *Requires:* `--h3_resolution`

5. **h3_time**  
   Performs combined spatial and temporal analysis.  
   *Requires:* `--start_date`, `--end_date`, `--h3_resolution`

6. **custom_sql**  
   Executes a custom SQL query.  
   *Requires:* `--sql_query`
## Run example
```bash
python script/query_example.py \

--parquet_path /path/to/parquet \

--query_type custom_sql \

--sql_query "SELECT * FROM weather_data WHERE date_format(time, 'yyyy-MM-dd') = '2022-03-31'"
```
