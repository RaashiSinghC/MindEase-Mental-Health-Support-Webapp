from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UserProgress, MoodEntry, JournalEntry, ChatSession, Assessment
from datetime import datetime, timedelta
import json

game_bp = Blueprint('game', __name__)

# Game configuration
GAME_LEVELS = {
    'beginner': {'points_required': 0, 'title': 'Mindfulness Beginner'},
    'explorer': {'points_required': 50, 'title': 'Emotion Explorer'},
    'practitioner': {'points_required': 150, 'title': 'Mental Wellness Practitioner'},
    'master': {'points_required': 300, 'title': 'Mindfulness Master'},
    'guru': {'points_required': 500, 'title': 'Mental Wellness Guru'}
}

ACHIEVEMENTS = {
    'first_mood': {'name': 'First Step', 'points': 20, 'description': 'Track your first mood'},
    'week_streak': {'name': 'Weekly Warrior', 'points': 50, 'description': '7-day activity streak'},
    'journal_enthusiast': {'name': 'Journal Enthusiast', 'points': 30, 'description': 'Write 5 journal entries'},
    'mood_analyst': {'name': 'Mood Analyst', 'points': 40, 'description': 'Track mood for 7 days'},
    'assessment_pro': {'name': 'Assessment Pro', 'points': 25, 'description': 'Complete both assessments'},
    'chat_regular': {'name': 'Chat Regular', 'points': 20, 'description': 'Have 5 chat conversations'},
    'self_care_champ': {'name': 'Self-Care Champion', 'points': 60, 'description': 'Complete 10 exercises'}
}

