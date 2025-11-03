from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Assessment, User
import json

assessment_bp = Blueprint('assessment', __name__)

# Keep your existing questions
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless", 
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way"
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen"
]

@assessment_bp.route('/assessment/questions', methods=['GET'])
@jwt_required()
def get_assessment_questions():
    try:
        assessment_type = request.args.get('type', 'phq9')
        
        if assessment_type == 'phq9':
            questions = PHQ9_QUESTIONS
            title = "PHQ-9 Depression Assessment"
            instructions = "Over the last 2 weeks, how often have you been bothered by the following problems?"
        else:
            questions = GAD7_QUESTIONS
            title = "GAD-7 Anxiety Assessment" 
            instructions = "Over the last 2 weeks, how often have you been bothered by the following problems?"
        
        return jsonify({
            "success": True,
            "assessment_type": assessment_type,
            "title": title,
            "instructions": instructions,
            "questions": questions,
            "scale": {
                "0": "Not at all",
                "1": "Several days", 
                "2": "More than half the days",
                "3": "Nearly every day"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assessment_bp.route('/assessment/submit', methods=['POST'])
@jwt_required()
def submit_assessment():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.get_json()
        assessment_type = data['assessment_type']
        responses = data['responses']
        total_score = data['total_score']
        
        # Calculate severity level
        if assessment_type == 'phq9':
            if total_score <= 4:
                severity = "Minimal depression"
                recommendation = "Your mood appears to be within a normal range. Continue practicing good self-care."
            elif total_score <= 9:
                severity = "Mild depression"
                recommendation = "You may be experiencing mild depression. Consider talking to someone you trust."
            elif total_score <= 14:
                severity = "Moderate depression" 
                recommendation = "You appear to have moderate depression. Consider speaking with a healthcare provider."
            elif total_score <= 19:
                severity = "Moderately severe depression"
                recommendation = "You appear to have moderately severe depression. We recommend speaking with a healthcare provider soon."
            else:
                severity = "Severe depression"
                recommendation = "You appear to have severe depression. Please consider reaching out to a healthcare provider or mental health professional."
                
        else:  # GAD-7
            if total_score <= 4:
                severity = "Minimal anxiety"
                recommendation = "Your anxiety levels appear to be within a normal range."
            elif total_score <= 9:
                severity = "Mild anxiety"
                recommendation = "You may be experiencing mild anxiety. Practice relaxation techniques."
            elif total_score <= 14:
                severity = "Moderate anxiety"
                recommendation = "You appear to have moderate anxiety. Consider speaking with a healthcare provider."
            else:
                severity = "Severe anxiety"
                recommendation = "You appear to have severe anxiety. We recommend speaking with a healthcare provider."
        
        # Store assessment in database
        assessment = Assessment(
            user_id=user.id,
            assessment_type=assessment_type,
            total_score=total_score,
            severity=severity,
            recommendation=recommendation
        )
        assessment.set_responses(responses)
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Assessment submitted successfully",
            "result": {
                "total_score": total_score,
                "severity": severity,
                "recommendation": recommendation,
                "timestamp": assessment.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assessment_bp.route('/assessment/history', methods=['GET'])
@jwt_required()
def get_assessment_history():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        assessments = Assessment.query.filter_by(user_id=user.id)\
            .order_by(Assessment.created_at.desc())\
            .limit(10)\
            .all()
        
        return jsonify({
            "success": True,
            "assessments": [assessment.to_dict() for assessment in assessments]
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500