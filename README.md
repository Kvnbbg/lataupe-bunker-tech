# 🏠 Lataupe Bunker Tech MVP

> **Application Flask de surveillance environnementale pour bunkers post-apocalyptiques**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MPL_2.0-red.svg)](LICENSE)

## 🌟 Vue d'Ensemble

Lataupe Bunker Tech est une application web moderne conçue pour la surveillance et la gestion d'environnements de bunkers souterrains. Dans un scénario post-apocalyptique où la couche d'ozone a disparu, cette application permet aux habitants de bunkers de surveiller les conditions environnementales critiques et de gérer les communications d'urgence.

### ✨ Fonctionnalités Principales

- 📊 **Surveillance Environnementale en Temps Réel**

  - Température, humidité, qualité de l'air
  - Niveaux d'oxygène et de CO2
  - Détection de radiations UV
  - Graphiques interactifs avec Chart.js

- 🚨 **Système d'Alertes Intelligent**

  - Détection automatique des seuils critiques
  - Classification par niveaux de sévérité
  - Historique complet des incidents
  - Interface de résolution des alertes

- 📱 **Communication d'Urgence**

  - Messages SMS, email, radio, satellite
  - Templates prédéfinis pour situations d'urgence
  - Suivi du statut de livraison
  - Historique des communications

- 🔐 **Sécurité Avancée**

  - Authentification multi-rôles (Résident, Sécurité, Admin)
  - Protection CSRF et XSS
  - Sessions sécurisées
  - Hachage sécurisé des mots de passe

- 📱 **Interface Responsive**
  - Design moderne avec Tailwind CSS
  - Compatible mobile et desktop
  - Accessibilité WCAG
  - Mode sombre optimisé pour bunkers

## 🚀 Installation Rapide

### Prérequis

- Python 3.11+

- pip (gestionnaire de paquets Python)

- Git (optionnel)

### Installation

```bash
# 1. Cloner ou télécharger le projet
git clone <repository-url>
cd lataupe-bunker-tech

# 2. Créer un environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env selon vos besoins

# 5. Démarrer l'application
python run.py
```

L'application sera accessible à l'adresse : `http://localhost:5001`

### Comptes par Défaut

- **Administrateur** : `admin` / `admin123`

- **Résident** : `resident` / `resident123`

## 🏗️ Architecture

```
lataupe-bunker-tech/
├── app/
│   ├── __init__.py          # Factory create_app
│   ├── config.py            # Configuration (SQLite pour le MVP)
│   ├── models.py            # Modèles SQLAlchemy
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentification
│   │   ├── dashboard.py     # Tableau de bord
│   │   └── alerts.py        # Alertes et communications d'urgence
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_simulator.py  # Génération de données
│   │   └── message_sender.py  # Simulation d'envoi de messages
│   └── templates/
│       ├── base.html
│       ├── auth/login.html
│       ├── dashboard/index.html
│       └── alerts/index.html
├── static/
│   ├── css/style.css        # Styles (ex. Tailwind compilé)
│   ├── js/main.js           # Logique front-end
│   └── img/logo.png
├── tests/
│   ├── test_auth.py
│   ├── test_dashboard.py
│   └── test_api.py
├── run.py                   # Point d'entrée (create_app)
├── requirements.txt
└── README.md
```

> ℹ️ **MVP vs Production** : Le MVP s'appuie sur SQLite (`sqlite:///bunker.db`) pour accélérer le développement. La migration vers PostgreSQL est planifiée pour l'environnement de production.

## 🔧 Configuration

### Variables d'Environnement

