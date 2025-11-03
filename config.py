"""
Configuration Manager for Price Tracker Application
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from pathlib import Path


class Config:
    """Central configuration class for the Price Tracker app."""

    # ------------------------------------------------------------------
    # Base directories
    # ------------------------------------------------------------------
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    ASSETS_DIR: Path = BASE_DIR / "assets"

    # ------------------------------------------------------------------
    # Environment setup
    # ------------------------------------------------------------------
    # Load environment variables from .env file only once
    load_dotenv(BASE_DIR / ".env")

    # ------------------------------------------------------------------
    # Database settings
    # ------------------------------------------------------------------
    DB_PATH: Path = DATA_DIR / "price_tracker.db"

    # ------------------------------------------------------------------
    # Email configuration
    # ------------------------------------------------------------------
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    # ------------------------------------------------------------------
    # Application settings
    # ------------------------------------------------------------------
    DEFAULT_CHECK_FREQUENCY: int = int(os.getenv("DEFAULT_CHECK_FREQUENCY", "30"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ------------------------------------------------------------------
    # GUI settings
    # ------------------------------------------------------------------
    WINDOW_WIDTH: int = 1000
    WINDOW_HEIGHT: int = 700
    APP_NAME: str = "Price Tracker Pro"

    # ------------------------------------------------------------------
    # Frequency options (in minutes)
    # ------------------------------------------------------------------
    FREQUENCY_OPTIONS: dict[str, int] = {
        "5 minutes": 5,
        "10 minutes": 10,
        "30 minutes": 30,
        "1 hour": 60,
        "12 hours": 720,
    }

    # ------------------------------------------------------------------
    # Alert and display settings
    # ------------------------------------------------------------------
    ENABLE_SOUND: bool = True
    DEFAULT_CURRENCY: str = "INR"
    TIMEZONE: str = "Asia/Kolkata"
    TIME_FORMAT: str = "%d/%m/%Y %I:%M %p IST"
    DATE_FORMAT: str = "%d/%m/%Y"

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @classmethod
    def create_directories(cls) -> None:
        """Create required directories if they don't exist."""
        for directory in (cls.DATA_DIR, cls.LOGS_DIR, cls.ASSETS_DIR):
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"[Warning] Could not create directory {directory}: {e}")

    @classmethod
    def validate_email_config(cls) -> bool:
        """Return True if email and password are properly set."""
        return bool(
            cls.EMAIL_ADDRESS
            and cls.EMAIL_PASSWORD
            and "@" in cls.EMAIL_ADDRESS
            and len(cls.EMAIL_PASSWORD) > 0
        )
    
    @classmethod
    def reload_env(cls) -> None:
        """Reload environment variables from .env file."""
        load_dotenv(cls.BASE_DIR / ".env", override=True)
        # Update class variables
        cls.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
        cls.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
        cls.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        cls.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        cls.DEFAULT_CHECK_FREQUENCY = int(os.getenv("DEFAULT_CHECK_FREQUENCY", "30"))
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ----------------------------------------------------------------------
# Initialization on import
# ----------------------------------------------------------------------
Config.create_directories()

# ----------------------------------------------------------------------
# Optional utility function to access scraper easily
# ----------------------------------------------------------------------
try:
    from scraper import PriceScraper

    def get_product_data(url: str):
        """Compatibility wrapper for legacy imports."""
        scraper = PriceScraper()
        return scraper.scrape_price(url)

except ImportError:
    # scraper.py not yet available or missing dependency
    pass

# ---------------------------------------------------------------------
# Compatibility wrapper for older imports (used by config.py)
# ---------------------------------------------------------------------
def get_product_data(url: str):
    """
    Wrapper for backward compatibility.
    Allows 'from scraper import get_product_data' to work.
    """
    scraper = PriceScraper()
    return scraper.scrape_price(url)
