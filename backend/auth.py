from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import datetime, timedelta
import re
import secrets
import os  # Add this import

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"message": "Email and password are required"}), 400
        
        if not is_valid_email(data['email']):
            return jsonify({"message": "Invalid email format"}), 400
        
        if len(data['password']) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        
        if data['password'] != data.get('confirmPassword', ''):
            return jsonify({"message": "Passwords do not match"}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "User already exists"}), 400
        
        # Create new user
        new_user = User(email=data['email'])
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=new_user.email,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            "message": "User created successfully",
            "token": access_token,
            "user": new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print("Registration error:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"message": "Email and password are required"}), 400
        
        # Find user in database
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=user.email,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@auth_bp.route('/protected')
@jwt_required()
def protected():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "message": f"Hello {user.email}, this is a protected route!",
        "user": user.to_dict()
    }), 200

# ===== PASSWORD RESET ROUTES =====

# In-memory storage for reset tokens (replace with database in production)
password_reset_tokens = {}

def generate_reset_token():
    return secrets.token_urlsafe(32)

def send_reset_email(email, reset_token):
    """
    Mock email function - replace with real email service in production
    For testing, we'll just log the reset link to console
    """
    reset_link = f"http://localhost:5000/reset-password.html?token={reset_token}"
    
    print("=" * 50)
    print("📧 PASSWORD RESET EMAIL (Mock)")
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print("=" * 50)
    
    return True
    
    # For production, uncomment and use this:
    """
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    reset_link = f"https://yourapp.com/reset-password.html?token={reset_token}"
    
    message = Mail(
        from_email='noreply@mindease.com',
        to_emails=email,
        subject='MindEase - Password Reset',
        html_content=f'Click <a href="{reset_link}">here</a> to reset your password.'
    )
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
    """

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"message": "Email is required"}), 400
        
        if not is_valid_email(email):
            return jsonify({"message": "Invalid email format"}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # For security, don't reveal if email exists
            return jsonify({
                "message": "If that email exists in our system, we've sent a password reset link."
            }), 200
        
        # Generate reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Store token (in production, use database)
        password_reset_tokens[reset_token] = {
            'email': email,
            'expires_at': expires_at,
            'used': False
        }
        
        # Send reset email
        send_reset_email(email, reset_token)
        
        return jsonify({
            "message": "If that email exists in our system, we've sent a password reset link.",
            "reset_token": reset_token  # Remove this in production - only for testing
        }), 200
        
    except Exception as e:
        print("Forgot password error:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not token or not new_password:
            return jsonify({"message": "Token and new password are required"}), 400
        
        if new_password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400
        
        if len(new_password) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        
        # Validate token
        token_data = password_reset_tokens.get(token)
        if not token_data:
            return jsonify({"message": "Invalid or expired reset token"}), 400
        
        if token_data['used']:
            return jsonify({"message": "This reset token has already been used"}), 400
        
        if datetime.utcnow() > token_data['expires_at']:
            return jsonify({"message": "Reset token has expired"}), 400
        
        # Find user and update password
        user = User.query.filter_by(email=token_data['email']).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user.set_password(new_password)
        db.session.commit()
        
        # Mark token as used
        token_data['used'] = True
        
        return jsonify({
            "message": "Password reset successfully. You can now login with your new password."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print("Reset password error:", str(e))
        return jsonify({"message": "Server error", "error": str(e)}), 500

@auth_bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token():
    """Check if a reset token is valid"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"valid": False, "message": "Token is required"}), 400
        
        token_data = password_reset_tokens.get(token)
        if not token_data:
            return jsonify({"valid": False, "message": "Invalid token"}), 200
        
        if token_data['used']:
            return jsonify({"valid": False, "message": "Token already used"}), 200
        
        if datetime.utcnow() > token_data['expires_at']:
            return jsonify({"valid": False, "message": "Token expired"}), 200
        
        return jsonify({
            "valid": True,
            "email": token_data['email']
        }), 200
        
    except Exception as e:
        return jsonify({"valid": False, "message": "Server error"}), 500