#!/usr/bin/env python3
"""
PassHolder Virtual Environment Installation Script
For systems with externally managed Python environments
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def main():
    """Install PassHolder using virtual environment"""
    print("🚀 PassHolder Virtual Environment Installation")
    print("=" * 50)

    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / ".venv"

    print(f"📁 Installing from: {script_dir}")

    # Create virtual environment
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"✅ Virtual environment created at {venv_path}")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        print("   On Ubuntu/Debian, you may need: sudo apt install python3-venv")
        sys.exit(1)

    # Get virtual environment Python
    if platform.system() == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"

    # Install packages in virtual environment
    print("📦 Installing packages in virtual environment...")
    requirements_file = script_dir / "requirements.txt"

    # Try to upgrade pip, but don't fail if it doesn't work
    try:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print("⚠️  Pip upgrade failed, continuing with existing pip...")

    # Install requirements
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)],
        check=True,
    )

    print("✅ Packages installed successfully")

    # Create wrapper script that uses virtual environment
    bin_dir = script_dir / "bin"
    bin_dir.mkdir(exist_ok=True)

    if platform.system() == "Windows":
        wrapper_path = bin_dir / "passholder.bat"
        wrapper_content = f"""@echo off
"{venv_python}" "{script_dir / "passholder.py"}" %*
"""
    else:
        wrapper_path = bin_dir / "passholder"
        wrapper_content = f"""#!/bin/bash
"{venv_python}" "{script_dir / "passholder.py"}" "$@"
"""

    wrapper_path.write_text(wrapper_content)

    if platform.system() != "Windows":
        os.chmod(wrapper_path, 0o755)

    print(f"✅ Wrapper script created at {wrapper_path}")

    # Create aliases on Unix systems
    if platform.system() != "Windows":
        print("🔗 Setting up shell aliases...")

        # Add alias to bash profile
        bashrc_path = Path.home() / ".bashrc"
        if bashrc_path.exists():
            bashrc_content = bashrc_path.read_text()
            if "alias passholder=" not in bashrc_content:
                with bashrc_path.open("a") as f:
                    f.write(f"\n# PassHolder alias added by installer\n")
                    f.write(
                        f"alias passholder='{venv_path}  {script_dir / 'passholder.py'}'\n"
                    )
                print("✅ Added alias to ~/.bashrc")
            else:
                print("✅ Alias already exists in ~/.bashrc")

        # Add alias to zsh profile
        zshrc_path = Path.home() / ".zshrc"
        if zshrc_path.exists():
            zshrc_content = zshrc_path.read_text()
            if "alias passholder=" not in zshrc_content:
                with zshrc_path.open("a") as f:
                    f.write(f"\n# PassHolder alias added by installer\n")
                    f.write(f"alias passholder='{wrapper_path}'\n")
                print("✅ Added alias to ~/.zshrc")
            else:
                print("✅ Alias already exists in ~/.zshrc")

    print("\n" + "=" * 50)
    print("🎉 Virtual Environment Installation Complete!")

    if platform.system() == "Windows":
        print("\nTo use PassHolder:")
        print(f"   {wrapper_path} --help")
        print(f"   {wrapper_path} add")
        print(f"   {wrapper_path} view")
        print("\nOr add to your PATH:")
        print(f'   $env:PATH += ";{bin_dir}"')
    else:
        print("\nAfter restarting your terminal or running:")
        print("   source ~/.bashrc    # if using bash")
        print("   source ~/.zshrc     # if using zsh")
        print("\nYou can use:")
        print("   passholder --help")
        print("   passholder add")
        print("   passholder view")


if __name__ == "__main__":
    main()
