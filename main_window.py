"""
Price Tracker Pro - Modern Dashboard (Image + Info Card)
Built with CustomTkinter + Pillow
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import requests
from typing import Any, Dict, Optional
from datetime import datetime

# Internal modules
from database import db
from scraper import get_product_data
from scheduler import Scheduler
from notifications import notifier

# Optional plotting support
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class MainWindow(ctk.CTk):
    """Main Dashboard Window"""

    def __init__(self, user: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.title("📊 Price Tracker Pro Dashboard")
        self.geometry("1200x700")
        self.minsize(1100, 600)
        self.configure(fg_color="#EAF6FF")

        self.user: Dict[str, Any] = user or {"id": 1, "username": "Guest"}
        self.scheduler = Scheduler(self.user)
        self.freq_var = tk.StringVar(value="30m")

        # placeholders
        self.url_entry: Optional[ctk.CTkEntry] = None
        self.preview_frame: Optional[ctk.CTkFrame] = None
        self.image_label: Optional[ctk.CTkLabel] = None
        self.product_name_label: Optional[ctk.CTkLabel] = None
        self.product_price_label: Optional[ctk.CTkLabel] = None
        self.product_data: Optional[Dict[str, Any]] = None

        # colors
        self.sidebar_color = "#0078D7"
        self.header_color = "#00A3E0"
        self.content_bg = "#FFFFFF"

        self._build_sidebar()
        self._build_header()
        self._build_main_area()

    # ==============================
    # SIDEBAR + HEADER
    # ==============================
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, fg_color=self.sidebar_color, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(sidebar, text="📦 MENU", text_color="white",
                             font=("Segoe UI", 16, "bold"))
        title.pack(pady=(20, 30))

        buttons = [
            ("🧠 Fetch Info", self.fetch_product_info),
            ("💾 Save Product", self.save_product),
            ("📈 Graph", self.show_price_graph),
            ("💾 Export CSV", lambda: self.export_data("csv")),
            ("📘 Export Excel", lambda: self.export_data("excel")),
            ("🕒 Start Auto", self.start_scheduler),
            ("⏹ Stop Auto", self.stop_scheduler),
            ("🗑 Clear All", self.clear_all),
            ("🚪 Exit", self.exit_app)
        ]

        for text, command in buttons:
            ctk.CTkButton(
                sidebar, text=text, width=160, height=35,
                corner_radius=8, fg_color="white",
                text_color=self.sidebar_color,
                hover_color="#cce6ff", command=command
            ).pack(pady=5)

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, fg_color=self.header_color, corner_radius=0)
        header.pack(side="top", fill="x")

        ctk.CTkLabel(header, text="🏷️ PRICE TRACKER PRO", text_color="white",
                     font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        ctk.CTkLabel(header, text=f"👤 {self.user['username']}", text_color="white",
                     font=("Segoe UI", 14)).pack(side="right", padx=20)

    # ==============================
    # MAIN AREA
    # ==============================
    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color=self.content_bg, corner_radius=15)
        main.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # URL input
        input_frame = ctk.CTkFrame(main, fg_color="#f2f9ff", corner_radius=10)
        input_frame.pack(fill="x", pady=(10, 5), padx=10)

        ctk.CTkLabel(input_frame, text="Product URL:", text_color="#333",
                     font=("Segoe UI", 13, "bold")).pack(side="left", padx=10)
        self.url_entry = ctk.CTkEntry(input_frame, width=500,
                                      placeholder_text="Enter product URL...")
        self.url_entry.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(input_frame, text="Fetch Info", width=120, fg_color="#00A3E0",
                      command=self.fetch_product_info).pack(side="left", padx=5)

        # Product Preview Card
        self.preview_frame = ctk.CTkFrame(main, fg_color="white", corner_radius=15)
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.image_label.pack(pady=20)

        self.product_name_label = ctk.CTkLabel(self.preview_frame, text="Product Name",
                                               font=("Segoe UI", 18, "bold"),
                                               text_color="#222")
        self.product_name_label.pack(pady=5)

        self.product_price_label = ctk.CTkLabel(self.preview_frame, text="₹0.00",
                                                font=("Segoe UI", 20, "bold"),
                                                text_color="#00A3E0")
        self.product_price_label.pack(pady=5)

        ctk.CTkButton(self.preview_frame, text="Save Product", width=160,
                      fg_color="#00A3E0", command=self.save_product).pack(pady=15)

    # ==============================
    # PRODUCT FETCHING
    # ==============================
    def fetch_product_info(self):
        """Fetch and display product details"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a product URL.")
            return

        try:
            self.product_data = get_product_data(url)
            if not self.product_data:
                messagebox.showerror("Error", "Failed to fetch product data.")
                return

            name = self.product_data.get("name", "Unknown Product")
            price = self.product_data.get("price", 0.0)
            image_url = self.product_data.get("image")

            # update UI
            self.product_name_label.configure(text=name)
            self.product_price_label.configure(text=f"₹{price:,.2f}" if price else "N/A")

            # load image
            if image_url:
                try:
                    img_data = requests.get(image_url, timeout=10).content
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((300, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.configure(image=photo, text="")
                    self.image_label.image = photo
                except Exception:
                    self.image_label.configure(text="🖼️ No Image", image=None)
            else:
                self.image_label.configure(text="🖼️ No Image", image=None)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch product info:\n{e}")

    # ==============================
    # SAVE PRODUCT
    # ==============================
    def save_product(self):
        """Save product to database"""
        if not self.product_data:
            messagebox.showwarning("No Product", "Fetch a product first.")
            return

        try:
            db.add_product(
                user_id=self.user.get("id", 1),
                product_name=self.product_data.get("name", "Unnamed Product"),
                product_url=self.product_data.get("url", ""),
                target_price=self.product_data.get("price", 0.0) or 0.0,
                notification_email="",
                image_url=self.product_data.get("image", None), # type: ignore
            )
            messagebox.showinfo("Saved", "✅ Product saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product:\n{e}")

    # ==============================
    # EXPORT / GRAPH / SCHEDULER
    # ==============================
    def show_price_graph(self):
        messagebox.showinfo("Graph", "Graph feature coming soon!")

    def export_data(self, mode: str = "excel"):
        messagebox.showinfo("Export", "Export feature coming soon!")

    def start_scheduler(self):
        try:
            freq = self.freq_var.get()
            self.scheduler.set_frequency(freq)
            self.scheduler.schedule_all_products()
            self.scheduler.start()
            messagebox.showinfo("Scheduler", f"Scheduler started ({freq} interval).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scheduler:\n{e}")

    def stop_scheduler(self):
        try:
            self.scheduler.stop()
            messagebox.showinfo("Scheduler", "Scheduler stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop scheduler:\n{e}")

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all products?"):
            try:
                db.clear_all_products()
                self.product_name_label.configure(text="Product Name")
                self.product_price_label.configure(text="₹0.00")
                self.image_label.configure(text="", image=None)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear products:\n{e}")

    def exit_app(self):
        try:
            self.stop_scheduler()
        except Exception:
            pass
        self.destroy()


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app = MainWindow(user={"id": 1, "username": "demo_user"})
    app.mainloop()
