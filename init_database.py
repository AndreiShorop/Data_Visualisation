from app.services.auth_service import AuthService
from app.config import USERS_DB_PATH
import os

def init_db():
    print("--- Analytical Platform Pro: Database Initialization ---")
    
    # Ensure the database file location is clear
    db_file = USERS_DB_PATH
    if db_file.exists():
        print(f"Database already exists at: {db_file}")
        confirm = input("Do you want to re-initialize it? All data will be lost! (y/N): ")
        if confirm.lower() != 'y':
            print("Initialization cancelled.")
            return
        os.remove(db_file)
        print("Existing database deleted.")

    # Initialize AuthService (this creates tables automatically)
    auth = AuthService(db_file)
    print(f"Base schema created at {db_file}")

    # Add default admin
    admin_user = "admin"
    admin_pass = "admin123"
    
    success = auth.register_user(admin_user, admin_pass, is_admin=True)
    if success:
        print(f"Successfully created default admin user:")
        print(f"  - Username: {admin_user}")
        print(f"  - Password: {admin_pass}")
    else:
        print("Failed to create admin user.")

    print("\nInitialization complete! You can now run 'streamlit run streamlit_app.py'")

if __name__ == "__main__":
    init_db()
