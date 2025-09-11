"""
DDT (Data Download Tool) - Main Entry Point

A data visualization application for Longwall Shearer diagnostics.
Processes, SQlite databases, creates interactive Bokeh charts, and provides
a CustomTkinter GUI for user interaction

Author: Dane Ley
Version: 2.0
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent  # Go up one level to DDT directory
sys.path.insert(0, str(project_root))

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))


def main():
    """Main entry point for DDT"""
    from core.application_controller import run_application

    run_application()


if __name__ == "__main__":
    main()
