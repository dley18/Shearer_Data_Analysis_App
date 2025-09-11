"""Database operations and logic"""

import json
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from config.constants import DATA_FOLDER_PATH, TIME_ZONE_OFFSET_ID
from config.point_mapping import IO_TYPES, VFD_POINTS


class DatabaseManager:
    """Handles database connections and operations."""

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize DatabaseManager.

        Parameters:
            database_path (str, optional): Path to database file.
                                         Defaults to merged_db.sqlite in DATA_FOLDER_PATH
        """
        if database_path is None:
            self.database_path = os.path.join(DATA_FOLDER_PATH, "merged_db.sqlite")
        else:
            self.database_path = database_path

        self._connection = None

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection cleanup.

        Yields:
            sqlite3.Connection: Database connection
        """
        connection = None
        try:
            connection = sqlite3.connect(self.database_path)
            connection.row_factory = sqlite3.Row  # Enable column access by name
            yield connection
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()

    def get_io_point_info(self, name: str) -> dict:
        """
        Retrieve ioid, iotype, ioname, and active from IOConfig.

        Parameters:
            name (str): ioName to retrieve info for

        Returns:
            dict: Dictionary containing io point info
        """
        # Extract the JSON fields
        query = """
                SELECT 
                    json_extract(rti_json_sample, '$.ioId') as io_id,
                    json_extract(rti_json_sample, '$.ioType') as io_type,
                    json_extract(rti_json_sample, '$.active') as active
                FROM "IOConfig@0"
                WHERE json_extract(rti_json_sample, '$.ioName') = ?
                """

        result = self.execute_custom_query(query, (name,))
        return result[0] if result else {}

    def get_io_point_value(self, io_id: str, io_type: str) -> List:
        """
        Retrieve io point values across time.

        Parameters:
            io_id (str): io id of point
            io_type (str): io type of point

        Returns:
            List: List of dictionaries containing the time and value
        """
        base_query = """
                    SELECT 
                        SampleInfo_source_timestamp as timestamp,
                        json_extract(rti_json_sample, '$.value') as value
                    FROM "{}"
                    WHERE json_extract(rti_json_sample, '$.ioId') = ?
                    """.format(
            IO_TYPES[io_type]
        )

        query = base_query + " ORDER BY SampleInfo_source_timestamp"
        return self.execute_custom_query(query, (int(io_id),))

    def get_vfd_point_info(self, name: str) -> dict:
        """
        Retrieve vfdID, and active from VFDConfig.

        Parameters:
            name (str): Readable name from vfd points mapping

        Returns:
            dict: Dictionary containing vfd point info
        """
        query = """
                SELECT 
                    json_extract(rti_json_sample, '$.vfdId') as vfd_id,
                    json_extract(rti_json_sample, '$.active') as active
                FROM "VFDConfig@0"
                WHERE json_extract(rti_json_sample, '$.vfdName') = ?
                """
        result = self.execute_custom_query(query, (VFD_POINTS[name]["name"],))
        return result[0] if result else {}

    def get_vfd_point_value(self, vfd_id: str, vfd_type: str) -> List:
        """
        Retrieve VFD point values across time.

        Parameters:
            vfd_id (str): VFD ID of vfd point
            vfd_type (str): VFD type of vfd point

        Returns:
            List: List of dictionaries containing the time and value
        """
        base_query = """
                    SELECT
                        SampleInfo_source_timestamp as timestamp,
                        json_extract(rti_json_sample, '$.{}') as value
                    FROM "VFDInfo@0"
                    WHERE json_extract(rti_json_sample, '$.vfdId') = ?
                    """.format(
            vfd_type
        )
        query = base_query + " ORDER BY SampleInfo_source_timestamp"
        return self.execute_custom_query(query, (int(vfd_id),))

    def get_all_incidents(self) -> List:
        """
        Retrieve all incidents in the database.

        Returns:
            List: List of dictionaries containing: (timestamp, tidx, type, state, and args)
        """

        query = """
                SELECT
                    SampleInfo_source_timestamp as timestamp,
                    json_extract(rti_json_sample, '$.incidentTidx') as tidx,
                    json_extract(rti_json_sample, '$.helpTidx') as help_tidx,
                    json_extract(rti_json_sample, '$.type') as type,
                    json_extract(rti_json_sample, '$.state') as state,
                    json_extract(rti_json_sample, '$.args') as args
                FROM "IncidentAll@0"
                ORDER BY SampleInfo_source_timestamp
                """

        return self.execute_custom_query(query)

    def find_user_id(self, user_id: str) -> List:
        """
        Searches fbhmi database for matching user_id and returns login name.

        Parameters:
            user_id (str): User id to look up

        Returns:
            List: List containg data
        """
        query = """
                SELECT
                    userId as user_id,
                    loginId as user_name
                FROM "fb_users"
                WHERE userId == ?
                """
        return self.execute_custom_query(query, user_id)

    def get_report_info(self) -> Dict:
        """
        Get report info for incident viewer screen.

        Returns:
            Dict: Dictionary containing report info.
        """

        query = """
                SELECT
                    json_extract(rti_json_sample, '$.machineId') as id,
                    MIN(SampleInfo_source_timestamp) AS first_timestamp,
                    MAX(SampleInfo_source_timestamp) AS last_timestamp
                FROM "CCUSync@0"
                """
        return self.execute_custom_query(query)

    def get_time_zone_offset(self) -> Optional[Dict]:
        """
        Get time zone offset to use for shearer location specific timestamps.

        Returns:
            Optional[Dict]: Dictionary containing offset, or None if not found.
        """
        query_to_find_tidx = """
                            SELECT
                                json_extract(rti_json_sample, '$.parNameTidx') as tidx
                            FROM "ParConfig@0"
                            WHERE json_extract(rti_json_sample, '$.parName') == "TimeZoneOffset"
                            ORDER BY SampleInfo_source_timestamp
                            LIMIT 1
                            """
        tidx = self.execute_custom_query(query_to_find_tidx)
        tidx = tidx[0]["tidx"]

        query_to_find_offset = """
                                SELECT
                                    json_extract(rti_json_sample, '$.value') as value
                                from "ParValue@0"
                                WHERE json_extract(rti_json_sample, '$.parNameTidx') == ?
                                ORDER BY SampleInfo_source_timestamp
                                LIMIT 1
                                """

        offset = self.execute_custom_query(query_to_find_offset, (tidx,))
        if offset:
            offset = offset[0]
            return json.loads(offset["value"])["longValue"]
        else:
            return None

    def database_exists(self) -> bool:
        """
        Check if the database file exists.

        Returns:
            bool: True if database exists, False otherwise
        """
        return os.path.exists(self.database_path)

    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database.

        Returns:
            List[str]: List of table names

        Raises:
            sqlite3.Error: If database operation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """
        Get schema information for a specific table.

        Parameters:
            table_name (str): Name of the table

        Returns:
            List[Tuple[str, str]]: List of (column_name, column_type) tuples

        Raises:
            sqlite3.Error: If table doesn't exist or database operation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema_info = cursor.fetchall()
            return [(row[1], row[2]) for row in schema_info]

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Parameters:
            table_name (str): Name of the table to check

        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            table_names = self.get_table_names()
            return table_name in table_names
        except sqlite3.Error:
            return False

    def get_table_row_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table.

        Parameters:
            table_name (str): Name of the table

        Returns:
            int: Number of rows in the table

        Raises:
            sqlite3.Error: If table doesn't exist or database operation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]

    def query_table(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query data from a specific table.

        Parameters:
            table_name (str): Name of the table to query
            columns (List[str], optional): List of columns to select. Defaults to all columns.
            where_clause (str, optional): WHERE clause (without 'WHERE' keyword)
            order_by (str, optional): ORDER BY clause (without 'ORDER BY' keyword)
            limit (int, optional): Maximum number of rows to return

        Returns:
            List[Dict[str, Any]]: List of rows as dictionaries

        Raises:
            sqlite3.Error: If database operation fails
        """
        # Build SELECT clause
        if columns is None:
            select_clause = "*"
        else:
            select_clause = ", ".join(columns)

        # Build query
        query = f"SELECT {select_clause} FROM {table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            # Convert rows to dictionaries
            return [dict(row) for row in rows]

    def execute_custom_query(
        self, query: str, parameters: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query.

        Parameters:
            query (str): SQL query to execute
            parameters (Tuple, optional): Parameters for parameterized queries

        Returns:
            List[Dict[str, Any]]: Query results as list of dictionaries

        Raises:
            sqlite3.Error: If database operation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_data_by_time_range(
        self,
        table_name: str,
        time_column: str,
        start_time: str,
        end_time: str,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query data within a specific time range.

        Parameters:
            table_name (str): Name of the table to query
            time_column (str): Name of the timestamp column
            start_time (str): Start time (in database format)
            end_time (str): End time (in database format)
            columns (List[str], optional): Columns to select

        Returns:
            List[Dict[str, Any]]: Rows within the time range
        """
        where_clause = f"{time_column} BETWEEN ? AND ?"

        # Build SELECT clause
        if columns is None:
            select_clause = "*"
        else:
            select_clause = ", ".join(columns)

        query = f"SELECT {select_clause} FROM {table_name} WHERE {where_clause} ORDER BY {time_column}"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_time, end_time))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_io_point_data(
        self,
        table_name: str,
        io_points: List[str],
        time_column: str = "timestamp",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get data for specific IO points.

        Parameters:
            table_name (str): Name of the table to query
            io_points (List[str]): List of IO point column names
            time_column (str): Name of the timestamp column
            start_time (str, optional): Start time filter
            end_time (str, optional): End time filter

        Returns:
            List[Dict[str, Any]]: Data for specified IO points
        """
        # Include timestamp in columns
        columns = [time_column] + io_points

        if start_time and end_time:
            return self.get_data_by_time_range(
                table_name, time_column, start_time, end_time, columns
            )
        else:
            return self.query_table(table_name, columns=columns, order_by=time_column)

    def get_sample_data(
        self, table_name: str, sample_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get a sample of data from a table for inspection.

        Parameters:
            table_name (str): Name of the table
            sample_size (int): Number of rows to sample

        Returns:
            List[Dict[str, Any]]: Sample data
        """
        return self.query_table(table_name, limit=sample_size)

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get general information about the database.

        Returns:
            Dict[str, Any]: Database information including tables, sizes, etc.
        """
        info = {
            "database_path": self.database_path,
            "database_exists": self.database_exists(),
            "database_size": 0,
            "tables": {},
        }

        if info["database_exists"]:
            # Get database file size
            info["database_size"] = os.path.getsize(self.database_path)

            # Get table information
            table_names = self.get_table_names()
            for table_name in table_names:
                try:
                    row_count = self.get_table_row_count(table_name)
                    schema = self.get_table_schema(table_name)
                    info["tables"][table_name] = {
                        "row_count": row_count,
                        "columns": len(schema),
                        "schema": schema,
                    }
                except sqlite3.Error as e:
                    info["tables"][table_name] = {"error": str(e)}

        return info

    def close(self):
        """Clean up any persistent connections."""
        if self._connection:
            self._connection.close()
            self._connection = None
