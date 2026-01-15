#!/usr/bin/env python3
"""
Test script to verify FragDenStaat monitoring setup

This script tests:
1. Environment configuration
2. OAuth authentication
3. API access
4. Email configuration
5. File permissions

Run this before scheduling the monitoring system.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
import requests


def print_header(text):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_mark(passed):
    """Return check or cross mark"""
    return "✓" if passed else "✗"


def test_environment():
    """Test environment configuration"""
    print_header("1. TESTING ENVIRONMENT CONFIGURATION")

    # Check .env file exists
    env_file = REPO_ROOT / ".env"
    env_exists = env_file.exists()
    print(f"{check_mark(env_exists)} .env file exists: {env_file}")

    if not env_exists:
        print("  ERROR: Create .env file in repository root")
        return False

    # Load environment
    load_dotenv(env_file)

    # Check required variables
    required_vars = [
        "FRAGDENSTAAT_EMAIL",
        "FRAGDENSTAAT_PASSWORD",
        "FRAGDENSTAAT_OAUTH_CLIENT_ID",
        "FRAGDENSTAAT_OAUTH_CLIENT_SECRET",
    ]

    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        is_set = bool(value and len(value) > 0)
        print(f"{check_mark(is_set)} {var}: {'SET' if is_set else 'MISSING'}")
        all_present = all_present and is_set

    # Check email configuration
    email_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]
    print("\nEmail configuration (optional for testing):")
    for var in email_vars:
        value = os.getenv(var)
        is_set = bool(value and len(value) > 0)
        print(f"  {check_mark(is_set)} {var}: {'SET' if is_set else 'NOT SET'}")

    return all_present


def test_oauth_authentication():
    """Test OAuth authentication"""
    print_header("2. TESTING OAUTH AUTHENTICATION")

    client_id = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_ID")
    client_secret = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_SECRET")
    email = os.getenv("FRAGDENSTAAT_EMAIL")
    password = os.getenv("FRAGDENSTAAT_PASSWORD")

    if not all([client_id, client_secret, email, password]):
        print("✗ Cannot test authentication - missing credentials")
        return False

    try:
        print("Attempting OAuth authentication...")

        data = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "read:user read:request read:document"
        }

        response = requests.post(
            "https://fragdenstaat.de/oauth/token/",
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            token_data = response.json()
            print(f"✓ Authentication successful!")
            print(f"  Token type: {token_data.get('token_type')}")
            print(f"  Expires in: {token_data.get('expires_in')} seconds")
            print(f"  Scope: {token_data.get('scope')}")
            return True
        else:
            print(f"✗ Authentication failed: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return False


def test_api_access():
    """Test API access"""
    print_header("3. TESTING API ACCESS")

    client_id = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_ID")
    client_secret = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_SECRET")
    email = os.getenv("FRAGDENSTAAT_EMAIL")
    password = os.getenv("FRAGDENSTAAT_PASSWORD")

    try:
        # Get access token
        print("Getting access token...")
        data = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "read:user read:request read:document"
        }

        response = requests.post(
            "https://fragdenstaat.de/oauth/token/",
            data=data,
            timeout=30
        )
        response.raise_for_status()

        access_token = response.json()["access_token"]
        print("✓ Access token obtained")

        # Test API endpoints
        headers = {"Authorization": f"Bearer {access_token}"}

        # Test user endpoint
        print("\nTesting user endpoint...")
        response = requests.get(
            "https://fragdenstaat.de/api/v1/user/",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("results"):
                user = user_data["results"][0]
                print(f"✓ User endpoint accessible")
                print(f"  User ID: {user.get('id')}")
                print(f"  Username: {user.get('username')}")
            else:
                print("✗ No user data returned")
                return False
        else:
            print(f"✗ User endpoint failed: HTTP {response.status_code}")
            return False

        # Test request endpoint
        print("\nTesting request endpoint...")
        user_id = user_data["results"][0]["id"]
        response = requests.get(
            "https://fragdenstaat.de/api/v1/request/",
            headers=headers,
            params={"user": user_id, "limit": 5},
            timeout=30
        )

        if response.status_code == 200:
            request_data = response.json()
            request_count = len(request_data.get("results", []))
            print(f"✓ Request endpoint accessible")
            print(f"  Found {request_count} request(s)")

            if request_count > 0:
                req = request_data["results"][0]
                print(f"  Example: {req.get('title', 'Unknown')}")
        else:
            print(f"✗ Request endpoint failed: HTTP {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"✗ API access error: {e}")
        return False


def test_email_config():
    """Test email configuration"""
    print_header("4. TESTING EMAIL CONFIGURATION")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_host, smtp_user, smtp_password]):
        print("⚠  Email configuration incomplete (optional for monitoring)")
        print("  Email notifications will be disabled")
        return True  # Not critical

    try:
        import smtplib

        print(f"Testing SMTP connection to {smtp_host}:{smtp_port}...")

        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)

        print("✓ SMTP authentication successful")
        print(f"  Server: {smtp_host}:{smtp_port}")
        print(f"  User: {smtp_user}")
        return True

    except Exception as e:
        print(f"✗ SMTP connection failed: {e}")
        print("  Email notifications will not work")
        return False


def test_file_permissions():
    """Test file permissions"""
    print_header("5. TESTING FILE PERMISSIONS")

    # Check script permissions
    monitor_script = SCRIPT_DIR / "monitor_fragdenstaat.py"
    wrapper_script = SCRIPT_DIR / "monitor.sh"

    scripts_ok = True

    for script in [monitor_script, wrapper_script]:
        if script.exists():
            is_executable = os.access(script, os.X_OK)
            print(f"{check_mark(is_executable)} {script.name} executable: {is_executable}")
            if not is_executable:
                print(f"  Fix with: chmod +x {script}")
                scripts_ok = False
        else:
            print(f"✗ {script.name} not found")
            scripts_ok = False

    # Check writable directories
    directories = [
        (REPO_ROOT, "Repository root"),
        (SCRIPT_DIR, "Scripts directory"),
        (REPO_ROOT / "data", "Data directory (will be created if needed)"),
    ]

    dirs_ok = True
    for directory, name in directories:
        if directory.exists():
            is_writable = os.access(directory, os.W_OK)
            print(f"{check_mark(is_writable)} {name} writable: {is_writable}")
            if not is_writable:
                dirs_ok = False
        else:
            print(f"⚠  {name} does not exist (will be created)")

    return scripts_ok and dirs_ok


def test_python_dependencies():
    """Test Python dependencies"""
    print_header("6. TESTING PYTHON DEPENDENCIES")

    required_modules = [
        ("requests", "HTTP library"),
        ("dotenv", "Environment configuration"),
    ]

    all_present = True

    for module, description in required_modules:
        try:
            if module == "dotenv":
                __import__("dotenv")
            else:
                __import__(module)
            print(f"✓ {module}: {description}")
        except ImportError:
            print(f"✗ {module}: MISSING - {description}")
            print(f"  Install with: pip install {module}")
            all_present = False

    return all_present


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  FRAGDENSTAAT MONITORING SETUP TEST")
    print("=" * 70)
    print("\nThis script will verify your monitoring system setup.")
    print("All tests must pass before scheduling the monitoring system.\n")

    results = {
        "Environment": test_environment(),
        "Dependencies": test_python_dependencies(),
        "OAuth": test_oauth_authentication(),
        "API Access": test_api_access(),
        "Email": test_email_config(),
        "Permissions": test_file_permissions(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  {check_mark(passed)} {test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)

    if all_passed:
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nYour monitoring system is ready to use.")
        print("\nNext steps:")
        print("  1. Run manually: ./scripts/monitor.sh")
        print("  2. Check logs: tail -f monitoring.log")
        print("  3. Schedule with cron: See MONITORING_QUICKSTART.md")
        return 0
    else:
        print("  ✗ SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above before scheduling the monitoring.")
        print("See MONITORING_SETUP.md for detailed instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
