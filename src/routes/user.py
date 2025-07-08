from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.bunker import BunkerUser
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile information."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    
    profile_data = user.to_dict()
    if bunker_user:
        profile_data.update({
            'bunker_id': bunker_user.bunker_id,
            'access_level': bunker_user.access_level,
            'room_assignment': bunker_user.room_assignment,
            'emergency_contact': bunker_user.emergency_contact
        })
    
    return jsonify(profile_data)

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile information."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update basic user info
    if 'email' in data:
        user.email = data['email']
    
    # Update bunker-specific info
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    if bunker_user:
        if 'emergency_contact' in data:
            bunker_user.emergency_contact = data['emergency_contact']
        if 'medical_info' in data:
            bunker_user.medical_info = data['medical_info']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not all(key in data for key in ['current_password', 'new_password']):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500
