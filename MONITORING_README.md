# FragDenStaat Automated Monitoring System

**Automatically monitor your FragDenStaat FOI requests for new replies**

## What It Does

This system automatically checks your FragDenStaat account every 2 hours and:

✅ **Downloads data files** - Excel, CSV, PDF files automatically saved to `data/fragdenstaat_updates/`
📧 **Emails you about questions** - Get notified when responses need your attention
📝 **Logs acknowledgments** - Simple confirmations recorded to `monitoring.log`

## Quick Start

**For first-time setup (5 minutes):**

1. Get OAuth credentials from https://fragdenstaat.de/account/settings/applications/
2. Update `.env` with your Client ID and Client Secret
3. Run: `./scripts/install_monitoring.sh`

**See detailed instructions**: [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md)

## Files Created

### Core Scripts
- **`scripts/monitor_fragdenstaat.py`** - Main monitoring script (650 lines)
- **`scripts/monitor.sh`** - Wrapper script for cron/systemd
- **`scripts/test_setup.py`** - Configuration testing tool
- **`scripts/install_monitoring.sh`** - Automated installation

### Configuration
- **`.env`** - Updated with email/SMTP configuration
- **`pyproject.toml`** - Updated with `requests` dependency
- **`scripts/monitor_state.json`** - Auto-generated state file

### Scheduling
- **`cron/monitor.cron`** - Cron job configuration example
- **`systemd/fragdenstaat-monitor.service`** - Systemd service unit
- **`systemd/fragdenstaat-monitor.timer`** - Systemd timer unit

### Documentation
- **`MONITORING_QUICKSTART.md`** - 5-minute setup guide
- **`MONITORING_SETUP.md`** - Complete setup and configuration guide
- **`scripts/README.md`** - Script-specific documentation
- **`MONITORING_README.md`** - This file

### Generated at Runtime
- **`monitoring.log`** - Activity log (created on first run)
- **`data/fragdenstaat_updates/`** - Downloaded files (created as needed)

## Installation

### Option 1: Automated (Recommended)

```bash
cd /home/david/german-protest-registrations
./scripts/install_monitoring.sh
```

This will:
- Install dependencies
- Test your configuration
- Set up cron or systemd scheduling

### Option 2: Manual

See [MONITORING_SETUP.md](MONITORING_SETUP.md) for step-by-step instructions.

## Usage

### Run Manually
```bash
./scripts/monitor.sh
```

### View Logs
```bash
tail -f monitoring.log
```

### Test Configuration
```bash
./scripts/test_setup.py
```

### Check Scheduled Status

**Cron:**
```bash
crontab -l
```

**Systemd:**
```bash
sudo systemctl status fragdenstaat-monitor.timer
```

## How It Works

### 1. Authentication
- Uses OAuth2 password grant with your FragDenStaat credentials
- Tokens cached in `monitor_state.json` and auto-refreshed

### 2. Monitoring
- Fetches all your FOI requests via the API
- Checks each request for new messages since last run
- Tracks processed messages to avoid duplicates

### 3. Classification
Messages are automatically classified as:

- **Data files**: Contains `.xlsx`, `.xls`, `.csv`, `.pdf`, `.json`, `.xml`, `.zip`, or `.ods` files
- **Questions**: Contains keywords like "frage", "klärung", "rückfrage", "question", "clarification"
- **Acknowledgments**: Contains keywords like "eingangsbestätigung", "erhalten", "vielen dank"

### 4. Actions
- **Data files**: Downloaded to `data/fragdenstaat_updates/{request-slug}/`
- **Questions**: Email sent to `davidpomerenke@mailbox.org` with message details
- **Acknowledgments**: Logged to `monitoring.log`

## Features

### Production-Ready
✅ OAuth2 authentication with token caching
✅ Persistent state management (no duplicate processing)
✅ Comprehensive error handling and logging
✅ Graceful failure recovery
✅ Email notifications via SMTP
✅ Automatic file downloads with progress tracking

