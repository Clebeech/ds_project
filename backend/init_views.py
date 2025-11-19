import os
import sys
import pymysql

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection

def init_views():
    print("Creating Database Views...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Read SQL file
        with open('plan/13_create_views.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL statements properly (handle multi-line CREATE VIEW)
        # Remove comments first
        lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                # Remove inline comments
                if '--' in line:
                    line = line.split('--')[0].strip()
                if line:
                    lines.append(line)
        
        # Join all lines and split by semicolon
        full_sql = ' '.join(lines)
        statements = [s.strip() for s in full_sql.split(';') if s.strip()]
        
        # Execute each statement separately
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                continue
            
            try:
                # Handle DROP VIEW IF EXISTS separately if needed
                if statement.upper().startswith('DROP VIEW'):
                    cursor.execute(statement)
                    print(f"✓ Dropped view if exists: {statement.split()[2] if len(statement.split()) > 2 else 'unknown'}")
                elif statement.upper().startswith('CREATE VIEW'):
                    cursor.execute(statement)
                    view_name = statement.split()[2] if len(statement.split()) > 2 else 'unknown'
                    print(f"✓ Created view: {view_name}")
                else:
                    cursor.execute(statement)
                    print(f"✓ Executed statement {i}")
            except Exception as e:
                print(f"✗ Error executing statement {i}: {e}")
                print(f"  Statement: {statement[:100]}...")  # Print first 100 chars for debugging
        
        conn.commit()
        print(f"\nViews created successfully! Total: {len(statements)}")
        
        # Verify views
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        print("\nExisting views:")
        for view in views:
            print(f"  - {view[list(view.keys())[0]]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_views()

