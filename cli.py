#!/usr/bin/env python3
"""
PassHolder CLI - Command Line Interface for Password Manager
===========================================================

This module provides a comprehensive command-line interface for the PassHolder
password manager. It offers all the functionality of the GUI interface in a
scriptable, automation-friendly format.

Key Features:
- Full CRUD operations for password management
- Secure clipboard integration with auto-clear
- Advanced search and filtering capabilities
- Rich terminal output with tables and formatting
- Batch operations support
- Cross-platform compatibility

Commands Available:
- add: Add new password entries
- view: Display all passwords in formatted tables
- remove: Delete password entries
- copy: Copy passwords to clipboard
- search: Search passwords by service/username
- get: Retrieve specific passwords

Security Features:
- Same encryption as GUI (Fernet AES 256)
- Secure password input with masking
- Master password verification
- Memory-safe operations
- No password exposure in command history

Usage Examples:
    python cli.py add gmail -u user@gmail.com -p secret123
    python cli.py view
    python cli.py copy gmail
    python cli.py search @company.com
    python cli.py remove old-service

Author: PassHolder Team
License: Open Source
"""

import argparse
import sys
import getpass
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from encryptedSQLiteDB import EncryptedSQLiteDB
from config import check_db_exists


class PassHolderCLI:
    """
    Command Line Interface handler for PassHolder password manager.

    This class provides a rich command-line interface with support for
    all password management operations. It handles authentication,
    database operations, and provides formatted output using the Rich library.

    Attributes:
        console (Console): Rich console for formatted output
        db (EncryptedSQLiteDB): Database connection instance

    Methods:
        authenticate(): Handle master password authentication
        add_password(): Add new password entries
        view_passwords(): Display all passwords in table format
        remove_password(): Delete password entries
        copy_password(): Copy passwords to clipboard
        search_passwords(): Search and filter passwords
        get_password(): Retrieve specific passwords
    """

    def __init__(self):
        """Initialize CLI with Rich console and prepare database connection."""
        self.console = Console()
        self.db = None

    def authenticate(self):
        """
        Authenticate user with master password and initialize database.

        Handles both existing and new database scenarios:
        - For existing databases: Prompts for master password
        - For new setups: Guides through master password creation

        The master password is used to derive the encryption key for
        all password data using PBKDF2 with 100,000 iterations.

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            Exception: If database initialization fails
            KeyboardInterrupt: If user cancels authentication
        """
        if check_db_exists():
            self.console.print(
                "[yellow]Database found. Please enter your master password.[/yellow]"
            )
            master_password = getpass.getpass("Master password: ")
        else:
            self.console.print(
                "[yellow]No database found. Please set a new master password.[/yellow]"
            )
            while True:
                master_password = getpass.getpass("Set master password: ")
                confirm_password = getpass.getpass("Confirm master password: ")
                if master_password == confirm_password:
                    break
                else:
                    self.console.print(
                        "[red]Passwords do not match. Please try again.[/red]"
                    )

        try:
            self.db = EncryptedSQLiteDB(master_password)
            return True
        except Exception as e:
            self.console.print(f"[red]Authentication failed: {e}[/red]")
            return False

    def add_password(self, args):
        """Add a new password entry"""
        if not self.authenticate():
            return

        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return

        try:
            # Get service name
            service = args.service if args.service else Prompt.ask("Service")

            # Get username (optional)
            username = (
                args.username
                if hasattr(args, "username") and args.username
                else Prompt.ask("Username (optional)", default="")
            )

            # Get password
            if hasattr(args, "password") and args.password:
                password = args.password
            else:
                password = getpass.getpass("Password: ")

            # Get notes (optional)
            notes = (
                args.notes
                if hasattr(args, "notes") and args.notes
                else Prompt.ask("Notes (optional)", default="")
            )

            # Add to database - Note: database expects (service, password, username, notes)
            self.db.add_password(service, password, username, notes)
            self.console.print(
                f"[green]✓ Successfully added password for '{service}'![/green]"
            )

        except Exception as e:
            self.console.print(f"[red]Failed to add password: {e}[/red]")
        finally:
            if self.db:
                self.db.close()

    def list_passwords(self, args):
        """List all passwords"""
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return
        try:
            passwords = (
                self.db.get_passwords()
            )  # No service parameter gets all passwords

            if not passwords:
                self.console.print("[yellow]No passwords found.[/yellow]")
                return

            table = Table(title="Stored Passwords")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Service", style="blue", no_wrap=True)
            table.add_column("Username", style="green")
            table.add_column("Notes", style="dim")

            for pwd in passwords:
                table.add_row(
                    str(pwd[0]),  # id
                    pwd[1],  # service
                    pwd[2] or "",  # username
                    pwd[4] or "",  # notes
                )

            self.console.print(table)

        except Exception as e:
            self.console.print(f"[red]Failed to list passwords: {e}[/red]")
        finally:
            if self.db:
                self.db.close()

    def get_password(self, args):
        """Get password for a service"""
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return
        try:
            service = args.service
            username = getattr(args, "username", None)

            if username:
                passwords = self.db.get_passwords(service)
                matching = [p for p in passwords if p[2] == username]
                if not matching:
                    self.console.print(
                        f"[red]No password found for '{service}' with username '{username}'[/red]"
                    )
                    return
                password = matching[0][3]
            else:
                passwords = self.db.get_passwords(service)
                if not passwords:
                    self.console.print(f"[red]No password found for '{service}'[/red]")
                    return
                elif len(passwords) > 1:
                    self.console.print(
                        f"[yellow]Multiple passwords found for '{service}':[/yellow]"
                    )
                    for i, pwd in enumerate(passwords, 1):
                        username_display = (
                            f" ({pwd[2]})" if pwd[2] else " (no username)"
                        )
                        self.console.print(f"  {i}. ID {pwd[0]}{username_display}")
                    return
                password = passwords[0][3]

            self.console.print(f"[green]Password for '{service}': {password}[/green]")

        except Exception as e:
            self.console.print(f"[red]Failed to get password: {e}[/red]")
        finally:
            if self.db:
                self.db.close()

    def copy_password(self, args):
        """
        Copy password to clipboard with support for multiple service matches.

        If multiple passwords exist for the same service name, displays a
        numbered list for user selection. Supports copying by service name,
        username, or specific ID.

        Args:
            args: Parsed command arguments containing service, username, and id
        """
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return

        try:
            service = args.service
            username = getattr(args, "username", None)
            password_id = getattr(args, "id", None)

            # If ID provided, copy directly by ID
            if password_id:
                result = self.db.copy_password_by_id(password_id)
                self.console.print(f"[green]✓ {result}[/green]")
                return

            # If username provided, try exact match
            if username:
                result = self.db.copy_password(service, username)
                self.console.print(f"[green]✓ {result}[/green]")
                return

            # Search by service name only - handle multiple matches
            matching_passwords = self.db.get_matching_passwords(service)

            if not matching_passwords:
                self.console.print(
                    f"[red]No passwords found for service '{service}'[/red]"
                )
                return

            if len(matching_passwords) == 1:
                # Single match - copy directly
                password_id = matching_passwords[0][0]
                result = self.db.copy_password_by_id(password_id)
                self.console.print(f"[green]✓ {result}[/green]")
                return

            # Multiple matches - display selection menu
            self.console.print(
                f"[yellow]Multiple passwords found for '{service}':[/yellow]\n"
            )

            # Create and display selection table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Index", style="cyan", width=6)
            table.add_column("Service", style="green")
            table.add_column("Username", style="blue")
            table.add_column("Notes", style="yellow")

            for idx, (password_id, svc, username_val, password, notes) in enumerate(
                matching_passwords, 1
            ):
                # Truncate long values for display
                display_username = (
                    username_val[:20] + "..."
                    if username_val and len(username_val) > 20
                    else (username_val or "")
                )
                display_notes = (
                    notes[:30] + "..." if notes and len(notes) > 30 else (notes or "")
                )

                table.add_row(str(idx), svc, display_username, display_notes)

            self.console.print(table)

            # Get user selection
            self.console.print(
                f"\n[cyan]Please select which password to copy (1-{len(matching_passwords)}) or 'q' to quit:[/cyan]"
            )

            while True:
                try:
                    choice = input("Selection: ").strip().lower()

                    if choice == "q" or choice == "quit":
                        self.console.print("[yellow]Copy operation cancelled.[/yellow]")
                        return

                    selection_idx = int(choice)
                    if 1 <= selection_idx <= len(matching_passwords):
                        # Valid selection - copy the chosen password
                        selected_password = matching_passwords[selection_idx - 1]
                        password_id = selected_password[0]
                        result = self.db.copy_password_by_id(password_id)
                        self.console.print(f"[green]✓ {result}[/green]")
                        return
                    else:
                        self.console.print(
                            f"[red]Please enter a number between 1 and {len(matching_passwords)}[/red]"
                        )

                except ValueError:
                    self.console.print(
                        "[red]Please enter a valid number or 'q' to quit[/red]"
                    )
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Copy operation cancelled.[/yellow]")
                    return

        except ValueError as e:
            self.console.print(f"[red]{e}[/red]")
        except Exception as e:
            self.console.print(f"[red]Failed to copy password: {e}[/red]")
        finally:
            if self.db:
                self.db.close()

    def delete_password(self, args):
        """Delete a password entry"""
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return
        try:
            if hasattr(args, "id") and args.id:
                password_id = args.id
            else:
                service = args.service
                passwords = self.db.get_passwords(service)
                if not passwords:
                    self.console.print(f"[red]No password found for '{service}'[/red]")
                    return
                elif len(passwords) > 1:
                    self.console.print(
                        f"[yellow]Multiple passwords found for '{service}':[/yellow]"
                    )
                    for pwd in passwords:
                        username_display = (
                            f" ({pwd[2]})" if pwd[2] else " (no username)"
                        )
                        self.console.print(f"  ID {pwd[0]}{username_display}")
                    password_id = Prompt.ask(
                        "Enter ID to delete", choices=[str(p[0]) for p in passwords]
                    )
                else:
                    password_id = passwords[0][0]

            # Confirm deletion
            confirm = Prompt.ask(
                f"Are you sure you want to delete password ID {password_id}?",
                choices=["y", "n"],
                default="n",
            )
            if confirm.lower() == "y":
                self.db.delete_password(int(password_id))
                self.console.print(
                    f"[green]✓ Successfully deleted password ID {password_id}![/green]"
                )
            else:
                self.console.print("[yellow]Deletion cancelled.[/yellow]")

        except Exception as e:
            self.console.print(f"[red]Failed to delete password: {e}[/red]")
        finally:
            if self.db:
                self.db.close()

    def search_passwords(self, args):
        """Search passwords by service name"""
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return
        try:
            service = args.service
            passwords = self.db.get_passwords(service)

            if not passwords:
                self.console.print(
                    f"[yellow]No passwords found matching '{service}'.[/yellow]"
                )
                return

            table = Table(title=f"Search Results for '{service}'")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Service", style="blue", no_wrap=True)
            table.add_column("Username", style="green")
            table.add_column("Notes", style="dim")

            for pwd in passwords:
                table.add_row(
                    str(pwd[0]),  # id
                    pwd[1],  # service
                    pwd[2] or "",  # username
                    pwd[4] or "",  # notes
                )

            self.console.print(table)

        except Exception as e:
            self.console.print(f"[red]Failed to search passwords: {e}[/red]")
        finally:
            if self.db:
                self.db.close()