### Well-Documented
✅ 650+ lines of documented Python code
✅ Quick start guide (5 minutes)
✅ Complete setup guide (detailed)
✅ Inline code comments
✅ Example configurations

### Flexible Scheduling
✅ Cron job support (traditional)
✅ Systemd service/timer (modern)
✅ Configurable check frequency

### Secure
✅ Credentials stored in `.env` (not in code)
✅ `.env` already in `.gitignore`
✅ Systemd security hardening
✅ Token expiry and refresh handling

## Configuration

All configuration is in `.env`:

```bash
# FragDenStaat OAuth
FRAGDENSTAAT_EMAIL=davidpomerenke@mailbox.org
FRAGDENSTAAT_PASSWORD=your_password
FRAGDENSTAAT_OAUTH_CLIENT_ID=your_client_id
FRAGDENSTAAT_OAUTH_CLIENT_SECRET=your_client_secret

# Email Notifications
SMTP_HOST=smtp.mailbox.org
SMTP_PORT=587
SMTP_USER=davidpomerenke@mailbox.org
SMTP_PASSWORD=your_password
EMAIL_RECIPIENT=davidpomerenke@mailbox.org
```

## Customization

### Change Check Frequency
Edit cron schedule or systemd timer interval:
- Every hour: `0 * * * *`
- Every 4 hours: `0 */4 * * *`
- Twice daily: `0 8,20 * * *`

### Modify Message Classification
Edit keyword lists in `scripts/monitor_fragdenstaat.py`:
- `DATA_FILE_EXTENSIONS`
- `QUESTION_KEYWORDS`
- `ACKNOWLEDGMENT_KEYWORDS`

### Change Email Template
Edit `handle_question()` method in `MessageHandler` class

## Troubleshooting

### Authentication Issues
```bash
# Test OAuth credentials
./scripts/test_setup.py
```

### View Recent Activity
```bash
tail -n 50 monitoring.log
```

### Reset State (Force Recheck)
```bash
rm scripts/monitor_state.json
```

### Check Systemd Status
```bash
sudo systemctl status fragdenstaat-monitor.timer
sudo journalctl -u fragdenstaat-monitor.service -f
```

**See full troubleshooting guide**: [MONITORING_SETUP.md](MONITORING_SETUP.md#troubleshooting)

## API Reference

Uses FragDenStaat API v1: https://fragdenstaat.de/api/

**Endpoints used:**
- `POST /oauth/token/` - Authentication
- `GET /api/v1/user/` - Get user ID
- `GET /api/v1/request/` - List user's requests
- `GET /api/v1/message/` - Get messages for requests
- `GET /api/v1/attachment/` - Get attachments for messages

**OAuth Scopes:**
- `read:user` - Authentication and user info
- `read:request` - Access to FOI requests
- `read:document` - Access to attachments

## Requirements

- Python 3.11+
- Virtual environment (`.venv`)
- Dependencies: `requests`, `python-dotenv`
- FragDenStaat account with OAuth application
- SMTP access (mailbox.org by default)
- Cron or systemd for scheduling

## Security Notes

1. **Protect `.env`**: Contains sensitive credentials
   ```bash
   chmod 600 .env
   ```

2. **Never commit `.env`**: Already in `.gitignore`

3. **Secure state file**: Contains access tokens
   ```bash
   chmod 600 scripts/monitor_state.json
   ```

4. **Monitor log size**: Rotate if needed
   ```bash
   mv monitoring.log monitoring.log.$(date +%Y%m%d)
   ```

## Support

**Documentation:**
- Quick Start: [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md)
- Full Guide: [MONITORING_SETUP.md](MONITORING_SETUP.md)
- Scripts: [scripts/README.md](scripts/README.md)

**Testing:**
```bash
./scripts/test_setup.py  # Test configuration
./scripts/monitor.sh     # Manual test run
```

**FragDenStaat:**
- API Docs: https://fragdenstaat.de/api/
- OAuth Apps: https://fragdenstaat.de/account/settings/applications/

## License

Part of the german-protest-registrations project.

---

**Status**: ✅ Production-ready, fully documented, tested

**Last Updated**: 2026-01-15
