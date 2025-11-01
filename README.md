## Overview  
  
The project follows an architecture with the following structure:  
  
```  
.  
├── src/              # Source code  
│   ├── ingestion/    # ERA5 dataset download logic  
│   ├── processing/   # Data processing and H3 indexing  
│   └── query/        # Spark query implementation  
├── tests/            # Test files  
├── script/           # Entry point scripts  
├── Taskfile.yml      # Task runner configuration  
├── pyproject.toml    # Python project dependencies and configuration  
├── requirements.lock # Locked dependencies for reproducible builds  
└── Dockerfile        # Docker image definition  
```  
  
The project is structured into three main components:  

- **Ingestion**: ERA5 dataset download  
- **Processing**: Processing downloaded files with H3 index addition and Parquet saving  
- **Query**: Execute queries on Parquet data, with support for custom SQL queries, using Spark.

The three component are meant to be run one after another like if it was an ETL pipeline.
  
## Minimum Requirements  
  
- **Task** (similiar to MAKE for makefile, https://taskfile.dev/)
- **Docker**
  
## Configuration  
Once task is installed, it is possibile to just build an image and run the script from there.
To get started, you only need to modify two variables in `Taskfile.yml`:  
  
```yaml  
# Taskfile.yml  
vars:  
  RAW_DATA_DIR: /path/to/your/raw/data/directory 
  PROCESSING_DATA_DIR: /path/to/your/processing/data/directory  
```
The first one is the folder where you want the data to be downloaded and the second one the folder where you want to save the parquet files. Docker will use this folder mounted in the image when running. 
## Project Management with Task and uv  
  
The project uses Task as a command runner (similar to Make but with YAML 
syntax) and uv (https://docs.astral.sh/uv/) as a Python package manager for an isolated development environment.  

## How to run 
Once you have installed Task, and change the folder path you can procede to build the image using task so just open a terminal window and do 

```bash
task build
```
this will run the task associate with the build that will create the image from the dockerfile. 
With the image created one can run the three script one after another and see the log in the shell. 

```bash
task run-ingestion
task run-processing
task run-query
```
this will run the script downloading all the 2022 data, add the H3 index to all the data and write the parquet file, and then perform a simple query on the data.

All the script are parametric, so it is possibile to change the behaviour, for example how many data to download or to process, which partition strategy to use and so on. 
A guide on how every script works can be found in the following documentation:

- [Ingestion Script Guide](docs/ingestion.md)
- [Processing Script Guide](docs/processing.md)
- [Query Script Guide](docs/query.md)

## Alternative Approach  
If you prefer not to use Task, you can still build and run the project manually. Below are two alternative methods to set up and execute the scripts.  
### Using Docker Without Task  
1. **Build the Docker Image:**
2. You can build the Docker image directly from the `Dockerfile` using the following command:      
```bash    
  docker build -t project-image
```
3. **Run the Scripts:**  
    Execute the scripts inside the Docker container using `docker run`. For example: 
``` bash
docker run -script name, and argument following the documentation
```

### Setting Up a Local Environment

You can also run the scripts locally by setting up a Python environment and installing the required dependencies.

1. **Install uv and Sync the Environment:**

    This will recreate the exact same environment used in the docker image and in the development phase thanks to the lock file.
  ```bash
    uv sync --frozen
  ```

2. **Install Spark:**  
    Download and install Apache Spark.
    
3. **Run the Scripts Locally:**  
    With the environment set up, you can run the scripts directly from the `script/` directory:
```bash
  uv run script/ingestion.py with arugment 
 ```
4. **Run Tests:**  
To verify that your environment is correctly set up for both Python and Spark, you can run the tests included in the project:
```bash
  uv run pytest 
```
Also, the task file contains 3 task to run the script in your local environment just check the task with the local suffix.
If one want to check how to run an example of the script.

## Code Quality Tools

The project employs some tool for the quality of the code:

- **Ruff**:
  - Automatic code formatting
  - Style error checking
  - Automatic fixes for common issues
- **Mypy**: 
  - Static type checker for Python
- **isort**: Automatic import organizer
  - Sorts and groups imports
  - Maintains consistent style

These tools are integrated into the task runner and can be executed with:

```bash
task lint
```

The configuration for these tools is located in `pyproject.toml` and they should run automatically before each build as a 
dependency of the `build` task in the CI/CD pipeline even with the test task that run all the test.