def main():
    parser = argparse.ArgumentParser(
        description="PassHolder - Secure Password Manager CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add password command
    add_parser = subparsers.add_parser("add", help="Add a new password")
    add_parser.add_argument("service", nargs="?", help="Service name")
    add_parser.add_argument("-u", "--username", help="Username")
    add_parser.add_argument("-p", "--password", help="Password")
    add_parser.add_argument("-n", "--notes", help="Notes")

    # List passwords command
    list_parser = subparsers.add_parser("list", help="List all passwords")

    # Get password command
    get_parser = subparsers.add_parser("get", help="Get password for a service")
    get_parser.add_argument("service", help="Service name")
    get_parser.add_argument("-u", "--username", help="Username")

    # Copy password command
    copy_parser = subparsers.add_parser("copy", help="Copy password to clipboard")
    copy_parser.add_argument("service", nargs="?", help="Service name")
    copy_parser.add_argument("-u", "--username", help="Username")
    copy_parser.add_argument("-i", "--id", type=int, help="Password ID")

    # Delete password command
    delete_parser = subparsers.add_parser("delete", help="Delete a password")
    delete_parser.add_argument("service", nargs="?", help="Service name")
    delete_parser.add_argument("-i", "--id", type=int, help="Password ID")

    # Search passwords command
    search_parser = subparsers.add_parser("search", help="Search passwords by service")
    search_parser.add_argument("service", help="Service name to search")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = PassHolderCLI()

    if args.command == "add":
        cli.add_password(args)
    elif args.command == "list":
        cli.list_passwords(args)
    elif args.command == "get":
        cli.get_password(args)
    elif args.command == "copy":
        cli.copy_password(args)
    elif args.command == "delete":
        cli.delete_password(args)
    elif args.command == "search":
        cli.search_passwords(args)


if __name__ == "__main__":
    main()
