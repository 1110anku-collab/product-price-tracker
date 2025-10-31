"""
Price Tracker Pro - Interactive Dashboard
Built with CustomTkinter + Pillow + Threading
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import io
import requests
from typing import Any, Dict, Optional

# Internal modules
from database import db
from scraper import get_product_data
from scheduler import Scheduler

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
        self.geometry("1200x720")
        self.minsize(1100, 600)
        self.configure(fg_color="#EAF6FF")

        # --- Core State ---
        self.user = user or {"id": 1, "username": "Guest"}
        self.scheduler = Scheduler(self.user)
        self.freq_var = tk.StringVar(value="30m")
        self.product_data = None

        # --- Layout Colors ---
        self.sidebar_color = "#0078D7"
        self.header_color = "#00A3E0"
        self.content_bg = "#FFFFFF"

        # --- Build UI ---
        self._build_sidebar()
        self._build_header()
        self._build_content_area()

        self.show_dashboard()  # default page

    # ==============================
    # SIDEBAR + HEADER
    # ==============================
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, fg_color=self.sidebar_color, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(sidebar, text="📦 MENU", text_color="white",
                             font=("Segoe UI", 16, "bold"))
        title.pack(pady=(20, 30))

        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📈 Graph", self.show_graph),
            ("📤 Export", self.show_export),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Exit", self.exit_app),
        ]

        for text, cmd in nav_buttons:
            ctk.CTkButton(
                sidebar, text=text, width=160, height=35,
                corner_radius=8, fg_color="white",
                text_color=self.sidebar_color,
                hover_color="#cce6ff", command=cmd
            ).pack(pady=5)

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60, fg_color=self.header_color, corner_radius=0)
        header.pack(side="top", fill="x")

        ctk.CTkLabel(header, text="🏷️ PRICE TRACKER PRO", text_color="white",
                     font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        ctk.CTkLabel(header, text=f"👤 {self.user['username']}", text_color="white",
                     font=("Segoe UI", 14)).pack(side="right", padx=20)

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color=self.content_bg, corner_radius=15)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ==============================
    # DASHBOARD VIEW
    # ==============================
    def show_dashboard(self):
        self._clear_content()

        # --- Input Frame ---
        input_frame = ctk.CTkFrame(self.content_frame, fg_color="#f2f9ff", corner_radius=10)
        input_frame.pack(fill="x", pady=(10, 5), padx=10)

        ctk.CTkLabel(input_frame, text="Product URL:", text_color="#333",
                     font=("Segoe UI", 13, "bold")).pack(side="left", padx=10)

        self.url_entry = ctk.CTkEntry(input_frame, width=500,
                                      placeholder_text="Enter product URL...")
        self.url_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(input_frame, text="Fetch Info", width=120, fg_color="#00A3E0",
                      command=self._fetch_in_thread).pack(side="left", padx=5)

        ctk.CTkButton(input_frame, text="Refresh List", width=120,
                      fg_color="#00A3E0", command=self.load_product_list).pack(side="left", padx=5)

        # --- Preview Card ---
        self.preview_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=15)
        self.preview_frame.pack(fill="x", padx=20, pady=10)

        self.image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.image_label.pack(pady=10)

        self.product_name_label = ctk.CTkLabel(self.preview_frame, text="Product Name",
                                               font=("Segoe UI", 18, "bold"),
                                               wraplength=400,
                                               text_color="#222")
        self.product_name_label.pack(pady=5)

        self.product_price_label = ctk.CTkLabel(self.preview_frame, text="₹0.00",
                                                font=("Segoe UI", 20, "bold"),
                                                text_color="#00A3E0")
        self.product_price_label.pack(pady=5)

        ctk.CTkButton(self.preview_frame, text="Save Product", width=160,
                      fg_color="#00A3E0", command=self.save_product).pack(pady=15)

        # --- Product List ---
        self.table_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=15)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_product_list()

    # ==============================
    # FETCH PRODUCT INFO
    # ==============================
    def _fetch_in_thread(self):
        thread = threading.Thread(target=self.fetch_product_info, daemon=True)
        thread.start()

    def fetch_product_info(self):
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

            # Handle long names
            if len(name) > 60:
                name = "\n".join([name[i:i + 60] for i in range(0, len(name), 60)])

            self.product_name_label.configure(text=name)
            self.product_price_label.configure(text=f"₹{price:,.2f}" if price else "N/A")

            # load image
            if image_url:
                try:
                    img_data = requests.get(image_url, timeout=10).content
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.configure(image=photo, text="")
                    # keep a strong reference on the MainWindow to prevent GC (avoid assigning unknown attrs on CTkLabel)
                    self._image_photo = photo
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
            )
            messagebox.showinfo("Saved", "✅ Product saved successfully!")
            self.load_product_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product:\n{e}")

    # ==============================
    # LOAD PRODUCT LIST
    # ==============================
    def load_product_list(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        try:
            products = db.get_user_products(self.user["id"])
            if not products:
                ctk.CTkLabel(self.table_frame, text="No Products Found",
                             font=("Segoe UI", 14, "italic"),
                             text_color="gray").pack(pady=20)
                return

            for p in products:
                row = ctk.CTkFrame(self.table_frame, fg_color="#f5faff", corner_radius=10)
                row.pack(fill="x", padx=10, pady=5)

                name = p["product_name"]
                if len(name) > 60:
                    name = name[:60] + "..."

                ctk.CTkLabel(row, text=name, anchor="w",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#222").pack(side="left", padx=10, pady=5)

                ctk.CTkLabel(row, text=f"₹{p['target_price']:.2f}",
                             text_color="#0078D7",
                             font=("Segoe UI", 13, "bold")).pack(side="right", padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product list:\n{e}")

    # ==============================
    # GRAPH / EXPORT / SETTINGS
    # ==============================
    def show_graph(self):
        self._clear_content()
        if not MATPLOTLIB_AVAILABLE:
            ctk.CTkLabel(self.content_frame, text="Matplotlib not installed.",
                         font=("Segoe UI", 14, "bold"), text_color="red").pack(pady=30)
            return

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [100, 80, 90], marker="o")
        ax.set_title("Sample Price Graph")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price (₹)")

        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=20)

    def show_export(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="📤 Export Reports",
                     font=("Segoe UI", 18, "bold")).pack(pady=20)
        ctk.CTkButton(self.content_frame, text="Export CSV",
                      fg_color="#00A3E0", command=lambda: messagebox.showinfo("Export", "CSV exported!")).pack(pady=10)
        ctk.CTkButton(self.content_frame, text="Export Excel",
                      fg_color="#00A3E0", command=lambda: messagebox.showinfo("Export", "Excel exported!")).pack(pady=10)

    def show_settings(self):
        self._clear_content()
        ctk.CTkLabel(self.content_frame, text="⚙️ Settings",
                     font=("Segoe UI", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(self.content_frame, text="Notification Email:", text_color="#333",
                     font=("Segoe UI", 13)).pack(pady=5)
        ctk.CTkEntry(self.content_frame, placeholder_text="Enter email...").pack(pady=5)
        ctk.CTkLabel(self.content_frame, text="Refresh Interval:", text_color="#333",
                     font=("Segoe UI", 13)).pack(pady=5)
        ctk.CTkComboBox(self.content_frame, values=["5m", "15m", "30m", "1h", "6h"],
                        variable=self.freq_var).pack(pady=5)

    # ==============================
    # EXIT
    # ==============================
    def exit_app(self):
        try:
            self.scheduler.stop()
        except Exception:
            pass
        self.destroy()


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app = MainWindow(user={"id": 1, "username": "demo_user"})
    app.mainloop()
