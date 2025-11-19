import os
import sys
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection

def init_auth_db():
    print("Initializing Authentication System...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Execute SQL file
        print("Creating tables...")
        with open('plan/07_create_auth_tables.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            # Split by semicolon and execute each statement
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
        
        # 2. Create default users
        print("Creating default users...")
        
        users = [
            ('admin', 'admin123', 'admin'),
            ('analyst', 'analyst123', 'analyst')
        ]
        
        for username, password, role in users:
            # Check if user exists
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
        print("Authentication system initialized successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_auth_db()

