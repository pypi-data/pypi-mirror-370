"""
Module provides a class for executing BigQuery queries and returning results in JSON format.

Classes:
    BigqueryQuery: A class to execute BigQuery queries and return results in JSON format.
"""

from datetime import date, datetime
from typing import Any

from google.cloud import bigquery

from brownllama.logger import get_logger

logger = get_logger(__name__)


class BigqueryQuery:
    """
    A class to execute BigQuery queries and return results in JSON format.

    Attributes:
        client (google.cloud.bigquery.client.Client): The BigQuery client used to execute queries.

    """

    def __init__(self, project_id: str) -> None:
        """
        Initialize the BigqueryQuery client.

        Args:
            project_id (str): Your Google Cloud Project ID.

        """
        self.client = bigquery.Client(project=project_id)
        logger.debug(
            f"{'=' * 10} BigQuery client initialized for project: {project_id} {'=' * 10}"
        )

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a BigQuery SQL query and returns the results as a list of dictionaries.

        Date and datetime objects are converted to ISO 8601 strings to ensure JSON serializability.
        Raises an exception if the query fails or data processing encounters an issue.

        Args:
            query (str): The SQL query string to execute.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing the query results,
                                   with dates/datetimes formatted as ISO strings.

        """
        logger.debug(f"{'=' * 10} Executing query in BQ {'=' * 10}")
        query_job = self.client.query(query)
        results = query_job.result()

        # Convert results to a list of dictionaries
        rows_dict = []
        for row in results:
            row_dict = {}
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    # Convert date/datetime objects to ISO 8601 string format
                    row_dict[key] = value.isoformat()
                else:
                    # Keep other values as they are from the query result
                    row_dict[key] = value
            rows_dict.append(row_dict)

        logger.debug(f"{'=' * 10} Query executed successfully.  {'=' * 10}")
        return rows_dict
