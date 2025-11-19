import os
import sys
import pymysql

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection

def init_triggers():
    print("Initializing Database Triggers...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Read SQL file
        with open('plan/08_create_triggers.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by 'DELIMITER' to handle trigger syntax properly
        # This is a simple parser for the specific file format
        statements = []
        current_statement = []
        
        # Manual parsing because pymysql doesn't support DELIMITER syntax directly
        # We just need to extract the CREATE TRIGGER part
        
        # Strategy: Execute the DROP first
        cursor.execute("DROP TRIGGER IF EXISTS trg_update_interview_count")
        print("Dropped existing trigger.")
        
        # Execute the CREATE TRIGGER
        create_sql = """
        CREATE TRIGGER trg_update_interview_count
        AFTER INSERT ON interviews
        FOR EACH ROW
        BEGIN
            UPDATE surveyors 
            SET CompletedInterviews = COALESCE(CompletedInterviews, 0) + 1
            WHERE SurveyorID = NEW.SurveyorID;
        END;
        """
        cursor.execute(create_sql)
        print("Created trigger: trg_update_interview_count")
        
        conn.commit()
        print("Triggers initialized successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_triggers()

