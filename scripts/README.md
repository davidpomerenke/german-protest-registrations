# FragDenStaat Monitoring Scripts

This directory contains the automated monitoring system for FragDenStaat FOI requests.

## Files

- **`monitor_fragdenstaat.py`** - Main monitoring script (Python 3.11+)
- **`monitor.sh`** - Wrapper script for cron/systemd execution
- **`monitor_state.json`** - Persistent state file (auto-generated)

## Quick Commands

### Run monitoring manually
```bash
./monitor.sh
```

### View logs
```bash
tail -f ../monitoring.log
```

### Check state
```bash
cat monitor_state.json | python3 -m json.tool
```

### Reset state (force recheck all messages)
```bash
rm monitor_state.json
```

## Documentation

- **Quick Start**: See `../MONITORING_QUICKSTART.md`
- **Full Setup Guide**: See `../MONITORING_SETUP.md`

## Requirements

- Python 3.11+
- Virtual environment at `../.venv`
- Dependencies: `requests`, `python-dotenv` (auto-installed with project)
- Valid `.env` configuration in repository root

## Scheduling

The monitoring runs every 2 hours via:
- **Cron**: See `../cron/monitor.cron`
- **Systemd**: See `../systemd/fragdenstaat-monitor.{service,timer}`

## Troubleshooting

**Script not executing:**
```bash
chmod +x monitor.sh monitor_fragdenstaat.py
```

**Dependencies missing:**
```bash
source ../.venv/bin/activate
pip install requests python-dotenv
```

**Authentication errors:**
- Check OAuth credentials in `../.env`
- Verify OAuth app exists: https://fragdenstaat.de/account/settings/applications/
- Ensure scopes: `read:user`, `read:request`, `read:document`

## Support

For detailed information, see the main monitoring documentation in the repository root.
