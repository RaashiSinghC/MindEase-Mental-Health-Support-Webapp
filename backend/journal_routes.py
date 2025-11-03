from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, JournalEntry, User
import json
from collections import Counter
import numpy as np

journal_bp = Blueprint('journal', __name__)

# Data science analysis functions (keep your existing ones)
def analyze_journal_sentiment(text):
    # ... your existing function code ...
    positive_words = ['happy', 'good', 'great', 'excited', 'joy', 'love', 'peace', 'calm', 'grateful', 'thankful', 'blessed', 'amazing', 'wonderful', 'better', 'improved']
    negative_words = ['sad', 'bad', 'terrible', 'angry', 'anxious', 'stress', 'worried', 'fear', 'hurt', 'pain', 'tired', 'exhausted', 'hopeless', 'lonely', 'overwhelmed']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    total_words = len(text.split())
    
    if total_words == 0:
        return "neutral"
    
    sentiment_score = (positive_count - negative_count) / total_words
    
    if sentiment_score > 0.1:
        return "positive"
    elif sentiment_score < -0.1:
        return "negative"
    else:
        return "neutral"

def extract_emotions(text):
    # ... your existing function code ...
    emotion_keywords = {
        'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'fear', 'panic'],
        'depression': ['sad', 'hopeless', 'empty', 'numb', 'worthless'],
        'anger': ['angry', 'mad', 'frustrated', 'irritated', 'annoyed'],
        'joy': ['happy', 'joy', 'excited', 'thrilled', 'delighted'],
        'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed'],
        'stress': ['stressed', 'overwhelmed', 'pressure', 'burdened'],
        'peace': ['calm', 'peaceful', 'relaxed', 'serene', 'content']
    }
    
    text_lower = text.lower()
    detected_emotions = []
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_emotions.append(emotion)
    
    return detected_emotions

@journal_bp.route('/journal/entry', methods=['POST'])
@jwt_required()
def add_journal_entry():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.get_json()
        content = data['content']
        title = data.get('title', 'Journal Entry')
        
        if not content.strip():
            return jsonify({"success": False, "error": "Journal content cannot be empty"}), 400
        
        # Data science analysis
        sentiment = analyze_journal_sentiment(content)
        emotions = extract_emotions(content)
        
        # Create journal entry in database
        journal_entry = JournalEntry(
            user_id=user.id,
            title=title,
            content=content,
            sentiment=sentiment,
            word_count=len(content.split())
        )
        journal_entry.set_emotions(emotions)
        
        db.session.add(journal_entry)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Journal entry saved successfully",
            "analysis": {
                "sentiment": sentiment,
                "emotions": emotions,
                "word_count": journal_entry.word_count
            },
            "entry": journal_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@journal_bp.route('/journal/entries', methods=['GET'])
@jwt_required()
def get_journal_entries():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        journal_entries = JournalEntry.query.filter_by(user_id=user.id)\
            .order_by(JournalEntry.created_at.desc())\
            .all()
        
        return jsonify({
            "success": True,
            "entries": [entry.to_dict() for entry in journal_entries],
            "total_entries": len(journal_entries)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@journal_bp.route('/journal/analytics', methods=['GET'])
@jwt_required()
def get_journal_analytics():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        journal_entries = JournalEntry.query.filter_by(user_id=user.id).all()
        
        if not journal_entries:
            return jsonify({"message": "No journal entries yet"}), 200
        
        # Basic analytics
        sentiment_counts = Counter(entry.sentiment for entry in journal_entries)
        all_emotions = [emotion for entry in journal_entries for emotion in entry.get_emotions()]
        common_emotions = Counter(all_emotions).most_common(5)
        
        # Advanced pattern analysis
        total_words = sum(entry.word_count for entry in journal_entries)
        avg_length = np.mean([entry.word_count for entry in journal_entries]) if journal_entries else 0
        
        analytics = {
            "total_entries": len(journal_entries),
            "sentiment_distribution": dict(sentiment_counts),
            "common_emotions": dict(common_emotions),
            "writing_insights": {
                "total_words_written": total_words,
                "average_entry_length": round(avg_length, 1),
                "writing_consistency": f"{len(journal_entries)} entries over time"
            }
        }
        
        return jsonify({
            "success": True,
            "analytics": analytics
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@journal_bp.route('/journal/entry/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_journal_entry(entry_id):
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        journal_entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
        
        if not journal_entry:
            return jsonify({"success": False, "error": "Journal entry not found"}), 404
        
        db.session.delete(journal_entry)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Journal entry deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500