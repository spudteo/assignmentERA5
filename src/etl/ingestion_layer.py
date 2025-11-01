import logging
import os
import time
from datetime import datetime, timedelta

from google.cloud.storage import Client, transfer_manager  # type: ignore

logger = logging.getLogger(__name__)


class DataIngestionManager:
    def __init__(
        self, bucket_name: str, base_path: str, storage_client: Client, destination_directory: str | None = None
    ) -> None:
        """
        Initialize the DataIngestionManager.

        :param bucket_name: Name of the GCP bucket.
        :param base_path: Base path template for blob paths.
        :param storage_client: GCP Storage client.
        :param destination_directory: Local directory to store downloaded blobs.
        """
        self.bucket_name = bucket_name
        self.base_path = base_path
        self.storage_client = storage_client
        self.destination_directory = destination_directory
        logger.debug(f"Initialized DataIngestionManager for bucket '{bucket_name}'.")

    def generate_paths(self, start_date: str, end_date: str, partition_format: str = "%Y/%m/%d") -> list[str]:
        """
        Generate a list of blob paths between start_date and end_date.

        :param start_date: Start date in the format 'YYYY-MM-DD'.
        :param end_date: End date in the format 'YYYY-MM-DD'.
        :param partition_format: Date format for the paths.
        :return: List of blob paths.
        """
        logger.debug(f"Generating paths from {start_date} to {end_date} with format '{partition_format}'.")

        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_dt < start_date_dt:
            error_message = f"End date ({end_date}) cannot be earlier than start date ({start_date})."
            logger.error(error_message)
            raise ValueError(error_message)

        paths = []
        delta = timedelta(days=1)

        while start_date_dt <= end_date_dt:
            date_str: str = start_date_dt.strftime(partition_format)
            path = self.base_path.format(date_str=date_str)
            logger.debug(f"Generated path: {path}")
            paths.append(path)
            start_date_dt += delta

        logger.debug(f"Generated {len(paths)} paths.")
        return paths

    def download_blobs(
        self,
        start_date: str,
        end_date: str,
        workers: int = 4,
        timer_verbose: bool = False,
    ) -> None:
        """
        Download blobs in parallel using process between start_date and end_date.

        :param start_date: Start date in the format 'YYYY-MM-DD'.
        :param end_date: End date in the format 'YYYY-MM-DD'.
        :param workers: Number of workers to use for downloading. Defaults to the number of CPU cores.
        :param timer_verbose: If True, logs the time taken for the download process.
        """
        logger.info(f"Starting download of blobs from {start_date} to {end_date} using {workers} workers.")

        start_time = time.time() if timer_verbose else None

        blob_names: list[str] = self.generate_paths(start_date, end_date)
        bucket = self.storage_client.bucket(self.bucket_name)

        try:
            results = transfer_manager.download_many_to_path(
                bucket,
                blob_names,
                destination_directory=self.destination_directory,
                max_workers=workers,
                worker_type="process",
            )
        except Exception as e:
            logger.error(f"Failed to initiate download: {str(e)}")
            return

        for name, result in zip(blob_names, results, strict=False):
            if isinstance(result, Exception):
                logger.error(f"Failed to download {name}: {str(result)}")
            else:
                if self.destination_directory is not None:
                    local_path = os.path.join(self.destination_directory, name)
                    logger.debug(f"Downloaded {name} to {local_path}.")
                else:
                    logger.warning("Destination directory is None, skipping join operation.")

        if timer_verbose and start_time is not None:
            elapsed_time = time.time() - start_time
            logger.info(f"Download process completed in {elapsed_time:.2f} seconds.")
        else:
            logger.info("Download process completed")
