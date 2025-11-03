from app import app, db
from models import User, MoodEntry, JournalEntry, ChatSession, Assessment

def initialize_database():
    print("🔧 Starting database setup...")
    
    with app.app_context():
        try:
            print("🔄 Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Test: Count tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            
            # Test: Check if test user exists, if not create one
            print("\n👤 Checking test user...")
            test_user = User.query.filter_by(email="test@mindease.com").first()
            
            if not test_user:
                print("Creating test user...")
                test_user = User(email="test@mindease.com")
                test_user.set_password("test123")
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created successfully!")
            else:
                print("✅ Test user already exists!")
            
            # Count records in each table
            users_count = User.query.count()
            mood_count = MoodEntry.query.count()
            journal_count = JournalEntry.query.count()
            chat_count = ChatSession.query.count()
            assessment_count = Assessment.query.count()
            
            print(f"\n📈 Database Statistics:")
            print(f"   👥 Users: {users_count}")
            print(f"   😊 Mood Entries: {mood_count}")
            print(f"   📖 Journal Entries: {journal_count}")
            print(f"   💬 Chat Sessions: {chat_count}")
            print(f"   📊 Assessments: {assessment_count}")
            
            print("\n🎉 Database setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            db.session.rollback()
            print("Please check the error above and fix it.")

if __name__ == '__main__':
    initialize_database()