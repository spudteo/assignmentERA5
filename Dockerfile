FROM ubuntu:22.04

# Install minimal requirements for uv and Java
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    openjdk-11-jre \
    wget \
    tar \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Download and install Apache Spark
ENV SPARK_VERSION=3.4.3
RUN wget https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz \
    && tar -xzf spark-$SPARK_VERSION-bin-hadoop3.tgz -C /opt \
    && ln -s /opt/spark-$SPARK_VERSION-bin-hadoop3 /opt/spark \
    && rm spark-$SPARK_VERSION-bin-hadoop3.tgz

# Set Spark environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

WORKDIR /app
COPY src /app/src/
COPY script /app/script/
COPY pyproject.toml /app/
COPY uv.lock /app/
COPY .python-version /app/

ENV PYTHONPATH=/app:${PYTHONPATH}

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen
# Create entrypoint script with error handling and proper argument passing
RUN echo '#!/bin/bash\n\
if [ -z "$1" ]; then\n\
    echo "Error: You must specify which script to run!"\n\
    echo "Usage: docker run <script>"\n\
    echo "Available options:"\n\
    echo "  - ingestion.py"\n\
    echo "  - processing.py"\n\
    echo "  - query_example.py"\n\
    exit 1\n\
fi\n\
\n\
SCRIPT=$1\n\
shift\n\
if [ "$1" = "--" ]; then\n\
    shift\n\
fi\n\
uv run script/$SCRIPT "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
