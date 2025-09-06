# PassHolder - Secure Password Manager

A cross-platform password manager with encryption, built in Python.

## Features

- 🔐 **Secure Encryption**: Uses Fernet (AES 128) with PBKDF2 key derivation
- 🖥️ **Cross-Platform**: Works on Windows, Linux, and macOS  
- 🎨 **Rich Terminal UI**: Beautiful interface with tables and progress bars
- 📋 **Clipboard Integration**: Copy passwords directly to clipboard
- 🔍 **Search Functionality**: Find passwords by service name
- 🛡️ **Master Password**: Single password protects all your data
- 📦 **Easy Installation**: One-command setup with virtual environment

## Quick Installation

### Windows
```powershell
python install.py
```

### Linux/macOS
```bash
./install.sh
```

### Manual Installation Requirements
- Python 3.8 or higher
- On Linux: `python3-venv` package may be needed

## Usage

After installation, restart your terminal and use these commands:

### Automatic Mode Selection

```bash
# Enter interactive UI mode (no arguments)
passholder

# Use CLI mode (with arguments)
passholder add          # Add a new password
passholder view         # View all passwords
passholder remove       # Remove a password
passholder copy         # Copy password to clipboard
passholder search <service_name>  # Search for passwords
passholder get <service_name>     # Get specific password
passholder --help       # Show help
```

The program automatically detects:
- **UI Mode**: When you type just `passholder` (no arguments)
- **CLI Mode**: When you provide any arguments like `passholder view`

## First Time Setup

1. Run `passholder add` to create your first password entry
2. You'll be prompted to create a master password
3. Your master password encrypts all stored data

## Security Features

- **Encryption**: All passwords encrypted with Fernet (AES 128)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Password Hashing**: Argon2 for master password verification
- **Local Storage**: Data stored locally in encrypted database
- **No Network**: No internet connection required or used

## Installation Details

The installer:
1. ✅ Creates a Python virtual environment
2. ✅ Installs all required packages
3. ✅ Creates a `passholder` command wrapper
4. ✅ Adds the command to your system PATH
5. ✅ Configures shell profile files (bash/zsh)

## Uninstallation

To remove PassHolder:
1. Remove the installation directory
2. Remove the PATH entry from your shell profile
3. On Windows: Remove from Environment Variables

## Development

### Project Structure
```
PassHolder/
├── main.py              # Main application entry point
├── cli.py               # Command-line interface
├── ui.py                # Rich terminal UI components
├── encryptedSQLiteDB.py # Encrypted database handler
├── config.py            # Configuration management
├── passholder.py        # CLI wrapper script
├── install.py           # Cross-platform installer
├── install.sh           # Unix installation script
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Project configuration
```

### Dependencies
- `rich>=14.1.0` - Terminal UI framework
- `cryptography>=41.0.0` - Encryption library
- `argon2-cffi>=25.1.0` - Password hashing
- `pyperclip>=1.8.0` - Clipboard integration

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check that Python 3.8+ is installed
2. Verify all dependencies are installed
3. Ensure the virtual environment is activated
4. Try reinstalling with the installation script

---

**⚠️ Important**: Keep your master password safe! Without it, your stored passwords cannot be recovered.
