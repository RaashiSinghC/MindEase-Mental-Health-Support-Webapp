from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from game_routes import game_bp
from analytics_routes import analytics_bp

load_dotenv()

# Create Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mindease-super-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'mindease-jwt-secret-key-2024')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ ADD THIS DATABASE CONFIGURATION SECTION
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Handle Render's PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print("🔗 Using PostgreSQL database from DATABASE_URL")
else:
    # Fallback for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_database.db'
    print("🔧 Using SQLite database for local development")

# Initialize extensions
from models import db
db.init_app(app)

CORS(app)

# ✅ IMPORTANT: Initialize JWTManager with the app
jwt = JWTManager(app)

# Import and register blueprints
def register_blueprints():
    try:
        from auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')
        print("✅ Auth routes registered")
    except ImportError as e:
        print(f"❌ Auth routes: {e}")

    try:
        from mood_routes import mood_bp
        app.register_blueprint(mood_bp, url_prefix='/api')
        print("✅ Mood routes registered")
    except ImportError as e:
        print(f"❌ Mood routes: {e}")

    try:
        from chat_routes import chat_bp
        app.register_blueprint(chat_bp, url_prefix='/api')
        print("✅ Chat routes registered")
    except ImportError as e:
        print(f"❌ Chat routes: {e}")

    try:
        from assessment_routes import assessment_bp
        app.register_blueprint(assessment_bp, url_prefix='/api')
        print("✅ Assessment routes registered")
    except ImportError as e:
        print(f"❌ Assessment routes: {e}")

    try:
        from journal_routes import journal_bp
        app.register_blueprint(journal_bp, url_prefix='/api')
        print("✅ Journal routes registered")
    except ImportError as e:
        print(f"❌ Journal routes: {e}")

    try:
        from game_routes import game_bp
        app.register_blueprint(game_bp, url_prefix='/api')
        print("✅ Game routes registered")
    except ImportError as e:
        print(f"❌ Game routes: {e}")

    try:
        from analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/api')
        print("✅ Analytics routes registered")
    except ImportError as e:
        print(f"❌ Analytics routes: {e}")

# Register all blueprints
register_blueprints()

@app.route('/')
def home():
    return jsonify({
        "message": "MindEase API is running!", 
        "database": "PostgreSQL 17",
        "status": "healthy"
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "API is working", 
        "database": "Connected",
        "tables": 5
    })
# ✅ ADD THIS AT THE VERY END OF app.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"🚀 Starting MindEase server on port {port}")
    print(f"🔗 Database: {os.environ.get('DATABASE_URL', 'Not set')}")
    app.run(host='0.0.0.0', port=port, debug=debug)



