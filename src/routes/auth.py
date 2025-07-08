from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.bunker import BunkerUser
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
    
    return jsonify({'authenticated': False})

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session."""
    data = request.get_json()
    
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create session
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear user session."""
    session.clear()
    return jsonify({'message': 'Logout successful'})

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (admin only)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'resident')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    
    try:
        db.session.flush()  # Get the user ID
        
        # Create bunker user profile if bunker info provided
        if 'bunker_id' in data:
            bunker_user = BunkerUser(
                user_id=user.id,
                bunker_id=data['bunker_id'],
                access_level=data.get('access_level', 'basic'),
                room_assignment=data.get('room_assignment'),
                emergency_contact=data.get('emergency_contact')
            )
            db.session.add(bunker_user)
        
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500
