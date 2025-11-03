# 📦 Installation Guide - Price Tracker Pro

## Prerequisites

- **Python 3.11 or higher** (Recommended: Python 3.11+)
- **Google Chrome Browser** (Required for web scraping)

## Installation Steps

### 1. Install Python Packages

Open your terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
# Essential GUI & Core Packages
pip install customtkinter==5.2.1
pip install pillow==10.1.0
pip install requests==2.31.0

# Web Scraping
pip install selenium==4.27.1
pip install undetected-chromedriver==3.5.5

# Data Handling
pip install pandas==2.1.4
pip install openpyxl==3.1.2

# Scheduling & Notifications
pip install schedule==1.2.0
pip install plyer==2.1.0

# Configuration
pip install python-dotenv==1.0.0
```

### 2. Required Packages Summary

#### **Core GUI:**
- `customtkinter` - Modern GUI framework
- `pillow` - Image processing
- `tkinter` - Built-in Python (usually included)

#### **Web Scraping:**
- `selenium` - Browser automation
- `undetected-chromedriver` - Anti-detection Chrome driver
- `requests` - HTTP requests for images

#### **Data Processing:**
- `pandas` - CSV/Excel file handling
- `openpyxl` - Excel file creation (.xlsx)

#### **Scheduling & Automation:**
- `schedule` - Price check scheduling
- `threading` - Built-in Python (for parallel scraping)

#### **Notifications:**
- `plyer` - Desktop notifications
- `smtplib` - Built-in Python (for email)

#### **Configuration:**
- `python-dotenv` - Environment variables (.env file)

### 3. Setup Email Configuration (Optional but Recommended)

Create a `.env` file in the project root:

```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Note:** For Gmail, you need to use an **App Password**, not your regular password.

### 4. Verify Installation

Run the application:

```bash
python main.py
```

If you encounter any import errors, install the missing packages using `pip install <package-name>`.

## Troubleshooting

### Chrome Driver Issues
- Make sure Google Chrome is installed
- `undetected-chromedriver` will automatically download the correct ChromeDriver version
- If issues persist, manually install ChromeDriver from: https://chromedriver.chromium.org/

### Missing Packages
- If you get `ModuleNotFoundError`, install the missing package:
  ```bash
  pip install <package-name>
  ```

### Excel Export Issues
- Make sure `openpyxl` is installed: `pip install openpyxl`

### Desktop Notifications Not Working
- Make sure `plyer` is installed: `pip install plyer`
- On Linux, you may need: `sudo apt-get install libnotify-bin`

## Quick Install (All-in-One)

```bash
pip install customtkinter pillow requests selenium undetected-chromedriver pandas openpyxl schedule plyer python-dotenv
```

## Project Structure Dependencies

The project uses these modules:
- `main_window.py` → customtkinter, PIL, pandas, tkinter
- `dual_scraper.py` → selenium, undetected-chromedriver
- `scheduler.py` → schedule
- `notifications.py` → plyer, smtplib (built-in)
- `database.py` → sqlite3 (built-in)
- `price_comparator.py` → notifications module
- `config.py` → python-dotenv

## Version Compatibility

- **Python:** 3.11+ (tested on 3.11, 3.12)
- **Chrome:** Latest version recommended
- **Windows:** Windows 10/11
- **Linux/Mac:** Should work but may need additional setup

---

**That's it! You're ready to run the Price Tracker Pro! 🚀**

