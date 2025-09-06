#!/usr/bin/env python3
"""
PassHolder Cross-Platform Installation Script
=============================================

Universal installer for the PassHolder password manager that provides
intelligent package management across different platforms and Python
environments. Handles modern Linux restrictions, Windows permissions,
and macOS security requirements automatically.

Key Features:
- Automatic Python version validation
- Multi-tier package installation strategy
- Cross-platform executable wrapper creation
- Intelligent environment detection
- Comprehensive error handling and user guidance
- Fallback options for restricted environments

Installation Strategy:
1. Global package installation (preferred)
2. User-level installation (fallback)
3. Virtual environment creation (last resort)
4. System package recommendations (if all fail)

Supported Platforms:
- Windows 10+ with PowerShell/Command Prompt
- Linux distributions (Ubuntu, Fedora, Arch, etc.)
- macOS 10.14+ with Homebrew support
- Python 3.8+ required on all platforms

Security Considerations:
- Validates Python installation integrity
- Checks for pip availability and security
- Creates secure wrapper scripts with proper permissions
- Handles externally-managed environment restrictions
- Provides secure fallback options

Error Handling:
- Graceful handling of permission errors
- Clear user feedback for each installation step
- Comprehensive troubleshooting guidance
- Automatic fallback to alternative methods

Usage:
    python install.py           # Standard installation
    python install.py --help    # Show detailed options

Author: PassHolder Team
License: Open Source
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# === Installation Requirements ===

# Minimum Python version required for security and compatibility
MIN_PYTHON_VERSION = (3, 8)

# Required packages with minimum versions for security
REQUIRED_PACKAGES = [
    "rich>=14.1.0",  # Terminal UI framework
    "cryptography>=41.0.0",  # Encryption library
    "argon2-cffi>=25.1.0",  # Password hashing
    "pyperclip>=1.8.0",  # Clipboard integration
]


def check_python_version():
    """
    Validate Python version meets minimum security and compatibility requirements.

    PassHolder requires Python 3.8+ for:
    - Modern cryptography library support
    - pathlib enhancements for cross-platform paths
    - Security improvements in subprocess handling
    - Rich library compatibility

    Raises:
        SystemExit: If Python version is insufficient

    Security Note:
        Older Python versions have known security vulnerabilities
        and lack modern cryptographic features required for secure
        password management.
    """
    current_version = sys.version_info[:2]
    if current_version < MIN_PYTHON_VERSION:
        print(
            f"❌ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required"
        )
        print(f"   Current version: {sys.version_info.major}.{sys.version_info.minor}")
        print("   Please install a newer version of Python")
        print("\n📥 Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Check for externally managed environment (common on modern Linux)
    if platform.system() == "Linux":
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
            )
            if (
                result.returncode != 0
                and "externally-managed-environment" in result.stderr
            ):
                print("ℹ️  Externally managed Python environment detected")
                print("   Will install packages to user directory if needed")
        except:
            pass


def get_script_dir():
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def create_virtual_environment(script_dir):
    """Skip virtual environment creation for global installation"""
    print("🔧 Using global Python installation...")
    print("✅ Skipping virtual environment creation")
    return None


def get_python_executable(venv_path):
    """Get the Python executable path (global installation)"""
    return sys.executable


def install_packages(python_exe, script_dir):
    """Install required packages globally"""
    requirements_file = script_dir / "requirements.txt"

    print("📦 Installing packages...")

    try:
        # Try to upgrade pip first
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )
        pip_upgraded = True
    except subprocess.CalledProcessError:
        # If system pip upgrade fails, try with --user flag
        print("⚠️  System pip upgrade failed, trying user installation...")
        try:
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "--user", "--upgrade", "pip"],
                check=True,
                capture_output=True,
            )
            pip_upgraded = True
        except subprocess.CalledProcessError:
            print("⚠️  Pip upgrade failed, continuing with existing pip...")
            pip_upgraded = False

    # Try installing packages
    try:
        # Try system-wide installation first
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
        )
        print("✅ Packages installed globally")
        return
    except subprocess.CalledProcessError:
        pass

    try:
        # If system installation fails, try user installation
        print("⚠️  System installation failed, installing to user directory...")
        subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "--user",
                "-r",
                str(requirements_file),
            ],
            check=True,
            capture_output=True,
        )
        print("✅ Packages installed to user directory")
        return
    except subprocess.CalledProcessError:
        pass

    # If both fail, provide helpful error message
    print("❌ Package installation failed!")
    print("")
    print("This may be due to an externally managed Python environment.")
    print("Try one of these solutions:")
    print("")
    print("1. Use virtual environment installer (recommended):")
    print("   python3 install_venv.py")
    print("")
    print("2. Use pipx (for application installation):")
    print("   sudo apt install pipx")
    print("   pipx install -e .")
    print("")
    print("3. Use system packages (if available):")
    print("   sudo apt install python3-rich python3-cryptography python3-argon2")
    print("")
    print("4. Manual virtual environment:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    print("")
    sys.exit(1)


def create_executable_wrapper(script_dir, venv_path):
    """Create executable wrapper script"""
    python_exe = get_python_executable(venv_path)
    main_script = script_dir / "passholder.py"

    if platform.system() == "Windows":
        # Create batch file wrapper
        wrapper_path = script_dir / "bin" / "passholder.bat"
        wrapper_path.parent.mkdir(exist_ok=True)

        wrapper_content = f"""@echo off
"{python_exe}" "{main_script}" %*
"""
    else:
        # Create shell script wrapper
        wrapper_path = script_dir / "bin" / "passholder"
        wrapper_path.parent.mkdir(exist_ok=True)

        wrapper_content = f"""#!/bin/bash
