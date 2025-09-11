"""CSV file generator module."""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.constants import DATA_FOLDER_PATH, CSV_TITLE, CSV_HEADERS


class CSVGenerator:
    """Manages CSV file creation and operations."""

    def __init__(self):
        self.csv_file_path = None

    def create_csv(self) -> bool:
        """
        Create a new CSV file with headers.

        Returns:
          bool: True if generation successful, False otherwise
        """
        try:
            self.csv_file_path = os.path.join(DATA_FOLDER_PATH, CSV_TITLE)

            with open(self.csv_file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
                writer.writeheader()

            return True
        except Exception as e:
            print(f"Failed to create CSV file: {e}")
            return False

    def add_point_rows(self, point_name: str, row_data: List[Dict[str, Any]]) -> bool:
        """
        Add a single point row to the CSV file following the format: Preset Name, Point Name, Timestamp, Value

        Parameters:
            point_name (str): Name of the point
            row_data (List[Dict[str, Any]]): List of dictionaries containing timestamp and value

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows_to_append = []

            # For each timestamp-value pair for this point
            for entry in row_data:
                row = {
                    "Preset Name": "",
                    "Point Name": point_name,
                    "Timestamp": entry["timestamp"],
                    "Value": entry["value"],
                }
                rows_to_append.append(row)

            with open(self.csv_file_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
                writer.writerows(rows_to_append)

            return True

        except Exception as e:
            print(f"Failed to add point to csv file: {e}")
            return False

    def add_preset_rows(
        self, preset_name: str, rows_data: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """
        Add preset rows to the CSV file following the format: Preset Name, Point Name, Timestamp, Value.

        Parameters:
          preset_name (str): Name of the preset
          rows_data (Dict): Preset dictionary containing data

        Returns:
          bool: True if successful, False otherwise
        """

        try:
            rows_to_append = []

            # For each point in the preset
            for point_name, time_value_list in rows_data.items():
                # For each timestamp-value pair for this point
                for entry in time_value_list:
                    row = {
                        "Preset Name": preset_name,
                        "Point Name": point_name,
                        "Timestamp": entry["timestamp"],
                        "Value": entry["value"],
                    }
                    rows_to_append.append(row)

            with open(self.csv_file_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
                writer.writerows(rows_to_append)

            return True

        except Exception as e:
            print(f"Failed to add preset to csv file: {e}")
            return False
