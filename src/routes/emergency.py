from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.bunker import BunkerUser, EmergencyMessage
from datetime import datetime

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

@emergency_bp.route('/messages', methods=['GET'])
def get_messages():
    """Get emergency messages."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Get query parameters
    limit = request.args.get('limit', 50, type=int)
    message_type = request.args.get('type')
    status = request.args.get('status')
    
    query = EmergencyMessage.query.filter_by(bunker_id=bunker_id)
    
    if message_type:
        query = query.filter_by(message_type=message_type)
    
    if status:
        query = query.filter_by(status=status)
    
    messages = query.order_by(EmergencyMessage.timestamp.desc()).limit(limit).all()
    
    return jsonify([msg.to_dict() for msg in messages])

@emergency_bp.route('/messages', methods=['POST'])
def send_message():
    """Send an emergency message."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Check permissions for emergency messaging
    if user.role not in ['admin', 'security']:
        return jsonify({'error': 'Insufficient permissions for emergency messaging'}), 403
    
    data = request.get_json()
    
    if not data or not all(key in data for key in ['message_type', 'recipient', 'content']):
        return jsonify({'error': 'Message type, recipient, and content are required'}), 400
    
    # Validate message type
    valid_types = ['sms', 'email', 'radio', 'satellite']
    if data['message_type'] not in valid_types:
        return jsonify({'error': f'Invalid message type. Must be one of: {valid_types}'}), 400
    
    # Create emergency message
    message = EmergencyMessage(
        message_type=data['message_type'],
        recipient=data['recipient'],
        subject=data.get('subject', ''),
        content=data['content'],
        priority=data.get('priority', 'normal'),
        sent_by=user.id,
        bunker_id=bunker_id
    )
    
    db.session.add(message)
    
    try:
        db.session.flush()  # Get the message ID
        
        # Simulate sending the message
        success = simulate_message_sending(message)
        
        if success:
            message.status = 'sent'
            message.delivery_confirmation = datetime.utcnow()
        else:
            message.status = 'failed'
            message.error_message = 'Failed to establish connection'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Emergency message processed',
            'id': message.id,
            'status': message.status
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send message'}), 500

@emergency_bp.route('/messages/<int:message_id>/retry', methods=['POST'])
def retry_message(message_id):
    """Retry sending a failed message."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if user.role not in ['admin', 'security']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    message = EmergencyMessage.query.get_or_404(message_id)
    
    if message.status not in ['failed', 'pending']:
        return jsonify({'error': 'Message cannot be retried'}), 400
    
    # Simulate retrying the message
    success = simulate_message_sending(message)
    
    if success:
        message.status = 'sent'
        message.delivery_confirmation = datetime.utcnow()
        message.error_message = None
    else:
        message.status = 'failed'
        message.error_message = 'Retry failed - connection unavailable'
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Message retry completed',
            'status': message.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to retry message'}), 500

@emergency_bp.route('/templates', methods=['GET'])
def get_message_templates():
    """Get emergency message templates."""
    templates = {
        'evacuation': {
            'subject': 'URGENT: Bunker Evacuation Required',
            'content': 'Immediate evacuation of all bunker residents is required. Proceed to emergency exit points Alpha and Beta. Follow evacuation protocols. This is not a drill.'
        },
        'lockdown': {
            'subject': 'ALERT: Bunker Lockdown Initiated',
            'content': 'Bunker is now in lockdown mode. All residents must remain in their designated areas. External threat detected. Await further instructions.'
        },
        'system_failure': {
            'subject': 'CRITICAL: Life Support System Alert',
            'content': 'Critical system failure detected in life support systems. Engineering teams respond immediately. All non-essential personnel report to safe zones.'
        },
        'radiation_warning': {
            'subject': 'WARNING: Elevated Radiation Detected',
            'content': 'Elevated radiation levels detected. All external activities suspended. Seal all air intakes. Await radiation assessment update.'
        },
        'medical_emergency': {
            'subject': 'MEDICAL: Emergency Response Required',
            'content': 'Medical emergency in progress. Medical personnel respond immediately. Clear corridors for emergency transport.'
        },
        'all_clear': {
            'subject': 'STATUS: All Clear - Normal Operations',
            'content': 'Emergency situation resolved. Normal bunker operations may resume. Thank you for your cooperation during the emergency.'
        }
    }
    
    return jsonify(templates)

@emergency_bp.route('/broadcast', methods=['POST'])
def emergency_broadcast():
    """Send emergency broadcast to all residents."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Message content is required'}), 400
    
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Get all users in the same bunker
    bunker_users = db.session.query(User).join(BunkerUser).filter_by(bunker_id=bunker_id).all()
    
    messages_created = 0
    
    for recipient_user in bunker_users:
        message = EmergencyMessage(
            message_type='internal',
            recipient=recipient_user.username,
            subject=data.get('subject', 'Emergency Broadcast'),
            content=data['content'],
            priority='urgent',
            sent_by=user.id,
            bunker_id=bunker_id,
            status='delivered'  # Internal messages are immediately delivered
        )
        db.session.add(message)
        messages_created += 1
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Emergency broadcast sent to {messages_created} residents',
            'recipients': messages_created
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send broadcast'}), 500

def simulate_message_sending(message):
    """Simulate sending a message (placeholder implementation)."""
    import random
    
    # Simulate different success rates for different message types
    success_rates = {
        'internal': 1.0,    # Always successful
        'radio': 0.8,       # 80% success
        'sms': 0.7,         # 70% success
        'email': 0.9,       # 90% success
        'satellite': 0.6    # 60% success (challenging conditions)
    }
    
    success_rate = success_rates.get(message.message_type, 0.5)
    return random.random() < success_rate
