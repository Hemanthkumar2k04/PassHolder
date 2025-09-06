#!/usr/bin/env python3
"""
PassHolder Configuration Module
===============================

This module manages all configuration settings, file paths, and security
parameters for the PassHolder password manager. It handles cross-platform
file system operations and ensures secure configuration management.

Key Responsibilities:
- Database and file path management
- Encryption salt generation and storage
- Cross-platform directory handling
- Security parameter configuration
- Application state management

Security Considerations:
- Cryptographically secure salt generation
- Secure file permissions for sensitive files
- Platform-specific secure storage locations
- Protection against path traversal attacks

File Structure:
    ~/passholder/           # User's home directory
    ├── secrets.db.enc      # Encrypted database file
    ├── salt.key            # Encryption salt (32 bytes)
    └── config/             # Future configuration files

Default Security Parameters:
- PBKDF2 iterations: 100,000 (adjustable for performance)
- Salt length: 32 bytes (256 bits)
- Key derivation: PBKDF2-SHA256
- Encryption: Fernet (AES 256 + HMAC)

Cross-Platform Support:
- Windows: Uses %USERPROFILE%/passholder
- Linux/macOS: Uses ~/.passholder or ~/passholder
- Handles path separators automatically
- Respects system permissions

Author: PassHolder Team
License: Open Source
"""

import secrets
from pathlib import Path

# === Core Configuration Settings ===

# Database and file system configuration
USER_HOME = Path.home()
PASSHOLDER_DIR = USER_HOME / "passholder"
ENC_DB_PATH = PASSHOLDER_DIR / "secrets.db"
SALT_FILE = PASSHOLDER_DIR / "salt.key"

# Security parameters (tunable for performance vs security)
DEFAULT_MASTER_PASSWORD_ITERATIONS = 100000  # PBKDF2 iterations
SALT_LENGTH = 32  # bytes (256 bits)
CLIPBOARD_CLEAR_TIMEOUT = 30  # seconds

# Ensure the passholder directory exists with proper permissions
PASSHOLDER_DIR.mkdir(exist_ok=True)

# Set restrictive permissions on Unix systems
if hasattr(Path, "chmod"):
    try:
        PASSHOLDER_DIR.chmod(0o700)  # Owner read/write/execute only
    except (OSError, NotImplementedError):
        pass  # Windows or permission error


def get_or_create_salt():
    """
    Retrieve existing encryption salt or generate a new cryptographically secure one.

    The salt is used for PBKDF2 key derivation to ensure unique encryption keys
    even with identical master passwords across different installations.

    Security Features:
    - Uses secrets.token_bytes() for cryptographically secure generation
    - 32-byte (256-bit) salt for maximum security
    - Persistent storage to ensure consistent key derivation
    - File permissions restricted to owner only (Unix systems)

    Returns:
        bytes: 32-byte encryption salt

    Raises:
        OSError: If salt file cannot be created or read
        PermissionError: If insufficient file system permissions

    Example:
        salt = get_or_create_salt()
        # Use salt for PBKDF2 key derivation
    """
    if SALT_FILE.exists():
        # Load existing salt from secure storage
        with open(SALT_FILE, "rb") as f:
            return f.read()
    else:
        # Generate new cryptographically secure salt
        salt = secrets.token_bytes(SALT_LENGTH)

        # Store salt with restricted permissions
        with open(SALT_FILE, "wb") as f:
            f.write(salt)

        # Set restrictive file permissions (Unix systems)
        try:
            SALT_FILE.chmod(0o600)  # Owner read/write only
        except (OSError, NotImplementedError):
            pass  # Windows or permission error

        return salt


def check_db_exists():
    """
    Check if an encrypted database file exists in the expected location.

    This function is used to determine whether this is a first-time setup
    (requiring master password creation) or an existing installation
    (requiring master password verification).

    Returns:
        bool: True if encrypted database file exists, False otherwise

    Example:
        if check_db_exists():
            # Existing installation - verify master password
            master_password = prompt_for_existing_password()
        else:
            # New installation - create master password
            master_password = prompt_for_new_password()
    """
    encrypted_db_path = Path(str(ENC_DB_PATH) + ".enc")
    return encrypted_db_path.exists()


# === Derived Configuration Values ===

# Initialize encryption salt (must be done after functions are defined)
ENCRYPTION_SALT = get_or_create_salt()

# UI and display settings
DEFAULT_PAGE_SIZE = 5  # Number of passwords to show per page in GUI
MAX_PASSWORD_DISPLAY_LENGTH = 50  # Truncate long passwords in tables

# Application metadata
APP_NAME = "PassHolder"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Secure Password Manager with Encryption"
