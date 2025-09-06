from rich.prompt import Prompt
from ui import UI
from encryptedSQLiteDB import EncryptedSQLiteDB
from config import check_db_exists
import sys
import argparse


def run_gui():
    """Run the graphical user interface"""
    try:
        # Show loading animation
        temp_ui = UI(None)
        temp_ui.loading_animation()

        # Get master password
        if check_db_exists():
            print("Database found. Please enter your master password to unlock.")
            master_password = Prompt.ask("Enter master password", password=True)
        else:
            print("No database found. Please set a new master password.")
            while True:
                master_password = Prompt.ask("Set master password", password=True)
                confirm_password = Prompt.ask("Confirm master password", password=True)
                if master_password == confirm_password:
                    break
                else:
                    print("Passwords do not match. Please try again.")

        # Initialize encrypted database
        db = EncryptedSQLiteDB(master_password)

        # Initialize UI with database
        ui = UI(db)

        # Start main loop
        ui.main_loop()

        # Close database
        db.close()

    except KeyboardInterrupt:
        ui_temp = UI(None)
        ui_temp.closing_animation()


def main_cli():
    """Main CLI entry point for 'passholder' command"""
    from cli import PassHolderCLI

    # Parse CLI arguments with simplified commands
    parser = argparse.ArgumentParser(description="PassHolder - Secure Password Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add password command
    add_parser = subparsers.add_parser("add", help="Add a new password")
    add_parser.add_argument("service", nargs="?", help="Service name")
    add_parser.add_argument("-u", "--username", help="Username")
    add_parser.add_argument("-p", "--password", help="Password")
    add_parser.add_argument("-n", "--notes", help="Notes")

    # View passwords command (renamed from list)
    view_parser = subparsers.add_parser("view", help="View all passwords")

    # Remove password command (renamed from delete)
    remove_parser = subparsers.add_parser("remove", help="Remove a password")
    remove_parser.add_argument("service", nargs="?", help="Service name")
    remove_parser.add_argument("-i", "--id", type=int, help="Password ID")

    # Copy password command
    copy_parser = subparsers.add_parser("copy", help="Copy password to clipboard")
    copy_parser.add_argument("service", nargs="?", help="Service name")
    copy_parser.add_argument("-u", "--username", help="Username")
    copy_parser.add_argument("-i", "--id", type=int, help="Password ID")

    # Search passwords command
    search_parser = subparsers.add_parser("search", help="Search passwords by service")
    search_parser.add_argument("service", help="Service name to search")

    # Get password command
    get_parser = subparsers.add_parser("get", help="Get password for a service")
    get_parser.add_argument("service", help="Service name")
    get_parser.add_argument("-u", "--username", help="Username")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = PassHolderCLI()

    if args.command == "add":
        cli.add_password(args)
    elif args.command == "view":
        cli.list_passwords(args)
    elif args.command == "remove":
        cli.delete_password(args)
    elif args.command == "copy":
        cli.copy_password(args)
    elif args.command == "search":
        cli.search_passwords(args)
    elif args.command == "get":
        cli.get_password(args)


def run_cli():
    """Run the command-line interface (legacy)"""
    from cli import PassHolderCLI

    # Parse CLI arguments (skip 'main.py' and 'cli' from sys.argv)
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

    # Parse arguments from sys.argv[2:] (skip 'main.py' and 'cli')
    args = parser.parse_args(sys.argv[2:])

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


def main():
    """Main function to start the PassHolder application"""
    try:
        # Check if CLI mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "cli":
            run_cli()
        else:
            # Run GUI mode by default
            run_gui()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
