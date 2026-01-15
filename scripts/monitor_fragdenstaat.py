#!/usr/bin/env python3
"""
FragDenStaat Request Monitoring System

Monitors FragDenStaat FOI requests for new replies and takes automated actions:
- Downloads data file attachments automatically
- Sends email notifications for questions/clarifications
- Logs simple acknowledgments

Runs every 2 hours via cron job.
"""

import json
import logging
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests
from dotenv import load_dotenv


# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
STATE_FILE = SCRIPT_DIR / "monitor_state.json"
LOG_FILE = REPO_ROOT / "monitoring.log"
DOWNLOAD_DIR = REPO_ROOT / "data" / "fragdenstaat_updates"

# API Configuration
API_BASE_URL = "https://fragdenstaat.de/api/v1"
OAUTH_TOKEN_URL = "https://fragdenstaat.de/oauth/token/"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class MonitorState:
    """Manages persistent state between monitoring runs"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state file: {e}")
                return self._default_state()
        return self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        """Return default state structure"""
        return {
            "last_check": None,
            "processed_messages": set(),  # Will be converted to list for JSON
            "user_id": None,
            "access_token": None,
            "token_expiry": None
        }

    def save(self):
        """Save state to file"""
        try:
            # Convert sets to lists for JSON serialization
            data_to_save = self.data.copy()
            if isinstance(data_to_save.get("processed_messages"), set):
                data_to_save["processed_messages"] = list(data_to_save["processed_messages"])

            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            logger.debug("State saved successfully")
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def get_processed_messages(self) -> Set[int]:
        """Get set of processed message IDs"""
        messages = self.data.get("processed_messages", [])
        if isinstance(messages, list):
            return set(messages)
        return messages

    def mark_message_processed(self, message_id: int):
        """Mark a message as processed"""
        processed = self.get_processed_messages()
        processed.add(message_id)
        self.data["processed_messages"] = processed

    def get_last_check(self) -> Optional[str]:
        """Get last check timestamp"""
        return self.data.get("last_check")

    def update_last_check(self):
        """Update last check timestamp to now"""
        self.data["last_check"] = datetime.now().isoformat()

    def get_access_token(self) -> Optional[str]:
        """Get stored access token"""
        # Check if token is expired
        token_expiry = self.data.get("token_expiry")
        if token_expiry:
            expiry_time = datetime.fromisoformat(token_expiry)
            if datetime.now() >= expiry_time:
                logger.info("Access token expired, will request new one")
                return None
        return self.data.get("access_token")

    def store_access_token(self, token: str, expires_in: int):
        """Store access token with expiry"""
        self.data["access_token"] = token
        # Store expiry time with 60 second buffer
        expiry_time = datetime.now().timestamp() + expires_in - 60
        self.data["token_expiry"] = datetime.fromtimestamp(expiry_time).isoformat()

    def get_user_id(self) -> Optional[int]:
        """Get stored user ID"""
        return self.data.get("user_id")

    def set_user_id(self, user_id: int):
        """Store user ID"""
        self.data["user_id"] = user_id


# =============================================================================
# FRAGDENSTAAT API CLIENT
# =============================================================================

class FragDenStaatClient:
    """Client for FragDenStaat API with OAuth authentication"""

    def __init__(self, client_id: str, client_secret: str, email: str, password: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def authenticate(self) -> bool:
        """
        Authenticate with OAuth2 password grant flow
        Returns True if successful
        """
        try:
            logger.info("Authenticating with FragDenStaat API...")

            data = {
                "grant_type": "password",
                "username": self.email,
                "password": self.password,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "read:user read:request read:document"
            }

            response = requests.post(OAUTH_TOKEN_URL, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 36000)

            # Store token in state
            state.store_access_token(self.access_token, expires_in)

            logger.info("✓ Authentication successful")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_user_id(self) -> Optional[int]:
        """Get current user's ID"""
        try:
            url = f"{API_BASE_URL}/user/"
            response = self.session.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("results"):
                user_id = data["results"][0]["id"]
                logger.info(f"Retrieved user ID: {user_id}")
                return user_id

            logger.error("Could not find user ID in response")
            return None

        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None

    def get_user_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all FOI requests for a user
        Returns list of request objects
        """
        try:
            logger.info(f"Fetching requests for user {user_id}...")

            url = f"{API_BASE_URL}/request/"
            params = {
                "user": user_id,
                "limit": 100  # Adjust if user has more requests
            }

            response = self.session.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            requests_list = data.get("results", [])

            logger.info(f"✓ Found {len(requests_list)} requests")
            return requests_list

        except Exception as e:
            logger.error(f"Error fetching user requests: {e}")
            return []

    def get_messages_for_request(self, request_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages for a specific request
        Returns list of message objects
        """
        try:
            url = f"{API_BASE_URL}/message/"
            params = {
                "request": request_id,
                "limit": 100
            }

            response = self.session.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            messages = data.get("results", [])

            return messages

        except Exception as e:
            logger.error(f"Error fetching messages for request {request_id}: {e}")
            return []

    def get_attachments_for_message(self, message_id: int) -> List[Dict[str, Any]]:
        """
        Get all attachments for a specific message
        Returns list of attachment objects
        """
        try:
            url = f"{API_BASE_URL}/attachment/"
            params = {
                "belongs_to": message_id,
                "limit": 50
            }

            response = self.session.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            attachments = data.get("results", [])

            return attachments

        except Exception as e:
            logger.error(f"Error fetching attachments for message {message_id}: {e}")
            return []

    def download_attachment(self, attachment_url: str, output_path: Path) -> bool:
        """
        Download an attachment file
        Returns True if successful
        """
        try:
            logger.info(f"Downloading attachment to {output_path}...")

            response = self.session.get(
                attachment_url,
                headers=self._get_headers(),
                timeout=120,
                stream=True
            )
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            size_kb = output_path.stat().st_size / 1024
            logger.info(f"✓ Downloaded {size_kb:.1f} KB")
            return True

        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return False