```bash
# Configuration Flask
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
PORT=5001

# Configuration Base de Données
DATABASE_URL=sqlite:///bunker.db

# Configuration Sécurité
SESSION_COOKIE_SECURE=False  # True en production
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Configuration de Production

Pour un déploiement en production :

1. **Base de Données** : Migrer vers PostgreSQL

1. **Serveur Web** : Utiliser Gunicorn + Nginx

1. **HTTPS** : Configurer SSL/TLS

1. **Monitoring** : Implémenter logs et métriques

1. **Sécurité** : Durcir la configuration

## 📊 API Endpoints

### Authentification

- `GET /api/auth/status` - Statut de connexion

- `POST /api/auth/login` - Connexion utilisateur

- `POST /api/auth/logout` - Déconnexion

### Tableau de Bord

- `GET /api/dashboard/system-status` - Statut système

- `GET /api/dashboard/environmental-data` - Données environnementales

- `POST /api/dashboard/environmental-data/generate` - Générer données test

### Alertes & Communications d'Urgence

- `GET /api/alerts/active` - Alertes actives

- `POST /api/alerts/{id}/resolve` - Résoudre une alerte

- `GET /api/alerts/messages` - Historique des messages envoyés

- `POST /api/alerts/messages` - Envoyer un message d'urgence

## 🧪 Tests et Développement

### Génération de Données de Test

L'application inclut des fonctionnalités de simulation pour les tests :

- **Données Normales** : Génère des valeurs environnementales réalistes

- **Scénarios d'Urgence** : Simule des pannes et situations critiques

- **Messages de Test** : Teste les canaux de communication

### Scénarios d'Urgence Disponibles

- `ventilation_failure` - Panne de ventilation

- `heating_failure` - Panne de chauffage

- `external_contamination` - Contamination externe

- `power_shortage` - Pénurie d'énergie

## 🔒 Sécurité

### Mesures Implémentées

- ✅ Hachage sécurisé des mots de passe (PBKDF2)

- ✅ Protection CSRF avec Flask-WTF

- ✅ Sessions sécurisées avec cookies HTTPOnly

- ✅ Validation stricte des entrées utilisateur

- ✅ Protection XSS avec échappement automatique

- ✅ Contrôle d'accès basé sur les rôles

### Recommandations de Production

- Utiliser HTTPS exclusivement

- Configurer des mots de passe forts

- Implémenter la limitation de taux

- Surveiller les logs de sécurité

- Maintenir les dépendances à jour

## 🚀 Déploiement

### Docker (Recommandé)

```
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY run.py .
EXPOSE 5001

CMD ["python", "run.py"]
```

### Déploiement Cloud

L'application est compatible avec :

- **Heroku** : Avec Procfile inclus

- **AWS** : EC2, ECS, ou Lambda

- **Google Cloud** : App Engine ou Cloud Run

- **Azure** : App Service ou Container Instances

## 🚀 Railway Deployment

You can deploy this app to Railway with one click:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/lzsD1L?referralCode=74Ni9C)

### Manual Steps

1. Push this repo to your own GitHub.
2. Go to [Railway](https://railway.app/) and create a new project from your repo.
3. Set environment variables (SECRET_KEY, JWT_SECRET_KEY, etc) in Railway dashboard.
4. Deploy! The app will be available at your Railway URL.

- The app listens on `$PORT` (default 8080 for Railway).
- All secrets/config are read from environment variables.
- Dockerfile and Procfile are provided for compatibility.

## 🛠️ Extensibilité

### Intégration d'API

L'architecture permet l'intégration facile de :

- APIs météorologiques (OpenWeatherMap, AccuWeather)

- Services de communication (Twilio, SendGrid)

- Capteurs IoT (MQTT, HTTP REST)

- Systèmes de surveillance externes

### Plugins et Extensions

- Système de plugins modulaire

- Adaptateurs pour nouveaux capteurs

- Algorithmes d'analyse personnalisés

- Interfaces utilisateur spécialisées

## 📚 Documentation

- [Guide Complet du MVP](<DATA/Guide Complet du MVP Lataupe Bunker Tech _ Application Flask de Surveillance Environnementale.md>) - Documentation détaillée

- [Conception de l'Architecture](<DATA/Conception de l'Architecture de l'Application Flask pour le MVP Lataupe-Bunker-Tech.md>) - Structure et décisions techniques

- [Guide d'Intégration d'API](<DATA/Guide d'Intégration d'API - Lataupe Bunker Tech.md>) - Intégrations externes planifiées

- [Sécurité](SECURITY.md) - Guide de sécurité

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet

1. Créer une branche feature (`git checkout -b feature/AmazingFeature`)

1. Commit vos changements (`git commit -m 'Add AmazingFeature'`)

1. Push vers la branche (`git push origin feature/AmazingFeature`)

1. Ouvrir une Pull Request

## 📄 Licence

Ce projet est distribué sous licence Mozilla Public License 2.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

Pour obtenir de l'aide :

- 📖 Consultez la [documentation complète](<DATA/Guide Complet du MVP Lataupe Bunker Tech _ Application Flask de Surveillance Environnementale.md>)

- 🐛 Signalez les bugs via les Issues GitHub

- 💬 Posez vos questions dans les Discussions

## 🙏 Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web Python

- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utilitaire

- [Chart.js](https://www.chartjs.org/) - Bibliothèque de graphiques

- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python

---

**Développé avec ❤️**
