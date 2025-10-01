"""Application controller that coordinates UI and business logic."""

import threading
import gc

from config.constants import DATA_FOLDER_PATH, DATA_FOLDER_HOME
from core.workflow_manager import WorkflowManager
from data.database_manager import DatabaseManager
from ui.screen.main_window import MainWindow
from util.file_util import cleanup_data_directory, create_folder, get_xml_file


class ApplicationController:
    """Main application controller that coordinates UI and buisness logic."""

    def __init__(self):
        self.main_window = None
        self.database_manager = DatabaseManager()
        self.workflow_manager = WorkflowManager(self.database_manager)
        self.merged_file = None
        self.file_ready_event = threading.Event()

    def start_application(self) -> None:
        """Start the main application"""
        try:
            # Create data folder
            create_folder(DATA_FOLDER_PATH)

            # Create main window
            print("DEBUG: Creating MainWindow()")
            self.main_window = MainWindow()
            print("DEBUG: MainWindow created")

            # Set up UI callbacks
            self.setup_ui_callbacks()
            print("DEBUG: UI callbacks set up")

            # Start main loop
            print("DEBUG: Entering Tk mainloop")
            self.main_window.run()
            print("DEBUG: Tk mainloop exited")

        except Exception as e:
            # Do NOT swallow startup errors; write a log so packaged exe isn't silent
            try:
                import os, traceback
                from util.file_util import ensure_directory_exists

                ensure_directory_exists(DATA_FOLDER_HOME)
                log_path = os.path.join(DATA_FOLDER_HOME, "startup_error.log")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("DDT failed to start due to an exception.\n\n")
                    traceback.print_exc(file=f)
                    f.write("\nMessage: " + str(e) + "\n")
                # Best-effort user hint via console if available
                print(f"Startup error written to: {log_path}")
            except Exception:
                # If even logging fails, re-raise so outer handler can capture
                pass
            # Re-raise to let outer handler report/exit appropriately
            raise

    def setup_ui_callbacks(self) -> None:
        """Set up callbacks for UI events."""
        if not self.main_window:
            return

        # File selection callbacks
        self.main_window.set_callback("files_added", self.on_files_added)
        self.main_window.set_callback("files_removed", self.on_files_removed)
        self.main_window.set_callback("files_cleared", self.on_files_cleared)
        self.main_window.set_callback(
            "close_database_connections", self.close_database_connections
        )
        self.main_window.set_callback("database_deleted", self.on_database_deleted)

        # Graphing callbacks
        self.main_window.set_callback(
            "cleared_custom_points", self.on_cleared_custom_points
        )
        self.main_window.set_callback(
            "cleared_graph_presets", self.on_cleared_graph_presets
        )
        self.main_window.set_callback("generate_graphs", self.on_generate_graphs)

        # Incident callbacks
        self.main_window.set_callback("populate_incidents", self.on_populate_incidents)
        self.main_window.set_callback("populate_report", self.on_populate_report)

    def on_files_added(self, count: int) -> None:
        """Handle files added event."""
        try:
            # Log or process the file addition
            pass
            # Additional business logic could go here

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing added files: {e}")

    def on_files_removed(self, count: int) -> None:
        """Handle files removed event."""
        try:
            # Log or process the file removal
            pass
            # Additional business logic could go here

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing removed files: {e}")

    def on_files_cleared(self, count: int) -> None:
        """Handle files cleared event."""
        try:
            # Log or process the file clearing
            pass
            # Additional business logic could go here

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared files: {e}")

    def close_database_connections(self) -> None:
        """Close all open connections before deletion."""
        try:
            pass

            # Close WorkflowManager connections
            if self.workflow_manager:
                if hasattr(self.workflow_manager, "close_database_connections"):
                    self.workflow_manager.close_database_connections()

            # Close any direct connections
            if hasattr(self, "database_manager") and self.database_manager:
                self.database_manager.close()

            gc.collect()

            pass
        except Exception as e:
            pass

    def on_database_deleted(self) -> None:
        """Handle deletion of main database."""

        self.merged_file = None

        if self.workflow_manager:
            if hasattr(self.workflow_manager, "clear_cached_data"):
                self.workflow_manager.clear_cached_data()

    def on_cleared_custom_points(self, count: int) -> None:
        """Handle cleared custom points event."""
        try:
            # Log points clearing
            pass

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared points: {e}")

    def on_cleared_graph_presets(self, count: int) -> None:
        """Handle cleared presets event."""
        try:
            # Log clearing
            pass

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared presets: {e}")

    def on_generate_graphs(self, params: dict) -> None:
        """Handle graph generation request with collected parameters."""

        try:
            self.file_ready_event.clear()
            thread = threading.Thread(
                target=self._generate_graphs_background,
                args=(params,),
                name="GraphGeneration",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_populate_incidents(self, params: dict) -> None:
        """Handle incident population request."""

        try:
            thread = threading.Thread(
                target=self._populate_incidents_background,
                args=(params,),
                name="IncidentPopulation",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_populate_report(self, params: dict) -> None:
        """Handle populate request from incident viewer screen."""

        try:
            self.file_ready_event.clear()
            thread = threading.Thread(
                target=self._populate_report_background,
                args=(params,),
                name="ReportPopulation",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def _generate_graphs_background(self, params: dict) -> None:
        """Background thread for graph generation."""
        try:
            # Check if file has previously been created
            if self.merged_file is None:
                # Stage 1: File loading (20% progress)
                self._update_ui_safe("Loading files...", 0.1)
                if params["files"]:
                    self.merged_file = self.workflow_manager.load_files(params["files"])
                    self.file_ready_event.set()
                    self.workflow_manager.set_time_zone_offset(None)

                else:
                    self._update_ui_safe("No files selected on Home screen.", 0)
                    self.main_window.enable_graphing_btns()
                    return

            # Check if file loaded
            if self.merged_file != "":
                self._update_ui_safe("Files loaded", 0.2)
                self.main_window.enable_database_deletion()
            else:
                self._update_ui_safe("Failed to load merged file", 0)

            # Stage 2: Data processing (40% progress)
            self._update_ui_safe("Processing data...", 0.3)
            if params["io_points"] or params["vfd_points"] or params["preset_graphs"]:
                processed_data = self.workflow_manager.process_data(
                    params["io_points"],
                    params["vfd_points"],
                    params["preset_graphs"],
                )
                self._update_ui_safe("Data processed...", 0.4)
            else:
                self._update_ui_safe("No points or graphs selected for plotting.", 0)
                self.main_window.enable_graphing_btns()
                return

            # Stage 3: Generate CSV (optional 60% progess)
            if params["include_csv"] is True:
                self._update_ui_safe("Generating CSV File...", 0.5)
                self.workflow_manager.generate_csv(processed_data)
                self._update_ui_safe("CSV Generated", 0.6)

            # Stage 4: Graph data to Bokeh plots (80% progress)
            self._update_ui_safe("Creating plots...", 0.7)
            self.workflow_manager.generate_graphs(
                processed_data, params["jna_current_limit"], params["cutter_amp_limit"]
            )
            self._update_ui_safe("Plots generated...", 0.8)

            # Stage 5: Clean up directory (100% progress)
            self._update_ui_safe("Cleaning directory...", 0.9)
            cleanup_data_directory()
            self._update_ui_safe("Task complete.", 1)

            # Re-enable graphing buttons
            self.main_window.enable_graphing_btns()

        except Exception as e:
            self._update_ui_safe(f"An error occured when generating graphs: {e}", 0)

    def _populate_incidents_background(self, params: dict) -> None:
        """Background thread for incident population."""

        # Check if file has previously been created
        if self.merged_file is None:
            # Stage 1: File loading (20% progress)
            self._update_ui_safe("Loading files...", 0.1)
            self.merged_file = self.workflow_manager.load_files(params["files"])

            self.workflow_manager.set_time_zone_offset(None)

        self.file_ready_event.set()

        # Check if text dictionary exists
        if get_xml_file() is not None:

            self._update_ui_safe("Processing incidents...", 0.4)
            # Stage 2: Proccess incidents in DB
            incidents = self.workflow_manager.process_incidents()

            self._update_ui_safe("Rendering incidents...", 0.7)
            # Stage 3: Pass incidents to component for rendering
            params["incident_viewer"].populate_incidents(incidents)

            self._update_ui_safe("Population complete.", 1)

        else:  # No text dictionary was found
            self._update_ui_safe("Data download did not contain a text dictionary", 0.0)

    def _populate_report_background(self, params: dict) -> None:
        """Background thread for report population."""

        if not self.merged_file:
            self.file_ready_event.wait()  # Block until file creation

        self.workflow_manager.populate_report(params)

    def _update_ui_safe(self, message: str, progress: float) -> None:
        """
        Safely update UI from background thread.

        Parameters:
            message (str): Message to display to UI
            progress (float): Value from 0 - 1 to set progress bar
        """

        def update():
            self.main_window.update_status(message)
            self.main_window.update_progress(progress)

        self.main_window.root.after(0, update)


def create_application() -> ApplicationController:
    """
    Create and return a new application instance.

    Returns:
      ApplicationController: New application controller instance
    """
    return ApplicationController()


def run_application() -> None:
    """Run DDT application."""
    try:
        app = create_application()
        app.start_application()
    except Exception as e:
        # Log to user's Documents/DDT for visibility in both dev and packaged exe
        try:
            import os, traceback
            from util.file_util import ensure_directory_exists

            ensure_directory_exists(DATA_FOLDER_HOME)
            log_path = os.path.join(DATA_FOLDER_HOME, "startup_error.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n=== Application start failure ===\n")
                traceback.print_exc(file=f)
                f.write("\nMessage: " + str(e) + "\n")
            print(f"Startup error written to: {log_path}")
        except Exception:
            pass
        # Re-raise so a console build also shows the error
        raise
