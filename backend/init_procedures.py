"""
初始化数据库存储过程
"""
import os
import sys
import pymysql
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection

def init_procedures():
    print("Creating Database Stored Procedures...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Read SQL file
        with open('plan/14_create_procedures.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Parse each procedure manually
        # Each procedure is: DROP ... DELIMITER // CREATE ... END // DELIMITER ;
        procedures_created = []
        
        # Extract procedure definitions
        # Pattern: DROP PROCEDURE IF EXISTS name; ... CREATE PROCEDURE name(...) BEGIN ... END //
        proc_pattern = r'DROP PROCEDURE IF EXISTS\s+(\w+);[\s\S]*?CREATE PROCEDURE\s+(\w+)\s*\([^)]*\)\s*(BEGIN[\s\S]*?)END\s*//'
        matches = re.finditer(proc_pattern, sql_content)
        
        for match in matches:
            drop_name = match.group(1)
            create_name = match.group(2)
            proc_body = match.group(3).strip()
            
            # Clean up procedure body - remove DELIMITER lines and comments
            lines = proc_body.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('--') and 'DELIMITER' not in line.upper():
                    # Remove inline comments
                    if '--' in line:
                        line = line.split('--')[0].strip()
                    if line:
                        cleaned_lines.append(line)
            
            proc_body_clean = ' '.join(cleaned_lines)
            
            # Build CREATE PROCEDURE statement
            # Extract procedure signature (parameter part)
            sig_match = re.search(r'CREATE PROCEDURE\s+(\w+)\s*\((.*?)\)', match.group(0))
            if sig_match:
                proc_name = sig_match.group(1)
                proc_params = sig_match.group(2)
                
                create_stmt = f"CREATE PROCEDURE {proc_name}({proc_params}) {proc_body_clean} END"
                
                try:
                    # Drop first
                    cursor.execute(f"DROP PROCEDURE IF EXISTS {proc_name}")
                    print(f"✓ Dropped procedure if exists: {proc_name}")
                    
                    # Create procedure
                    cursor.execute(create_stmt)
                    procedures_created.append(proc_name)
                    print(f"✓ Created procedure: {proc_name}")
                except Exception as e:
                    print(f"✗ Error creating procedure {proc_name}: {e}")
                    print(f"  Preview: {create_stmt[:200]}...")
        
        # Alternative: if regex didn't work, parse manually
        if not procedures_created:
            # Split by DELIMITER blocks
            parts = re.split(r'DELIMITER\s+//|DELIMITER\s+;', sql_content)
            current_proc = None
            current_body = []
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                # Check if this is a DROP PROCEDURE line
                drop_match = re.search(r'DROP PROCEDURE IF EXISTS\s+(\w+)', part)
                if drop_match:
                    current_proc = drop_match.group(1)
                    try:
                        cursor.execute(f"DROP PROCEDURE IF EXISTS {current_proc}")
                        print(f"✓ Dropped procedure if exists: {current_proc}")
                    except:
                        pass
                    continue
                
                # Check if this is a CREATE PROCEDURE block
                create_match = re.search(r'CREATE PROCEDURE\s+(\w+)\s*\((.*?)\)\s*(BEGIN.*)', part, re.DOTALL)
                if create_match:
                    proc_name = create_match.group(1)
                    proc_params = create_match.group(2)
                    proc_body = create_match.group(3)
                    
                    # Clean up body - remove END // at the end
                    proc_body = re.sub(r'\s+END\s*//\s*$', '', proc_body, flags=re.DOTALL)
                    
                    # Build statement
                    create_stmt = f"CREATE PROCEDURE {proc_name}({proc_params}) {proc_body} END"
                    
                    try:
                        cursor.execute(create_stmt)
                        procedures_created.append(proc_name)
                        print(f"✓ Created procedure: {proc_name}")
                    except Exception as e:
                        print(f"✗ Error creating procedure {proc_name}: {e}")
                        print(f"  Error: {str(e)[:200]}")
        
        conn.commit()
        print(f"\nStored procedures created successfully! Total: {len(procedures_created)}")
        
        # Verify procedures
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
        procedures = cursor.fetchall()
        print("\nExisting procedures:")
        for proc in procedures:
            print(f"  - {proc['Name']}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_procedures()
