#!/usr/bin/env python3
"""
PassHolder CLI - Command Line Interface for Password Manager
Usage: python cli.py <command> [options]
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
    def __init__(self):
        self.console = Console()
        self.db = None

    def authenticate(self):
        """Authenticate user with master password"""
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

            # Add to database
            self.db.add_password(service, username, password, notes)
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
        """Copy password to clipboard"""
        if not self.authenticate():
            return
        if self.db is None:
            self.console.print("[red]Database connection failed.[/red]")
            return
        try:
            service = args.service
            username = getattr(args, "username", None)
            password_id = getattr(args, "id", None)

            if password_id:
                result = self.db.copy_password_by_id(password_id)
            else:
                result = self.db.copy_password(service, username)

            self.console.print(f"[green]✓ {result}[/green]")

        except ValueError as e:
            error_str = str(e)
            if "Multiple passwords found" in error_str:
                self.console.print(f"[yellow]{e}[/yellow]")
            else:
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
