import logging
import sys
import tkinter as tk
from pathlib import Path

LOG_PATH = Path(__file__).parent / "clock_app.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

from db_manager import DatabaseManager
from clock_state import ClockState
from themes import Theme
from clock_view import ClockView
from clock_controller import ClockController


def main() -> None:
    logger.info("========== Reloj Analógico - iniciando ==========")

    db = DatabaseManager()

    prefs = db.load_all_preferences()
    state = ClockState(
        timezone_name="America/Bogota",  # Siempre inicia con Bogotá, Colombia
        offset_seconds=int(prefs.get("offset_seconds", "0")),
        hour_format_24=prefs.get("hour_format_24", "false").lower() == "true",
    )

    root = tk.Tk()
    initial_theme = Theme.get(prefs.get("theme", "Claro"))
    view = ClockView(root, initial_theme)

    controller = ClockController(root, state, view, db)

    logger.info("Entering Tkinter main loop.")
    root.mainloop()
    logger.info("Application closed.")


if __name__ == "__main__":
    main()