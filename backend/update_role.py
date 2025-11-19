import os
import sys
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection

def update_surveyor_role():
    print("Updating Surveyor Role...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Modify Column Schema
        print("Updating users table schema...")
        try:
            cursor.execute("ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'analyst', 'surveyor', 'guest') NOT NULL DEFAULT 'guest'")
        except Exception as e:
            print(f"Schema update notice: {e}")

        # 2. Create default surveyor user
        print("Creating default surveyor user...")
        username = 'surveyor'
        password = 'surveyor123'
        role = 'surveyor'
        
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if not cursor.fetchone():
            pwd_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, pwd_hash, role)
            )
            print(f"Created user: {username} (Role: {role})")
        else:
            print(f"User {username} already exists.")

        conn.commit()
        print("Surveyor role update completed!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_surveyor_role()