@game_bp.route('/game/progress', methods=['GET'])
@jwt_required()
def get_game_progress():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get or create user progress
        progress = UserProgress.query.filter_by(user_id=user.id).first()
        if not progress:
            progress = UserProgress(user_id=user.id)
            db.session.add(progress)
            db.session.commit()
        
        # Update progress based on recent activity
        update_user_progress(user.id)
        
        # Get fresh data after update
        progress = UserProgress.query.filter_by(user_id=user.id).first()
        
        # Get activity counts for display
        activity_counts = get_activity_counts(user.id)
        
        return jsonify({
            "success": True,
            "progress": {
                "level": progress.level,
                "points": progress.points,
                "streak_days": progress.streak_days,
                "achievements": progress.get_achievements(),
                "next_level": get_next_level(progress.points),
                "progress_percentage": calculate_level_progress(progress.points)
            },
            "activity_counts": activity_counts
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def get_activity_counts(user_id):
    """Get counts of all user activities"""
    return {
        "mood_entries": MoodEntry.query.filter_by(user_id=user_id).count(),
        "journal_entries": JournalEntry.query.filter_by(user_id=user_id).count(),
        "chat_sessions": ChatSession.query.filter_by(user_id=user_id).count(),
        "assessments": Assessment.query.filter_by(user_id=user_id).count()
    }

def update_user_progress(user_id):
    progress = UserProgress.query.filter_by(user_id=user_id).first()
    if not progress:
        return
    
    # Calculate new achievements
    new_achievements = check_new_achievements(user_id, progress.get_achievements())
    
    # Update points based on all activities
    new_points = calculate_points(user_id)
    
    # Update streak
    current_streak = calculate_streak(user_id)
    
    progress.points = new_points
    progress.streak_days = current_streak
    progress.level = calculate_level(new_points)
    
    # Add new achievements
    if new_achievements:
        current_achievements = progress.get_achievements()
        current_achievements.extend(new_achievements)
        # Remove duplicates
        progress.set_achievements(list(set(current_achievements)))
    
    progress.last_activity = datetime.utcnow()
    db.session.commit()

def calculate_points(user_id):
    """Calculate total points from all activities"""
    points = 0
    
    # Points from mood entries (2 points each)
    mood_count = MoodEntry.query.filter_by(user_id=user_id).count()
    points += mood_count * 2
    
    # Points from journal entries (3 points each)
    journal_count = JournalEntry.query.filter_by(user_id=user_id).count()
    points += journal_count * 3
    
    # Points from chat sessions (1 point each)
    chat_count = ChatSession.query.filter_by(user_id=user_id).count()
    points += chat_count * 1
    
    # Points from assessments (10 points each)
    assessment_count = Assessment.query.filter_by(user_id=user_id).count()
    points += assessment_count * 10
    
    # Additional points from achievements
    progress = UserProgress.query.filter_by(user_id=user_id).first()
    if progress:
        for achievement in progress.get_achievements():
            points += ACHIEVEMENTS.get(achievement, {}).get('points', 0)
    
    return points

def check_new_achievements(user_id, current_achievements):
    """Check if user has earned new achievements"""
    new_achievements = []
    
    # Check mood achievements
    mood_count = MoodEntry.query.filter_by(user_id=user_id).count()
    if mood_count >= 1 and 'first_mood' not in current_achievements:
        new_achievements.append('first_mood')
    if mood_count >= 7 and 'mood_analyst' not in current_achievements:
        new_achievements.append('mood_analyst')
    
    # Check journal achievements
    journal_count = JournalEntry.query.filter_by(user_id=user_id).count()
    if journal_count >= 5 and 'journal_enthusiast' not in current_achievements:
        new_achievements.append('journal_enthusiast')
    
    # Check chat achievements
    chat_count = ChatSession.query.filter_by(user_id=user_id).count()
    if chat_count >= 5 and 'chat_regular' not in current_achievements:
        new_achievements.append('chat_regular')
    
    # Check assessment achievements
    assessment_count = Assessment.query.filter_by(user_id=user_id).count()
    if assessment_count >= 2 and 'assessment_pro' not in current_achievements:
        new_achievements.append('assessment_pro')
    
    return new_achievements

def calculate_streak(user_id):
    """Calculate current activity streak"""
    # Get the last 7 days
    today = datetime.utcnow().date()
    dates_to_check = [today - timedelta(days=i) for i in range(7)]
    
    streak = 0
    for date in dates_to_check:
        # Check if user had any activity on this date
        had_activity = False
        
        # Check mood entries
        mood_activity = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            db.func.date(MoodEntry.created_at) == date
        ).first()
        
        # Check journal entries
        journal_activity = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            db.func.date(JournalEntry.created_at) == date
        ).first()
        
        # Check chat sessions
        chat_activity = ChatSession.query.filter(
            ChatSession.user_id == user_id,
            db.func.date(ChatSession.created_at) == date
        ).first()
        
        if mood_activity or journal_activity or chat_activity:
            streak += 1
        else:
            # Streak broken
            break
    
    return streak

def calculate_level(points):
    """Determine user level based on points"""
    current_level = 'beginner'
    for level, config in GAME_LEVELS.items():
        if points >= config['points_required']:
            current_level = level
    return current_level

def get_next_level(points):
    """Get information about the next level"""
    levels = list(GAME_LEVELS.keys())
    current_level = calculate_level(points)
    
    try:
        current_index = levels.index(current_level)
        if current_index + 1 < len(levels):
            next_level = levels[current_index + 1]
            return {
                'name': next_level,
                'title': GAME_LEVELS[next_level]['title'],
                'points_required': GAME_LEVELS[next_level]['points_required'],
                'points_needed': GAME_LEVELS[next_level]['points_required'] - points
            }
    except ValueError:
        pass
    
    return None

def calculate_level_progress(points):
    """Calculate progress percentage to next level"""
    current_level = calculate_level(points)
    current_level_points = GAME_LEVELS[current_level]['points_required']
    
    if current_level == 'guru':
        return 100
    
    next_level = get_next_level(points)
    if next_level:
        level_range = next_level['points_required'] - current_level_points
        progress_in_level = points - current_level_points
        return min(100, int((progress_in_level / level_range) * 100))
    
    return 0

# Add this route to manually trigger progress update
@game_bp.route('/game/update-progress', methods=['POST'])
@jwt_required()
def manual_update_progress():
    """Manually update user progress (useful for testing)"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        update_user_progress(user.id)
        
        return jsonify({
            "success": True,
            "message": "Progress updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500