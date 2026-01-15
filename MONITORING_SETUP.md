# FragDenStaat Monitoring System - Setup Guide

This document provides complete instructions for setting up and running the automated FragDenStaat monitoring system.

## Overview

The monitoring system automatically checks your FragDenStaat FOI requests every 2 hours and takes the following actions:

- **Data files attached**: Automatically downloads and organizes them in `data/fragdenstaat_updates/`
- **Question/clarification needed**: Sends email notification to `davidpomerenke@mailbox.org`
- **Simple acknowledgment**: Logs the message for your records

All actions are logged to `monitoring.log` in the repository root.

## Prerequisites

1. Python 3.8+ with virtual environment
2. Access to cron (Linux/macOS) or systemd (Linux)
3. Valid FragDenStaat OAuth credentials
4. SMTP server access for email notifications

## Installation

### Step 1: Install Python Dependencies

```bash
cd /home/david/german-protest-registrations

# Activate virtual environment
source .venv/bin/activate

# Install required packages
pip install requests python-dotenv
```

### Step 2: Configure OAuth Application

1. Log in to FragDenStaat: https://fragdenstaat.de/account/login/
2. Navigate to Settings → Applications: https://fragdenstaat.de/account/settings/applications/
3. Create a new OAuth application:
   - **Name**: "Monitoring System" (or any name you prefer)
   - **Redirect URIs**: Leave empty (not needed for password grant)
   - **Scopes**: Select:
     - `read:user` - Authentication status
     - `read:request` - Access to your requests
     - `read:document` - Access to documents/attachments
4. Save the application and copy the:
   - **Client ID**
   - **Client Secret**

### Step 3: Update .env File

The `.env` file has been updated with email configuration. Verify the OAuth credentials:

```bash
# FragDenStaat OAuth Credentials
FRAGDENSTAAT_EMAIL=davidpomerenke@mailbox.org
FRAGDENSTAAT_PASSWORD=your_password
FRAGDENSTAAT_OAUTH_CLIENT_ID=your_client_id_here
FRAGDENSTAAT_OAUTH_CLIENT_SECRET=your_client_secret_here

# Email Configuration
SMTP_HOST=smtp.mailbox.org
SMTP_PORT=587
SMTP_USER=davidpomerenke@mailbox.org
SMTP_PASSWORD=your_password
EMAIL_RECIPIENT=davidpomerenke@mailbox.org
```

**Note**: The email credentials default to your FragDenStaat credentials. mailbox.org uses the same email/password for SMTP.

### Step 4: Make Scripts Executable

```bash
chmod +x /home/david/german-protest-registrations/scripts/monitor.sh
chmod +x /home/david/german-protest-registrations/scripts/monitor_fragdenstaat.py
```

### Step 5: Test the Monitoring Script

Run manually to verify everything works:

```bash
/home/david/german-protest-registrations/scripts/monitor.sh
```

Check the output and log file:

```bash
tail -f /home/david/german-protest-registrations/monitoring.log
```

## Scheduling Options

You have two options for scheduling the monitoring: **cron** (traditional) or **systemd** (modern).

### Option A: Using Cron (Recommended for simplicity)

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line to run every 2 hours:
   ```
   0 */2 * * * /home/david/german-protest-registrations/scripts/monitor.sh
   ```

3. Save and exit. The cron job is now active.

4. Verify the cron job was added:
   ```bash
   crontab -l
   ```

**Alternative schedules:**
- Every hour: `0 * * * *`
- Every 4 hours: `0 */4 * * *`
- Business hours only (8 AM - 6 PM, Mon-Fri): `0 8-18/2 * * 1-5`
- Twice daily (8 AM and 8 PM): `0 8,20 * * *`

### Option B: Using systemd (Recommended for system integration)

1. Copy the service files to systemd directory:
   ```bash
   sudo cp /home/david/german-protest-registrations/systemd/fragdenstaat-monitor.service /etc/systemd/system/
   sudo cp /home/david/german-protest-registrations/systemd/fragdenstaat-monitor.timer /etc/systemd/system/
   ```

2. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable and start the timer:
   ```bash
   sudo systemctl enable fragdenstaat-monitor.timer
   sudo systemctl start fragdenstaat-monitor.timer
   ```

4. Check timer status:
   ```bash
   sudo systemctl status fragdenstaat-monitor.timer
   sudo systemctl list-timers --all | grep fragdenstaat
   ```

5. View logs:
   ```bash
   sudo journalctl -u fragdenstaat-monitor.service -f
   ```

**Systemd Commands:**
- Stop timer: `sudo systemctl stop fragdenstaat-monitor.timer`
- Disable timer: `sudo systemctl disable fragdenstaat-monitor.timer`
- Run service manually: `sudo systemctl start fragdenstaat-monitor.service`
- View last run: `sudo systemctl status fragdenstaat-monitor.service`

## File Structure

```
german-protest-registrations/
├── scripts/
│   ├── monitor_fragdenstaat.py    # Main monitoring script
│   ├── monitor.sh                  # Wrapper script
│   └── monitor_state.json          # Persistent state (auto-created)
├── cron/
│   └── monitor.cron                # Cron configuration example
├── systemd/
│   ├── fragdenstaat-monitor.service  # Systemd service
│   └── fragdenstaat-monitor.timer    # Systemd timer
├── data/
│   └── fragdenstaat_updates/       # Downloaded attachments (auto-created)
├── monitoring.log                  # Activity log (auto-created)
└── .env                            # Credentials (KEEP PRIVATE!)
```

