import argparse
import logging
from multiprocessing import cpu_count

from google.cloud.storage import Client  # type: ignore

from src.etl.ingestion_layer import DataIngestionManager


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the data ingestion process.")
    parser.add_argument("--timer-verbose", action="store_true", help="Enable detailed timing logs.")
    parser.add_argument(
        "--raw-directory",
        type=str,
        required=True,
        help="Directory to store downloaded files.",
    )
    parser.add_argument("--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", type=str, required=True, help="End date in YYYY-MM-DD format")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level (default: INFO)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting the data ingestion process.")
    bucket_name: str = "gcp-public-data-arco-era5"
    base_path: str = "raw/date-variable-single_level/{date_str}/total_precipitation/surface.nc"
    worker_number: int = cpu_count()
    storage_client: Client = Client.create_anonymous_client()

    logger.info(f"Detected {worker_number} CPU cores for parallel processing.")

    ingestion_manager = DataIngestionManager(bucket_name, base_path, storage_client, args.raw_directory)
    ingestion_manager.download_blobs(args.start_date, args.end_date, worker_number, timer_verbose=args.timer_verbose)
    logger.info("Data ingestion process completed.")


if __name__ == "__main__":
    main()
