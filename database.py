"""
Database Module for Price Tracker Pro
Handles all SQLite operations safely and efficiently.
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from config import Config

# Logging
logging.basicConfig(
    filename=Config.LOGS_DIR / "database.log",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = Config.DB_PATH


class Database:
    """Handles all database interactions for the Price Tracker."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    # ==============================
    # CONNECTION HANDLER
    # ==============================
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ==============================
    # INITIALIZATION
    # ==============================
    def _initialize_db(self) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_name TEXT,
                    product_url TEXT,
                    product_url2 TEXT,
                    site1_name TEXT,
                    site2_name TEXT,
                    site1_price REAL,
                    site2_price REAL,
                    site1_image TEXT,
                    site2_image TEXT,
                    target_price REAL,
                    current_price REAL,
                    currency TEXT,
                    image_url TEXT,
                    status TEXT DEFAULT 'Tracking',
                    notification_email TEXT,
                    last_checked TEXT,
                    is_tracking INTEGER DEFAULT 0
                )
                """
            )
            # Add new columns to existing table if they don't exist
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN product_url2 TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site1_name TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site2_name TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site1_price REAL")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site2_price REAL")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site1_image TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN site2_image TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN is_tracking INTEGER DEFAULT 0")
            except:
                pass
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    price REAL,
                    timestamp TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    type TEXT,
                    message TEXT,
                    timestamp TEXT
                )
                """
            )
            conn.commit()
            logger.info("Database initialized successfully.")

    # ==============================
    # PRODUCT MANAGEMENT
    # ==============================
    def add_product(
        self,
        user_id: int,
        product_name: str,
        product_url: str,
        product_url2: str = "",
        target_price: float = 0.0,
        notification_email: str = "",
        site1_name: str = "",
        site2_name: str = "",
        site1_price: float = 0.0,
        site2_price: float = 0.0,
        site1_image: str = "",
        site2_image: str = "",
    ) -> Optional[int]:
        """Add a new product to track (supports dual URLs)."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                # Try to insert; if UNIQUE constraint exists on product_url in older DBs,
                # this will be ignored and we'll update the existing row instead.
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO products
                    (user_id, product_name, product_url, product_url2, target_price, notification_email,
                     site1_name, site2_name, site1_price, site2_price, site1_image, site2_image, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        product_name,
                        product_url,
                        product_url2,
                        target_price,
                        notification_email,
                        site1_name,
                        site2_name,
                        site1_price,
                        site2_price,
                        site1_image,
                        site2_image,
                        datetime.now().isoformat(),
                    ),
                )
                product_id = int(cursor.lastrowid or 0)
                if product_id == 0:
                    # Already exists; find existing row by primary URL first
                    cursor.execute("SELECT id FROM products WHERE product_url = ?", (product_url,))
                    row = cursor.fetchone()
                    if not row and product_url2:
                        cursor.execute("SELECT id FROM products WHERE product_url = ?", (product_url2,))
                        row = cursor.fetchone()
                    if row:
                        product_id = int(row["id"]) if isinstance(row, sqlite3.Row) else int(row[0])
                        # Update the existing product with latest details
                        cursor.execute(
                            """
                            UPDATE products
                            SET user_id = ?, product_name = ?, product_url2 = ?, target_price = ?,
                                notification_email = ?, site1_name = ?, site2_name = ?,
                                site1_price = ?, site2_price = ?, site1_image = ?, site2_image = ?,
                                last_checked = ?, is_tracking = COALESCE(is_tracking, 0)
                            WHERE id = ?
                            """,
                            (
                                user_id,
                                product_name,
                                product_url2,
                                target_price,
                                notification_email,
                                site1_name,
                                site2_name,
                                site1_price,
                                site2_price,
                                site1_image,
                                site2_image,
                                datetime.now().isoformat(),
                                product_id,
                            ),
                        )
                        conn.commit()
                        logger.info(f"Updated existing product (ID: {product_id}) for URL conflict")
                        return product_id
                    else:
                        # Could not locate existing row; surface a helpful error
                        raise sqlite3.IntegrityError("Duplicate URL but existing record not found")
                else:
                    conn.commit()
                    logger.info(f"Added product: {product_name} (ID: {product_id})")
                    return product_id
        except Exception as e:
            logger.exception(f"Error adding product: {e}")
            return None

    def delete_product(self, product_id: int) -> None:
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
                logger.info(f"Deleted product {product_id}")
        except Exception as e:
            logger.exception(f"Error deleting product {product_id}: {e}")

    def clear_all_products(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM products")
                conn.execute("DELETE FROM price_history")
                conn.execute("DELETE FROM notifications")
                logger.info("All product data cleared.")
        except Exception as e:
            logger.exception(f"Error clearing database: {e}")

    # ==============================
    # PRODUCT QUERIES
    # ==============================
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_products(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM products")
            return [dict(row) for row in cursor.fetchall()]

    def get_user_products(self, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products WHERE user_id = ?"
        params = [user_id]
        if active_only:
            query += " AND status NOT LIKE 'Error%'"
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # ==============================
    # PRODUCT UPDATES
    # ==============================
    def update_product_price(self, product_id: int, current_price: float, image_url: str = "") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE products
                SET current_price = ?, image_url = ?, last_checked = ?
                WHERE id = ?
                """,
                (current_price, image_url, datetime.now().isoformat(), product_id),
            )
            conn.execute(
                "INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, ?)",
                (product_id, current_price, datetime.now().isoformat()),
            )

    def update_dual_prices(
        self,
        product_id: int,
        site1_price: float,
        site2_price: float,
        site1_image: str = "",
        site2_image: str = ""
    ) -> None:
        """Update prices from both sites"""
        with self._connect() as conn:
            # Determine current_price as the minimum of both
            current_price = min(site1_price, site2_price) if site1_price > 0 and site2_price > 0 else (site1_price if site1_price > 0 else site2_price)
            
            conn.execute(
                """
                UPDATE products
                SET site1_price = ?, site2_price = ?, current_price = ?,
                    site1_image = ?, site2_image = ?, last_checked = ?
                WHERE id = ?
                """,
                (site1_price, site2_price, current_price, site1_image, site2_image, datetime.now().isoformat(), product_id),
            )
            # Log both prices in history
            if site1_price > 0:
                conn.execute(
                    "INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, ?)",
                    (product_id, site1_price, datetime.now().isoformat()),
                )
            if site2_price > 0:
                conn.execute(
                    "INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, ?)",
                    (product_id, site2_price, datetime.now().isoformat()),
                )

    def set_tracking_status(self, product_id: int, is_tracking: bool) -> None:
        """Set whether product is being tracked"""
        with self._connect() as conn:
            conn.execute(
                "UPDATE products SET is_tracking = ? WHERE id = ?",
                (1 if is_tracking else 0, product_id),
            )

    def update_product_name(self, product_id: int, new_name: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE products SET product_name = ? WHERE id = ?", (new_name, product_id))

    def update_product_status(self, product_id: int, status: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE products SET status = ? WHERE id = ?", (status, product_id))

    # ==============================
    # PRICE HISTORY
    # ==============================
    def get_price_history(self, product_id: int) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT price, timestamp FROM price_history WHERE product_id = ? ORDER BY id DESC LIMIT 50",
                (product_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==============================
    # NOTIFICATIONS
    # ==============================
    def log_notification(self, product_id: int, notif_type: str, message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO notifications (product_id, type, message, timestamp) VALUES (?, ?, ?, ?)",
                (product_id, notif_type, message, datetime.now().isoformat()),
            )

    # ==============================
    # BULK PRICE CHECK (Optional)
    # ==============================
    def check_all_prices(self) -> List[Dict[str, Any]]:
        """Return all products for scheduled price checking."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM products")
            return [dict(row) for row in cursor.fetchall()]


# Global instance
db = Database()
