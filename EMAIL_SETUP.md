# 📧 Email Setup Guide - Price Tracker Pro

## Why emails aren't working?

If you're not receiving confirmation emails, follow these steps:

## Step 1: Create .env File

Create a file named `.env` in your project root directory with the following content:

```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Step 2: Get Gmail App Password

For Gmail, you **CANNOT use your regular password**. You need to generate an **App Password**:

### Instructions for Gmail:

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Under **2-Step Verification**, make sure it's **ON**
4. Scroll down to **App passwords**
5. Click **App passwords**
6. Select app: **Mail**
7. Select device: **Other (Custom name)**
8. Enter: **Price Tracker**
9. Click **Generate**
10. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)
11. Paste this password in your `.env` file (remove spaces: `abcdefghijklmnop`)

## Step 3: Verify .env File Location

Make sure `.env` is in the same folder as `main.py`:
```
product-price-tracker/
  ├── .env          ← Should be here
  ├── main.py
  ├── config.py
  └── ...
```

## Step 4: Test Email Configuration

After setting up `.env`, run the application and try tracking a product. You should receive:
- Desktop notification (if enabled)
- Email confirmation

## Troubleshooting

### Issue: "Email configuration not valid"
- **Solution**: Check that `.env` file exists and has all required fields

### Issue: "SMTP authentication failed"
- **Solution**: Make sure you're using App Password, not regular password
- **Solution**: Verify 2-Step Verification is enabled on Gmail

### Issue: "Recipient email refused"
- **Solution**: Check that the email address you entered is correct

### Issue: Email goes to spam
- **Solution**: Check your spam/junk folder
- **Solution**: Mark emails from the app as "Not Spam"

## Alternative Email Providers

### Outlook/Hotmail:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo:
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## Important Notes

1. **Never commit .env file to git** - It contains your password!
2. **App Passwords are safer** than using your main password
3. **Gmail requires App Password** if 2-Step Verification is enabled
4. The email will be sent **immediately** when you click "Start Price Tracking"

---

**Need help?** Check the logs folder for detailed error messages: `logs/notifications.log`

