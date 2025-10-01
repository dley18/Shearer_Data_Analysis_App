"""File utility functions."""

import os
import sqlite3
import sys
import tarfile
from typing import List
import glob

import lz4.frame

from config.constants import BATCH_SIZE, DATA_FOLDER_PATH


def get_unique_folder(path: str) -> str:
    """
    Create a unique folder.

    Parameters:
        path (str): Base path

    Returns:
        str: New path with (number) if needed
    """

    counter = 1
    while os.path.exists(path):
        path = f"{path}({counter})"
        counter += 1
    return path


def create_folder(path: str) -> None:
    """
    Create a folder from a path.

    Parameters:
        path (str): Path to folder
    """
    os.makedirs(path)


def get_path(path: str) -> str:
    """
    Get the path of dependencies.

    Parameters:
      path (str): The given path

    Returns:
      str: The local path on machine
    """

    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", None) or os.path.dirname(
            os.path.abspath(__file__)
        )
        # In packaged builds, incoming paths may contain '../../assets/...'.
        # Strip any parent traversal and anchor from the bundle root.
        norm = path.replace("/", os.sep).replace("\\", os.sep)
        # If path contains 'assets/', keep from there; else use normalized path without leading '..'
        marker = f"assets{os.sep}"
        idx = norm.find(marker)
        if idx != -1:
            norm = norm[idx:]
        else:
            while norm.startswith(f"..{os.sep}"):
                norm = norm[3:]
        return os.path.join(base_path, norm)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, path)


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creting it if necessary.

    Parameters:
      directory (str): The directory path to ensure exists

    Returns:
      str: A unique folder name
    """

    if not os.path.exists(directory):
        os.makedirs(directory)


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Parameters:
      file_path (str): Path to the file

    Returns:
      int: File size in bytes, or 0 if file doesn't exist
    """

    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return 0


def decompress_datadownload(file_paths: List[str]) -> bool:
    """
    Decompress .lz4 data download files.

    Parameters:
      file_paths (List[str]): Files to decompress

    Returns:
      bool: True if decompression successful, False otherwise
    """
    try:
        for file in file_paths:
            with open(file, "rb") as f:
                with lz4.frame.open(f, mode="rb") as extracted_file:
                    with tarfile.open(fileobj=extracted_file, mode="r|") as tar:
                        tar.extractall(path=DATA_FOLDER_PATH)
        return True
    except Exception as e:
        pass
        return False


def merge_batch(
    file_paths: List[str], target_database: str, create_tables: bool = True
) -> bool:
    """
    Merge a batch of databases into a target database.

    Parameters:
      file_paths (List[str]): Database files in batch
      target_databse (str): Target database file
      create_tables (bool): True if creating tables in database, False if not

    Returns:
      bool: True if merging successful, False otherwise
    """
    try:
        pass
        with sqlite3.connect(target_database) as database_connection:
            database_cursor = database_connection.cursor()

            # Set the target database to use WAL mode
            try:
                database_cursor.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError as e:
                pass  # Add logic later

            # Attach the first source database to copy schema
            alias = "source_temp"
            attached_database = None
            for db in file_paths:
                if not os.path.exists(db):
                    pass
                    continue

                if "FB20.DC.1" in db or "temp_merge" in db:
                    try:
                        database_cursor.execute(f"ATTACH DATABASE '{db}' AS {alias}")
                        attached_database = db
                        break
                    except Exception as e:
                        pass
                        continue

            # Get list of tables and create them in the target database
            try:
                try:
                    database_cursor.execute(
                        f"SELECT name, sql FROM {alias}.sqlite_master WHERE type = 'table'",
                    )
                except sqlite3.OperationalError as e:
                    pass  # Add logic later

                tables = database_cursor.fetchall()
                if not tables:
                    pass
                else:
                    pass

            except Exception as e:
                pass
                try:
                    database_cursor.execute(f"DETACH DATABASE {alias}")
                except sqlite3.OperationalError as e:
                    pass  # Add logic later
                raise RuntimeError(
                    f"Failed to access sqlite_master in {attached_database}"
                )
            if create_tables:
                for table in tables:
                    table_name, create_table_sql = table
                    try:
                        database_cursor.execute(create_table_sql)
                    except sqlite3.OperationalError as e:
                        pass

            # Detach the database
            try:
                database_cursor.execute(f"DETACH DATABASE {alias}")
            except sqlite3.OperationalError as e:
                pass  # Add logic later

            for i, source_database in enumerate(file_paths):
                if not os.path.exists(source_database):
                    pass
                    continue

                # Attach the source database to the target database
                alias = f"source_{i}"
                try:
                    database_cursor.execute(
                        f"ATTACH DATABASE '{source_database}' AS {alias}"
                    )
                except (sqlite3.OperationalError, Exception) as e:
                    pass

                # Insert data from each table
                for table_name, _ in tables:
                    table_name = "'" + table_name + "'"
                    try:
                        database_cursor.execute(
                            f"INSERT INTO {table_name} SELECT * FROM {alias}.{table_name}"
                        )
                    except Exception as e:
                        # Used to filter out blank entries between databases
                        pass

                # Detach the source database
                try:
                    database_cursor.execute(f"DETACH DATABASE {alias}")
                except sqlite3.OperationalError as e:
                    pass  # Add logic later

            database_connection.commit()
            return True

    except Exception as e:
        pass
        return False


def merge_database_files(file_paths: List[str]) -> bool:
    """
    Merge database files into one DB.

    Parameters:
      file_paths (List[str]): Database file paths.

    Returns:
      bool: True if merging successful, False otherwise
    """
    try:
        target_database = os.path.join(DATA_FOLDER_PATH, "merged_db.sqlite")

        # Process database files in batches of 9 (SQLITE3 limit is 10)
        for i in range(0, len(file_paths), BATCH_SIZE):
            current_batch = file_paths[i : i + BATCH_SIZE]
            temp_target_database = (
                target_database
                if i == 0
                else os.path.join(DATA_FOLDER_PATH, f"temp_merge_{i}.sqlite")
            )

            # Merging logic
            merge_batch(current_batch, temp_target_database)
            if i > 0:
                # Merge temp database into target database
                merge_batch(
                    [temp_target_database], target_database, create_tables=False
                )
        return True

    except Exception as e:
        pass
        return False


def get_database_filepaths() -> List[str]:
    """Get the file paths of valid databases in DDT Data directory."""
    return [
        os.path.join(DATA_FOLDER_PATH, filename)
        for filename in os.listdir(DATA_FOLDER_PATH)
        if "FB20.DC" in filename
    ]


def cleanup_data_directory() -> bool:
    """
    Clean up DDT DATA directory:
    DELETES:
    *.db
    """
    pattern = os.path.join(DATA_FOLDER_PATH, "*.db")
    db_files = glob.glob(pattern)

    for db_file in db_files:
        try:
            if db_file != os.path.join(DATA_FOLDER_PATH, "fbhmi.db"):
                os.remove(db_file)
        except OSError as e:
            pass
            return False

    return True


def get_xml_file() -> str:
    """
    Get the path to the text dictionary file.

    Returns:
        str: Path to text dic or None if not found
    """

    pattern = os.path.join(DATA_FOLDER_PATH, "*textDic*")
    text_dic = glob.glob(pattern)

    if text_dic[0]:
        return text_dic[0]
    else:
        return None
