from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.bunker import BunkerUser, EnvironmentalsData, Alert
from datetime import datetime, timedelta
import random

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/system-status', methods=['GET'])
def system_status():
    """Get overall system status."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get current user's bunker
    user = User.query.get(session['user_id'])
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Get latest environmental data
    latest_data = EnvironmentalsData.query.filter_by(bunker_id=bunker_id)\
                                          .order_by(EnvironmentalsData.timestamp.desc())\
                                          .first()
    
    # Get active alerts
    active_alerts = Alert.query.filter_by(bunker_id=bunker_id, is_resolved=False)\
                              .order_by(Alert.timestamp.desc())\
                              .limit(5).all()
    
    # Calculate system health score
    health_score = calculate_health_score(latest_data)
    
    return jsonify({
        'bunker_id': bunker_id,
        'health_score': health_score,
        'latest_environmental_data': latest_data.to_dict() if latest_data else None,
        'active_alerts': [alert.to_dict() for alert in active_alerts],
        'total_residents': User.query.join(BunkerUser).filter_by(bunker_id=bunker_id).count(),
        'system_uptime': get_system_uptime()
    })

@dashboard_bp.route('/environmental-data', methods=['GET'])
def environmental_data():
    """Get environmental data for charts."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get query parameters
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    user = User.query.get(session['user_id'])
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Get data from the last N hours
    since = datetime.utcnow() - timedelta(hours=hours)
    
    data = EnvironmentalsData.query.filter_by(bunker_id=bunker_id)\
                                   .filter(EnvironmentalsData.timestamp >= since)\
                                   .order_by(EnvironmentalsData.timestamp.desc())\
                                   .limit(limit).all()
    
    return jsonify([item.to_dict() for item in data])

@dashboard_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alerts with filtering."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    bunker_user = BunkerUser.query.filter_by(user_id=user.id).first()
    bunker_id = bunker_user.bunker_id if bunker_user else 'bunker-01'
    
    # Get query parameters
    resolved = request.args.get('resolved', 'false').lower() == 'true'
    severity = request.args.get('severity')
    limit = request.args.get('limit', 50, type=int)
    
    query = Alert.query.filter_by(bunker_id=bunker_id, is_resolved=resolved)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    return jsonify([alert.to_dict() for alert in alerts])

@dashboard_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if user.role not in ['admin', 'security']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    alert = Alert.query.get_or_404(alert_id)
    
    data = request.get_json() or {}
    
    alert.is_resolved = True
    alert.resolved_by = user.id
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = data.get('notes', '')
    
    try:
        db.session.commit()
        return jsonify({'message': 'Alert resolved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to resolve alert'}), 500

def calculate_health_score(environmental_data):
    """Calculate system health score based on environmental data."""
    if not environmental_data:
        return 0
    
    score = 100
    
    # Temperature check (optimal: 18-24°C)
    if environmental_data.temperature:
        if environmental_data.temperature < 15 or environmental_data.temperature > 28:
            score -= 20
        elif environmental_data.temperature < 18 or environmental_data.temperature > 24:
            score -= 10
    
    # Humidity check (optimal: 40-60%)
    if environmental_data.humidity:
        if environmental_data.humidity < 30 or environmental_data.humidity > 70:
            score -= 15
        elif environmental_data.humidity < 40 or environmental_data.humidity > 60:
            score -= 5
    
    # Oxygen level check (critical: >19%)
    if environmental_data.oxygen_level:
        if environmental_data.oxygen_level < 19:
            score -= 30
        elif environmental_data.oxygen_level < 20:
            score -= 15
    
    # CO2 level check (critical: >1000 ppm)
    if environmental_data.co2_level:
        if environmental_data.co2_level > 1000:
            score -= 25
        elif environmental_data.co2_level > 800:
            score -= 10
    
    # Radiation level check (warning: >1 µSv/h)
    if environmental_data.radiation_level:
        if environmental_data.radiation_level > 5:
            score -= 40
        elif environmental_data.radiation_level > 1:
            score -= 20
    
    return max(0, score)

def get_system_uptime():
    """Get system uptime (placeholder implementation)."""
    return "72 hours, 15 minutes"
