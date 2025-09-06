import secrets
from pathlib import Path

# Configuration for PassHolder

# Database configuration
USER_HOME = Path.home()
PASSHOLDER_DIR = USER_HOME / "passholder"
ENC_DB_PATH = PASSHOLDER_DIR / "secrets.db"
SALT_FILE = PASSHOLDER_DIR / "salt.key"

# Ensure the passholder directory exists
PASSHOLDER_DIR.mkdir(exist_ok=True)


def get_or_create_salt():
    """Get existing salt or create a new random one"""
    if SALT_FILE.exists():
        # Load existing salt
        with open(SALT_FILE, "rb") as f:
            return f.read()
    else:
        # Generate new random salt
        salt = secrets.token_bytes(32)  # 32 bytes = 256 bits
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        return salt


def check_db_exists():
    """Check if the encrypted database file exists"""
    encrypted_db_path = Path(str(ENC_DB_PATH) + ".enc")
    return encrypted_db_path.exists()


# Salt for encryption key derivation
ENCRYPTION_SALT = get_or_create_salt()

# Default settings
DEFAULT_PAGE_SIZE = 5
DEFAULT_MASTER_PASSWORD_ITERATIONS = 100000
