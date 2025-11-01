import argparse
import logging
import traceback

from src.configuration.dask_setup import ClusterFactory
from src.etl.processing_layer import DataProcessor


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process meteorological data with H3 indices")
    parser.add_argument("--raw-directory", type=str, required=True, help="Directory of NetCDF files to process")
    parser.add_argument("--output-directory", type=str, required=True, help="Directory to save Parquet files")
    parser.add_argument(
        "--h3-resolutions",
        type=str,
        required=True,
        help='Comma-separated list of H3 resolutions to calculate (e.g.: "4,8")',
    )
    parser.add_argument(
        "--compression", type=str, default="snappy", help="Compression algorithm for Parquet files (default: snappy)"
    )
    parser.add_argument(
        "--partition-cols",
        type=str,
        default=None,
        help='Comma-separated list of columns to partition by (e.g.: "time,h3_res_4")',
    )
    parser.add_argument("--overwrite", action="store_true", default=False, help="Overwrite existing files if present")
    parser.add_argument("--n-workers", type=int, default=1, help="Number of Dask workers (default: 1)")
    parser.add_argument("--threads-per-worker", type=int, default=2, help="Number of threads per worker (default: 2)")
    parser.add_argument("--memory-limit", type=str, default="16GB", help="Memory limit per worker (default: 16GB)")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level (default: INFO)",
    )
    args = parser.parse_args()

    # Convert comma-separated string to list of integers
    args.h3_resolutions = [int(x.strip()) for x in args.h3_resolutions.split(",")]

    # Convert partition columns string to list if provided
    if args.partition_cols:
        args.partition_cols = [x.strip() for x in args.partition_cols.split(",")]

    return args


def main() -> None:
    args = parse_arguments()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting data processing pipeline")
    logger.debug(f"Raw data path: {args.raw_directory}")
    logger.debug(f"Output path: {args.output_directory}")
    logger.debug(f"H3 resolutions: {args.h3_resolutions}")
    logger.debug(f"Compression: {args.compression}")
    logger.debug(f"Partition columns: {args.partition_cols}")
    logger.debug(f"Overwrite: {args.overwrite}")
    logger.debug("Dask configuration:")
    logger.debug(f"  - Workers: {args.n_workers}")
    logger.debug(f"  - Threads per worker: {args.threads_per_worker}")
    logger.debug(f"  - Memory limit: {args.memory_limit}")

    # Create cluster using the factory
    factory = ClusterFactory()
    client, cluster = factory.create_cluster(
        cluster_type="local",
        n_workers=args.n_workers,
        threads_per_worker=args.threads_per_worker,
        memory_limit=args.memory_limit,
    )

    try:
        processor = DataProcessor(args.raw_directory, client)
        processor.read_data()
        processor.transform_data(args.h3_resolutions)
        processor.write_data(
            args.output_directory,
            partition_cols=args.partition_cols,
            overwrite=args.overwrite,
            compression=args.compression,
        )
        logger.info("Pipeline execution completed successfully")
    except Exception as e:
        logger.error("An error occurred during execution:")
        logger.error(f"Error: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
