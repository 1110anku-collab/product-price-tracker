# 🏷️ Price Tracker Pro

**Automated product tracking with smart scraping, background scheduling, and real-time alerts — built with Python 3.11 and CustomTkinter.**

## 💡 Overview  
Product Price Tracker is a standalone desktop tool that continuously monitors prices from multiple e-commerce platforms.  
It automatically fetches, analyzes, and logs product data — helping you spot discounts instantly through email or desktop notifications.  

No browser extensions. No manual refreshes. Just plug in product URLs, and the tracker does the rest.

## ✨ Core Features  

### 🧩 Tracking & Monitoring
- Track **unlimited products** simultaneously  
- Support for **Amazon, Flipkart, Meesho, Myntra**, and most major sites  
- Adjustable check frequency (5 min → 12 hrs)  
- Smart retry system for failed requests  

### 📦 Data Handling
- Local SQLite database with persistent product history  
- Optional JSON user data (`users.json`) for lightweight setups  
- Real-time logging in `/logs/` for debugging and analysis  

### 🖥️ GUI & Visualization
- Clean, modern interface powered by **CustomTkinter**  
- Live dashboard showing all tracked products  
- Product cards include images, prices, and timestamps  
- Matplotlib graphs for price trends  

### 🔔 Notifications
- **Email alerts** for price drops (via SMTP, stored securely in `.env`)  
- **Desktop notifications** using **Plyer**  
- Optional sound alerts  

### 🛠️ Advanced Capabilities
- Multi-scraper logic in `combine_scraper.py` (for hybrid scraping)  
- Debugging utilities in `debug_product_fetching.py`  
- Currency conversion support via `currency_converter.py`  
- Configurable settings via `config.json`  
- Background job management with `scheduler.py`  

---

## 🧰 Tech Stack  

| Layer | Technology |
|-------|-------------|
| GUI | CustomTkinter |
| Scraping | Requests + BeautifulSoup |
| Data | SQLite3 + JSON |
| Visualization | Matplotlib |
| Alerts | Plyer + smtplib |
| Config | python-dotenv |
| OS | Windows 10+ |



## ⚙️ Installation  

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/product-price-tracker.git
cd product-price-tracker

### 2️⃣ Create and Activate Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```
### 3️⃣ Install Dependencies
```
pip install -r requirements.txt

```
### 4️⃣ Configure ```.env```
```
EMAIL_ADDRESS=youremail@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```
### 5️⃣ Start the App
```
python main.py
```

## 📁 Project Structure

```
PRODUCT-PRICE-TRACKER/
├── assets/ # Icons, fonts, and image assets
├── data/ # Product and export data
├── logs/ # Log files (scraper, scheduler, etc.)
├── .env # User email credentials (ignored by Git)
├── .env.template # Example environment configuration
├── advanced_features.py # Optional enhancements (e.g., automation)
├── combine_scraper.py # Multi-website scraping handler
├── config.json # Persistent user settings
├── config.py # Configuration management logic
├── currency_converter.py # Currency conversion handler
├── database.py # SQLite operations and schema
├── debug_product_fetching.py# Debugging tool for scraper verification
├── main_window.py # CustomTkinter GUI dashboard
├── main.py # Application entry point
├── notifications.py # Email and desktop notification system
├── scheduler.py # Background price-check manager
├── scraper.py # Primary scraping functions
├── start.bat # Quick launcher for Windows
├── users.json # Stores user preferences
└── requirements.txt # Dependency list
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
- ✅ Flipkart
- ✅ Meesho
- ✅ Myntra
- ✅ Nykaa

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