# =============================================================================
# MESSAGE CLASSIFICATION & HANDLING
# =============================================================================

class MessageHandler:
    """Handles different types of messages with appropriate actions"""

    # Keywords for classification
    DATA_FILE_EXTENSIONS = {
        ".xlsx", ".xls", ".csv", ".pdf", ".json", ".xml", ".zip", ".ods"
    }

    QUESTION_KEYWORDS = [
        "frage", "klärung", "rückfrage", "erläuterung", "nachfrage",
        "question", "clarification", "please explain", "could you",
        "benötigen wir", "könnten sie", "bitte um"
    ]

    ACKNOWLEDGMENT_KEYWORDS = [
        "eingangsbestätigung", "erhalten", "vielen dank", "danke für",
        "acknowledgment", "received", "thank you", "we received",
        "eingegangen", "zur kenntnis"
    ]

    def __init__(self, client: FragDenStaatClient, email_config: Dict[str, str]):
        self.client = client
        self.email_config = email_config

    def classify_message(self, message: Dict[str, Any], attachments: List[Dict[str, Any]]) -> str:
        """
        Classify message type
        Returns: "data_files", "question", "acknowledgment"
        """
        # Check for data file attachments
        has_data_files = any(
            Path(att.get("name", "")).suffix.lower() in self.DATA_FILE_EXTENSIONS
            for att in attachments
        )

        if has_data_files:
            return "data_files"

        # Check message content
        content = message.get("content", "").lower()
        subject = message.get("subject", "").lower()
        full_text = f"{subject} {content}"

        # Check for questions
        if any(keyword in full_text for keyword in self.QUESTION_KEYWORDS):
            return "question"

        # Check for acknowledgments
        if any(keyword in full_text for keyword in self.ACKNOWLEDGMENT_KEYWORDS):
            return "acknowledgment"

        # Default: treat as question to be safe
        return "question"

    def handle_data_files(self, message: Dict[str, Any], attachments: List[Dict[str, Any]],
                          request_info: Dict[str, Any]) -> bool:
        """
        Handle message with data file attachments
        Downloads files and logs the action
        Returns True if successful
        """
        logger.info(f"📥 Processing data files for message {message['id']}...")

        request_slug = request_info.get("slug", "unknown")
        message_timestamp = message.get("timestamp", "unknown")

        success_count = 0
        fail_count = 0

        for attachment in attachments:
            name = attachment.get("name", "unknown")
            file_url = attachment.get("file_url")

            if not file_url:
                logger.warning(f"No file URL for attachment: {name}")
                continue

            # Create organized directory structure
            download_path = DOWNLOAD_DIR / request_slug / name

            if self.client.download_attachment(file_url, download_path):
                success_count += 1
                logger.info(f"✓ Downloaded: {name}")
            else:
                fail_count += 1
                logger.error(f"✗ Failed to download: {name}")

        # Log summary
        summary = (
            f"DATA FILES: Request '{request_info.get('title', 'Unknown')}' "
            f"- Downloaded {success_count} files, {fail_count} failed"
        )
        logger.info(summary)

        return fail_count == 0

    def handle_question(self, message: Dict[str, Any], request_info: Dict[str, Any]) -> bool:
        """
        Handle message that requires user attention (question/clarification)
        Sends email notification
        Returns True if successful
        """
        logger.info(f"❓ Processing question/clarification for message {message['id']}...")

        subject = f"[FragDenStaat] Rückfrage zu: {request_info.get('title', 'Unknown')}"

        # Build email body
        body = f"""
Hallo,

Es gibt eine neue Nachricht zu Ihrer FragDenStaat-Anfrage, die Ihre Aufmerksamkeit erfordert.

Anfrage: {request_info.get('title', 'Unknown')}
Link: https://fragdenstaat.de{request_info.get('url', '')}

Nachricht vom: {message.get('timestamp', 'Unknown')}
Von: {message.get('sender_public_body', {}).get('name', 'Unknown')}

Betreff: {message.get('subject', 'Kein Betreff')}

Inhalt:
{message.get('content_rendered', message.get('content', 'Kein Inhalt'))}

---

Bitte antworten Sie auf diese Nachricht über die FragDenStaat-Website.

Dieser Bericht wurde automatisch generiert vom FragDenStaat Monitoring System.
        """

        return self._send_email(subject, body)

    def handle_acknowledgment(self, message: Dict[str, Any], request_info: Dict[str, Any]) -> bool:
        """
        Handle simple acknowledgment message
        Just logs it, no other action needed
        Returns True (always successful)
        """
        logger.info(
            f"✉️  ACKNOWLEDGMENT: Request '{request_info.get('title', 'Unknown')}' "
            f"- Message from {message.get('sender_public_body', {}).get('name', 'Unknown')}"
        )
        return True

    def _send_email(self, subject: str, body: str) -> bool:
        """
        Send email notification
        Returns True if successful
        """
        try:
            # Get email configuration
            smtp_host = self.email_config.get("smtp_host")
            smtp_port = int(self.email_config.get("smtp_port", 587))
            smtp_user = self.email_config.get("smtp_user")
            smtp_password = self.email_config.get("smtp_password")
            recipient = self.email_config.get("recipient")

            if not all([smtp_host, smtp_user, smtp_password, recipient]):
                logger.error("Missing email configuration")
                return False

            # Create message
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Send email
            logger.info(f"Sending email notification to {recipient}...")

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info("✓ Email sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


# =============================================================================
# MAIN MONITORING LOGIC
# =============================================================================

def monitor_requests(client: FragDenStaatClient, handler: MessageHandler) -> Dict[str, int]:
    """
    Main monitoring logic
    Returns statistics about processed messages
    """
    stats = {
        "data_files": 0,
        "questions": 0,
        "acknowledgments": 0,
        "errors": 0
    }

    # Get user ID
    user_id = state.get_user_id()
    if not user_id:
        user_id = client.get_user_id()
        if not user_id:
            logger.error("Could not get user ID")
            return stats
        state.set_user_id(user_id)
        state.save()

    # Get all user's requests
    requests_list = client.get_user_requests(user_id)

    if not requests_list:
        logger.info("No requests found")
        return stats

    # Get set of already processed messages
    processed_messages = state.get_processed_messages()

    # Check each request for new messages
    for request_info in requests_list:
        request_id = request_info["id"]
        request_title = request_info.get("title", "Unknown")

        logger.info(f"Checking request: {request_title} (ID: {request_id})")

        # Get messages for this request
        messages = client.get_messages_for_request(request_id)

        # Filter to only response messages (not from user)
        response_messages = [
            msg for msg in messages
            if msg.get("is_response", False) and msg["id"] not in processed_messages
        ]

        if not response_messages:
            logger.debug(f"No new messages for request {request_id}")
            continue

        logger.info(f"Found {len(response_messages)} new message(s)")

        # Process each new message
        for message in response_messages:
            message_id = message["id"]

            try:
                # Get attachments
                attachments = client.get_attachments_for_message(message_id)

                # Classify and handle message
                message_type = handler.classify_message(message, attachments)

                logger.info(f"Message {message_id} classified as: {message_type}")

                if message_type == "data_files":
                    if handler.handle_data_files(message, attachments, request_info):
                        stats["data_files"] += 1
                    else:
                        stats["errors"] += 1

                elif message_type == "question":
                    if handler.handle_question(message, request_info):
                        stats["questions"] += 1
                    else:
                        stats["errors"] += 1

                else:  # acknowledgment
                    if handler.handle_acknowledgment(message, request_info):
                        stats["acknowledgments"] += 1
                    else:
                        stats["errors"] += 1

                # Mark as processed
                state.mark_message_processed(message_id)

            except Exception as e:
                logger.error(f"Error processing message {message_id}: {e}")
                stats["errors"] += 1

    return stats


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> int:
    """
    Main entry point
    Returns exit code (0 for success)
    """
    logger.info("=" * 80)
    logger.info("FRAGDENSTAAT MONITORING SYSTEM - STARTING")
    logger.info("=" * 80)

    # Load environment variables
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        logger.error(f"Environment file not found: {env_file}")
        return 1

    load_dotenv(env_file)

    # Get credentials from environment
    client_id = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_ID")
    client_secret = os.getenv("FRAGDENSTAAT_OAUTH_CLIENT_SECRET")
    email = os.getenv("FRAGDENSTAAT_EMAIL")
    password = os.getenv("FRAGDENSTAAT_PASSWORD")

    if not all([client_id, client_secret, email, password]):
        logger.error("Missing FragDenStaat credentials in .env file")
        return 1

    # Get email configuration
    email_config = {
        "smtp_host": os.getenv("SMTP_HOST", "smtp.mailbox.org"),
        "smtp_port": os.getenv("SMTP_PORT", "587"),
        "smtp_user": os.getenv("SMTP_USER", email),
        "smtp_password": os.getenv("SMTP_PASSWORD", password),
        "recipient": os.getenv("EMAIL_RECIPIENT", email)
    }

    try:
        # Initialize client
        client = FragDenStaatClient(client_id, client_secret, email, password)

        # Try to use cached token first
        cached_token = state.get_access_token()
        if cached_token:
            logger.info("Using cached access token")
            client.access_token = cached_token
        else:
            # Authenticate
            if not client.authenticate():
                logger.error("Authentication failed")
                return 1

        # Initialize handler
        handler = MessageHandler(client, email_config)

        # Run monitoring
        stats = monitor_requests(client, handler)

        # Update last check time
        state.update_last_check()
        state.save()

        # Print summary
        logger.info("=" * 80)
        logger.info("MONITORING COMPLETE - SUMMARY:")
        logger.info(f"  Data files processed: {stats['data_files']}")
        logger.info(f"  Questions/clarifications: {stats['questions']}")
        logger.info(f"  Acknowledgments: {stats['acknowledgments']}")
        logger.info(f"  Errors: {stats['errors']}")
        logger.info("=" * 80)

        return 0 if stats["errors"] == 0 else 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


# =============================================================================
# INITIALIZE STATE
# =============================================================================

state = MonitorState(STATE_FILE)

if __name__ == "__main__":
    sys.exit(main())