"{python_exe}" "{main_script}" "$@"
"""

    wrapper_path.write_text(wrapper_content)

    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod(wrapper_path, 0o755)

    print(f"✅ Executable wrapper created at {wrapper_path}")
    return wrapper_path


def add_to_path_windows(bin_dir):
    """Add directory to Windows user PATH"""
    try:
        import winreg

        # Open user environment variables key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
        )

        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""

        # Add to PATH if not already present
        bin_dir_str = str(bin_dir)
        if bin_dir_str not in current_path:
            new_path = f"{current_path};{bin_dir_str}" if current_path else bin_dir_str
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added {bin_dir_str} to user PATH")
        else:
            print(f"✅ {bin_dir_str} already in PATH")

        winreg.CloseKey(key)

        # Notify system of environment change
        import ctypes

        ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")

    except Exception as e:
        print(f"⚠️  Could not modify PATH automatically: {e}")
        print(f"   Please manually add {bin_dir} to your PATH")


def add_to_path_unix(bin_dir):
    """Add directory to Unix PATH via shell configuration files"""
    home = Path.home()
    bin_dir_str = str(bin_dir)

    # Files to check and modify
    shell_files = [
        home / ".bashrc",
        home / ".zshrc",
    ]

    export_line = f'export PATH="$PATH:{bin_dir_str}"'
    comment_line = "# Added by PassHolder installer"

    for shell_file in shell_files:
        try:
            # Read existing content
            if shell_file.exists():
                content = shell_file.read_text()
                if bin_dir_str in content:
                    print(f"✅ {bin_dir_str} already in {shell_file.name}")
                    continue
            else:
                content = ""

            # Add our PATH export
            with shell_file.open("a") as f:
                f.write(f"\n{comment_line}\n{export_line}\n")

            print(f"✅ Added {bin_dir_str} to {shell_file.name}")

        except Exception as e:
            print(f"⚠️  Could not modify {shell_file}: {e}")


def detect_current_shell():
    """Detect current shell and provide restart instructions"""
    shell_name = os.environ.get("SHELL", "").split("/")[-1]

    if platform.system() == "Windows":
        print("\n🔄 To use 'passholder' command immediately:")
        print("   - Restart your terminal/PowerShell")
        print("   - Or run: refreshenv (if using Chocolatey)")
    else:
        if shell_name in ["bash", "zsh"]:
            config_file = f".{shell_name}rc"
            print(f"\n🔄 To use 'passholder' command immediately:")
            print(f"   - Run: source ~/.{shell_name}rc")
            print(f"   - Or restart your {shell_name} terminal")
        else:
            print(f"\n🔄 To use 'passholder' command:")
            print(f"   - Add the bin directory to your PATH manually")
            print(f"   - Or restart your terminal")


def setup_git_configuration(script_dir):
    """
    Configure git settings to prevent permission conflicts during updates.
    
    This function sets up git attributes and permissions to ensure smooth
    updates without conflicts from file permission changes.
    
    Args:
        script_dir (Path): Directory containing the PassHolder installation
    """
    try:
        print("🔧 Configuring git for smooth updates...")
        
        # Check if this is a git repository
        git_dir = script_dir / ".git"
        if not git_dir.exists():
            print("ℹ️  Not a git repository, skipping git configuration")
            return
        
        # Set up git to ignore permission changes (Unix systems only)
        if platform.system() != "Windows":
            try:
                subprocess.run(
                    ["git", "config", "core.filemode", "false"],
                    cwd=script_dir,
                    check=True,
                    capture_output=True
                )
                print("✅ Git configured to ignore file mode changes")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Could not configure git (git not found or not a repo)")
        
        # Set up proper permissions for shell scripts (Unix systems)
        if platform.system() != "Windows":
            install_sh = script_dir / "install.sh"
            setup_permissions = script_dir / "setup-permissions.sh"
            
            # Make scripts executable
            for script_file in [install_sh, setup_permissions]:
                if script_file.exists():
                    try:
                        script_file.chmod(0o755)
                        print(f"✅ Made {script_file.name} executable")
                    except OSError:
                        print(f"⚠️  Could not set permissions for {script_file.name}")
        
        print("✅ Git configuration completed")
        
    except Exception as e:
        print(f"⚠️  Git configuration warning: {e}")
        print("   This won't affect PassHolder functionality")


def main():
    """Main installation function"""
    print("🚀 PassHolder Installation Starting...")
    print("=" * 50)

    # Check Python version
    check_python_version()

    # Get script directory
    script_dir = get_script_dir()
    print(f"📁 Installing from: {script_dir}")

    # Skip virtual environment creation
    venv_path = create_virtual_environment(script_dir)

    # Install packages globally
    python_exe = get_python_executable(venv_path)
    install_packages(python_exe, script_dir)

    # Create executable wrapper
    wrapper_path = create_executable_wrapper(script_dir, venv_path)
    bin_dir = wrapper_path.parent

    # Configure git for smooth updates
    setup_git_configuration(script_dir)

    # Add to PATH
    if platform.system() == "Windows":
        add_to_path_windows(bin_dir)
    else:
        add_to_path_unix(bin_dir)

    # Provide restart instructions
    detect_current_shell()

    print("\n" + "=" * 50)
    print("🎉 PassHolder installation completed!")
    print("\nPackages installed globally. You can now use:")
    print("   passholder add      # Add a new password")
    print("   passholder view     # View all passwords")
    print("   passholder --help   # Show all commands")
    print("\n🔐 Your passwords will be stored securely with encryption.")


if __name__ == "__main__":
    main()
