from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, MoodEntry, User

mood_bp = Blueprint('mood', __name__)

@mood_bp.route('/mood/entry', methods=['POST'])
@jwt_required()
def add_mood_entry():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.get_json()
        print("Mood data received:", data)
        
        # Create mood entry in database
        mood_entry = MoodEntry(
            user_id=user.id,
            mood_score=data['mood_score'],
            notes=data.get('notes', '')
        )
        
        db.session.add(mood_entry)
        db.session.commit()
        
        return jsonify({
            "message": "Mood saved successfully!",
            "entry": mood_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print("Error saving mood:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@mood_bp.route('/mood/history', methods=['GET'])
@jwt_required()
def get_mood_history():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        # Get mood entries
        mood_entries = MoodEntry.query.filter_by(user_id=user.id)\
            .order_by(MoodEntry.created_at.desc())\
            .limit(10)\
            .all()
        
        return jsonify({
            "mood_history": [entry.to_dict() for entry in mood_entries],
            "total_entries": len(mood_entries)
        }), 200
        
    except Exception as e:
        print("Error fetching mood history:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@mood_bp.route('/mood/insights', methods=['GET'])
@jwt_required()
def get_mood_insights():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        # Get all mood entries for user
        mood_entries = MoodEntry.query.filter_by(user_id=user.id).all()
        
        if len(mood_entries) == 0:
            return jsonify({
                "message": "Not enough data yet",
                "recommendation": "Start tracking your mood to get insights!"
            }), 200
        
        # Calculate average mood
        mood_scores = [entry.mood_score for entry in mood_entries]
        avg_mood = sum(mood_scores) / len(mood_scores)
        
        # Simple insights
        if avg_mood >= 4:
            insight = "You've been feeling positive lately! 😊"
            recommendation = "Keep up the good work! Consider practicing gratitude."
        elif avg_mood <= 2:
            insight = "We notice you've been feeling down. 😔"
            recommendation = "Try our breathing exercises or reach out to talk."
        else:
            insight = "Your mood has been fairly stable. 🙂"
            recommendation = "Regular exercise can help maintain balance."
        
        return jsonify({
            "average_mood": round(avg_mood, 2),
            "insight": insight,
            "recommendation": recommendation,
            "total_entries": len(mood_entries)
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
@mood_bp.route('/mood/debug', methods=['GET'])
@jwt_required()
def debug_mood():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        return jsonify({
            "message": "Mood API is working",
            "user": user.email if user else "No user found",
            "total_mood_entries": MoodEntry.query.filter_by(user_id=user.id).count() if user else 0
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500