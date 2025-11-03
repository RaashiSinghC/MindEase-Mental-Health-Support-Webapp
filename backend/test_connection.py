import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        print(f"🔗 Connecting to: {database_url}")
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ PostgreSQL connection successful!")
        print(f"📊 Database version: {db_version[0]}")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"📋 Tables in database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Is PostgreSQL running?")
        print("2. Check database URL in .env file")
        print("3. Verify user/password in pgAdmin")
        print("4. Check if database exists")

if __name__ == '__main__':
    test_connection()