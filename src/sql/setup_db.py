"""
Database setup script for the news thread analysis system.
Run this script to create the required database schema.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Setup the database schema using the SQL script."""
    
    # Debug: Print loaded environment variables
    print("=== Environment Variables Loaded ===")
    print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'news_threads')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'postgres')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', '5432')}")
    print(f"DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
    print("=====================================\n")
    
    try:
        # Connect to PostgreSQL (connect to default database first)
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database='postgres',  # Connect to default database first
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create the database if it doesn't exist
        db_name = os.getenv('DB_NAME', 'news_threads')
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Created database: {db_name}")
        else:
            print(f"Database {db_name} already exists")
        
        cursor.close()
        conn.close()
        
        # Connect to the target database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=db_name,
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        cursor = conn.cursor()
        
        # Read and execute the schema SQL
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        print(f"Looking for schema file at: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        cursor.execute(schema_sql)
        conn.commit()
        
        print("Database schema setup completed successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    setup_database()
