import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db, User
from src.models.bunker import BunkerUser, EnvironmentalsData, Alert, EmergencyMessage
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.emergency import emergency_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configure CORS pour permettre les requêtes cross-origin
CORS(app, supports_credentials=True)

# Configuration de la base de données
app.config['SECRET_KEY'] = 'bunker-tech-secret-key-change-in-production'
app.config['SESSION_COOKIE_SECURE'] = False  # True en production avec HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # True pour empêcher l'accès JavaScript to the cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax pour les requêtes cross-site

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bunker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(emergency_bp)

# Static file serving
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

def create_default_users():
    """Create default users if they don't exist."""
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@bunker.tech',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create bunker profile for admin
        admin_bunker = BunkerUser(
            user_id=admin.id,
            bunker_id='bunker-01',
            access_level='full',
            room_assignment='Command Center',
            emergency_contact='Internal Communications'
        )
        db.session.add(admin_bunker)
    
    # Create resident user
    resident = User.query.filter_by(username='resident').first()
    if not resident:
        resident = User(
            username='resident',
            email='resident@bunker.tech',
            role='resident'
        )
        resident.set_password('resident123')
        db.session.add(resident)
        
        # Create bunker profile for resident
        resident_bunker = BunkerUser(
            user_id=resident.id,
            bunker_id='bunker-01',
            access_level='basic',
            room_assignment='Residential Block A-12',
            emergency_contact='Emergency Services'
        )
        db.session.add(resident_bunker)
    
    db.session.commit()

def create_sample_data():
    """Create sample environmental data and alerts."""
    import random
    from datetime import datetime, timedelta
    
    # Create sample environmental data
    for i in range(10):
        timestamp = datetime.utcnow() - timedelta(hours=i)
        data = EnvironmentalsData(
            timestamp=timestamp,
            temperature=random.uniform(18, 24),
            humidity=random.uniform(40, 60),
            air_quality=random.uniform(50, 100),
            oxygen_level=random.uniform(20, 21),
            co2_level=random.uniform(400, 800),
            radiation_level=random.uniform(0.1, 0.5),
            atmospheric_pressure=random.uniform(1000, 1020),
            bunker_id='bunker-01',
            sensor_location=f'Sensor-{i % 3 + 1}'
        )
        db.session.add(data)
    
    # Create a sample alert
    alert = Alert(
        alert_type='temperature',
        severity='medium',
        message='Temperature slightly above optimal range in Sector A',
        bunker_id='bunker-01',
        sensor_location='Sensor-1'
    )
    db.session.add(alert)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create default users and sample data
        create_default_users()
        create_sample_data()
    
    # Run the application
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
