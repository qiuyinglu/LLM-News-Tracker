"""
Database patch script to add llm_blocked columns to existing tables.
Run this script to add the new llm_blocked and llm_blocked_reason columns.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def patch_database():
    """Apply database patches for llm_blocked columns."""
    
    try:
        # Connect to the target database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'news_threads'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        cursor = conn.cursor()
        
        print("Applying database patches...")
        
        # Patch to add llm_blocked columns to existing tables
        patches = [
            "ALTER TABLE News ADD COLUMN IF NOT EXISTS llm_blocked BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE News ADD COLUMN IF NOT EXISTS llm_blocked_reason TEXT DEFAULT '';",
            "ALTER TABLE Threads ADD COLUMN IF NOT EXISTS llm_blocked BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE Threads ADD COLUMN IF NOT EXISTS llm_blocked_reason TEXT DEFAULT '';"
        ]
        
        for patch in patches:
            try:
                cursor.execute(patch)
                print(f"✓ Applied: {patch}")
            except Exception as e:
                print(f"⚠ Warning applying patch '{patch}': {e}")
        
        conn.commit()
        print("\nDatabase patches applied successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error applying database patches: {e}")

if __name__ == "__main__":
    patch_database()
