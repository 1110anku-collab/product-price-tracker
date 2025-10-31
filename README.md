# 🏷️ Price Tracker Pro

A comprehensive Python application for automated price tracking with email alerts, desktop notifications, and analytics dashboard.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Core Functionality (20 Features)

1. **Multi-Product Tracking** - Track unlimited products simultaneously
2. **Customizable Check Frequency** - 5min, 10min, 30min, 1hr, 12hr intervals
3. **Email Alerts** - Automatic email notifications when price drops
4. **Desktop Notifications** - Windows toast notifications
5. **Sound Alerts** - Optional audio alerts for price drops
6. **Price History Graphs** - Visual price trends with Matplotlib
7. **Dark/Light Mode** - Customizable theme support
8. **User Authentication** - Secure login system with SQLite
9. **Data Export** - Export to CSV and Excel formats
10. **Currency Support** - Multiple currency conversion
11. **Smart Web Scraping** - Works with Amazon, eBay, Walmart, Target, and generic sites
12. **Error Handling & Retry** - Automatic retry on failures with logging
13. **Secure Email Storage** - Credentials stored in .env file
14. **Custom Email Templates** - Beautiful HTML email alerts
15. **Dashboard Summary** - Real-time product status overview
16. **Background Threading** - Non-blocking price checks
17. **Search & Filter** - Easy product management
18. **Auto-Save** - Automatic data persistence
19. **Comprehensive Logging** - Track all operations
20. **Product Status Tracking** - Active/Paused/Error states

### GUI Components

- **Home Tab** - Add new products to track
- **Dashboard Tab** - View and manage all tracked products
- **Graph Tab** - Price history visualization (Now with scrollable view for better visualization)
- **Settings Tab** - Configure app preferences

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10+ (for desktop notifications)
- Internet connection

### Step 1: Clone or Download

```bash
cd price-tracker-pro
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Email (Optional but Recommended)

1. Copy `.env.template` to `.env`:
   ```bash
   copy .env.template .env
   ```

2. Edit `.env` file with your email settings:
   ```env
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password_here
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

**For Gmail Users:**
- Enable 2-Factor Authentication
- Generate an App Password: https://myaccount.google.com/apppasswords
- Use the App Password (not your regular password)

## 📖 Usage

### Running the Application

```bash
python main.py
```

### First Time Setup

1. **Register Account**
   - Click "Register" tab
   - Enter username and password
   - Optionally add email
   - Click "Create Account"

2. **Login**
   - Enter your credentials
   - Click "Login"

### Adding Products

1. Go to **Home** tab
2. Enter product URL (Amazon, eBay, Walmart, etc.)
3. Set target price
4. Choose check frequency
5. Add notification email (optional)
6. Click "Fetch & Add Product"

### Managing Products

**Dashboard Tab:**
- **Check Now** - Manual price check
- **Pause/Resume** - Toggle tracking
- **Graph** - View price history
- **Delete** - Remove product
- **Start All** - Begin tracking all products
- **Stop All** - Pause all tracking
- **Export** - Save data to CSV/Excel

### Viewing Price History

1. Go to **Graph** tab
2. Select product from dropdown
3. View price trend chart

### Settings

Configure:
- Theme (Dark/Light/System)
- Email notifications
- Desktop notifications
- Sound alerts
- Email configuration (New enhanced UI for setting up email credentials)

## 📁 Project Structure

```
price-tracker-pro/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── database.py                # SQLite database handler
├── scraper.py                 # Web scraping module
├── scheduler.py               # Price check scheduler
├── notifications.py           # Email & desktop notifications
├── data_export.py             # CSV/Excel export
├── currency_converter.py      # Currency conversion
├── login_window.py            # Login GUI
├── main_window.py             # Main application GUI
├── requirements.txt           # Python dependencies
├── .env.template              # Environment template
├── README.md                  # Documentation
├── data/                      # Data directory
│   ├── price_tracker.db       # SQLite database
│   └── exports/               # Exported files
├── logs/                      # Application logs
└── assets/                    # Assets (if any)
```

## 🔧 Configuration

### Check Frequencies

- **5 minutes** - Very frequent updates (high server load)
- **10 minutes** - Frequent updates
- **30 minutes** - Default, balanced
- **1 hour** - Moderate updates
- **12 hours** - Twice daily

### Email Configuration

Supports any SMTP server:

**Gmail:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Outlook:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## 🌐 Supported Websites

### Optimized For:
- ✅ Amazon
- ✅ eBay
- ✅ Walmart
- ✅ Target
- ✅ Flipkart
- ✅ Meesho
- ✅ Myntra
- ✅ Nykaa
- ✅ Ajio
- ✅ Snapdeal
- ✅ Shopclues
- ✅ Pepperfry
- ✅ Croma
- ✅ Blinkit
- ✅ Firstcry

### Generic Support:
- ✅ Most e-commerce websites with standard HTML structure

## 📊 Database Schema

### Tables:
- **users** - User accounts
- **products** - Tracked products
- **price_history** - Historical price data
- **notifications** - Notification log
- **settings** - User preferences

## 🐛 Troubleshooting

### Email Not Working
- Check .env configuration
- Verify SMTP settings
- Use App Password for Gmail
- Check firewall settings

### Scraping Errors
- Some sites may block automated requests
- Try different check frequencies
- Check internet connection
- Review logs in `logs/scraper.log`

### Desktop Notifications Not Showing
- Enable notifications in Windows Settings
- Check Focus Assist settings
- Run as administrator (if needed)

### Database Errors
- Delete `data/price_tracker.db` to reset
- Check file permissions
- Review logs in `logs/database.log`

## 📝 Logging

Logs are stored in `logs/` directory:
- `app.log` - Main application
- `database.log` - Database operations
- `scraper.log` - Web scraping
- `scheduler.log` - Price checking
- `notifications.log` - Email/notifications
- `currency.log` - Currency conversion
- `export.log` - Data exports

## 🔒 Security

- Passwords hashed with SHA-256
- Email credentials in .env (gitignored)
- SQLite database with CASCADE deletes
- Input validation on all forms

## 🎯 Future Enhancements

- [ ] Cloud backup integration
- [ ] Browser extension
- [ ] Mobile app companion
- [ ] Price prediction ML model
- [ ] Multi-user collaboration
- [ ] Telegram/Discord notifications
- [ ] Price comparison features
- [ ] Wishlist sharing

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## ⚠️ Disclaimer

This tool is for personal use only. Respect website terms of service and rate limits. The developers are not responsible for any misuse.

## 💡 Tips

1. **Optimal Frequency**: Use 30min-1hr for most products
2. **Target Price**: Set realistic targets based on price history
3. **Email Setup**: Essential for alerts when you're away
4. **Regular Exports**: Backup your data periodically
5. **Multiple Products**: Track competitors or variants

## 📞 Support

For issues or questions:
- Check logs in `logs/` directory
- Review troubleshooting section
- Create GitHub issue

## 🎉 Acknowledgments

Built with:
- CustomTkinter - Modern GUI
- BeautifulSoup - Web scraping
- Matplotlib - Data visualization
- Plyer - Cross-platform notifications
- SQLite - Database
- Python ❤️

---

**Made with ❤️ for smart shoppers worldwide**

Happy Savings! 💰
