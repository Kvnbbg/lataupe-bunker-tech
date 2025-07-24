import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db, User
from src.models.bunker import BunkerUser, EnvironmentalsData, Alert, EmergencyMessage
from src.models.user import user_bp
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.emergency import emergency_bp

# Story and slides data
STORY_DATA = {
    'en': {
        'title': 'The Last Bunker: Chronicles of the Ozone Crisis',
        'chapters': [
            {
                'id': 'prologue',
                'title': 'Prologue: The Vanishing Shield',
                'content': '''In the year 2025, humanity faced its greatest challenge yet. The ozone layer, Earth's natural protective shield for millions of years, began its rapid and irreversible collapse. What scientists had predicted would take decades happened in mere years.
                
The signs were unmistakable: UV radiation levels skyrocketed, surface temperatures became unbearable during daylight hours, and the very air outside became hostile to human life. Traditional technology, designed for a world with atmospheric protection, began to fail catastrophically.
                
As governments scrambled for solutions, a new reality emerged: humanity would have to go underground.'''
            },
            {
                'id': 'chapter1',
                'title': 'Chapter 1: The Great Descent',
                'content': '''The Lataupe Bunker Project was born from necessity. Named after the French word for "mole," it represented humanity's adaptation to a subterranean existence. Deep beneath the earth's surface, networks of interconnected bunkers became the new cities of tomorrow.
                
You are Alex Chen, Chief Environmental Monitor of Bunker Complex Alpha-7. Your mission: ensure the survival of 847 residents in a world where the surface has become uninhabitable. Every day brings new challenges as you monitor air quality, radiation levels, and the fragile life support systems that keep your underground community alive.
                
The bunker's advanced monitoring system, developed specifically for post-ozone survival, tracks everything from oxygen levels to psychological well-being of residents. Your decisions could mean the difference between life and death for everyone under your care.'''
            },
            {
                'id': 'chapter2',
                'title': 'Chapter 2: The Technology Crisis',
                'content': '''Traditional electronics weren't designed for the extreme conditions of underground living. High humidity, limited ventilation, and the constant threat of system failures meant that every piece of technology had to be reimagined.
                
The bunker's computers run on hardened systems, resistant to electromagnetic interference and capable of operating in low-power modes for extended periods. Communication with other bunker complexes relies on a combination of underground fiber networks and heavily shielded radio systems.
                
But technology is only as reliable as the people maintaining it. When critical systems fail, it's up to you and your team to diagnose problems, implement solutions, and keep the community functioning. The weight of responsibility is immense - a single system failure could cascade into a life-threatening emergency.'''
            },
            {
                'id': 'chapter3',
                'title': 'Chapter 3: Life Underground',
                'content': '''Six months into the bunker operation, routines have emerged. Residents work in shifts to maintain the complex machinery that keeps them alive. Hydroponics bays provide fresh food, water recycling systems ensure nothing is wasted, and carefully controlled air circulation maintains breathable atmosphere.
                
But human psychology wasn't designed for permanent underground living. Depression, anxiety, and cabin fever are constant threats. The bunker's recreational areas, artificial sky systems, and community spaces are as vital as the life support systems themselves.
                
Emergency drills are a weekly occurrence. Every resident knows their role in case of system failures, contamination alerts, or the dreaded possibility of surface breach. The emergency communication system you monitor isn't just about technical alerts - it's the lifeline that holds the community together during crisis.'''
            },
            {
                'id': 'chapter4',
                'title': 'Chapter 4: The Network',
                'content': '''Your bunker isn't alone. Across the globe, similar facilities house the survivors of humanity's greatest crisis. The underground network exchanges vital information, resources, and hope. Trading surplus food for medical supplies, sharing technological innovations, and coordinating research efforts to eventually reclaim the surface.
                
Communication protocols are strict and essential. Every message between bunkers is logged, verified, and analyzed. The emergency broadcast system can reach allied facilities within minutes, but it can also reveal your location to hostile groups that roam the wasteland above.
                
Today's monitoring shift reveals concerning data: radiation levels are spiking beyond normal parameters, and seismic sensors detect unusual activity. These readings could indicate anything from geological instability to... something else moving on the surface.'''
            },
            {
                'id': 'epilogue',
                'title': 'Epilogue: Hope in the Depths',
                'content': '''As you review the day's environmental data, you reflect on humanity's incredible adaptability. The bunker that seemed like a temporary refuge is becoming a permanent home. Children born underground know no other world, yet they're already showing remarkable innovation in solving problems their surface-dwelling ancestors never imagined.
                
The monitoring systems you oversee aren't just about survival anymore - they're about building a foundation for the future. Every data point collected, every system optimized, every crisis successfully managed brings humanity one step closer to thriving in this new world.
                
The surface may be lost, but hope lives on in the depths. In the warm glow of your monitoring screens, surrounded by the quiet hum of life support systems, you know that humanity's story is far from over. It's just being written in a place where the sun never shines, but the human spirit burns brighter than ever.'''
            }
        ]
    },
    'fr': {
        'title': 'Le Dernier Bunker: Chroniques de la Crise de l\'Ozone',
        'chapters': [
            {
                'id': 'prologue',
                'title': 'Prologue: Le Bouclier Qui Disparaît',
                'content': '''En l'année 2025, l'humanité fit face à son plus grand défi. La couche d'ozone, bouclier protecteur naturel de la Terre depuis des millions d'années, commença son effondrement rapide et irréversible. Ce que les scientifiques avaient prédit prendre des décennies arriva en quelques années seulement.
                
Les signes étaient indéniables : les niveaux de radiation UV montèrent en flèche, les températures de surface devinrent insupportables pendant les heures de jour, et l'air extérieur lui-même devint hostile à la vie humaine. La technologie traditionnelle, conçue pour un monde avec protection atmosphérique, commença à défaillir de manière catastrophique.
                
Alors que les gouvernements cherchaient des solutions, une nouvelle réalité émergea : l'humanité devrait descendre sous terre.'''
            },
            {
                'id': 'chapter1',
                'title': 'Chapitre 1: La Grande Descente',
                'content': '''Le Projet Bunker Lataupe naquit de la nécessité. Nommé d'après le mot français "taupe", il représentait l'adaptation de l'humanité à une existence souterraine. Profondément sous la surface terrestre, des réseaux de bunkers interconnectés devinrent les nouvelles villes de demain.
                
Vous êtes Alex Chen, Moniteur Environnemental en Chef du Complexe Bunker Alpha-7. Votre mission : assurer la survie de 847 résidents dans un monde où la surface est devenue inhabitable. Chaque jour apporte de nouveaux défis alors que vous surveillez la qualité de l'air, les niveaux de radiation, et les systèmes de support de vie fragiles qui maintiennent votre communauté souterraine en vie.
                
Le système de surveillance avancé du bunker, développé spécifiquement pour la survie post-ozone, suit tout, des niveaux d'oxygène au bien-être psychologique des résidents. Vos décisions pourraient faire la différence entre la vie et la mort pour tous ceux sous votre garde.'''
            },
            {
                'id': 'chapter2',
                'title': 'Chapitre 2: La Crise Technologique',
                'content': '''L'électronique traditionnelle n'était pas conçue pour les conditions extrêmes de la vie souterraine. Haute humidité, ventilation limitée, et la menace constante de défaillances système signifiaient que chaque pièce de technologie devait être repensée.
                
Les ordinateurs du bunker fonctionnent sur des systèmes durcis, résistants aux interférences électromagnétiques et capables d'opérer en modes basse consommation pendant des périodes prolongées. La communication avec d'autres complexes de bunkers repose sur une combinaison de réseaux de fibre souterrains et de systèmes radio fortement blindés.
                
Mais la technologie n'est fiable que tant que les gens qui la maintiennent le sont. Quand des systèmes critiques échouent, c'est à vous et votre équipe de diagnostiquer les problèmes, implémenter des solutions, et maintenir la communauté fonctionnelle.'''
            },
            {
                'id': 'chapter3',
                'title': 'Chapitre 3: La Vie Souterraine',
                'content': '''Six mois après le début des opérations du bunker, des routines ont émergé. Les résidents travaillent par équipes pour maintenir les machines complexes qui les gardent en vie. Les baies hydroponiques fournissent de la nourriture fraîche, les systèmes de recyclage d'eau assurent que rien n'est gaspillé, et la circulation d'air soigneusement contrôlée maintient une atmosphère respirable.
                
Mais la psychologie humaine n'était pas conçue pour une vie souterraine permanente. Dépression, anxiété, et claustrophobie sont des menaces constantes. Les zones récréatives du bunker, les systèmes de ciel artificiel, et les espaces communautaires sont aussi vitaux que les systèmes de support de vie eux-mêmes.
                
Les exercices d'urgence sont hebdomadaires. Chaque résident connaît son rôle en cas de défaillances système, d'alertes de contamination, ou de la redoutable possibilité d'une brèche de surface.'''
            },
            {
                'id': 'chapter4',
                'title': 'Chapitre 4: Le Réseau',
                'content': '''Votre bunker n'est pas seul. À travers le globe, des installations similaires abritent les survivants de la plus grande crise de l'humanité. Le réseau souterrain échange des informations vitales, des ressources, et de l'espoir. Échangeant surplus de nourriture contre fournitures médicales, partageant innovations technologiques, et coordonnant efforts de recherche pour éventuellement reconquérir la surface.
                
Les protocoles de communication sont stricts et essentiels. Chaque message entre bunkers est enregistré, vérifié, et analysé. Le système de diffusion d'urgence peut atteindre les installations alliées en minutes, mais il peut aussi révéler votre position aux groupes hostiles qui errent dans le désert au-dessus.
                
Le quart de surveillance d'aujourd'hui révèle des données préoccupantes : les niveaux de radiation augmentent au-delà des paramètres normaux, et les capteurs sismiques détectent une activité inhabituelle.'''
            },
            {
                'id': 'epilogue',
                'title': 'Épilogue: L\'Espoir dans les Profondeurs',
                'content': '''Alors que vous révisez les données environnementales de la journée, vous réfléchissez à l'incroyable adaptabilité de l'humanité. Le bunker qui semblait être un refuge temporaire devient un foyer permanent. Les enfants nés sous terre ne connaissent aucun autre monde, pourtant ils montrent déjà une innovation remarquable pour résoudre des problèmes que leurs ancêtres de surface n'avaient jamais imaginés.
                
Les systèmes de surveillance que vous supervisez ne concernent plus seulement la survie - ils construisent une fondation pour l'avenir. Chaque point de données collecté, chaque système optimisé, chaque crise gérée avec succès rapproche l'humanité d'un pas vers la prospérité dans ce nouveau monde.
                
La surface peut être perdue, mais l'espoir vit dans les profondeurs. Dans la lueur chaude de vos écrans de surveillance, entouré par le bourdonnement silencieux des systèmes de support de vie, vous savez que l'histoire de l'humanité est loin d'être terminée.'''
            }
        ]
    },
    'fr': {
        'title': 'Le Dernier Bunker: Chroniques de la Crise de l\'Ozone',
        'chapters': [
            {
                'id': 'prologue',
                'title': 'Prologue: Le Bouclier Qui Disparaît',
                'content': '''En l'année 2025, l'humanité fit face à son plus grand défi. La couche d'ozone, bouclier protecteur naturel de la Terre depuis des millions d'années, commença son effondrement rapide et irréversible. Ce que les scientifiques avaient prédit prendre des décennies arriva en quelques années seulement.
                
Les signes étaient indéniables : les niveaux de radiation UV montèrent en flèche, les températures de surface devinrent insupportables pendant les heures de jour, et l'air extérieur lui-même devint hostile à la vie humaine. La technologie traditionnelle, conçue pour un monde avec protection atmosphérique, commença à défaillir de manière catastrophique.
                
Alors que les gouvernements cherchaient des solutions, une nouvelle réalité émergea : l'humanité devrait descendre sous terre.'''
            },
            {
                'id': 'chapter1',
                'title': 'Chapitre 1: La Grande Descente',
                'content': '''Le Projet Bunker Lataupe naquit de la nécessité. Nommé d'après le mot français "taupe", il représentait l'adaptation de l'humanité à une existence souterraine. Profondément sous la surface terrestre, des réseaux de bunkers interconnectés devinrent les nouvelles villes de demain.
                
Vous êtes Alex Chen, Moniteur Environnemental en Chef du Complexe Bunker Alpha-7. Votre mission : assurer la survie de 847 résidents dans un monde où la surface est devenue inhabitable. Chaque jour apporte de nouveaux défis alors que vous surveillez la qualité de l'air, les niveaux de radiation, et les systèmes de support de vie fragiles qui maintiennent votre communauté souterraine en vie.
                
Le système de surveillance avancé du bunker, développé spécifiquement pour la survie post-ozone, suit tout, des niveaux d'oxygène au bien-être psychologique des résidents. Vos décisions pourraient faire la différence entre la vie et la mort pour tous ceux sous votre garde.'''
            },
            {
                'id': 'chapter2',
                'title': 'Chapitre 2: La Crise Technologique',
                'content': '''L'électronique traditionnelle n'était pas conçue pour les conditions extrêmes de la vie souterraine. Haute humidité, ventilation limitée, et la menace constante de défaillances système signifiaient que chaque pièce de technologie devait être repensée.
                
Les ordinateurs du bunker fonctionnent sur des systèmes durcis, résistants aux interférences électromagnétiques et capables d'opérer en modes basse consommation pendant des périodes prolongées. La communication avec d'autres complexes de bunkers repose sur une combinaison de réseaux de fibre souterrains et de systèmes radio fortement blindés.
                
Mais la technologie n'est fiable que tant que les gens qui la maintiennent le sont. Quand des systèmes critiques échouent, c'est à vous et votre équipe de diagnostiquer les problèmes, implémenter des solutions, et maintenir la communauté fonctionnelle.'''
            },
            {
                'id': 'chapter3',
                'title': 'Chapitre 3: La Vie Souterraine',
                'content': '''Six mois après le début des opérations du bunker, des routines ont émergé. Les résidents travaillent par équipes pour maintenir les machines complexes qui les gardent en vie. Les baies hydroponiques fournissent de la nourriture fraîche, les systèmes de recyclage d'eau assurent que rien n'est gaspillé, et la circulation d'air soigneusement contrôlée maintient une atmosphère respirable.
                
Mais la psychologie humaine n'était pas conçue pour une vie souterraine permanente. Dépression, anxiété, et claustrophobie sont des menaces constantes. Les zones récréatives du bunker, les systèmes de ciel artificiel, et les espaces communautaires sont aussi vitaux que les systèmes de support de vie eux-mêmes.
                
Les exercices d'urgence sont hebdomadaires. Chaque résident connaît son rôle en cas de défaillances système, d'alertes de contamination, ou de la redoutable possibilité d'une brèche de surface.'''
            },
            {
                'id': 'chapter4',
                'title': 'Chapitre 4: Le Réseau',
                'content': '''Votre bunker n'est pas seul. À travers le globe, des installations similaires abritent les survivants de la plus grande crise de l'humanité. Le réseau souterrain échange des informations vitales, des ressources, et de l'espoir. Échangeant surplus de nourriture contre fournitures médicales, partageant innovations technologiques, et coordonnant efforts de recherche pour éventuellement reconquérir la surface.
                
Les protocoles de communication sont stricts et essentiels. Chaque message entre bunkers est enregistré, vérifié, et analysé. Le système de diffusion d'urgence peut atteindre les installations alliées en minutes, mais il peut aussi révéler votre position aux groupes hostiles qui errent dans le désert au-dessus.
                
Le quart de surveillance d'aujourd'hui révèle des données préoccupantes : les niveaux de radiation augmentent au-delà des paramètres normaux, et les capteurs sismiques détectent une activité inhabituelle.'''
            },
            {
                'id': 'epilogue',
                'title': 'Épilogue: L\'Espoir dans les Profondeurs',
                'content': '''Alors que vous révisez les données environnementales de la journée, vous réfléchissez à l'incroyable adaptabilité de l'humanité. Le bunker qui semblait être un refuge temporaire devient un foyer permanent. Les enfants nés sous terre ne connaissent aucun autre monde, pourtant ils montrent déjà une innovation remarquable pour résoudre des problèmes que leurs ancêtres de surface n'avaient jamais imaginés.
                
Les systèmes de surveillance que vous supervisez ne concernent plus seulement la survie - ils construisent une fondation pour l'avenir. Chaque point de données collecté, chaque système optimisé, chaque crise gérée avec succès rapproche l'humanité d'un pas vers la prospérité dans ce nouveau monde.
                
La surface peut être perdue, mais l'espoir vit dans les profondeurs. Dans la lueur chaude de vos écrans de surveillance, entouré par le bourdonnement silencieux des systèmes de support de vie, vous savez que l'histoire de l'humanité est loin d'être terminée.'''
            }
        ]
    }
}

