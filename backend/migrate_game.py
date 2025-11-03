# migrate_game.py - Create this as a NEW file in your main folder
from app import app, db
from models import User, MoodEntry, JournalEntry, ChatSession, Assessment, UserProgress

def migrate_game_tables():
    print("🔄 Creating game tables...")
    
    with app.app_context():
        try:
            # Create the user_progress table
            db.create_all()
            print("✅ Game tables created successfully!")
            
            # Count tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Tables in database: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
            
            # Initialize progress for existing users
            users = User.query.all()
            print(f"\n👥 Initializing progress for {len(users)} users...")
            
            for user in users:
                progress = UserProgress.query.filter_by(user_id=user.id).first()
                if not progress:
                    progress = UserProgress(user_id=user.id)
                    db.session.add(progress)
                    print(f"   ✅ Created progress for user: {user.email}")
            
            db.session.commit()
            print("🎉 Game system initialized successfully!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")

if __name__ == '__main__':
    migrate_game_tables()