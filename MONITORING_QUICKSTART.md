# FragDenStaat Monitoring - Quick Start Guide

Get the monitoring system running in 5 minutes!

## Prerequisites Check

```bash
# Verify Python 3.8+
python3 --version

# Verify virtual environment exists
ls /home/david/german-protest-registrations/.venv
```

## Quick Setup

### 1. Install Dependencies (30 seconds)

```bash
cd /home/david/german-protest-registrations
source .venv/bin/activate
pip install requests python-dotenv
```

### 2. Get OAuth Credentials (2 minutes)

1. Go to: https://fragdenstaat.de/account/settings/applications/
2. Click "Create Application"
3. Fill in:
   - **Name**: Monitoring System
   - **Scopes**: Check `read:user`, `read:request`, `read:document`
4. Click "Save"
5. Copy the **Client ID** and **Client Secret**

### 3. Update .env File (1 minute)

Edit `/home/david/german-protest-registrations/.env` and update:

```bash
FRAGDENSTAAT_OAUTH_CLIENT_ID=YOUR_CLIENT_ID_HERE
FRAGDENSTAAT_OAUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
```

### 4. Make Scripts Executable (10 seconds)

```bash
chmod +x scripts/monitor.sh scripts/monitor_fragdenstaat.py
```

### 5. Test Run (30 seconds)

```bash
./scripts/monitor.sh
```

You should see output like:
```
================================================================================
FRAGDENSTAAT MONITORING SYSTEM - STARTING
================================================================================
Authenticating with FragDenStaat API...
✓ Authentication successful
...
```

### 6. Schedule with Cron (30 seconds)

```bash
crontab -e
```

Add this line:
```
0 */2 * * * /home/david/german-protest-registrations/scripts/monitor.sh
```

Save and exit. Done!

## Verify It's Working

### Check logs:
```bash
tail -f monitoring.log
```

### Check cron is scheduled:
```bash
crontab -l
```

### Check for downloaded files:
```bash
ls -la data/fragdenstaat_updates/
```

## What Happens Next?

Every 2 hours, the system will:
- ✅ Check all your FragDenStaat requests
- ✅ Download any new data files to `data/fragdenstaat_updates/`
- ✅ Email you at `davidpomerenke@mailbox.org` if responses need attention
- ✅ Log everything to `monitoring.log`

## Need More Details?

See the full documentation: [MONITORING_SETUP.md](MONITORING_SETUP.md)

## Troubleshooting

**"Authentication failed"**
→ Double-check your OAuth credentials in `.env`

**"No module named 'requests'"**
→ Run: `source .venv/bin/activate && pip install requests python-dotenv`

**"Permission denied"**
→ Run: `chmod +x scripts/monitor.sh scripts/monitor_fragdenstaat.py`

**Email not working**
→ The email config is already set to use your mailbox.org credentials
