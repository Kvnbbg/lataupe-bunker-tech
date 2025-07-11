import os
import logging
import random
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
from src.models.user import db, User
from src.models.bunker import BunkerUser, EnvironmentalsData, Alert, EmergencyMessage
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.emergency import emergency_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(__file__), 'static'),
           static_url_path='/static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bunker-tech-secret-2025')
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bunker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app, supports_credentials=True)
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(emergency_bp)

# Story data
STORY_CHAPTERS = {
    "en": {
        "intro": {
            "title": "The Last Sanctuary",
            "content": "The year is 2025. The ozone layer has completely vanished, leaving Earth's surface uninhabitable. Humanity's last hope lies in underground bunkers scattered across the globe.",
            "slides": ["vanishing_shield", "scorched_earth"]
        },
        "chapter1": {
            "title": "Underground Haven",
            "content": "Welcome to Bunker-01, one of the few remaining safe havens. Here, advanced technology monitors every aspect of our survival - air quality, radiation levels, and life support systems.",
            "slides": ["underground_living", "technology_failure"]
        },
        "chapter2": {
            "title": "Your Mission",
            "content": "As a resident of this bunker, your role is crucial. Monitor environmental conditions, respond to emergencies, and help maintain the delicate balance that keeps our community alive.",
            "slides": ["call_to_action"]
        }
    },
    "fr": {
        "intro": {
            "title": "Le Dernier Sanctuaire",
            "content": "L'année est 2025. La couche d'ozone a complètement disparu, rendant la surface de la Terre inhabitable. Le dernier espoir de l'humanité réside dans les bunkers souterrains dispersés à travers le globe.",
            "slides": ["vanishing_shield", "scorched_earth"]
        },
        "chapter1": {
            "title": "Refuge Souterrain",
            "content": "Bienvenue dans le Bunker-01, l'un des rares havres de paix restants. Ici, une technologie avancée surveille chaque aspect de notre survie - qualité de l'air, niveaux de radiation et systèmes de survie.",
            "slides": ["underground_living", "technology_failure"]
        },
        "chapter2": {
            "title": "Votre Mission",
            "content": "En tant que résident de ce bunker, votre rôle est crucial. Surveillez les conditions environnementales, répondez aux urgences et aidez à maintenir l'équilibre délicat qui garde notre communauté en vie.",
            "slides": ["call_to_action"]
        }
    }
}

# Translations
TRANSLATIONS = {
    "en": {
        "app_title": "Lataupe Bunker Tech",
        "login": "Login",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "environmental": "Environmental",
        "alerts": "Alerts",
        "emergency": "Emergency",
        "story": "Story",
        "username": "Username",
        "password": "Password",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "oxygen": "Oxygen Level",
        "co2": "CO2 Level",
        "radiation": "Radiation",
        "system_status": "System Status",
        "bunker_health": "Bunker Health",
        "residents": "Residents",
        "uptime": "System Uptime",
        "welcome": "Welcome to the Underground",
        "survival_message": "Every moment counts in our fight for survival"
    },
    "fr": {
        "app_title": "Lataupe Bunker Tech",
        "login": "Connexion",
        "logout": "Déconnexion",
        "dashboard": "Tableau de Bord",
        "environmental": "Environnemental",
        "alerts": "Alertes",
        "emergency": "Urgence",
        "story": "Histoire",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "temperature": "Température",
        "humidity": "Humidité",
        "oxygen": "Niveau d'Oxygène",
        "co2": "Niveau de CO2",
        "radiation": "Radiation",
        "system_status": "État du Système",
        "bunker_health": "Santé du Bunker",
        "residents": "Résidents",
        "uptime": "Temps de Fonctionnement",
        "welcome": "Bienvenue dans le Souterrain",
        "survival_message": "Chaque moment compte dans notre lutte pour la survie"
    }
}

def create_tables():
    """Initialize database with sample data"""
    db.create_all()
    
    # Add sample users if none exist
    if User.query.count() == 0:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@bunker.tech',
            role='admin'
        )
        admin.set_password('admin123')
        
        # Create resident user
        resident = User(
            username='resident',
            email='resident@bunker.tech',
            role='resident'
        )
        resident.set_password('resident123')
        
        db.session.add(admin)
        db.session.add(resident)
        db.session.commit()
        
        # Create bunker profiles
        admin_bunker = BunkerUser(
            user_id=admin.id,
            bunker_id='bunker-01',
            access_level='admin',
            room_assignment='Control Room',
            emergency_contact='Command Center'
        )
        
        resident_bunker = BunkerUser(
            user_id=resident.id,
            bunker_id='bunker-01',
            access_level='basic',
            room_assignment='Living Quarter A-12',
            emergency_contact='+1-555-0123'
        )
        
        db.session.add(admin_bunker)
        db.session.add(resident_bunker)
        
        # Add sample environmental data
        for i in range(24):
            env_data = EnvironmentalsData(
                timestamp=datetime.utcnow() - timedelta(hours=i),
                temperature=random.uniform(18, 24),
                humidity=random.uniform(40, 60),
                air_quality=random.uniform(80, 100),
                oxygen_level=random.uniform(19, 21),
                co2_level=random.uniform(400, 800),
                radiation_level=random.uniform(0.1, 0.5),
                atmospheric_pressure=random.uniform(1010, 1020),
                bunker_id='bunker-01',
                sensor_location='Central Hub'
            )
            db.session.add(env_data)
        
        db.session.commit()
        logger.info("Database initialized with sample data")

# Routes
@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/story')
def get_story():
    """Get story chapters"""
    lang = request.args.get('lang', 'en')
    return jsonify(STORY_CHAPTERS.get(lang, STORY_CHAPTERS['en']))

@app.route('/api/translations')
def get_translations():
    """Get UI translations"""
    lang = request.args.get('lang', 'en')
    return jsonify(TRANSLATIONS.get(lang, TRANSLATIONS['en']))

@app.route('/api/slides/<slide_name>')
def get_slide(slide_name):
    """Serve slide content"""
    slide_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ozone_slides', f'{slide_name}.html')
    if os.path.exists(slide_path):
        with open(slide_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Slide not found", 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Lataupe Bunker Tech on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
