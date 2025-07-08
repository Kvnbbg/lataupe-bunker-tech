from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class BunkerUser(db.Model):
    __tablename__ = 'bunker_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bunker_id = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.String(50), nullable=False, default='basic')
    room_assignment = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(200))
    medical_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bunker_id': self.bunker_id,
            'access_level': self.access_level,
            'room_assignment': self.room_assignment,
            'emergency_contact': self.emergency_contact,
            'medical_info': self.medical_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EnvironmentalsData(db.Model):
    __tablename__ = 'environmental_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature = db.Column(db.Float)  # Celsius
    humidity = db.Column(db.Float)     # Percentage
    air_quality = db.Column(db.Float)  # Air Quality Index
    oxygen_level = db.Column(db.Float) # Percentage
    co2_level = db.Column(db.Float)    # PPM
    radiation_level = db.Column(db.Float) # µSv/h
    atmospheric_pressure = db.Column(db.Float) # hPa
    bunker_id = db.Column(db.String(50), nullable=False)
    sensor_location = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'air_quality': self.air_quality,
            'oxygen_level': self.oxygen_level,
            'co2_level': self.co2_level,
            'radiation_level': self.radiation_level,
            'atmospheric_pressure': self.atmospheric_pressure,
            'bunker_id': self.bunker_id,
            'sensor_location': self.sensor_location
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    message = db.Column(db.Text, nullable=False)
    bunker_id = db.Column(db.String(50), nullable=False)
    sensor_location = db.Column(db.String(100))
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'bunker_id': self.bunker_id,
            'sensor_location': self.sensor_location,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }

class EmergencyMessage(db.Model):
    __tablename__ = 'emergency_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # sms, email, radio, satellite
    recipient = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='normal')  # low, normal, high, urgent
    status = db.Column(db.String(20), nullable=False, default='pending')   # pending, sent, delivered, failed
    sent_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bunker_id = db.Column(db.String(50), nullable=False)
    delivery_confirmation = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'message_type': self.message_type,
            'recipient': self.recipient,
            'subject': self.subject,
            'content': self.content,
            'priority': self.priority,
            'status': self.status,
            'sent_by': self.sent_by,
            'bunker_id': self.bunker_id,
            'delivery_confirmation': self.delivery_confirmation.isoformat() if self.delivery_confirmation else None,
            'error_message': self.error_message
        }
