import logging
from multiprocessing import cpu_count
from typing import Any

from dask.distributed import Client, LocalCluster


class ClusterFactory:
    """Factory class for creating different types of Dask clusters"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def create_cluster(self, cluster_type: str = "local", **kwargs: Any) -> tuple[Client, LocalCluster]:
        """Creates a cluster of the specified type"""
        self.logger.info(f"Creating cluster of type: {cluster_type}")

        client, cluster = None, None
        if cluster_type == "local":
            client, cluster = self._create_local_cluster(**kwargs)
        else:
            raise ValueError(f"Unsupported cluster type: {cluster_type}")

        self.logger.info("Cluster configured for your hardware:")
        self.logger.info(f"- Dashboard link: {client.dashboard_link}")
        self.logger.debug(f"- Cluster info: {client.cluster}")

        return client, cluster

    def _create_local_cluster(
        self,
        n_workers: int = 8,
        threads_per_worker: int = 2,
        memory_limit: str | None = None,
        **kwargs: Any,
    ) -> tuple[Client, LocalCluster]:
        """Creates an optimized local cluster"""
        self.logger.debug(
            f"Creating local cluster with parameters: workers={n_workers}, "
            f"threads={threads_per_worker}, "
            f"memory={memory_limit}"
        )

        cluster = LocalCluster(
            n_workers=n_workers,
            threads_per_worker=threads_per_worker,
            memory_limit=memory_limit,
            processes=False,
            **kwargs,
        )

        client = Client(cluster)
        return client, cluster

    def setup_dask_client(
        self, n_workers: int | None = None, threads_per_worker: int = 1, memory_limit: str = "4GB"
    ) -> Client:
        """Setup Dask distributed client with specified configuration

        Args:
            n_workers: Number of workers. If None, uses CPU count
            threads_per_worker: Number of threads per worker
            memory_limit: Memory limit per worker

        Returns:
            Dask distributed Client
        """
        if n_workers is None:
            n_workers = cpu_count()

        cluster = LocalCluster(n_workers=n_workers, threads_per_worker=threads_per_worker, memory_limit=memory_limit)
        return Client(cluster)
