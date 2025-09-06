from rich.prompt import Prompt
from ui import UI
from encryptedSQLiteDB import EncryptedSQLiteDB
from config import check_db_exists


def main():
    """Main function to start the PassHolder application"""
    try:
        # Get master password
        temp_ui = UI(None)
        temp_ui.loading_animation()
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

    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        ui_temp = UI(None)
        ui_temp.closing_animation()


if __name__ == "__main__":
    main()