# Language support
TRANSLATIONS = {
    'en': {
        'nav': {
            'dashboard': 'Dashboard',
            'alerts': 'Alerts',
            'emergency': 'Emergency',
            'story': 'Story',
            'slides': 'Slides',
            'profile': 'Profile',
            'logout': 'Logout',
            'language': 'Language'
        },
        'dashboard': {
            'title': 'Environmental Monitoring Dashboard',
            'system_status': 'System Status',
            'health_score': 'Health Score',
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'oxygen': 'Oxygen Level',
            'co2': 'CO2 Level',
            'radiation': 'Radiation',
            'active_alerts': 'Active Alerts',
            'no_alerts': 'No active alerts',
            'residents': 'Total Residents',
            'uptime': 'System Uptime'
        },
        'alerts': {
            'title': 'Security Alerts',
            'severity': 'Severity',
            'message': 'Message',
            'timestamp': 'Time',
            'location': 'Location',
            'resolve': 'Resolve',
            'resolved': 'Resolved',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'critical': 'Critical'
        },
        'emergency': {
            'title': 'Emergency Communications',
            'send_message': 'Send Emergency Message',
            'broadcast': 'Broadcast to All',
            'templates': 'Message Templates',
            'message_type': 'Message Type',
            'recipient': 'Recipient',
            'subject': 'Subject',
            'content': 'Content',
            'priority': 'Priority',
            'send': 'Send',
            'status': 'Status'
        },
        'story': {
            'title': 'The Chronicles',
            'chapters': 'Chapters',
            'current_chapter': 'Current Chapter',
            'next': 'Next',
            'previous': 'Previous',
            'background_slides': 'Background Slides'
        },
        'login': {
            'title': 'Bunker Access Control',
            'username': 'Username',
            'password': 'Password',
            'login': 'Access Bunker',
            'welcome': 'Welcome to Lataupe Bunker Tech'
        }
    },
    'fr': {
        'nav': {
            'dashboard': 'Tableau de Bord',
            'alerts': 'Alertes',
            'emergency': 'Urgence',
            'story': 'Histoire',
            'slides': 'Diapositives',
            'profile': 'Profil',
            'logout': 'Déconnexion',
            'language': 'Langue'
        },
        'dashboard': {
            'title': 'Tableau de Bord de Surveillance Environnementale',
            'system_status': 'État du Système',
            'health_score': 'Score de Santé',
            'temperature': 'Température',
            'humidity': 'Humidité',
            'oxygen': 'Niveau d\'Oxygène',
            'co2': 'Niveau de CO2',
            'radiation': 'Radiation',
            'active_alerts': 'Alertes Actives',
            'no_alerts': 'Aucune alerte active',
            'residents': 'Résidents Totaux',
            'uptime': 'Temps de Fonctionnement'
        },
        'alerts': {
            'title': 'Alertes de Sécurité',
            'severity': 'Sévérité',
            'message': 'Message',
            'timestamp': 'Heure',
            'location': 'Emplacement',
            'resolve': 'Résoudre',
            'resolved': 'Résolu',
            'low': 'Faible',
            'medium': 'Moyen',
            'high': 'Élevé',
            'critical': 'Critique'
        },
        'emergency': {
            'title': 'Communications d\'Urgence',
            'send_message': 'Envoyer Message d\'Urgence',
            'broadcast': 'Diffuser à Tous',
            'templates': 'Modèles de Messages',
            'message_type': 'Type de Message',
            'recipient': 'Destinataire',
            'subject': 'Sujet',
            'content': 'Contenu',
            'priority': 'Priorité',
            'send': 'Envoyer',
            'status': 'Statut'
        },
        'story': {
            'title': 'Les Chroniques',
            'chapters': 'Chapitres',
            'current_chapter': 'Chapitre Actuel',
            'next': 'Suivant',
            'previous': 'Précédent',
            'background_slides': 'Diapositives d\'Arrière-plan'
        },
        'login': {
            'title': 'Contrôle d\'Accès au Bunker',
            'username': 'Nom d\'utilisateur',
            'password': 'Mot de passe',
            'login': 'Accéder au Bunker',
            'welcome': 'Bienvenue à Lataupe Bunker Tech'
        }
    }
}

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

