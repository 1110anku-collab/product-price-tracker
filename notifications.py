"""Notification System for Price Tracker
Handles email alerts, desktop notifications, and sound alerts
"""

import os
import sys
import logging
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict, Any
from plyer import notification
from config import Config

# Platform-specific sound import
if sys.platform == 'win32':
    import winsound
else:
    winsound = None

# Logging setup
logging.basicConfig(
    filename=str(Config.LOGS_DIR / "notifications.log"),
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)


class NotificationManager:
    """Handles email, desktop, and sound notifications"""

    def __init__(self) -> None:
        self.email_enabled: bool = Config.validate_email_config()
        self.sound_enabled: bool = getattr(Config, "ENABLE_SOUND", True)

    # --------------------------------------------------------------------------
    # 🔔 Compatibility Wrapper for GUI & Scheduler
    # --------------------------------------------------------------------------
    def notify_price_change(self, changed: Optional[List[Dict[str, Any]]]) -> None:
        """Legacy API compatibility for older code calling notifier.notify_price_change()."""
        if not changed:
            logger.debug("notify_price_change() called with no changed items.")
            return

        for item in changed:
            try:
                name = str(item.get("product_name") or "Unknown Product")
                current_price = item.get("current_price")
                target_price = item.get("target_price")

                # Handle safe numeric conversion
                try:
                    current = float(current_price) if current_price is not None else 0.0
                except (TypeError, ValueError):
                    current = 0.0

                try:
                    target = float(target_price) if target_price is not None else 0.0
                except (TypeError, ValueError):
                    target = 0.0

                url = str(item.get("url") or "")
                email = str(item.get("email") or Config.EMAIL_ADDRESS)

                logger.debug(f"Triggering price change alert for {name} @ ₹{current:.2f}")

                self.send_price_alert(
                    product_name=name,
                    current_price=current,
                    target_price=target,
                    product_url=url,
                    email_address=email,
                    enable_sound=True,
                    enable_desktop=True
                )

            except Exception as e:
                logger.error(f"notify_price_change() error for {item}: {e}", exc_info=True)

    # --------------------------------------------------------------------------
    # 🎯 Core Notification Methods
    # --------------------------------------------------------------------------
    def send_price_alert(
        self,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str,
        email_address: Optional[str] = None,
        enable_sound: bool = True,
        enable_desktop: bool = True
    ) -> bool:
        """Send desktop + email + sound notification"""
        success = True
        try:
            if enable_desktop:
                self.send_desktop_notification(
                    title="🎉 Price Drop Alert!",
                    message=f"{product_name}\nNow ₹{current_price:.2f} (Target ₹{target_price:.2f})",
                    timeout=10
                )

            if email_address and self.email_enabled:
                email_success = self.send_email_alert(
                    product_name, current_price, target_price, product_url, email_address
                )
                success = success and email_success

            if enable_sound and self.sound_enabled:
                self.play_alert_sound()

            logger.info(f"✅ Notification sent successfully for {product_name}")
            return success

        except Exception as e:
            logger.error(f"Error sending price alert: {e}", exc_info=True)
            return False

    # --------------------------------------------------------------------------
    # 📧 Email Notifications
    # --------------------------------------------------------------------------
    def send_email_alert(
        self,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str,
        recipient_email: str
    ) -> bool:
        """Send email notification for price change."""
        # Check email configuration
        if not Config.EMAIL_ADDRESS or not Config.EMAIL_PASSWORD:
            logger.error("Email configuration missing: EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env file")
            return False
            
        if not Config.validate_email_config():
            logger.error(f"Email configuration invalid. EMAIL_ADDRESS: {Config.EMAIL_ADDRESS[:5]}...@..., Password set: {bool(Config.EMAIL_PASSWORD)}")
            return False
            
        if not self.email_enabled:
            logger.warning("Email configuration not valid — skipping email alert.")
            return False

        try:
            # Validate recipient email
            if not recipient_email or "@" not in recipient_email:
                logger.error(f"Invalid recipient email: {recipient_email}")
                return False
            
            msg = MIMEMultipart("alternative")
            msg["From"] = Config.EMAIL_ADDRESS
            msg["To"] = recipient_email
            
            logger.info(f"Attempting to send email to {recipient_email} from {Config.EMAIL_ADDRESS}")
            # Customize subject based on content
            if "Tracking Started" in product_name:
                msg["Subject"] = f"✅ Price Tracking Started: {product_name.replace('Price Tracking Started: ', '')}"
            else:
                msg["Subject"] = f"🎉 Price Drop Alert: {product_name}"

            # Customize email body based on type
            if "Tracking Started" in product_name:
                html_body = self._create_tracking_started_template(
                    product_name.replace("Price Tracking Started: ", ""), 
                    current_price, 
                    target_price, 
                    product_url
                )
                text_body = (
                    f"Price Tracking Started!\n\n"
                    f"Product: {product_name.replace('Price Tracking Started: ', '')}\n"
                    f"Initial Price: ₹{current_price:.2f}\n"
                    f"You'll receive notifications when the price drops!\n"
                    f"Link: {product_url}\n\n"
                    f"Sent by Price Tracker Pro on {datetime.now():%Y-%m-%d %H:%M:%S}"
                )
            else:
                html_body = self._create_email_template(product_name, current_price, target_price, product_url)
                text_body = (
                    f"Price Drop Alert!\n\n"
                    f"Product: {product_name}\n"
                    f"Now: ₹{current_price:.2f}\n"
                    f"Target: ₹{target_price:.2f}\n"
                    f"Link: {product_url}\n\n"
                    f"Sent by Price Tracker Pro on {datetime.now():%Y-%m-%d %H:%M:%S}"
                )

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                logger.info(f"Connecting to SMTP server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
                server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
                logger.info("SMTP login successful")
                server.send_message(msg)
                logger.info(f"📧 Email message sent successfully to {recipient_email}")

            logger.info(f"✅ Email sent successfully to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            logger.error(f"SMTP authentication failed — check credentials: {e}")
            logger.error(f"Email: {Config.EMAIL_ADDRESS}, Server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
            if "username and password" in error_msg.lower() or "535" in error_msg:
                logger.error("⚠️ This usually means you need to use a Gmail App Password, not your regular password!")
                logger.error("Get App Password from: https://myaccount.google.com/apppasswords")
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipient email refused: {recipient_email} - {e}")
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP server disconnected: {e}")
        except smtplib.SMTPConnectError as e:
            logger.error(f"Cannot connect to SMTP server {Config.SMTP_SERVER}:{Config.SMTP_PORT} - {e}")
            logger.error("Check your internet connection and firewall settings")
        except Exception as e:
            logger.error(f"Email sending error: {e}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")

        return False

    def _create_tracking_started_template(
        self,
        product_name: str,
        initial_price: float,
        target_price: float,
        product_url: str
    ) -> str:
        """HTML email template for tracking started notification"""
        # Extract actual product name if it starts with "Price Tracking Started:"
        display_name = product_name.replace("Price Tracking Started: ", "").strip()
        
        return f"""
        <html><body style="font-family:Arial,sans-serif;">
        <div style="background:linear-gradient(135deg,#10b981,#059669);color:white;padding:20px;border-radius:10px;">
            <h2>✅ Product Price Tracking Started!</h2>
            <p style="font-size:16px;">Your product is now being monitored for price drops on Amazon and Flipkart.</p>
            <div style="background:white;color:#333;padding:20px;border-radius:8px;margin-top:15px;">
                <h3 style="margin-top:0;">{display_name}</h3>
                <p><b>Initial Price:</b> ₹{initial_price:.2f}</p>
                <p><b>Tracking Status:</b> <span style="color:#10b981;font-weight:bold;">Active</span></p>
                <p style="margin-top:20px;">✅ You will receive email notifications whenever the price drops on either Amazon or Flipkart!</p>
                <a href="{product_url}" style="display:inline-block;background:#10b981;color:white;padding:12px 24px;text-decoration:none;border-radius:5px;margin-top:15px;">View Product</a>
            </div>
            <p style="margin-top:15px;font-size:12px;opacity:0.8;">Price Tracker Pro — {datetime.now():%d/%m/%Y %I:%M %p}</p>
        </div></body></html>
        """

    def _create_email_template(
        self,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str
    ) -> str:
        """HTML email body template"""
        savings = target_price - current_price
        percent = (savings / target_price * 100) if target_price > 0 else 0.0
        return f"""
        <html><body style="font-family:Arial,sans-serif;">
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:20px;border-radius:10px;">
            <h2>🎉 Price Drop Alert!</h2>
            <p>{product_name}</p>
            <div style="background:white;color:#333;padding:15px;border-radius:8px;">
                <p><b>Now:</b> ₹{current_price:.2f}</p>
                <p><b>Was:</b> ₹{target_price:.2f}</p>
                <p><b>You Save:</b> ₹{savings:.2f} ({percent:.1f}% off)</p>
                <a href="{product_url}" style="display:inline-block;background:#28a745;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">View Product</a>
            </div>
            <p style="margin-top:15px;font-size:12px;opacity:0.8;">Sent by Price Tracker Pro — {datetime.now():%d/%m/%Y %I:%M %p}</p>
        </div></body></html>
        """

    # --------------------------------------------------------------------------
    # 💻 Desktop + Sound Alerts
    # --------------------------------------------------------------------------
    def send_desktop_notification(self, title: str, message: str, timeout: int = 10) -> None:
        """Send cross-platform desktop notification"""
        try:
            if hasattr(notification, "notify"):
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Price Tracker Pro",
                    timeout=timeout,
                    toast=True
                )
        except Exception as e:
            logger.error(f"Desktop notification error: {e}", exc_info=True)

    def play_alert_sound(self) -> None:
        """Play simple alert sound"""
        try:
            if sys.platform == "win32" and winsound:
                threading.Thread(target=self._play_win_pattern, daemon=True).start()
            elif sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Glass.aiff &")
            else:
                os.system("canberra-gtk-play -i message &")
        except Exception as e:
            logger.warning(f"Sound alert failed: {e}")
            print("\a")

    def _play_win_pattern(self) -> None:
        try:
            import time
            winsound.Beep(800, 150)
            time.sleep(0.1)
            winsound.Beep(1000, 150)
            time.sleep(0.1)
            winsound.Beep(1200, 200)
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # ⚠️ Error + Test Notifications
    # --------------------------------------------------------------------------
    def send_error_notification(self, product_name: str, error_message: str) -> None:
        """Notify about scraping or logic errors"""
        try:
            self.send_desktop_notification(
                title="⚠️ Price Check Error",
                message=f"{product_name}\n{error_message}",
                timeout=8
            )
        except Exception as e:
            logger.error(f"Error notification failed: {e}", exc_info=True)

    def send_test_notification(self) -> bool:
        """Send a test notification"""
        try:
            self.send_desktop_notification(
                title="✅ Test Notification",
                message="Price Tracker Pro notification system works!",
                timeout=5
            )
            return True
        except Exception as e:
            logger.error(f"Test notification failed: {e}", exc_info=True)
            return False


# --------------------------------------------------------------------------
# ✅ Global instance for other modules
# --------------------------------------------------------------------------
notifier = NotificationManager()
