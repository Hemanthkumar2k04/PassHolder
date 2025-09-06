#!/usr/bin/env python3
"""
PassHolder Installation Script
Cross-platform installer for PassHolder password manager
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Minimum Python version required
MIN_PYTHON_VERSION = (3, 8)


def check_python_version():
    """Check if Python version meets minimum requirements"""
    current_version = sys.version_info[:2]
    if current_version < MIN_PYTHON_VERSION:
        print(
            f"❌ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required"
        )
        print(f"   Current version: {sys.version_info.major}.{sys.version_info.minor}")
        print("   Please install a newer version of Python")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def get_script_dir():
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def create_virtual_environment(script_dir):
    """Create virtual environment"""
    venv_path = script_dir / ".venv"

    print("🔧 Creating virtual environment...")

    # On Linux, we might need to install python3-venv
    if platform.system() == "Linux":
        try:
            # Try to create venv, if it fails, suggest installing python3-venv
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print("⚠️  Virtual environment creation failed.")
            print("   On Ubuntu/Debian, run: sudo apt install python3-venv")
            print("   On CentOS/RHEL, run: sudo yum install python3-venv")
            print("   Then run this installer again.")
            sys.exit(1)
    else:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    print(f"✅ Virtual environment created at {venv_path}")
    return venv_path


def get_python_executable(venv_path):
    """Get the Python executable path from virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def install_packages(python_exe, script_dir):
    """Install required packages"""
    requirements_file = script_dir / "requirements.txt"

    print("📦 Installing packages...")

    # Upgrade pip first
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
    )

    # Install requirements
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)],
        check=True,
    )

    print("✅ Packages installed successfully")


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


def main():
    """Main installation function"""
    print("🚀 PassHolder Installation Starting...")
    print("=" * 50)

    # Check Python version
    check_python_version()

    # Get script directory
    script_dir = get_script_dir()
    print(f"📁 Installing from: {script_dir}")

    # Create virtual environment
    venv_path = create_virtual_environment(script_dir)

    # Install packages
    python_exe = get_python_executable(venv_path)
    install_packages(python_exe, script_dir)

    # Create executable wrapper
    wrapper_path = create_executable_wrapper(script_dir, venv_path)
    bin_dir = wrapper_path.parent

    # Add to PATH
    if platform.system() == "Windows":
        add_to_path_windows(bin_dir)
    else:
        add_to_path_unix(bin_dir)

    # Provide restart instructions
    detect_current_shell()

    print("\n" + "=" * 50)
    print("🎉 PassHolder installation completed!")
    print("\nAfter restarting your terminal, you can use:")
    print("   passholder add      # Add a new password")
    print("   passholder view     # View all passwords")
    print("   passholder --help   # Show all commands")
    print("\n🔐 Your passwords will be stored securely with encryption.")


if __name__ == "__main__":
    main()
