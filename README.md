# FB2 Data Download Tool

## Overview
An application for processing, analyzing, and visualizing data from FB2 Shearer data dumps.
The tool provides graphing capabilities and an alarm log. 

## Features
- **LZ4 Data import**: Process data from .LZ4 files from FB2 Shearer system

- **File Information**: Double click a file on the homescreen to view information about that file

- **Data Folder**: Creates a directory ~/Documents/DDT (if not found); each time the app is run, it will create a new directory inside that folder that holds the contents of the data analysis

- **Delete Data Folder Contents**: Required to use when processing a second data download within the same instance of the app being run

- **Custom Graphing**: Under Custom Graph on the Graphing screen, select an unlimited amount of data points to be graphed on the same graph

- **Preset Graphing**: Under Preset Graphs on the Graphing screen, select any number of predefined graphs (developer selected data points), to be graphed on separate graphs

- **Parameters**: JNA Current Limit and Cutter Amp Limit Parameters: Enter number to display as a reference line on the graph (Will only show on graphs that contain Haulage or Cutter Amps)

- **CSV Generation**: Select the "Generate CSV File with Raw Data" button on the graphing screen to include a CSV file with the selected data during graph generation

- **Incident Viewer**: Alarm log sorted by date/time

- **Incident Searching**: 2 search options for alarm log: Search by text (matches text to alarm text and renders only those alarms), and Search by occurrence (Finds first occurrence of the text and highlights it, press ENTER to go to the next occurrence of that text in the alarm log)

- **Help Text**: Click any incident in the alarm log to view help text about what the incident is

- **Report**: A small report on the incident viewer screen that displays the Shearer's serial number and date/time of the data download period

- **Time Zone Offset Detection**: Queries database for time zone offset parameter; if found, applies it to every timestamp, if not, prompts the user with a window to type in a custom offset

- **Status Text and Progress Bar**: Text and Progress bar at the bottom of every screen that shows what is currently happening in the program and how far along it is while doing that process


## Project Structure
```
assets/                          # Images and other dependencies
src/                             # Source code
    config/                      # Configuration files and constants
      chart_config.py            # Bokeh chart configuration model
      constants.py                # Apllication-wide constants
      incident_config.py         # Incident viewer configurations
      point_mapping.py           # IO, VFD, and Preset Graph definitions
      ui_config.py               # UI configuration presets 
   core/
      application_controller.py  # Main app controller
      workflow_manager.py        # Data processing workflow
   data/
      csv_generator.py           # Handles CSV creation
      database_manager.py        # Database operations
      incident_manager.py        # Incident management
      selected_data_manager.py   # Handles all USER selected data
   ui/
      components/
         custom_graph.py         # Custom graph UI component
         file_selector.py        # File selector UI component
         incident_viewer.py      # Alarm log UI component
         preset_graph.py         # Preset graph UI component
      screen/
         main_window.py          # Main application window
   util/
      file_util.py               # Various file utilities
      time_util.py               # Various time utilities
      validation.py              # File validation
   viz/
      graph_generator.py        # Bokeh graph generation
      plot_point.py              # Manages a single Bokeh plot
   main.py                       # Application entry point
```

## Workflow
1. **File Import**: Users select and import FB2 Shearer data dump files
2. **Graphing Route**: Workflow for graphing proceeds ->
3. **Data point selection**: Users select data points on the graphing screen and select GENERATE when ready
4. **Database Creation (if not found)**: Extracts the contents from .LZ4 Files and creates one MERGED database from all FB database files.
5. **Query**: Data points are queried from the MERGED database and stored in a python Dictionary
6. **Visualization**: Selected points/graphs are shown in the browser after completion of processing
7. **Incident Viewer Route**: Workflow for the incident viewer proceeds ->
8. **Database Creation (if not found)**: Extracts the contents from .LZ4 Files and creates one MERGED database
from all FB database files.
9. **Query**: Queries database for all incident ID's and help text
10. **Lookup**: Does a lookup in the extracted .XML file for matching ID's and grabs the corresponding text
11. **Population**: Populates the incident viewer component with all configured incidents
12. **Save Contents**: All imporant files (plots, CSV, .sqlite database) are saved after creation in 
~/Documents/DDT

## Installation

### Prerequisites
- Python 3.12 or higher
- Windows OS (developed for Windows environment)
- UV package manager

### Setup
1. Clone the repository:
   ```sh
   git clone https://ControlAutomation@dev.azure.com/ControlAutomation/C%20and%20A%20Projects/_git/FB2_DataDownloadTool
   cd FB2_DataDownloadTool
   ```
2. Install dependencies using UV
   ```sh
   uv sync
   ```
3. Verify installation:
   ```sh
   uv run src/main.py
   ```
## Basic Usage
```sh
# Start the application
uv run src/main.py

# Or with Python directly
python src/main.py
```

## Development

### Code Style
- **Black Formatter**: Automatic code formatting
- **Type Hints**: Full type annotation support
- **Modular Design**: Clear separation of concerns

## Best Practices
- Use type hints for all function signatures
- Follow PEP 8 style guidelines
- Add docstrings for all public methods
- Handle exceptions gracefully with user feedback


## Troubleshooting

### Common Issues
- **Timezone Missing from Data Dump**: Some data dumps will not include a time zone offset parameter, causing the "custom offset" dialog to show often

## Support
- **Contact**: Dane Ley (Intern) - dane.ley@global.komatsu

## Version History
- **v1.0**: Initial summer 2024 release with basic functionality and slow processing time
- **v2.0**: Summer 2025 release with improved functionality and processing time

---

*Built for shearer data analysis*
