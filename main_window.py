"""
Dual Site Price Tracker - Enhanced Colorful GUI
Scrapes and compares prices from 2 websites simultaneously
"""
# pyright: reportMissingImports=false

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import threading
import logging
import csv
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

# Internal modules
from database import db
from dual_scraper import dual_scraper
from price_comparator import price_comparator
from scheduler import Scheduler
from notifications import notifier
from config import Config

# Logging
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """Enhanced Main Dashboard Window with Dual Site Support"""

    def __init__(self, user: Optional[Dict[str, Any]] = None):
        super().__init__()
        
        # Window configuration
        self.title("🛒 Dual Site Price Tracker")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Color scheme - vibrant and modern
        self.colors = {
            "primary": "#6366f1",      # Indigo
            "secondary": "#8b5cf6",    # Purple
            "accent": "#ec4899",       # Pink
            "success": "#10b981",      # Green
            "warning": "#f59e0b",      # Orange
            "danger": "#ef4444",       # Red
            "bg_light": "#f8fafc",     # Light gray
            "bg_dark": "#1e293b",       # Dark slate
            "card_bg": "#ffffff",       # White
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        }
        
        self.configure(fg_color=self.colors["bg_light"])
        
        # Core State
        self.user = user or {"id": 1, "username": "Guest"}
        self.scheduler = Scheduler(self.user)
        self.current_product_id = None
        
        # Initialize UI attributes
        self.amazon_name_label = None
        self.amazon_price_label = None
        self.amazon_data = None
        
        self.flipkart_name_label = None
        self.flipkart_price_label = None
        self.flipkart_data = None
        
        self.tracked_email = ""
        
        # Settings state
        self.desktop_notify = True
        self.sound_enabled = True
        self.check_frequency = "30 minutes"
        self.language = "English"
        
        # Build UI
        self._build_sidebar()
        self._build_main_content()
        
        # Show welcome page initially
        self.show_welcome_page()

    # ==============================
    # SIDEBAR
    # ==============================
    def _build_sidebar(self):
        """Build fixed sidebar with navigation"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=self.colors["primary"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo and Title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(30, 40))
        
        ctk.CTkLabel(
            logo_frame,
            text="🛒",
            font=("Segoe UI", 40)
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Price Tracker",
            text_color="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(5, 0))
        
        # Navigation Buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15)
        
        buttons = [
            ("🏠 Home", self.show_home_page),
            ("📊 Dashboard", self.show_dashboard_page),
            ("⚙️ Settings", self.show_settings_page),
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                width=180,
                height=45,
                fg_color="transparent",
                hover_color=self.colors["secondary"],
                text_color="white",
                font=("Segoe UI", 14, "bold"),
                anchor="w",
                corner_radius=10,
                command=command
            )
            btn.pack(pady=8)
        
        # User info at bottom
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.user['username']}",
            text_color="white",
            font=("Segoe UI", 12)
        ).pack()

    # ==============================
    # MAIN CONTENT AREA
    # ==============================
    def _build_main_content(self):
        """Build main content area that changes based on navigation"""
        self.main_content = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_light"],
            corner_radius=0
        )
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.content_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    # ==============================
    # WELCOME PAGE
    # ==============================
    def show_welcome_page(self):
        """Show welcome/logo page"""
        self._clear_content()
        
        welcome_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        welcome_frame.pack(expand=True, fill="both")
        
        # Logo
        logo_label = ctk.CTkLabel(
            welcome_frame,
            text="🛒",
            font=("Segoe UI", 100)
        )
        logo_label.pack(pady=(100, 30))
        
        # Title
        title_label = ctk.CTkLabel(
            welcome_frame,
            text="Price Tracker Pro",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 42, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="Compare Prices: Amazon vs Flipkart",
            text_color=self.colors["text_secondary"],
            font=("Segoe UI", 20)
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Quick access button
        quick_start_btn = ctk.CTkButton(
            welcome_frame,
            text="Get Started →",
            width=250,
            height=55,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            font=("Segoe UI", 18, "bold"),
            command=self.show_home_page
        )
        quick_start_btn.pack()

    # ==============================
    # HOME PAGE (URL Fetching Page)
    # ==============================
    def show_home_page(self):
        """Show main dashboard with partitioned design"""
        self._clear_content()
        
        # Make content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["secondary"]
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable_frame,
            text="📊 Amazon vs Flipkart Price Tracker",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(pady=(15, 25))
        
        # Main Container - Two Sides Partitioned (Equal Width)
        main_container = ctk.CTkFrame(
            scrollable_frame,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ==================== LEFT SIDE - AMAZON ====================
        amazon_side = ctk.CTkFrame(
            main_container,
            fg_color=self.colors["card_bg"],
            corner_radius=20
        )
        amazon_side.pack(side="left", fill="both", expand=True, padx=(0, 5))
        # Both sides will be equal width due to expand=True
        
        # Amazon Header
        amazon_header = ctk.CTkFrame(amazon_side, fg_color=self.colors["primary"], corner_radius=0, height=50)
        amazon_header.pack(fill="x", pady=(0, 15))
        amazon_header.pack_propagate(False)
        
        ctk.CTkLabel(
            amazon_header,
            text="🛒 AMAZON",
            text_color="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=12)
        
        # Amazon URL Section
        amazon_url_frame = ctk.CTkFrame(amazon_side, fg_color="transparent")
        amazon_url_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        self.url1_entry = ctk.CTkEntry(
            amazon_url_frame,
            height=40,
            placeholder_text="Enter Amazon product URL (amazon.in/dp/...)",
            font=("Segoe UI", 12),
            border_color=self.colors["border"],
            fg_color="white",
            border_width=2
        )
        self.url1_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        amazon_fetch_btn = ctk.CTkButton(
            amazon_url_frame,
            text="Fetch",
            width=100,
            height=40,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._fetch_single_site("amazon")
        )
        amazon_fetch_btn.pack(side="right")
        
        # Amazon Product Display Section
        self.amazon_display_frame = ctk.CTkFrame(
            amazon_side,
            fg_color="#f8fafc",
            corner_radius=15
        )
        self.amazon_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._build_product_display(self.amazon_display_frame, "amazon")
        
        # ==================== RIGHT SIDE - FLIPKART ====================
        flipkart_side = ctk.CTkFrame(
            main_container,
            fg_color=self.colors["card_bg"],
            corner_radius=20
        )
        flipkart_side.pack(side="right", fill="both", expand=True, padx=(5, 0))
        # Ensure equal width with Amazon
        
        # Flipkart Header
        flipkart_header = ctk.CTkFrame(flipkart_side, fg_color="#ff9800", corner_radius=0, height=50)
        flipkart_header.pack(fill="x", pady=(0, 15))
        flipkart_header.pack_propagate(False)
        
        ctk.CTkLabel(
            flipkart_header,
            text="🛒 FLIPKART",
            text_color="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=12)
        
        # Flipkart URL Section
        flipkart_url_frame = ctk.CTkFrame(flipkart_side, fg_color="transparent")
        flipkart_url_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        self.url2_entry = ctk.CTkEntry(
            flipkart_url_frame,
            height=40,
            placeholder_text="Enter Flipkart product URL (flipkart.com/...)",
            font=("Segoe UI", 12),
            border_color=self.colors["border"],
            fg_color="white",
            border_width=2
        )
        self.url2_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        flipkart_fetch_btn = ctk.CTkButton(
            flipkart_url_frame,
            text="Fetch",
            width=100,
            height=40,
            fg_color="#ff9800",
            hover_color="#fb8c00",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._fetch_single_site("flipkart")
        )
        flipkart_fetch_btn.pack(side="right")
        
        # Flipkart Product Display Section
        self.flipkart_display_frame = ctk.CTkFrame(
            flipkart_side,
            fg_color="#f8fafc",
            corner_radius=15
        )
        self.flipkart_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._build_product_display(self.flipkart_display_frame, "flipkart")
        
        # ==================== BOTTOM SECTION ====================
        # Email Section
        email_container = ctk.CTkFrame(
            scrollable_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=15
        )
        email_container.pack(fill="x", padx=10, pady=(10, 5))
        
        email_inner_frame = ctk.CTkFrame(email_container, fg_color="transparent")
        email_inner_frame.pack(pady=15, padx=20)
        
        ctk.CTkLabel(
            email_inner_frame,
            text="📧 Email:",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 14, "bold"),
            width=80,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.email_entry = ctk.CTkEntry(
            email_inner_frame,
            height=40,
            width=400,
            placeholder_text="Enter your email address",
            font=("Segoe UI", 12),
            border_color=self.colors["border"],
            fg_color="white",
            border_width=2
        )
        self.email_entry.pack(side="left", padx=(0, 10))
        
        add_email_btn = ctk.CTkButton(
            email_inner_frame,
            text="Add Email",
            width=150,
            height=40,
            fg_color=self.colors["success"],
            hover_color="#059669",
            font=("Segoe UI", 12, "bold"),
            command=self._add_email
        )
        add_email_btn.pack(side="left")
        
        # Start Tracking Button (Centered)
        track_button_container = ctk.CTkFrame(
            scrollable_frame,
            fg_color="transparent"
        )
        track_button_container.pack(fill="x", pady=20)
        
        self.start_tracking_btn = ctk.CTkButton(
            track_button_container,
            text="🎯 Start Price Tracking",
            width=300,
            height=55,
            fg_color=self.colors["success"],
            hover_color="#059669",
            font=("Segoe UI", 18, "bold"),
            command=self.start_tracking
        )
        self.start_tracking_btn.pack()
        
        # Product List Section
        list_frame = ctk.CTkFrame(
            scrollable_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=15
        )
        list_frame.pack(fill="both", expand=True, pady=(10, 20), padx=10)
        
        ctk.CTkLabel(
            list_frame,
            text="📦 Tracked Products",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 10))
        
        self.table_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.load_product_list()

    def _build_product_display(self, parent, site_name):
        """Build product display section (name and price only)"""
        # Product Name
        name_label = ctk.CTkLabel(
            parent,
            text="Product Name\n(Will appear after fetch)",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 16, "bold"),
            wraplength=350,
            justify="center"
        )
        name_label.pack(pady=(40, 20), padx=20)
        setattr(self, f"{site_name}_name_label", name_label)
        
        # Price
        price_label = ctk.CTkLabel(
            parent,
            text="₹0.00",
            text_color=self.colors["primary"],
            font=("Segoe UI", 28, "bold")
        )
        price_label.pack(pady=(20, 40))
        setattr(self, f"{site_name}_price_label", price_label)
        
        # Store data references
        setattr(self, f"{site_name}_data", None)

    # ==============================
    # FETCH PRODUCT INFO (SINGLE SITE)
    # ==============================
    def _fetch_single_site(self, site_name):
        """Fetch product info for a single site"""
        thread = threading.Thread(target=self._fetch_single_product, args=(site_name,), daemon=True)
        thread.start()

    def _fetch_single_product(self, site_name):
        """Fetch product from a single site"""
        if site_name == "amazon":
            url = self.url1_entry.get().strip()
            if not url:
                messagebox.showwarning("Missing URL", "Please enter Amazon product URL.")
                return
            # More lenient validation - just check if it's a URL
            url_lower = url.lower()
            if not ("http" in url_lower or "www" in url_lower or "amazon" in url_lower):
                messagebox.showwarning("Invalid URL", "Please enter a valid Amazon URL starting with http:// or https://")
                return
        else:  # flipkart
            url = self.url2_entry.get().strip()
            if not url:
                messagebox.showwarning("Missing URL", "Please enter Flipkart product URL.")
                return
            # More lenient validation
            url_lower = url.lower()
            if not ("http" in url_lower or "www" in url_lower or "flipkart" in url_lower):
                messagebox.showwarning("Invalid URL", "Please enter a valid Flipkart URL starting with http:// or https://")
                return
        
        # Show loading state
        name_label = getattr(self, f"{site_name}_name_label")
        price_label = getattr(self, f"{site_name}_price_label")
        
        if name_label:
            name_label.configure(text="🔄 Fetching product info...")
        if price_label:
            price_label.configure(text="...")
        
        try:
            # Scrape single URL
            result = dual_scraper._scrape_single_url(url)
            
            # Store data
            setattr(self, f"{site_name}_data", result)
            
            # Update UI
            self._update_site_display(site_name, result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch {site_name} product:\n{e}")
            if name_label:
                name_label.configure(text=f"❌ Error fetching")
            if price_label:
                price_label.configure(text="N/A")

    def _update_site_display(self, site_name, data):
        """Update display for a specific site (name and price only)"""
        name_label = getattr(self, f"{site_name}_name_label")
        price_label = getattr(self, f"{site_name}_price_label")
        
        if not name_label or not price_label:
            return
        
        if data.get("error"):
            name_label.configure(text=f"❌ Error: {data['error'][:50]}")
            price_label.configure(text="N/A")
            return
        
        # Update name
        name = data.get("name", "Unknown Product")
        if len(name) > 80:
            name = "\n".join([name[i:i+80] for i in range(0, len(name), 80)])
        name_label.configure(text=name)
        
        # Update price
        price_value = data.get("price_value", 0.0)
        price_text = data.get("price", "N/A")
        if price_value > 0:
            price_label.configure(text=f"₹{price_value:,.2f}")
        else:
            price_label.configure(text=price_text or "N/A")
    
    def _add_email(self):
        """Add email for notifications"""
        email = self.email_entry.get().strip()
        if not email or "@" not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        
        self.tracked_email = email
        messagebox.showinfo("Success", f"Email '{email}' has been added for notifications!")

    # ==============================
    # START TRACKING
    # ==============================
    def start_tracking(self):
        """Start tracking the product"""
        if not self.amazon_data or not self.flipkart_data:
            messagebox.showwarning(
                "Missing Data",
                "Please fetch product information from both Amazon and Flipkart first."
            )
            return
        
        if not self.tracked_email:
            messagebox.showwarning(
                "Missing Email",
                "Please add your email address for notifications first."
            )
            return
        
        try:
            # Get product data
            product_name = (
                self.amazon_data.get("name") or
                self.flipkart_data.get("name") or
                "Unknown Product"
            )
            
            url1 = self.url1_entry.get().strip()
            url2 = self.url2_entry.get().strip()
            
            amazon_price = self.amazon_data.get("price_value", 0.0)
            flipkart_price = self.flipkart_data.get("price_value", 0.0)
            
            amazon_image = self.amazon_data.get("image", "")
            flipkart_image = self.flipkart_data.get("image", "")
            
            # Save to database
            product_id = db.add_product(
                user_id=self.user.get("id", 1),
                product_name=product_name,
                product_url=url1,
                product_url2=url2,
                target_price=min(amazon_price, flipkart_price) if amazon_price > 0 and flipkart_price > 0 else (amazon_price if amazon_price > 0 else flipkart_price),
                notification_email=self.tracked_email,
                site1_name="Amazon",
                site2_name="Flipkart",
                site1_price=amazon_price,
                site2_price=flipkart_price,
                site1_image=amazon_image,
                site2_image=flipkart_image,
            )
            
            if product_id:
                # Set tracking status
                db.set_tracking_status(product_id, True)
                
                # Schedule for tracking
                self.scheduler.schedule_product(product_id, 30)  # Check every 30 minutes
                
                # Desktop notification if enabled (shows immediately)
                if self.desktop_notify:
                    try:
                        notifier.send_desktop_notification(
                            title="✅ Product Price Tracking Started!",
                            message=f"{product_name}\nAmazon: ₹{amazon_price:,.2f} | Flipkart: ₹{flipkart_price:,.2f}\nPrice tracking is now active!",
                            timeout=10
                        )
                        if self.sound_enabled:
                            notifier.play_alert_sound()
                    except Exception as e:
                        logger.error(f"Desktop notification error: {e}")
                
                # Send email notification that tracking has started
                try:
                    if self.tracked_email:
                        # Verify email config first
                        from config import Config
                        
                        # Check if .env file exists
                        env_path = Path(".env")
                        if not env_path.exists():
                            messagebox.showwarning(
                                "⚠️ .env File Missing",
                                "Email notifications require a .env file.\n\n"
                                "I can create one for you. The file will be created in:\n"
                                f"{env_path.resolve()}\n\n"
                                "After creation, please edit it with your Gmail credentials:\n"
                                "• EMAIL_ADDRESS=your-email@gmail.com\n"
                                "• EMAIL_PASSWORD=your-app-password (NOT regular password!)\n"
                                "• Get App Password from: https://myaccount.google.com/apppasswords\n\n"
                                "Click OK to create .env template file."
                            )
                            # Create .env from template
                            template_path = Path(".env.template")
                            if template_path.exists():
                                env_path.write_text(template_path.read_text(), encoding="utf-8")
                                messagebox.showinfo(
                                    "✅ .env File Created",
                                    f".env file created at:\n{env_path.resolve()}\n\n"
                                    "Please edit it with your email credentials and restart the app."
                                )
                            else:
                                # Create basic .env
                                env_content = """EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
