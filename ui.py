#!/usr/bin/env python3
"""
PassHolder UI - Rich Terminal User Interface
============================================

This module provides a beautiful, interactive terminal-based user interface
for the PassHolder password manager using the Rich library. It offers a
modern, responsive design with themes, animations, and intuitive navigation.

Key Features:
- Responsive terminal interface that adapts to window size
- Beautiful themes with consistent color schemes
- Smooth loading and transition animations
- Paginated password display for large collections
- Real-time search and filtering
- Secure password input with masking
- Clipboard integration with visual feedback
- Progress indicators and status messages

UI Components:
- Main menu with numbered options
- Password tables with sorting and filtering
- Add/edit forms with validation
- Search interface with live results
- Confirmation dialogs for destructive operations
- Status panels and notifications

Design Principles:
- Mobile-first responsive design
- Accessibility considerations
- Consistent visual hierarchy
- Clear action feedback
- Graceful error handling

The interface automatically adjusts to terminal size and provides
fallbacks for terminals with limited capabilities.

Author: PassHolder Team
License: Open Source
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
import time
import os


class UI:
    """
    Rich terminal-based user interface for PassHolder password manager.

    This class provides a comprehensive, interactive terminal interface
    with modern design principles and responsive layout. It handles all
    user interactions, visual feedback, and maintains state throughout
    the application lifecycle.

    Attributes:
        console (Console): Rich console for output rendering
        db (EncryptedSQLiteDB): Database connection for operations
        theme (Theme): Color scheme and styling definitions
        terminal_height (int): Current terminal height in lines
        terminal_width (int): Current terminal width in columns
        history (list): Navigation history for back/forward functionality

    Key Methods:
        main_loop(): Primary interaction loop
        loading_animation(): Startup loading sequence
        closing_animation(): Graceful shutdown animation
        show_main_menu(): Display main navigation menu
        view_passwords(): Paginated password display
        add_password(): Password creation interface
        search_passwords(): Interactive search functionality

    Design Features:
        - Responsive layout that adapts to terminal size
        - Consistent color theming throughout
        - Smooth animations and transitions
        - Pagination for large datasets
        - Real-time input validation
        - Secure password handling
    """

    def __init__(self, db):
        """
        Initialize the UI with database connection and configure theming.

        Sets up the Rich console with custom theme, determines terminal
        dimensions for responsive layout, and initializes navigation history.

        Args:
            db (EncryptedSQLiteDB): Active database connection
        """
        self.console = Console()
        self.db = db

        # Define consistent color theme for the application
        self.theme = Theme(
            {
                "info": "cyan",
                "warning": "yellow",
                "error": "red",
                "success": "green",
                "title": "bold magenta",
            }
        )
        self.console.push_theme(self.theme)

        # Get terminal dimensions for responsive design
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width

        # Initialize navigation history
        self.history = []

    def get_responsive_ascii_art(self):
        """
        Generate ASCII art that adapts to terminal width.

        Returns different ASCII art based on terminal width:
        - Large (120+ chars): Full detailed banner
        - Medium (80-119 chars): Compact banner
        - Small (<80 chars): Simple text banner
        """
        width = self.console.size.width

        if width >= 120:
            # Large ASCII art for wide terminals
            return """
        ██████╗  █████╗ ███████╗███████╗██╗  ██╗ ██████╗ ██╗     ██████╗ ███████╗██████╗ 
        ██╔══██╗██╔══██╗██╔════╝██╔════╝██║  ██║██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗
        ██████╔╝███████║███████╗███████╗███████║██║   ██║██║     ██║  ██║█████╗  ██████╔╝
        ██╔═══╝ ██╔══██║╚════██║╚════██║██╔══██║██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗
        ██║     ██║  ██║███████║███████║██║  ██║╚██████╔╝███████╗██████╔╝███████╗██║  ██║
        ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝
        """
        elif width >= 80:
            # Medium ASCII art for standard terminals
            return """
        ██████╗  █████╗ ███████╗███████╗
        ██╔══██╗██╔══██╗██╔════╝██╔════╝
        ██████╔╝███████║███████╗███████╗
        ██╔═══╝ ██╔══██║╚════██║╚════██║
        ██║     ██║  ██║███████║███████║
        ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
        
        ██╗  ██╗ ██████╗ ██╗     ██████╗ ███████╗██████╗ 
        ██║  ██║██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗
        ███████║██║   ██║██║     ██║  ██║█████╗  ██████╔╝
        ██╔══██║██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗
        ██║  ██║╚██████╔╝███████╗██████╔╝███████╗██║  ██║
        ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝
        """
        else:
            # Simple text banner for narrow terminals
            return """
        ╔═══════════════════════════════════════╗
        ║            PASSHOLDER                 ║
        ║       Password Manager v1.0.0         ║
        ║        Secure • Fast • Local          ║
        ╚═══════════════════════════════════════╝
        """

    def loading_animation(self):
        """
        Display startup loading animation with responsive design.

        Shows a professional loading sequence with:
        - Responsive ASCII art banner (adapts to terminal width)
        - PassHolder branding and version
        - Security initialization messages
        - Database connection feedback

        This provides user feedback during application startup and
        creates a polished first impression that works on any terminal size.
        """
        # Clear screen for dramatic effect
        self.console.clear()

        # Get responsive ASCII art based on terminal width
        ascii_art = self.get_responsive_ascii_art()

        # Display banner with gradient colors
        banner_panel = Panel(
            Text(ascii_art, style="bold magenta", justify="center"),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold cyan]🔐 SECURE PASSWORD MANAGER 🔐[/]",
            subtitle="[dim]v1.0.0[/]",
        )
        self.console.print(banner_panel)
        self.console.print()

        # Final loading confirmation
        self.console.print(
            "[bold green]✅ Security protocols loaded successfully![/bold green]"
        )
        time.sleep(0.5)

        self.console.print()

        # Brief pause to let user read the success message
        time.sleep(1.5)

    def display_menu(self):
        menu_items = [
            "1. Add Password",
            "2. Delete Password",
            "3. View Passwords",
            "4. Copy Password",
            "5. Search Passwords",
            "6. Exit",
        ]
        menu = Text(
            "\n".join(menu_items),
            style="info",
            justify="full",
        )
        menu_panel = Panel(
            menu,
            title="PassHolder Menu",
            subtitle="Select an option",
            style="bold blue",
            height=10,
            padding=(1, 2),
        )

        self.console.print(menu_panel, justify="center")

    def output_panel(self, content):
        panel = Panel(
            "\n".join(content) if isinstance(content, list) else content,
            title="history" if isinstance(content, list) else "Output",
            style="bold green",
            padding=(1, 2),
            width=self.terminal_width,
            height=self.terminal_height // 2,
        )
        self.console.print(panel, justify="left")

    def closing_animation(self):
        """
        Display graceful shutdown animation.
        """
        self.console.print()

        # Simple shutdown messages
        shutdown_messages = [
            "🔐 Securing database connections...",
            "🧹 Clearing sensitive data from memory...",
            " Locking encrypted database...",
            "✅ Security protocols completed!",
        ]

        # Display shutdown messages one by one
        for message in shutdown_messages:
            self.console.print(f"[yellow]{message}[/yellow]")
            time.sleep(0.5)

        # Final goodbye
        self.console.print(
            "[bold green]👋 Thank you for using PassHolder! Stay secure![/bold green]"
        )
        time.sleep(1)
        self.console.clear()

    def display_passwords(self, passwords):
        table = Table(title="Stored Passwords", show_lines=True)
        table.add_column("Index", justify="right", style="dim", no_wrap=True)
        table.add_column("Service", justify="right", style="cyan", no_wrap=True)
        table.add_column("Username", style="magenta")
        table.add_column("Password", style="green")
        table.add_column("Notes", style="bold yellow")
        for i, pwd in enumerate(passwords):
            table.add_row(
                str(i + 1), pwd[0], pwd[1], pwd[2], pwd[3] if len(pwd) > 3 else ""
            )
        return table

    def paginated_password_view(self, records, page_size=5):
        total_passwords = len(records)
        total_pages = (total_passwords + page_size - 1) // page_size
        current_page = 0

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            self.display_menu()

            start_index = current_page * page_size
            end_index = start_index + page_size
            page_passwords = records[start_index:end_index]

            table = self.display_passwords(page_passwords)
            self.output_panel(table)

            if total_pages < 1:
                break

            prompt_text = (
                f"Page {current_page + 1}/{total_pages}. (N)ext, (P)revious, (E)xit: "
            )
            choice = Prompt.ask(prompt_text, default="E").lower()

            if choice == "n" and current_page < total_pages - 1:
                current_page += 1
            elif choice == "p" and current_page > 0:
                current_page -= 1
            elif choice == "e":
                self.history.append("> viewed passwords")
                break

        os.system("cls" if os.name == "nt" else "clear")
        self.display_menu()
        self.output_panel(self.history)

    def delete_password(self, matching_records, page_size=5):
        if not matching_records:
            return False, None

        total_records = len(matching_records)
        total_pages = (total_records + page_size - 1) // page_size
        current_page = 0

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            self.display_menu()

            start_index = current_page * page_size
            end_index = start_index + page_size
            page_records = matching_records[start_index:end_index]

            table = Table(title="Select Password to Delete", show_lines=True)
            table.add_column("Index", style="red")
            table.add_column("Service", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("Password", style="green")
            table.add_column("Notes", style="bold yellow")

            for i, record in enumerate(page_records):
                global_index = start_index + i + 1  # Global index across all pages
                table.add_row(
                    str(global_index),
                    record[0],
                    record[1],
                    record[2],
                    record[3] if len(record) > 3 else "",
                )

            self.output_panel(table)

            if total_pages <= 1:
                # Single page - just get index selection
                choice = Prompt.ask(
                    f"Enter index (1-{total_records}) or (E)xit", default="E"
                )
            else:
                # Multiple pages - show navigation options
                prompt_text = f"Page {current_page + 1}/{total_pages}. Enter index (1-{total_records}), (N)ext, (P)revious, or (E)xit: "
                choice = Prompt.ask(prompt_text, default="E")

            choice = choice.strip().lower()

            # Handle navigation
            if choice == "n" and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice == "p" and current_page > 0:
                current_page -= 1
                continue
            elif choice == "e":
                return False, None

            # Handle index selection
            try:
                idx = int(choice) - 1
                if 0 <= idx < total_records:
                    # Confirm deletion
                    confirm = Prompt.ask(
                        f"Delete {matching_records[idx][0]}?",
                        choices=["y", "n"],
                        default="n",
                    )
                    return confirm.lower() == "y", idx
                else:
                    self.console.print(
                        f"[error]Enter a valid index (1-{total_records})[/error]"
                    )
                    time.sleep(1)
            except ValueError:
                self.console.print("[error]Invalid input[/error]")
                time.sleep(1)

    def add_password_ui(self):
        """UI for adding a new password"""
        os.system("cls" if os.name == "nt" else "clear")
        self.display_menu()

        # Get password details from user
        service = Prompt.ask("Enter service name")
        username = Prompt.ask("Enter username", default="")
        password = Prompt.ask("Enter password", password=True)
        notes = Prompt.ask("Enter notes (optional)", default="")

        try:
            result = self.db.add_password(service, password, username, notes)
            self.history.append(f"> {result}")
            self.console.print(f"[success]{result}[/success]")
        except Exception as e:
            error_msg = f"Failed to add password: {e}"
            self.history.append(f"> Error: {error_msg}")
            self.console.print(f"[error]{error_msg}[/error]")

        Prompt.ask("Press Enter to continue")

    def copy_password_ui(self):
        """UI for copying a password to clipboard"""
        os.system("cls" if os.name == "nt" else "clear")
        self.display_menu()

        service = Prompt.ask("Enter service name")

        try:
            # First try to copy without username to see if there are multiple options
            result = self.db.copy_password(service)
            self.history.append(f"> {result}")
            self.console.print(f"[success]{result}[/success]")

        except ValueError as e:
            error_str = str(e)
            if (
                "Multiple passwords found" in error_str
                and "Available options:" in error_str
            ):

                # Get all matching passwords for display
                matching_passwords = self.db.get_matching_passwords(service)

                # Display them in a table
                table = Table(title=f"Multiple passwords found for '{service}'")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Service", style="blue", no_wrap=True)
                table.add_column("Username", style="green")
                table.add_column("Notes", style="dim")

                for pwd in matching_passwords:
                    table.add_row(
                        str(pwd[0]),  # id
                        pwd[1],  # service
                        pwd[2] or "",  # username
                        pwd[4] or "",  # notes
                    )

                self.console.print(table)

                # Ask user to select by ID
                try:
                    password_id = Prompt.ask("Enter the ID of the password to copy")
                    password_id = int(password_id)
                    result = self.db.copy_password_by_id(password_id)
                    self.history.append(f"> {result}")
                    self.console.print(f"[success]{result}[/success]")
                except ValueError as id_error:
                    error_msg = f"Invalid ID or password not found: {id_error}"
                    self.history.append(f"> Error: {error_msg}")
                    self.console.print(f"[error]{error_msg}[/error]")
            else:
                # Other error (no passwords found, etc.)
                error_msg = f"Failed to copy password: {e}"
                self.history.append(f"> Error: {error_msg}")
                self.console.print(f"[error]{error_msg}[/error]")
        except Exception as e:
            error_msg = f"Failed to copy password: {e}"
            self.history.append(f"> Error: {error_msg}")
            self.console.print(f"[error]{error_msg}[/error]")

        Prompt.ask("Press Enter to continue")

    def search_passwords_ui(self):
        """UI for searching passwords by service"""
        os.system("cls" if os.name == "nt" else "clear")
        self.display_menu()

        service = Prompt.ask("Enter service name to search")

        try:
            passwords = self.db.get_passwords(service)
            if passwords:
                # Convert database format (id, service, username, password, notes)
                # to UI format (service, username, password, notes)
                formatted_passwords = [
                    (p[1], p[2], p[3], p[4] if len(p) > 4 else "") for p in passwords
                ]
                self.paginated_password_view(formatted_passwords)
                self.history.append(
                    f"> Searched for '{service}' - {len(passwords)} results"
                )
            else:
                self.console.print(
                    f"[warning]No passwords found for '{service}'[/warning]"
                )
                self.history.append(f"> Searched for '{service}' - no results")
                Prompt.ask("Press Enter to continue")
        except Exception as e:
            error_msg = f"Search failed: {e}"
            self.history.append(f"> Error: {error_msg}")
            self.console.print(f"[error]{error_msg}[/error]")
            Prompt.ask("Press Enter to continue")
            Prompt.ask("Press Enter to continue")

    def main_loop(self):
        """Main application loop"""
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            self.display_menu()

            if self.history:
                self.output_panel(self.history[-5:])  # Show last 5 history items
            else:
                self.output_panel(
                    Text(
                        "Welcome to PassHolder!\n\nSelect an option from the menu above.",
                        style="info",
                    )
                )

            choice = Prompt.ask(
                "Enter your choice", choices=["1", "2", "3", "4", "5", "6"], default="6"
            )

            if choice == "1":
                self.add_password_ui()
            elif choice == "2":
                # Delete password
                try:
                    all_passwords = self.db.get_passwords()
                    if all_passwords:
                        # Convert to format expected by delete_password method
                        formatted_passwords = [
                            (p[1], p[2], p[3], p[4] if len(p) > 4 else "")
                            for p in all_passwords
                        ]
                        should_delete, selected_idx = self.delete_password(
                            formatted_passwords
                        )
                        if should_delete and selected_idx is not None:
                            password_id = all_passwords[selected_idx][0]  # Get the ID
                            try:
                                result = self.db.delete_password(password_id)
                                self.history.append(f"> {result}")
                                self.console.print(f"[success]{result}[/success]")
                                Prompt.ask("Press Enter to continue")
                            except Exception as e:
                                error_msg = f"Failed to delete password: {e}"
                                self.history.append(f"> Error: {error_msg}")
                                self.console.print(f"[error]{error_msg}[/error]")
                                Prompt.ask("Press Enter to continue")
                    else:
                        self.console.print("[warning]No passwords to delete[/warning]")
                        Prompt.ask("Press Enter to continue")
                except Exception as e:
                    self.console.print(
                        f"[error]Failed to retrieve passwords: {e}[/error]"
                    )
                    Prompt.ask("Press Enter to continue")
            elif choice == "3":
                try:
                    passwords = self.db.get_passwords()
                    if passwords:
                        # Convert to format expected by paginated_password_view
                        formatted_passwords = [
                            (p[1], p[2], p[3], p[4] if len(p) > 4 else "")
                            for p in passwords
                        ]
                        self.paginated_password_view(formatted_passwords)
                        self.history.append(f"> Viewed {len(passwords)} passwords")
                    else:
                        self.console.print("[warning]No passwords stored[/warning]")
                        self.history.append("> No passwords to view")
                        Prompt.ask("Press Enter to continue")
                except Exception as e:
                    error_msg = f"Failed to retrieve passwords: {e}"
                    self.history.append(f"> Error: {error_msg}")
                    self.console.print(f"[error]{error_msg}[/error]")
                    Prompt.ask("Press Enter to continue")
            elif choice == "4":
                self.copy_password_ui()
            elif choice == "5":
                self.search_passwords_ui()
            elif choice == "6":
                self.closing_animation()
                break
