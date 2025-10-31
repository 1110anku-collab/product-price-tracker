"""
Database Manager for Price Tracker Pro
Handles user accounts, product storage, price history, and notifications.
"""

import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import Config

# --------------------------------------------------------
# Logging setup
# --------------------------------------------------------
logging.basicConfig(
    filename=Config.LOGS_DIR / "database.log",
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all SQLite database operations"""

    def __init__(self, db_path: str = str(Config.DB_PATH)) -> None:
        self.db_path = db_path
        self._init_database()

    # --------------------------------------------------------
    # Connection Helpers
    # --------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # --------------------------------------------------------
    # Database Initialization
    # --------------------------------------------------------
    def _init_database(self) -> None:
        """Create all required tables if not existing"""
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    product_url TEXT NOT NULL,
                    image_url TEXT,
                    target_price REAL NOT NULL,
                    current_price REAL,
                    currency TEXT DEFAULT 'INR',
                    notification_email TEXT NOT NULL,
                    check_frequency INTEGER DEFAULT 30,
                    is_active INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'Active',
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    theme TEXT DEFAULT 'dark',
                    sound_enabled INTEGER DEFAULT 1,
                    email_notifications INTEGER DEFAULT 1,
                    desktop_notifications INTEGER DEFAULT 1,
                    default_currency TEXT DEFAULT 'INR',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )

            conn.commit()
            logger.info("Database initialized successfully")

    # --------------------------------------------------------
    # User Management
    # --------------------------------------------------------
    def create_user(self, username: str, password: str, email: str = "") -> bool:
        """Create a new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                    (username, password_hash, email),
                )
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
                conn.commit()
                logger.info(f"User created: {username}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Username already exists: {username}")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by username and password"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash),
                )
                user = cursor.fetchone()
                if user:
                    cursor.execute(
                        "UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now(), user["id"]),
                    )
                    conn.commit()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}", exc_info=True)
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by their ID"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}", exc_info=True)
            return None

    # --------------------------------------------------------
    # Product Management
    # --------------------------------------------------------
    def add_product(
        self,
        user_id: int,
        product_name: str,
        product_url: str,
        target_price: float,
        notification_email: str,
        check_frequency: int = 30,
        currency: str = "INR",
        image_url: Optional[str] = None,
    ) -> Optional[int]:
        """Add a product for tracking"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO products (
                        user_id, product_name, product_url, target_price,
                        notification_email, check_frequency, currency, image_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        product_name.strip(),
                        product_url.strip(),
                        target_price,
                        notification_email.strip(),
                        check_frequency,
                        currency,
                        image_url,
                    ),
                )
                product_id: int = int(cursor.lastrowid or 0)
                conn.commit()
                logger.info(f"Product added: {product_name} (ID {product_id})")
                return product_id
        except Exception as e:
            logger.error(f"Error adding product: {e}", exc_info=True)
            return None

    def get_user_products(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all products for a user"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM products WHERE user_id = ?"
                if active_only:
                    query += " AND is_active = 1"
                query += " ORDER BY created_at DESC"
                cursor.execute(query, (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user products: {e}", exc_info=True)
            return []

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single product by its ID"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting product: {e}", exc_info=True)
            return None

    def update_product_price(self, product_id: int, new_price: float, image_url: Optional[str] = None) -> None:
        """Update product price and add entry to price history"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET current_price = ?, last_checked = ? WHERE id = ?",
                    (new_price, datetime.now(), product_id),
                )
                cursor.execute(
                    "INSERT INTO price_history (product_id, price) VALUES (?, ?)",
                    (product_id, new_price),
                )
                if image_url:
                    cursor.execute("UPDATE products SET image_url = ? WHERE id = ?", (image_url, product_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating product price: {e}", exc_info=True)

    def update_product_status(self, product_id: int, status: str) -> None:
        """Update the tracking status of a product"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET status = ? WHERE id = ?", (status, product_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating product status: {e}", exc_info=True)

    def update_product_name(self, product_id: int, new_name: str) -> None:
        """Update a product's stored name"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET product_name = ? WHERE id = ?", (new_name, product_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating product name: {e}", exc_info=True)

    def delete_product(self, product_id: int) -> None:
        """Delete a single product"""
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                logger.info(f"Product deleted: {product_id}")
        except Exception as e:
            logger.error(f"Error deleting product: {e}", exc_info=True)

    # --------------------------------------------------------
    # Notifications and Settings
    # --------------------------------------------------------
    def log_notification(self, product_id: int, notification_type: str, message: str = "") -> None:
        """Record a notification event"""
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO notifications (product_id, notification_type, message) VALUES (?, ?, ?)",
                    (product_id, notification_type, message),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging notification: {e}", exc_info=True)

    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch settings for a given user"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user settings: {e}", exc_info=True)
            return None


# --------------------------------------------------------
# Global DB instance
# --------------------------------------------------------
db = DatabaseManager()
