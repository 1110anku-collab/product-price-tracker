"""
Price Tracker Pro - Main Entry Point
Compatible with Python 3.11+

Features:
- Multi-product price tracking
- Email and desktop notifications
- Customizable check frequencies (5m – 12h)
- Price history graphs
- Dark/Light mode
- CSV/Excel export
- User authentication (optional)
"""

import sys
import logging
from pathlib import Path

# ------------------------------------------------------------
# DPI fix for Windows (avoids blurry GUI on high-DPI screens)
# ------------------------------------------------------------
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# ------------------------------------------------------------
# Configuration and Logging
# ------------------------------------------------------------
try:
    from config import Config
except ImportError:
    print("❌ Missing config.py! Please ensure it exists in your project folder.")
    sys.exit(1)

LOGS_DIR = Path(getattr(Config, "LOGS_DIR", Path("./logs")))
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOGS_DIR / "app.log"),
    level=getattr(logging, "Config.LOG_LEVEL", logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("PriceTrackerPro")


# ------------------------------------------------------------
# Import GUI main window
# ------------------------------------------------------------
try:
    from main_window import MainWindow
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("➡️  Run: pip install -r requirements.txt")
    sys.exit(1)


# ------------------------------------------------------------
# Application Controller
# ------------------------------------------------------------
class PriceTrackerApp:
    """Main application controller (login skipped)."""

    def __init__(self):
        logger.info("Starting Price Tracker Pro ...")
        self.main_window = None

        # Check environment setup
        self.ensure_env_file()

        # Launch GUI
        self.launch_main_window()

    def ensure_env_file(self):
        """Ensure .env exists; create it from template if missing."""
        env_file = Path(".env")
        if not env_file.exists():
            print("⚠️  .env file missing — creating from template (if available).")
            template = Path(".env.template")
            if template.exists():
                env_file.write_text(template.read_text(), encoding="utf-8")
                print("✅ .env file created. Please update your email settings.")
            else:
                print("❌ .env.template not found. Email notifications may not work.")

    def launch_main_window(self):
        """Open the main dashboard."""
        user = {"id": 1, "username": "DemoUser"}  # Demo user for now
        self.main_window = MainWindow(user)
        self.main_window.mainloop()
        logger.info("Application closed.")


# ------------------------------------------------------------
# Program Entry Point
# ------------------------------------------------------------
def main():
    print("=" * 60)
    print("🏷️  PRICE TRACKER PRO")
    print("=" * 60)
    print("Automated Price Tracking with Notifications & Analytics")
    print("=" * 60)
    print()

    try:
        PriceTrackerApp()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        logger.info("Application interrupted.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error("Fatal error", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
