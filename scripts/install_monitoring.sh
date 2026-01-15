#!/bin/bash
#
# Installation script for FragDenStaat Monitoring System
#
# This script automates the setup process:
# - Installs dependencies
# - Makes scripts executable
# - Tests the configuration
# - Optionally installs cron job or systemd service
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}  FragDenStaat Monitoring System - Installation${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Check virtual environment
if [ ! -d "$REPO_ROOT/.venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    cd "$REPO_ROOT"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Step 2: Install dependencies
echo ""
echo -e "${YELLOW}Step 2: Installing Python dependencies...${NC}"

cd "$REPO_ROOT"
source .venv/bin/activate

# Check if using uv or pip
if command -v uv &> /dev/null; then
    echo "Using uv for installation..."
    uv pip install requests python-dotenv
else
    echo "Using pip for installation..."
    pip install requests python-dotenv
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Make scripts executable
echo ""
echo -e "${YELLOW}Step 3: Making scripts executable...${NC}"

chmod +x "$SCRIPT_DIR/monitor.sh"
chmod +x "$SCRIPT_DIR/monitor_fragdenstaat.py"
chmod +x "$SCRIPT_DIR/test_setup.py"

echo -e "${GREEN}✓ Scripts are executable${NC}"

# Step 4: Check .env configuration
echo ""
echo -e "${YELLOW}Step 4: Checking configuration...${NC}"

if [ ! -f "$REPO_ROOT/.env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo ""
    echo "Please create a .env file with the following configuration:"
    echo ""
    cat << 'EOF'
# FragDenStaat Credentials
FRAGDENSTAAT_EMAIL=your_email@example.com
FRAGDENSTAAT_PASSWORD=your_password
FRAGDENSTAAT_OAUTH_CLIENT_ID=your_client_id
FRAGDENSTAAT_OAUTH_CLIENT_SECRET=your_client_secret

# Email Configuration
SMTP_HOST=smtp.mailbox.org
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
EMAIL_RECIPIENT=your_email@example.com
EOF
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ .env file exists${NC}"

# Check for OAuth credentials
if grep -q "your_client_id" "$REPO_ROOT/.env" 2>/dev/null || \
   grep -q "YOUR_CLIENT_ID" "$REPO_ROOT/.env" 2>/dev/null; then
    echo -e "${YELLOW}⚠  .env file contains placeholder values${NC}"
    echo ""
    echo "Please update the .env file with your actual OAuth credentials."
    echo "Get them from: https://fragdenstaat.de/account/settings/applications/"
    echo ""
    echo "After updating .env, run the test script:"
    echo "  $SCRIPT_DIR/test_setup.py"
    echo ""
    exit 1
fi

# Step 5: Run tests
echo ""
echo -e "${YELLOW}Step 5: Running configuration tests...${NC}"
echo ""

"$SCRIPT_DIR/test_setup.py"
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Tests failed. Please fix the issues above.${NC}"
    exit 1
fi

# Step 6: Installation options
echo ""
echo -e "${YELLOW}Step 6: Schedule monitoring${NC}"
echo ""
echo "How would you like to schedule the monitoring?"
echo ""
echo "  1) Cron job (recommended for simplicity)"
echo "  2) Systemd service (recommended for system integration)"
echo "  3) Manual - I'll set it up myself"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Installing cron job...${NC}"
        echo ""
        echo "The following line will be added to your crontab:"
        echo "  0 */2 * * * $SCRIPT_DIR/monitor.sh"
        echo ""
        read -p "Proceed? (y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            # Add to crontab
            (crontab -l 2>/dev/null; echo "0 */2 * * * $SCRIPT_DIR/monitor.sh") | crontab -
            echo -e "${GREEN}✓ Cron job installed${NC}"
            echo ""
            echo "View your cron jobs with: crontab -l"
            echo "Remove with: crontab -e (then delete the line)"
        else
            echo "Skipped. You can add it manually later."
        fi
        ;;
    2)
        echo ""
        echo -e "${YELLOW}Installing systemd service...${NC}"
        echo ""
        echo "This requires sudo access."
        echo ""
        read -p "Proceed? (y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            sudo cp "$REPO_ROOT/systemd/fragdenstaat-monitor.service" /etc/systemd/system/
            sudo cp "$REPO_ROOT/systemd/fragdenstaat-monitor.timer" /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable fragdenstaat-monitor.timer
            sudo systemctl start fragdenstaat-monitor.timer
            echo -e "${GREEN}✓ Systemd service installed and started${NC}"
            echo ""
            echo "Check status with: sudo systemctl status fragdenstaat-monitor.timer"
            echo "View logs with: sudo journalctl -u fragdenstaat-monitor.service -f"
        else
            echo "Skipped. See MONITORING_SETUP.md for manual installation."
        fi
        ;;
    3)
        echo ""
        echo "Manual setup chosen."
        echo "See MONITORING_SETUP.md for instructions."
        ;;
    *)
        echo ""
        echo "Invalid choice. See MONITORING_SETUP.md for manual setup."
        ;;
esac

# Success message
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}  ✓ Installation complete!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo "Your monitoring system is ready."
echo ""
echo "Next steps:"
echo "  • Test run: $SCRIPT_DIR/monitor.sh"
echo "  • View logs: tail -f $REPO_ROOT/monitoring.log"
echo "  • Documentation: $REPO_ROOT/MONITORING_SETUP.md"
echo ""
echo "The system will check FragDenStaat every 2 hours for:"
echo "  • New data files (automatically downloaded)"
echo "  • Questions requiring your attention (email sent)"
echo "  • Acknowledgments (logged)"
echo ""