# Story API endpoints
@app.route('/api/story')
def get_story():
    """Get story data with language support."""
    lang = request.args.get('lang', 'en')
    if lang not in STORY_DATA:
        lang = 'en'
    
    return jsonify(STORY_DATA[lang])

@app.route('/api/story/chapter/<chapter_id>')
def get_chapter(chapter_id):
    """Get specific story chapter."""
    lang = request.args.get('lang', 'en')
    if lang not in STORY_DATA:
        lang = 'en'
    
    story = STORY_DATA[lang]
    chapter = next((ch for ch in story['chapters'] if ch['id'] == chapter_id), None)
    
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    return jsonify(chapter)

# Language support API
@app.route('/api/translations/<lang>')
def get_translations(lang):
    """Get translations for specified language."""
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    return jsonify(TRANSLATIONS[lang])

# Slides API endpoints
@app.route('/api/slides')
def get_slides():
    """Get available background slides."""
    slides_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ozone_slides')
    slides = []
    
    if os.path.exists(slides_dir):
        for filename in os.listdir(slides_dir):
            if filename.endswith('.html'):
                slide_name = filename.replace('.html', '').replace('_', ' ').title()
                slides.append({
                    'id': filename.replace('.html', ''),
                    'name': slide_name,
                    'filename': filename,
                    'url': f'/slides/{filename}'
                })
    
    return jsonify(slides)

@app.route('/slides/<filename>')
def serve_slide(filename):
    """Serve slide files."""
    slides_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ozone_slides')
    return send_from_directory(slides_dir, filename)

# API endpoint for slide content (for background integration)
@app.route('/api/slides/<slide_id>/content')
def get_slide_content(slide_id):
    """Get slide content for background integration."""
    slides_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ozone_slides')
    slide_file = f"{slide_id}.html"
    slide_path = os.path.join(slides_dir, slide_file)
    
    if not os.path.exists(slide_path):
        return jsonify({'error': 'Slide not found'}), 404
    
    try:
        with open(slide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'id': slide_id,
            'html_content': content,
            'url': f'/slides/{slide_file}'
        })
    except Exception as e:
        return jsonify({'error': 'Failed to read slide content'}), 500

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
