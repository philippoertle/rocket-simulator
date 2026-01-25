"""
Application entry point for GUI.

Usage:
    python -m rocket_sim.gui
"""

import sys
from PySide6.QtWidgets import QApplication
from rocket_sim.gui.main_window import MainWindow


def main():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PET Rocket Simulator")
    app.setOrganizationName("Rocket Simulator Team")
    app.setApplicationVersion("0.1.0")

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
