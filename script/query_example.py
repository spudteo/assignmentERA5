import argparse
import logging
import time

from src.etl.query_layer import QueryExample


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Execute queries on weather data")
    parser.add_argument("--parquet_path", required=True, help="Path to parquet file")
    parser.add_argument(
        "--query_type",
        choices=["march_30", "daily_sum", "time_stats", "h3_analysis", "h3_time", "custom_sql"],
        required=True,
        help="Type of query to execute",
    )
    parser.add_argument("--start_date", help="Start date for temporal analysis")
    parser.add_argument("--end_date", help="End date for temporal analysis")
    parser.add_argument("--h3_resolution", type=int, help="H3 resolution for spatial analysis")
    parser.add_argument("--sql_query", help="Custom SQL query to execute")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level (default: INFO)",
    )
    parser.add_argument(
        "--no-compute",
        action="store_false",
        dest="compute",
        help="If set, show query plan instead of computing results",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to execute queries based on command line arguments"""
    args = parse_arguments()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    logger.info("Initializing QueryExample class")
    query_example = QueryExample(args.parquet_path)

    logger.debug(f"Executing query type: {args.query_type}")

    start_time = time.time()

    if args.query_type == "custom_sql":
        if not args.sql_query:
            logger.error("Missing required parameter: sql_query")
            raise ValueError("sql_query is required for query_type 'custom_sql'")
        result = query_example.execute_sql_query(args.sql_query)
    elif args.query_type == "march_30":
        logger.debug("Executing March 30th filter query")
        result = query_example.filter_march_30()
    elif args.query_type == "daily_sum":
        logger.debug("Executing daily sum calculation")
        result = query_example.daily_tp_sum()
    elif args.query_type == "time_stats":
        if not (args.start_date and args.end_date):
            logger.error("Missing required parameters: start_date and end_date")
            raise ValueError("start_date and end_date are required for time_stats")
        logger.debug(f"Executing time stats analysis for period {args.start_date} to {args.end_date}")
        result = query_example.time_range_stats(args.start_date, args.end_date)
    elif args.query_type == "h3_analysis":
        if not args.h3_resolution:
            logger.error("Missing required parameter: h3_resolution")
            raise ValueError("h3_resolution is required for h3_analysis")
        logger.debug(f"Executing H3 analysis at resolution {args.h3_resolution}")
        result = query_example.analyze_by_h3_resolution(args.h3_resolution)
    elif args.query_type == "h3_time":
        if not (args.start_date and args.end_date and args.h3_resolution):
            logger.error("Missing required parameters: start_date, end_date, and h3_resolution")
            raise ValueError("start_date, end_date and h3_resolution are required for h3_time")
        logger.debug("Executing combined H3-temporal analysis")
        result = query_example.analyze_h3_time_combined(args.h3_resolution, args.start_date, args.end_date)

    if args.compute:
        result.show()
        execution_time = time.time() - start_time
        logger.info(f"Query executed in {execution_time:.2f} seconds")
    else:
        result.explain("formatted")


if __name__ == "__main__":
    main()
