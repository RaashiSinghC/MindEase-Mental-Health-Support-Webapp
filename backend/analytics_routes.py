from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, MoodEntry, JournalEntry, Assessment
from datetime import datetime, timedelta
import numpy as np
from collections import Counter
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/comprehensive-report', methods=['GET'])
@jwt_required()
def get_comprehensive_report():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get time ranges
        end_date = datetime.utcnow()
        start_date_30d = end_date - timedelta(days=30)
        start_date_7d = end_date - timedelta(days=7)
        
        report_data = {
            "user_info": {
                "email": user.email,
                "member_since": user.created_at.strftime("%B %d, %Y"),
                "days_active": (end_date - user.created_at).days
            },
            "time_period": {
                "start_date": start_date_30d.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            },
            "engagement_metrics": get_engagement_metrics(user.id, start_date_30d, end_date),
            "mood_analysis": get_mood_analysis(user.id, start_date_30d, end_date),
            "journal_insights": get_journal_insights(user.id, start_date_30d, end_date),
            "assessment_history": get_assessment_history(user.id),
            "weekly_comparison": get_weekly_comparison(user.id, start_date_7d, end_date),
            "recommendations": generate_recommendations(user.id)
        }
        
        return jsonify({
            "success": True,
            "report": report_data
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def get_engagement_metrics(user_id, start_date, end_date):
    # Activity counts
    mood_count = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).count()
    
    journal_count = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= start_date,
        JournalEntry.created_at <= end_date
    ).count()
    
    # Consistency score (percentage of days with at least one activity)
    total_days = (end_date - start_date).days
    active_days = db.session.query(db.func.count(db.func.distinct(db.func.date(MoodEntry.created_at)))).filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).scalar() or 0
    
    consistency_score = (active_days / total_days * 100) if total_days > 0 else 0
    
    return {
        "mood_entries": mood_count,
        "journal_entries": journal_count,
        "consistency_score": round(consistency_score, 1),
        "active_days": active_days,
        "total_days": total_days
    }

def get_mood_analysis(user_id, start_date, end_date):
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).all()
    
    if not mood_entries:
        return {"message": "No mood data available"}
    
    mood_scores = [entry.mood_score for entry in mood_entries]
    
    # Weekly trends
    weekly_data = {}
    for entry in mood_entries:
        week = entry.created_at.strftime("%Y-W%U")
        if week not in weekly_data:
            weekly_data[week] = []
        weekly_data[week].append(entry.mood_score)
    
    weekly_avg = {week: round(sum(scores)/len(scores), 2) for week, scores in weekly_data.items()}
    
    # Mood distribution
    mood_distribution = Counter(mood_scores)
    
    return {
        "average_mood": round(np.mean(mood_scores), 2),
        "mood_trend": "improving" if len(mood_scores) > 7 and mood_scores[-7] < mood_scores[-1] else "stable",
        "mood_stability": round(np.std(mood_scores), 2),
        "weekly_trends": weekly_avg,
        "mood_distribution": dict(mood_distribution),
        "best_mood_day": max(set([entry.created_at.strftime("%A") for entry in mood_entries]), 
                           key=[entry.created_at.strftime("%A") for entry in mood_entries].count) if mood_entries else "Not enough data"
    }

def get_journal_insights(user_id, start_date, end_date):
    journal_entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= start_date,
        JournalEntry.created_at <= end_date
    ).all()
    
    if not journal_entries:
        return {"message": "No journal data available"}
    
    sentiments = [entry.sentiment for entry in journal_entries if entry.sentiment]
    all_emotions = [emotion for entry in journal_entries for emotion in entry.get_emotions()]
    
    return {
        "total_entries": len(journal_entries),
        "total_words": sum(entry.word_count for entry in journal_entries),
        "avg_entry_length": round(np.mean([entry.word_count for entry in journal_entries]), 1),
        "sentiment_breakdown": dict(Counter(sentiments)),
        "common_emotions": dict(Counter(all_emotions).most_common(5)),
        "writing_frequency": f"{len(journal_entries)} entries in {(end_date - start_date).days} days"
    }

def get_assessment_history(user_id):
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.created_at.desc()).limit(5).all()
    
    assessment_history = []
    for assessment in assessments:
        assessment_history.append({
            "type": assessment.assessment_type.upper(),
            "score": assessment.total_score,
            "severity": assessment.severity,
            "date": assessment.created_at.strftime("%Y-%m-%d"),
            "recommendation": assessment.recommendation
        })
    
    return assessment_history

def get_weekly_comparison(user_id, start_date, end_date):
    # Compare current week with previous week
    previous_week_start = start_date - timedelta(days=7)
    
    current_week_moods = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).all()
    
    previous_week_moods = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= previous_week_start,
        MoodEntry.created_at < start_date
    ).all()
    
    current_avg = np.mean([m.mood_score for m in current_week_moods]) if current_week_moods else 0
    previous_avg = np.mean([m.mood_score for m in previous_week_moods]) if previous_week_moods else 0
    
    change = current_avg - previous_avg if previous_avg > 0 else 0
    
    return {
        "current_week_avg": round(current_avg, 2),
        "previous_week_avg": round(previous_avg, 2),
        "change": round(change, 2),
        "trend": "improving" if change > 0 else "declining" if change < 0 else "stable"
    }

def generate_recommendations(user_id):
    recommendations = []
    
    # Check engagement and suggest activities
    mood_count = MoodEntry.query.filter_by(user_id=user_id).count()
    journal_count = JournalEntry.query.filter_by(user_id=user_id).count()
    
    if mood_count < 7:
        recommendations.append("Try tracking your mood daily for a week to identify patterns")
    
    if journal_count < 3:
        recommendations.append("Regular journaling can help process emotions. Aim for 2-3 entries per week")
    
    # Add more personalized recommendations based on user data
    recommendations.extend([
        "Practice the 4-7-8 breathing technique when feeling anxious",
        "Schedule worry time to contain anxious thoughts",
        "Try behavioral activation by scheduling pleasant activities"
    ])
    
    return recommendations