## How It Works

### Authentication
- Uses OAuth2 password grant flow with your credentials
- Access tokens are cached in `monitor_state.json` and reused until expiry
- Automatically refreshes tokens when needed

### Message Detection
The script checks all your FOI requests for new messages since the last run.

### Message Classification
Each message is automatically classified:

1. **Data Files** - Contains attachments with extensions: `.xlsx`, `.xls`, `.csv`, `.pdf`, `.json`, `.xml`, `.zip`, `.ods`

2. **Question/Clarification** - Contains keywords like:
   - German: "frage", "klärung", "rückfrage", "erläuterung", "nachfrage", "benötigen wir", "könnten sie", "bitte um"
   - English: "question", "clarification", "please explain", "could you"

3. **Acknowledgment** - Contains keywords like:
   - German: "eingangsbestätigung", "erhalten", "vielen dank", "danke für", "eingegangen", "zur kenntnis"
   - English: "acknowledgment", "received", "thank you", "we received"

### Actions Taken

- **Data Files**: Downloaded to `data/fragdenstaat_updates/{request-slug}/{filename}`
- **Questions**: Email sent with message content and link to request
- **Acknowledgments**: Logged only

### State Management
- `monitor_state.json` tracks processed messages to avoid duplicates
- Stores last check timestamp
- Caches OAuth tokens

## Monitoring & Maintenance

### View Recent Activity
```bash
tail -n 100 /home/david/german-protest-registrations/monitoring.log
```

### View Real-time Logs
```bash
tail -f /home/david/german-protest-registrations/monitoring.log
```

### Check State File
```bash
cat /home/david/german-protest-registrations/scripts/monitor_state.json
```

### Reset State (Force Re-check All Messages)
```bash
rm /home/david/german-protest-registrations/scripts/monitor_state.json
```
**Warning**: This will cause all messages to be processed again, potentially sending duplicate notifications.

### Test Email Notifications
You can test the email system by manually running the script with `--test-email` flag (you'll need to modify the script to add this).

### Troubleshooting

**Problem**: "Authentication failed"
- **Solution**: Check OAuth credentials in `.env` file
- Verify the OAuth application still exists in FragDenStaat settings
- Check that scopes include: `read:user`, `read:request`, `read:document`

**Problem**: "Could not get user ID"
- **Solution**: Ensure the OAuth application has the `read:user` scope
- Try re-authenticating by removing the access token from `monitor_state.json`

**Problem**: "Error sending email"
- **Solution**: Verify SMTP credentials in `.env`
- For mailbox.org, ensure you're using your full email and password
- Check SMTP host (`smtp.mailbox.org`) and port (`587`)
- Verify your mailbox.org account allows SMTP access

**Problem**: Cron job not running
- **Solution**: Check cron is running: `systemctl status cron`
- Verify cron syntax: `crontab -l`
- Check for errors in system log: `grep CRON /var/log/syslog`
- Ensure scripts have execute permissions

**Problem**: Downloads failing
- **Solution**: Check internet connection
- Verify the download directory is writable
- Check disk space: `df -h`
- Look for specific errors in `monitoring.log`

## Security Considerations

1. **Protect .env file**:
   ```bash
   chmod 600 /home/david/german-protest-registrations/.env
   ```

2. **The .env file contains sensitive credentials** - never commit it to git (it's already in .gitignore)

3. **Monitor log file size** - rotate logs if they get too large:
   ```bash
   # Rotate logs manually
   mv monitoring.log monitoring.log.$(date +%Y%m%d)
   gzip monitoring.log.$(date +%Y%m%d)
   ```

4. **Secure state file** - contains access tokens:
   ```bash
   chmod 600 /home/david/german-protest-registrations/scripts/monitor_state.json
   ```

## Customization

### Change Check Frequency
Edit the cron schedule or systemd timer interval as shown in the scheduling sections above.

### Modify Message Classification
Edit the keyword lists in `scripts/monitor_fragdenstaat.py`:
- `DATA_FILE_EXTENSIONS` - file types to download
- `QUESTION_KEYWORDS` - keywords that trigger email notifications
- `ACKNOWLEDGMENT_KEYWORDS` - keywords for simple logging

### Change Email Template
Edit the `handle_question()` method in the `MessageHandler` class.

### Add Additional Recipients
Modify `EMAIL_RECIPIENT` in `.env` to include multiple addresses (comma-separated).

## Uninstallation

### Remove Cron Job
```bash
crontab -e
# Delete the line containing monitor.sh
```

### Remove Systemd Service
```bash
sudo systemctl stop fragdenstaat-monitor.timer
sudo systemctl disable fragdenstaat-monitor.timer
sudo rm /etc/systemd/system/fragdenstaat-monitor.service
sudo rm /etc/systemd/system/fragdenstaat-monitor.timer
sudo systemctl daemon-reload
```

### Remove Files
```bash
rm -rf /home/david/german-protest-registrations/scripts/monitor*
rm -rf /home/david/german-protest-registrations/systemd/
rm -rf /home/david/german-protest-registrations/cron/
rm /home/david/german-protest-registrations/monitoring.log
```

## Support

For issues or questions:
1. Check `monitoring.log` for error messages
2. Review this documentation
3. Check FragDenStaat API documentation: https://fragdenstaat.de/api/
4. Verify OAuth application settings: https://fragdenstaat.de/account/settings/applications/

## License

This monitoring system is part of the german-protest-registrations project.