"""
                                env_path.write_text(env_content, encoding="utf-8")
                                messagebox.showinfo(
                                    "✅ .env File Created",
                                    f".env file created. Please edit it with your Gmail credentials:\n\n"
                                    f"Location: {env_path.resolve()}\n\n"
                                    "You need to:\n"
                                    "1. Get Gmail App Password from:\n"
                                    "   https://myaccount.google.com/apppasswords\n"
                                    "2. Edit .env file with your email and app password\n"
                                    "3. Restart the application"
                                )
                            
                            # Reload config after creating .env (if method exists)
                            try:
                                if hasattr(Config, "reload_env"):
                                    Config.reload_env()  # type: ignore[attr-defined]
                            except Exception:
                                pass
                            
                            return  # Don't send email if .env was just created
                        
                        if not Config.EMAIL_ADDRESS or not Config.EMAIL_PASSWORD:
                            messagebox.showwarning(
                                "Email Not Configured",
                                "Please set up your .env file with email credentials.\n\n"
                                "Required in .env file:\n"
                                "EMAIL_ADDRESS=your-email@gmail.com\n"
                                "EMAIL_PASSWORD=your-gmail-app-password\n\n"
                                "Get App Password from:\n"
                                "https://myaccount.google.com/apppasswords\n\n"
                                "Desktop notification was sent instead."
                            )
                            return
                        
                        if not Config.validate_email_config():
                            messagebox.showwarning(
                                "Invalid Email Configuration",
                                "Email settings in .env file are invalid.\n\n"
                                "Please check:\n"
                                f"• EMAIL_ADDRESS: {Config.EMAIL_ADDRESS[:10]}...\n"
                                f"• EMAIL_PASSWORD: {'Set' if Config.EMAIL_PASSWORD else 'NOT SET'}\n"
                                f"• SMTP_SERVER: {Config.SMTP_SERVER}\n"
                                f"• SMTP_PORT: {Config.SMTP_PORT}\n\n"
                                "Desktop notification was sent instead."
                            )
                            return
                        
                        # Try to send email
                        email_sent = notifier.send_email_alert(
                            product_name=f"Price Tracking Started: {product_name}",
                            current_price=min(amazon_price, flipkart_price),
                            target_price=max(amazon_price, flipkart_price),
                            product_url=url1,
                            recipient_email=self.tracked_email
                        )
                        
                        if email_sent:
                            logger.info(f"✅ Tracking started email sent to {self.tracked_email}")
                        else:
                            # Prefer the precise error from notifier if available
                            error_details = getattr(notifier, "last_email_error", None) or "Unknown error"
                            # Fallback: try reading recent log lines
                            if error_details == "Unknown error":
                                log_file = Config.LOGS_DIR / "notifications.log"
                                try:
                                    if log_file.exists():
                                        with open(log_file, 'r', encoding='utf-8') as f:
                                            lines = f.readlines()
                                            error_lines = [l for l in lines[-15:] if 'error' in l.lower() or 'failed' in l.lower()]
                                            if error_lines:
                                                error_details = error_lines[-1].strip()
                                except Exception:
                                    pass

                            messagebox.showwarning(
                                "❌ Email Send Failed",
                                f"Could not send email to {self.tracked_email}.\n\n"
                                f"Error: {error_details}\n\n"
                                "Common fixes:\n"
                                "1. Use Gmail App Password (not regular password)\n"
                                "   Get it from: https://myaccount.google.com/apppasswords\n"
                                "2. Enable 2-Step Verification on Gmail\n"
                                "3. Check .env file has correct credentials\n"
                                "4. Check logs/notifications.log for details\n\n"
                                "Desktop notification was sent instead."
                            )
                except Exception as e:
                    logger.error(f"Failed to send tracking started email: {e}", exc_info=True)
                    messagebox.showwarning(
                        "Email Error",
                        f"Could not send confirmation email:\n\n{str(e)}\n\n"
                        "Please check:\n"
                        "1. .env file exists with email credentials\n"
                        "2. Using Gmail App Password (not regular password)\n"
                        "3. Check logs/notifications.log for details"
                    )
                
                messagebox.showinfo(
                    "✅ Tracking Started!",
                    f"Product tracking has been started!\n\n"
                    f"Product: {product_name}\n"
                    f"Amazon Price: ₹{amazon_price:,.2f}\n"
                    f"Flipkart Price: ₹{flipkart_price:,.2f}\n\n"
                    f"You'll be notified at '{self.tracked_email}' when the price drops.\n"
                    f"A confirmation email has been sent!"
                )
                
                # Clear inputs and displays
                self.url1_entry.delete(0, tk.END)
                self.url2_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                
                # Reset displays
                amazon_name = getattr(self, "amazon_name_label", None)
                amazon_price = getattr(self, "amazon_price_label", None)
                
                if amazon_name:
                    amazon_name.configure(text="Product Name\n(Will appear after fetch)")
                if amazon_price:
                    amazon_price.configure(text="₹0.00")
                
                flipkart_name = getattr(self, "flipkart_name_label", None)
                flipkart_price = getattr(self, "flipkart_price_label", None)
                
                if flipkart_name:
                    flipkart_name.configure(text="Product Name\n(Will appear after fetch)")
                if flipkart_price:
                    flipkart_price.configure(text="₹0.00")
                
                self.amazon_data = None
                self.flipkart_data = None
                self.tracked_email = ""
                
                # Reload product list
                self.load_product_list()
            else:
                # Try to surface a helpful reason from database logs
                error_details = "Unknown error"
                try:
                    from config import Config as _Cfg
                    log_file = _Cfg.LOGS_DIR / "database.log"
                    if log_file.exists():
                        with open(log_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            err_lines = [l for l in lines[-20:] if "ERROR" in l or "Exception" in l]
                            if err_lines:
                                error_details = err_lines[-1].strip()
                except Exception:
                    pass

                messagebox.showerror(
                    "Error",
                    f"Failed to save product to database.\n\nDetails: {error_details}"
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking:\n{e}")
            logger.error(f"Error starting tracking: {e}", exc_info=True)

    # ==============================
    # LOAD PRODUCT LIST
    # ==============================
    def load_product_list(self):
        """Load and display tracked products"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        try:
            products = db.get_user_products(self.user["id"])
            if not products:
                ctk.CTkLabel(
                    self.table_frame,
                    text="No tracked products yet. Fetch and track a product to get started!",
                    font=("Segoe UI", 13, "italic"),
                    text_color=self.colors["text_secondary"]
                ).pack(pady=20)
                return
            
            for p in products:
                row = ctk.CTkFrame(
                    self.table_frame,
                    fg_color="#f1f5f9",
                    corner_radius=10
                )
                row.pack(fill="x", padx=5, pady=5)
                
                # Product name
                name = p.get("product_name", "Unknown")
                if len(name) > 50:
                    name = name[:50] + "..."
                
                name_label = ctk.CTkLabel(
                    row,
                    text=name,
                    anchor="w",
                    font=("Segoe UI", 13, "bold"),
                    text_color=self.colors["text_primary"]
                )
                name_label.pack(side="left", padx=15, pady=10)
                
                # Prices
                price_text = ""
                site1_price = p.get("site1_price", 0.0) or 0.0
                site2_price = p.get("site2_price", 0.0) or 0.0
                
                if site1_price > 0 and site2_price > 0:
                    if site1_price < site2_price:
                        price_text = f"Amazon: ₹{site1_price:.2f} ⭐ (Cheaper) | Flipkart: ₹{site2_price:.2f}"
                    elif site2_price < site1_price:
                        price_text = f"Amazon: ₹{site1_price:.2f} | Flipkart: ₹{site2_price:.2f} ⭐ (Cheaper)"
                    else:
                        price_text = f"Amazon: ₹{site1_price:.2f} | Flipkart: ₹{site2_price:.2f} (Same Price)"
                elif site1_price > 0:
                    price_text = f"Amazon: ₹{site1_price:.2f}"
                elif site2_price > 0:
                    price_text = f"Flipkart: ₹{site2_price:.2f}"
                
                price_label = ctk.CTkLabel(
                    row,
                    text=price_text,
                    text_color=self.colors["primary"],
                    font=("Segoe UI", 12)
                )
                price_label.pack(side="left", padx=10, expand=True)
                
                # Status
                status = p.get("status", "Tracking")
                status_color = self.colors["success"] if "Tracking" in status else self.colors["warning"]
                
                status_label = ctk.CTkLabel(
                    row,
                    text=status,
                    text_color="white",
                    font=("Segoe UI", 11, "bold"),
                    fg_color=status_color,
                    corner_radius=5,
                    width=100
                )
                status_label.pack(side="right", padx=10)
                
                # Delete button
                delete_btn = ctk.CTkButton(
                    row,
                    text="🗑️",
                    width=40,
                    height=30,
                    fg_color=self.colors["danger"],
                    hover_color="#dc2626",
                    command=lambda pid=p["id"]: self._delete_product(pid)
                )
                delete_btn.pack(side="right", padx=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product list:\n{e}")

    def _delete_product(self, product_id: int):
        """Delete a tracked product"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            try:
                db.delete_product(product_id)
                self.scheduler.unschedule_product(product_id)
                self.load_product_list()
                messagebox.showinfo("Success", "Product deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product:\n{e}")

    # ==============================
    # DASHBOARD PAGE (CSV Tracking)
    # ==============================
    def show_dashboard_page(self):
        """Show dashboard page with CSV upload"""
        self._clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="📊 Dashboard - CSV Price Tracking",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(pady=(10, 30))
        
        # CSV Upload Section
        csv_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=15
        )
        csv_frame.pack(fill="x", padx=10, pady=10)
        
        csv_inner = ctk.CTkFrame(csv_frame, fg_color="transparent")
        csv_inner.pack(pady=20, padx=20)
        
        ctk.CTkLabel(
            csv_inner,
            text="📁 Upload CSV File:",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=(0, 15))
        
        self.csv_file_label = ctk.CTkLabel(
            csv_inner,
            text="No file selected",
            text_color=self.colors["text_secondary"],
            font=("Segoe UI", 12)
        )
        self.csv_file_label.pack(side="left", padx=(0, 15))
        
        upload_csv_btn = ctk.CTkButton(
            csv_inner,
            text="Choose CSV File",
            width=150,
            height=35,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            font=("Segoe UI", 12, "bold"),
            command=self._upload_csv_file
        )
        upload_csv_btn.pack(side="left")
        
        # Start Tracking Button
        start_csv_tracking_btn = ctk.CTkButton(
            self.content_frame,
            text="🚀 Start Tracking Price",
            width=300,
            height=50,
            fg_color=self.colors["success"],
            hover_color="#059669",
            font=("Segoe UI", 16, "bold"),
            command=self._start_csv_tracking
        )
        start_csv_tracking_btn.pack(pady=20)
        
        # CSV Products Display
        display_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=15
        )
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            display_frame,
            text="📦 CSV Products",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 10))
        
        self.csv_table_frame = ctk.CTkScrollableFrame(
            display_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.csv_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Clear All Button
        clear_all_btn = ctk.CTkButton(
            display_frame,
            text="🗑️ Clear All",
            width=200,
            height=40,
            fg_color=self.colors["danger"],
            hover_color="#dc2626",
            font=("Segoe UI", 13, "bold"),
            command=self._clear_csv_products
        )
        clear_all_btn.pack(pady=15)
        
        # Store CSV data
        if not hasattr(self, 'csv_products'):
            self.csv_products = []
        if not hasattr(self, 'csv_file_path'):
            self.csv_file_path = None

    def _upload_csv_file(self):
        """Upload and parse CSV file"""
        try:
            import pandas as pd  # local import to avoid global linter issue
        except Exception:
            messagebox.showerror(
                "Missing dependency",
                "pandas is not installed.\n\nInstall it with:\n    pip install pandas"
            )
            return
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Check required columns
            url_columns = [col for col in df.columns if "url" in col.lower()]
            if len(url_columns) < 2:
                messagebox.showerror("Error", "CSV must contain at least 2 URL columns (Amazon and Flipkart)")
                return
            
            self.csv_file_path = file_path
            self.csv_file_label.configure(text=f"Selected: {Path(file_path).name}")
            
            messagebox.showinfo("Success", f"CSV file loaded successfully!\nFound {len(df)} products.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV file:\n{e}")

    def _start_csv_tracking(self):
        """Start tracking products from CSV"""
        try:
            import pandas as pd  # local import to avoid global linter issue
        except Exception:
            messagebox.showerror(
                "Missing dependency",
                "pandas is not installed.\n\nInstall it with:\n    pip install pandas"
            )
            return
        if not self.csv_file_path:
            messagebox.showwarning("No File", "Please upload a CSV file first.")
            return
        
        try:
            # Clear previous CSV products display
            for widget in self.csv_table_frame.winfo_children():
                widget.destroy()
            
            # Read CSV
            df = pd.read_csv(self.csv_file_path)
            
            # Find URL columns
            amazon_col = None
            flipkart_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if "amazon" in col_lower and "url" in col_lower:
                    amazon_col = col
                elif "flipkart" in col_lower and "url" in col_lower:
                    flipkart_col = col
            
            if not amazon_col or not flipkart_col:
                messagebox.showerror("Error", "CSV must contain Amazon and Flipkart URL columns")
                return
            
            # Process each product
            self.csv_products = []
            
            def process_products():
                for idx, row in df.iterrows():
                    amazon_url = str(row[amazon_col]).strip() if pd.notna(row[amazon_col]) else ""
                    flipkart_url = str(row[flipkart_col]).strip() if pd.notna(row[flipkart_col]) else ""
                    
                    if not amazon_url or not flipkart_url:
                        continue
                    
                    # Scrape both URLs
                    result1, result2 = dual_scraper.scrape_dual_urls(amazon_url, flipkart_url)
                    
                    product_data = {
                        "name": result1.get("name") or result2.get("name") or f"Product {idx+1}",
                        "amazon_price": result1.get("price_value", 0.0),
                        "flipkart_price": result2.get("price_value", 0.0),
                        "amazon_url": amazon_url,
                        "flipkart_url": flipkart_url
                    }
                    
                    self.csv_products.append(product_data)
                    
                    # Update UI in main thread
                    self.after(0, lambda p=product_data: self._add_csv_product_to_display(p))
            
            # Process in background
            thread = threading.Thread(target=process_products, daemon=True)
            thread.start()
            
            messagebox.showinfo("Processing", "Fetching product data from CSV... This may take a while.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process CSV:\n{e}")

    def _add_csv_product_to_display(self, product_data):
        """Add a product to CSV display"""
        row = ctk.CTkFrame(
            self.csv_table_frame,
            fg_color="#f1f5f9",
            corner_radius=10
        )
        row.pack(fill="x", padx=5, pady=5)
        
        # Product Name
        name_label = ctk.CTkLabel(
            row,
            text=product_data["name"][:50] + ("..." if len(product_data["name"]) > 50 else ""),
            anchor="w",
            font=("Segoe UI", 13, "bold"),
            text_color=self.colors["text_primary"]
        )
        name_label.pack(side="left", padx=15, pady=10)
        
        # Prices
        price_text = f"Amazon: ₹{product_data['amazon_price']:.2f} | Flipkart: ₹{product_data['flipkart_price']:.2f}"
        price_label = ctk.CTkLabel(
            row,
            text=price_text,
            text_color=self.colors["primary"],
            font=("Segoe UI", 12)
        )
        price_label.pack(side="left", padx=10, expand=True)

    def _clear_csv_products(self):
        """Clear all CSV products"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all CSV products?"):
            for widget in self.csv_table_frame.winfo_children():
                widget.destroy()
            self.csv_products = []
            self.csv_file_path = None
            self.csv_file_label.configure(text="No file selected")
            messagebox.showinfo("Success", "All CSV products cleared!")

    # ==============================
    # SETTINGS PAGE
    # ==============================
    def show_settings_page(self):
        """Show settings page"""
        self._clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Settings",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(pady=(10, 30))
        
        # Settings Container
        settings_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=15
        )
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Language Preference
        lang_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            lang_frame,
            text="🌐 Language Preference:",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 14, "bold"),
            width=200,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        self.language_combo = ctk.CTkComboBox(
            lang_frame,
            values=["English", "Hindi", "Spanish", "French", "German"],
            width=200,
            height=35,
            command=self._on_language_change
        )
        self.language_combo.set(self.language)
        self.language_combo.pack(side="left")
        
        # Desktop Notification Checkbox
        notify_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        notify_frame.pack(fill="x", padx=30, pady=20)
        
        self.desktop_notify_var = tk.BooleanVar(value=self.desktop_notify)
        desktop_checkbox = ctk.CTkCheckBox(
            notify_frame,
            text="🔔 Notify for Desktop Popup",
            variable=self.desktop_notify_var,
            command=self._on_desktop_notify_change,
            font=("Segoe UI", 14),
            checkbox_width=20,
            checkbox_height=20
        )
        desktop_checkbox.pack(side="left")
        
        # Sound Alerts Checkbox
        sound_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        sound_frame.pack(fill="x", padx=30, pady=20)
        
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        sound_checkbox = ctk.CTkCheckBox(
            sound_frame,
            text="🔊 Enable Sound Alerts",
            variable=self.sound_var,
            command=self._on_sound_change,
            font=("Segoe UI", 14),
            checkbox_width=20,
            checkbox_height=20
        )
        sound_checkbox.pack(side="left")
        
        # Export Excel Button
        export_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=30, pady=20)
        
        export_btn = ctk.CTkButton(
            export_frame,
            text="📊 Export to Excel",
            width=250,
            height=45,
            fg_color=self.colors["success"],
            hover_color="#059669",
            font=("Segoe UI", 14, "bold"),
            command=self._export_to_excel
        )
        export_btn.pack()
        
        # Remove Products Dropdown
        remove_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        remove_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            remove_frame,
            text="🗑️ Remove Product:",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 14, "bold"),
            width=200,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        # Get tracked products for dropdown
        products = db.get_user_products(self.user["id"])
        product_names = [f"{p['id']}: {p['product_name'][:40]}" for p in products if p.get('is_tracking', 0)]
        
        self.remove_product_combo = ctk.CTkComboBox(
            remove_frame,
            values=product_names if product_names else ["No products tracked"],
            width=300,
            height=35,
            state="readonly" if product_names else "disabled"
        )
        self.remove_product_combo.pack(side="left", padx=(0, 15))
        
        remove_btn = ctk.CTkButton(
            remove_frame,
            text="Remove",
            width=100,
            height=35,
            fg_color=self.colors["danger"],
            hover_color="#dc2626",
            font=("Segoe UI", 12, "bold"),
            command=self._remove_product,
            state="normal" if product_names else "disabled"
        )
        remove_btn.pack(side="left")
        
        # Check Frequency Dropdown
        freq_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        freq_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            freq_frame,
            text="⏰ Check Frequency:",
            text_color=self.colors["text_primary"],
            font=("Segoe UI", 14, "bold"),
            width=200,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        self.frequency_combo = ctk.CTkComboBox(
            freq_frame,
            values=["5 minutes", "10 minutes", "15 minutes", "30 minutes", "1 hour", "2 hours", "10 hours", "1 day", "Manual"],
            width=200,
            height=35,
            command=self._on_frequency_change
        )
        self.frequency_combo.set(self.check_frequency)
        self.frequency_combo.pack(side="left")
        
        # Save Settings Button
        save_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        save_frame.pack(pady=30)
        
        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Save Settings",
            width=250,
            height=50,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            font=("Segoe UI", 16, "bold"),
            command=self._save_settings
        )
        save_btn.pack()

    def _on_language_change(self, value):
        """Handle language change"""
        self.language = value

    def _on_desktop_notify_change(self):
        """Handle desktop notification change"""
        self.desktop_notify = self.desktop_notify_var.get()

    def _on_sound_change(self):
        """Handle sound change"""
        self.sound_enabled = self.sound_var.get()

    def _on_frequency_change(self, value):
        """Handle frequency change"""
        self.check_frequency = value
        
        # Convert to minutes and update scheduler
        freq_map = {
            "5 minutes": 5,
            "10 minutes": 10,
            "15 minutes": 15,
            "30 minutes": 30,
            "1 hour": 60,
            "2 hours": 120,
            "10 hours": 600,
            "1 day": 1440,
            "Manual": 0
        }
        
        minutes = freq_map.get(value, 30)
        if minutes > 0:
            # Update scheduler frequency
            freq_text_map = {
                5: "5m", 10: "10m", 15: "15m", 30: "30m",
                60: "1h", 120: "2h", 600: "10h", 1440: "12h"
            }
            freq_text = freq_text_map.get(minutes, "30m")
            self.scheduler.set_frequency(freq_text)
            
            # Reschedule all products with new frequency
            products = db.get_user_products(self.user["id"], active_only=True)
            for product in products:
                if product.get('is_tracking', 0):
                    self.scheduler.unschedule_product(product['id'])
                    self.scheduler.schedule_product(product['id'], minutes)

    def _export_to_excel(self):
        """Export all products to Excel"""
        try:
            try:
                import pandas as pd  # local import to avoid global linter issues
            except Exception:
                messagebox.showerror(
                    "Missing dependency",
                    "pandas is not installed.\n\nInstall it with:\n    pip install pandas"
                )
                return
            products = db.get_user_products(self.user["id"])
            if not products:
                messagebox.showwarning("No Data", "No products to export.")
                return
            
            # Prepare data
            data = []
            for p in products:
                data.append({
                    "Product Name": p.get("product_name", ""),
                    "Amazon Price": p.get("site1_price", 0.0),
                    "Flipkart Price": p.get("site2_price", 0.0),
                    "Current Price": p.get("current_price", 0.0),
                    "Amazon URL": p.get("product_url", ""),
                    "Flipkart URL": p.get("product_url2", ""),
                    "Status": p.get("status", "")
                })
            
            # Save to Excel
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                try:
                    import pandas as pd  # local import to ensure availability
                except Exception:
                    messagebox.showerror(
                        "Missing dependency",
                        "pandas is not installed.\n\nInstall it with:\n    pip install pandas"
                    )
                    return
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Products exported to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{e}")

    def _remove_product(self):
        """Remove a tracked product"""
        selected = self.remove_product_combo.get()
        if not selected or selected == "No products tracked":
            return
        
        try:
            product_id = int(selected.split(":")[0])
            if messagebox.askyesno("Confirm", f"Remove product {selected.split(':', 1)[1]}?"):
                db.set_tracking_status(product_id, False)
                self.scheduler.unschedule_product(product_id)
                messagebox.showinfo("Success", "Product removed from tracking!")
                # Refresh settings page
                self.show_settings_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove product:\n{e}")

    def _save_settings(self):
        """Save all settings"""
        # Settings are already saved when changed
        messagebox.showinfo("Success", "Settings saved successfully!")

    # ==============================
    # EXIT
    # ==============================
    def exit_app(self):
        """Exit application"""
        try:
            self.scheduler.stop()
        except:
            pass
        self.destroy()


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app = MainWindow(user={"id": 1, "username": "demo_user"})
    app.mainloop()
