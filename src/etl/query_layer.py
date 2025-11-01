import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import avg, col, count, date_format, max, min

logger = logging.getLogger(__name__)


class QueryExample:
    def __init__(self, parquet_path: str) -> None:
        """Initialize the class with the parquet file path"""
        self.spark = SparkSession.builder.appName("Query layer").master("local[*]").getOrCreate()
        logger.debug("SparkSession initialization completed")
        self.df_raw = self.spark.read.parquet(parquet_path)
        logger.debug(f"Parquet file loaded from {parquet_path}")

    def filter_march_30(self) -> DataFrame:
        """Filter DataFrame to get only March 30th data"""
        logger.debug("Executing filter for March 30th")
        return self.df_raw.filter('time == "2022-03-30 00:01:00"')

    def daily_tp_sum(self) -> DataFrame:
        """Calculate daily sum of tp column"""
        logger.debug("Computing daily sum of tp")
        return self.df_raw.groupBy(date_format("time", "yyyy-MM-dd").alias("date")).agg({"tp": "sum"}).orderBy("date")

    def execute_sql_query(self, query: str) -> DataFrame:
        """
        Execute a generic SQL query on the DataFrame
        Args:
            query: SQL query to execute (string)
        Returns:
            DataFrame resulting from the query
        """
        logger.info("Executing custom SQL query")
        logger.debug(f"SQL Query: {query}")
        self.df_raw.createOrReplaceTempView("weather_data")
        return self.spark.sql(query)

    def time_range_stats(self, start_date: str, end_date: str) -> DataFrame:
        """
        Calculate daily statistics (max, min, average) of tp column
        in a specific time range
        """
        logger.info(f"Computing statistics for period {start_date} - {end_date}")
        return (
            self.df_raw.filter((col("time") >= start_date) & (col("time") <= end_date))
            .groupBy(date_format("time", "yyyy-MM-dd").alias("date"))
            .agg(max("tp").alias("tp_max"), min("tp").alias("tp_min"), avg("tp").alias("tp_avg"))
            .orderBy("date")
        )

    def analyze_by_h3_resolution(self, resolution: int, top_n: int = 5) -> DataFrame:
        """
        Analyze data grouped by H3 index at a specific resolution.
        Returns top N H3 indexes with highest average tp.
        Args:
            resolution: Desired H3 resolution
            top_n: Number of results to show
        """
        logger.info(f"Starting H3 analysis at resolution {resolution}")
        h3_column = f"h3_resolution_{resolution}"
        if h3_column not in self.df_raw.columns:
            logger.error(f"H3 resolution {resolution} not found in DataFrame")
            raise ValueError(
                f"H3 resolution {resolution} is not available in DataFrame. "
                f"Available columns: {[col for col in self.df_raw.columns if 'h3_resolution_' in col]}"
            )

        logger.debug(f"Computing averages for H3 cells, limiting to top {top_n}")
        return (
            self.df_raw.groupBy(h3_column)
            .agg(avg("tp").alias("tp_avg"), count("*").alias("observations_count"))
            .orderBy("tp_avg", ascending=False)
            .limit(top_n)
        )

    def analyze_h3_time_combined(self, resolution: int, start_date: str, end_date: str) -> DataFrame:
        """
        Combined temporal and spatial analysis:
        Calculate statistics by H3 index in a specific time range
        Args:
            resolution: Desired H3 resolution
            start_date: Analysis start date
            end_date: Analysis end date
        """
        logger.info(f"Starting combined H3-temporal analysis for period {start_date} - {end_date}")
        h3_column = f"h3_resolution_{resolution}"
        if h3_column not in self.df_raw.columns:
            logger.error(f"H3 resolution {resolution} not found in DataFrame")
            raise ValueError(
                f"H3 resolution {resolution} is not available in DataFrame. "
                f"Available columns: {[col for col in self.df_raw.columns if 'h3_resolution_' in col]}"
            )

        logger.debug("Computing statistics for H3 cells over time range")
        return (
            self.df_raw.filter((col("time") >= start_date) & (col("time") <= end_date))
            .groupBy(h3_column, date_format("time", "yyyy-MM-dd").alias("date"))
            .agg(avg("tp").alias("tp_avg"), max("tp").alias("tp_max"), min("tp").alias("tp_min"))
        )
