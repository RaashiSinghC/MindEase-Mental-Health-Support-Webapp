from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, ChatSession, User
import random

chat_bp = Blueprint('chat', __name__)

# Enhanced chatbot responses with multiple variations
def get_chatbot_response(user_message):
    user_message_lower = user_message.lower()
    
    # Response categories with multiple variations
    response_groups = {
        'greeting': [
            "Hello! I'm here to listen. How are you feeling today?",
            "Hi there! I'm your MindEase assistant. What would you like to talk about?",
            "Welcome! I'm here to support you. How has your day been?",
            "Hello! It's good to see you. What's on your mind today?"
        ],
        'sad': [
            "I'm sorry you're feeling sad. Would you like to talk about what's bothering you?",
            "It sounds like you're going through a tough time. I'm here to listen if you want to share more.",
            "Feeling sad is really difficult. Remember that these feelings are temporary. What's been happening?",
            "I hear the sadness in your message. Would it help to talk about what's causing these feelings?"
        ],
        'anxious': [
            "Anxiety can be overwhelming. Try this: inhale for 4 seconds, hold for 4, exhale for 6. Repeat 3 times.",
            "When anxiety shows up, it helps to ground yourself. Name 3 things you can see, 2 you can touch, 1 you can hear.",
            "Anxiety is tough, but remember - you've gotten through anxious moments before. What's triggering this now?",
            "Let's breathe together. Deep breaths can calm your nervous system. Want to try a quick breathing exercise?"
        ],
        'stressed': [
            "Stress can feel heavy. What's one small thing you could do right now to feel a bit better?",
            "When stress builds up, breaking things into smaller steps can help. What's the main stressor right now?",
            "Remember to take micro-breaks throughout the day. Even 30 seconds of stretching can help reset.",
            "Stress is your body's response to pressure. What self-care practices usually help you manage stress?"
        ],
        'happy': [
            "That's wonderful to hear! 😊 What's making you feel happy today?",
            "I'm so glad you're feeling good! Celebrating positive moments is important. Tell me more!",
            "Happiness is beautiful! Savor this feeling. What's contributing to your good mood?",
            "That's fantastic! Positive emotions help build resilience. What's bringing you joy right now?"
        ],
        'angry': [
            "Anger is a valid emotion. Try counting to 10 or taking a short walk to create space before reacting.",
            "When anger shows up, it's often protecting something important to you. What's beneath the anger?",
            "Anger needs movement. Could you do some physical activity to release that energy in a healthy way?",
            "It's okay to feel angry. The key is what we do with it. Want to explore healthy ways to express this?"
        ],
        'lonely': [
            "You're not alone - I'm here with you. Would you like to share what you're experiencing?",
            "Loneliness can be really painful. Sometimes reaching out to one person can make a difference.",
            "I'm listening. Even when physically alone, your feelings matter and are valid.",
            "Loneliness is a signal that we need connection. What kind of connection are you craving right now?"
        ],
        'tired': [
            "Rest is productive. Your body is asking for what it needs. Can you honor that request?",
            "Fatigue tells us something important. Are you getting enough quality sleep and nutrition?",
            "When tired, everything feels harder. What's one small way you could be gentle with yourself today?",
            "Rest isn't lazy - it's essential. Your worth isn't tied to your productivity."
        ],
        'help': [
            "I'm here to help! You can talk about feelings, track moods, get coping strategies, or just vent.",
            "I can listen, help you process emotions, suggest coping techniques, or just be here with you.",
            "How can I support you right now? We can talk, do a quick exercise, or explore resources.",
            "I'm your mental health companion. I can help with mood tracking, coping strategies, or just listening."
        ]
    }
    
    # Keyword mapping with priority
    keyword_map = {
        'hello': 'greeting', 'hi': 'greeting', 'hey': 'greeting',
        'sad': 'sad', 'depressed': 'sad', 'unhappy': 'sad', 'down': 'sad',
        'anxious': 'anxious', 'anxiety': 'anxious', 'nervous': 'anxious', 'worried': 'anxious',
        'stressed': 'stressed', 'stress': 'stressed', 'overwhelmed': 'stressed',
        'happy': 'happy', 'good': 'happy', 'great': 'happy', 'awesome': 'happy',
        'angry': 'angry', 'mad': 'angry', 'frustrated': 'angry',
        'lonely': 'lonely', 'alone': 'lonely', 'isolated': 'lonely',
        'tired': 'tired', 'exhausted': 'tired', 'fatigued': 'tired', 'sleepy': 'tired',
        'help': 'help', 'support': 'help', 'what can you do': 'help'
    }
    
    # Find the best matching category
    for keyword, category in keyword_map.items():
        if keyword in user_message_lower:
            responses = response_groups.get(category, response_groups['help'])
            return random.choice(responses)
    
    # Default empathetic responses for unmatched messages
    default_responses = [
        "Thank you for sharing that with me. How has this been affecting you?",
        "I appreciate you opening up about this. Would you like to explore it further?",
        "That sounds significant. Tell me more about what this is like for you.",
        "I'm listening carefully. What would be most helpful for you right now?",
        "Thank you for trusting me with this. How can I best support you with it?",
        "I hear you. What's the most challenging part of this for you?"
    ]
    
    return random.choice(default_responses)

@chat_bp.route('/chat/send', methods=['POST'])
@jwt_required()
def send_message():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.get_json()
        user_message = data['message']
        
        # Get chatbot response
        bot_response = get_chatbot_response(user_message)
        
        # Store in database
        chat_session = ChatSession(
            user_id=user.id,
            user_message=user_message,
            bot_response=bot_response
        )
        
        db.session.add(chat_session)
        db.session.commit()
        
        # Simulate typing delay
        import time
        time.sleep(random.uniform(1.0, 3.0))
        
        return jsonify({
            "success": True,
            "response": bot_response,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route('/chat/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        chat_sessions = ChatSession.query.filter_by(user_id=user.id)\
            .order_by(ChatSession.created_at.desc())\
            .limit(20)\
            .all()
        
        chat_history = [session.to_dict() for session in chat_sessions]
        
        return jsonify({
            "success": True,
            "chat_history": chat_history
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route('/chat/clear', methods=['POST'])
@jwt_required()
def clear_chat_history():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        # Delete user's chat history
        deleted_count = ChatSession.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Chat history cleared ({deleted_count} messages removed)",
            "removed_count": deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500