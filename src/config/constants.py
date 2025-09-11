"""Configuration constants for FB2 DDT."""

import os
import ctypes
from pathlib import Path


# Application constants
APP_NAME = "DDT"
APP_VERSION = "2.0"
APP_TITLE = "DDT"

# CSV file
CSV_TITLE = "data.csv"
CSV_HEADERS = ["Preset Name", "Point Name", "Timestamp", "Value"]

# Data extraction folder name
DATA_FOLDER_NAME = "data"

# Home for data folder
_home = Path.home()
DATA_FOLDER_HOME = str(_home / "Documents" / "DDT")

# Create new folder if folder exists
DATA_FOLDER_PATH = os.path.join(DATA_FOLDER_HOME, DATA_FOLDER_NAME)
_temp_data_folder_path = DATA_FOLDER_PATH
_counter = 1
while os.path.exists(DATA_FOLDER_PATH):
    DATA_FOLDER_PATH = f"{_temp_data_folder_path}({_counter})"
    _counter += 1

# File batching size
BATCH_SIZE = 9

# Screen size
_user32 = ctypes.windll.user32
_screensize = _user32.GetSystemMetrics(0), _user32.GetSystemMetrics(
    1
)  # SM_CXSCREEN, SM_CYSCREEN
SCREENSIZE = [int(_screensize[0] * 0.9895883), int(_screensize[1] * 0.775)]

# Time Zone Offset parNameTidx
TIME_ZONE_OFFSET_ID = 120184
