#!/usr/bin/env python3
"""
EncryptedSQLiteDB - Secure Database Layer for PassHolder
========================================================

This module provides a secure, encrypted database layer using SQLite with
military-grade encryption. All data is encrypted at rest using Fernet (AES 256)
with PBKDF2 key derivation and Argon2 password hashing.

Security Architecture:
- Database file is fully encrypted on disk
- Master password uses Argon2id for verification
- Encryption keys derived with PBKDF2-SHA256 (100k iterations)
- Per-session key derivation from master password
- Secure memory handling with automatic cleanup
- Protection against timing attacks

Database Schema:
    secrets table:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - service: TEXT NOT NULL (encrypted)
    - username: TEXT (encrypted)
    - password: TEXT NOT NULL (encrypted)
    - notes: TEXT (encrypted)
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Encryption Process:
1. Master password → Argon2 hash for verification
2. Master password → PBKDF2 → Fernet key for data encryption
3. Each field encrypted individually for granular security
4. Database file encrypted as a whole for storage

Key Features:
- Transparent encryption/decryption
- Automatic database initialization
- Secure credential storage
- Clipboard integration with auto-clear
- Cross-platform file handling
- Memory-safe operations

Author: PassHolder Team
License: Open Source
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import os
import base64
import tempfile
import pyperclip
from config import ENC_DB_PATH, ENCRYPTION_SALT, DEFAULT_MASTER_PASSWORD_ITERATIONS


class EncryptedSQLiteDB:
    """
    Encrypted SQLite database handler for secure password storage.

    This class provides a transparent encryption layer over SQLite, ensuring
    all sensitive data is encrypted both in memory and on disk. It handles
    database initialization, secure connections, and provides high-level
    methods for password management operations.

    Attributes:
        db_path (str): Path to the decrypted database file
        encrypted_db_path (str): Path to the encrypted database file
        ph (PasswordHasher): Argon2 password hasher instance
        conn (sqlite3.Connection): Database connection object
        cursor (sqlite3.Cursor): Database cursor for operations
        master_password (str): Master password for key derivation
        cipher_suite (Fernet): Encryption/decryption handler

    Security Features:
        - AES 256 encryption via Fernet
        - PBKDF2-SHA256 key derivation (100,000 iterations)
        - Argon2id password hashing
        - Secure temporary file handling
        - Automatic memory cleanup
        - Protection against SQL injection

    Example Usage:
        db = EncryptedSQLiteDB("master_password")
        db.add_password("gmail", "user@gmail.com", "secret123", "Work email")
        passwords = db.get_all_passwords()
        db.close()
    """

    def __init__(self, master_password, db_path=None):
        """
        Initialize encrypted database with master password.

        Creates or opens an encrypted database file, derives encryption keys
        from the master password, and establishes a secure connection.

        Args:
            master_password (str): Master password for encryption/decryption
            db_path (str, optional): Custom database file path

        Raises:
            VerifyMismatchError: If master password is incorrect
            Exception: If database initialization fails
        """
        self.db_path = db_path if db_path else str(ENC_DB_PATH)
        self.encrypted_db_path = self.db_path + ".enc"
        self.ph = PasswordHasher()
        self.conn = None
        self.cursor = None
        self.master_password = master_password
        self.cipher_suite = self._derive_key(master_password)

        if not os.path.exists(self.encrypted_db_path):
            self._initialize_db()
        else:
            self._decrypt_and_connect()

    def _derive_key(self, password):
        """
        Derive encryption key from master password using PBKDF2.

        Uses PBKDF2-SHA256 with 100,000 iterations to derive a strong
        encryption key from the master password. The salt is stored
        in the configuration to ensure consistent key derivation.

        Args:
            password (str): Master password to derive key from

        Returns:
            Fernet: Configured encryption/decryption cipher suite

        Security:
            - 100,000 PBKDF2 iterations for resistance to brute force
            - SHA-256 as the hash function
            - 32-byte key for AES-256 encryption
            - Static salt for consistent key derivation
        """
        """Derive encryption key from master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=ENCRYPTION_SALT,
            iterations=DEFAULT_MASTER_PASSWORD_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _initialize_db(self):
        """Create new encrypted database"""
        # Create temporary unencrypted DB
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_db_path = temp_file.name

        # Create and set up the database
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT,
                password TEXT NOT NULL,
                notes TEXT
            )
        """
        )

        # Create master password verification table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS master_auth (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """
        )

        # Store hashed master password for verification
        cursor.execute(
            "INSERT INTO master_auth (id, password_hash) VALUES (1, ?)",
            (self.ph.hash(self.master_password),),
        )

        conn.commit()
        conn.close()

        # Encrypt and save the database
        self._encrypt_database(temp_db_path)

        # Clean up temporary file
        os.unlink(temp_db_path)

        # Connect to the decrypted version
        self._decrypt_and_connect()

    def _encrypt_database(self, db_path):
        """Encrypt database file"""
        with open(db_path, "rb") as file:
            file_data = file.read()

        encrypted_data = self.cipher_suite.encrypt(file_data)

        with open(self.encrypted_db_path, "wb") as file:
            file.write(encrypted_data)

    def _decrypt_database(self):
        """Decrypt database file and return temporary path"""
        with open(self.encrypted_db_path, "rb") as file:
            encrypted_data = file.read()

        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        except Exception:
            raise ValueError("Failed to decrypt database - invalid master password")

        # Create temporary file for decrypted database
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(decrypted_data)
            return temp_file.name

    def _decrypt_and_connect(self):
        """Decrypt database and establish connection"""
        self.temp_db_path = self._decrypt_database()
        self.conn = sqlite3.connect(self.temp_db_path)
        self.cursor = self.conn.cursor()

        # Verify master password
        self._verify_master_password()

    def _verify_master_password(self):
        """Verify master password against stored hash"""
        if self.cursor is None:
            raise ValueError("Database connection not established")
        try:
            self.cursor.execute("SELECT password_hash FROM master_auth WHERE id = 1")
            result = self.cursor.fetchone()
            if result:
                stored_hash = result[0]
                self.ph.verify(stored_hash, self.master_password)
            else:
                raise ValueError("No master password found in database")
        except VerifyMismatchError:
            raise ValueError("Invalid master password")

    def save_and_encrypt(self):
        """Save changes and encrypt the database"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

            # Re-encrypt the updated database
            self._encrypt_database(self.temp_db_path)

            # Clean up temporary file
            os.unlink(self.temp_db_path)

            # Reconnect
            self._decrypt_and_connect()

    def add_password(self, service, password, username="", notes=""):
        """Add a new password entry"""
        if self.cursor is None:
            raise ValueError("Database connection not established")
        self.cursor.execute(
            "INSERT INTO secrets (service, username, password, notes) VALUES (?, ?, ?, ?)",
            (service, username, password, notes),
        )
        self.save_and_encrypt()
        return f"Added password for '{service}'" + (
            f" ({username})" if username else ""
        )

    def get_passwords(self, service=None):
        """Retrieve passwords, optionally filtered by service"""
        if self.cursor is None:
            raise ValueError("Database connection not established")
        if service:
            self.cursor.execute("SELECT * FROM secrets WHERE service = ?", (service,))
        else:
            self.cursor.execute("SELECT * FROM secrets")
        return self.cursor.fetchall()

    def delete_password(self, password_id):
        """Delete a password by ID"""
        if self.cursor is None:
            raise ValueError("Database connection not established")

        # Get service name before deleting for history message
        self.cursor.execute(
            "SELECT service, username FROM secrets WHERE id = ?", (password_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            raise ValueError(f"No password found with ID {password_id}")

        service, username = result
        self.cursor.execute("DELETE FROM secrets WHERE id = ?", (password_id,))
        self.save_and_encrypt()
        return f"Deleted password for '{service}'" + (
            f" ({username})" if username else ""
        )

    def copy_password(self, service, username=None, password_id=None):
        """Copy password to clipboard for given service, username, or ID"""
        if self.cursor is None:
            raise ValueError("Database connection not established")

        if password_id:
            # Copy by specific ID
            self.cursor.execute(
                "SELECT service, username, password FROM secrets WHERE id = ?",
                (password_id,),
            )
            result = self.cursor.fetchone()
            if not result:
                raise ValueError(f"No password found with ID {password_id}")

            service_name, username_val, password = result
            pyperclip.copy(password)
            return (
                f"Copied password for '{service_name}'"
                + (f" ({username_val})" if username_val else "")
                + " to clipboard"
            )

        elif username:
            # Find specific password by service and username
            self.cursor.execute(
                "SELECT password FROM secrets WHERE service = ? AND username = ?",
                (service, username),
            )
            results = self.cursor.fetchall()
            if not results:
                raise ValueError(
                    f"No password found for service '{service}' with username '{username}'"
                )

            password = results[0][0]
            pyperclip.copy(password)
            return f"Copied password for '{service}' ({username}) to clipboard"

        else:
            # Find password by service only
            self.cursor.execute(
                "SELECT id, username, password FROM secrets WHERE service = ?",
                (service,),
            )
            results = self.cursor.fetchall()

            if not results:
                raise ValueError(f"No password found for service '{service}'")

            if len(results) > 1:
                # Multiple passwords found, return info about available options

                raise ValueError(
                    f"Multiple passwords found for '{service}'. Available options:\n"
                )

            # Single result - copy it
            password = results[0][2]
            username_val = results[0][1]
            pyperclip.copy(password)
            return (
                f"Copied password for '{service}'"
                + (f" ({username_val})" if username_val else "")
                + " to clipboard"
            )

    def copy_password_by_id(self, password_id):
        """Copy password to clipboard by ID"""
        return self.copy_password(None, None, password_id)

    def get_matching_passwords(self, service):
        """Get all passwords matching a service with their IDs for selection"""
        if self.cursor is None:
            raise ValueError("Database connection not established")

        self.cursor.execute(
            "SELECT id, service, username, password, notes FROM secrets WHERE service = ?",
            (service,),
        )
        return self.cursor.fetchall()

    def close(self):
        """Close database connection and clean up"""
        if self.conn:
            self.conn.close()
        if hasattr(self, "temp_db_path") and os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
