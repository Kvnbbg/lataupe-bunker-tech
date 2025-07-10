# 🏠 Lataupe Bunker Tech - Underground Survival System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen.svg)](tests/)

> **A comprehensive underground bunker management system with real-time environmental monitoring, alert management, and survival coordination.**

## 🌐 Live Demo

**🚀 [Access the Live Application](https://mzhyi8cqmo7w.manus.space)**

## 📖 Overview

Lataupe Bunker Tech is a sophisticated web application designed for managing underground survival bunkers in extreme environmental conditions. The system provides real-time monitoring of environmental parameters, intelligent alert management, and comprehensive survival coordination tools.

### 🎯 Key Features

- **🌡️ Real-time Environmental Monitoring**: Temperature, humidity, air quality, oxygen levels, CO2, radiation
- **🚨 Intelligent Alert System**: Automated threat detection with severity-based prioritization
- **👥 Multi-user Management**: Role-based access control (Admin/Resident)
- **📱 Mobile-First Design**: Responsive interface optimized for all devices
- **🔒 Enterprise Security**: JWT authentication, bcrypt encryption, CORS protection
- **📊 Data Visualization**: Interactive charts and real-time dashboards
- **🌍 Multilingual Support**: English and French translations
- **🎮 Interactive Story Mode**: Immersive survival narrative
- **📈 Comprehensive Logging**: Structured logging with performance monitoring

## 🏗️ Architecture

### Microservices Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │  Environmental  │    │  Alert Service  │
│                 │    │    Service      │    │                 │
│ • JWT Tokens    │    │ • Sensor Data   │    │ • Alert Mgmt    │
│ • User Mgmt     │    │ • Trends        │    │ • Notifications │
│ • Permissions   │    │ • History       │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Logging Service │
                    │                 │
                    │ • Structured    │
                    │ • Performance   │
                    │ • Security      │
                    └─────────────────┘
```

### Technology Stack

**Backend:**
- **Flask 3.1.1** - Web framework
- **SQLAlchemy 2.0.41** - Database ORM
- **PyJWT 2.8.0** - Authentication
- **bcrypt 4.1.2** - Password hashing
- **Gunicorn 23.0.0** - WSGI server

**Frontend:**
- **Vanilla JavaScript** - Enhanced with modern ES6+
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

**Testing:**
- **pytest 7.4.3** - Testing framework
- **pytest-cov 4.1.0** - Coverage reporting
- **pytest-flask 1.3.0** - Flask testing utilities

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kvnbbg/lataupe-bunker-tech.git
   cd lataupe-bunker-tech
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   cd src
   python main_microservices.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5001`
   - Default login: `admin` / `admin123` or `resident` / `resident123`

### Docker Deployment

```bash
# Build the image
docker build -t lataupe-bunker-tech .

# Run the container
docker run -p 8080:8080 lataupe-bunker-tech
```

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Module
```bash
python run_tests.py auth_service
python run_tests.py environmental_service
python run_tests.py alert_service
python run_tests.py integration
```

### Coverage Report
```bash
pytest --cov=src tests/ --cov-report=html
```

## 📊 API Documentation

### Authentication Endpoints
```http
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

### Environmental Monitoring
```http
GET  /api/environmental/current
GET  /api/environmental/history?hours=24
POST /api/environmental/generate
```

### Alert Management
```http
GET  /api/alerts/active
POST /api/alerts/{id}/resolve
GET  /api/alerts/statistics?days=7
```

### System Information
```http
GET  /api/health
GET  /api/system/status
GET  /api/translations?lang=en
GET  /api/story?lang=en
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///bunker.db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# CORS Settings
CORS_ORIGINS=*

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
```

### Default Users
- **Admin**: `admin` / `admin123`
- **Resident**: `resident` / `resident123`

## 📱 Mobile Features

### Touch Interactions
- **Swipe Navigation**: Navigate slides with left/right swipes
- **Pull to Refresh**: Refresh data by pulling down
- **Touch Feedback**: Visual feedback for all interactions
- **Responsive Design**: Optimized for phones, tablets, and desktops

### Mobile-Specific UI
- **Collapsible Menu**: Space-efficient navigation
- **Touch-Friendly Controls**: Larger buttons and touch targets
- **Optimized Forms**: Mobile keyboard support
- **Progressive Loading**: Fast loading with lazy content

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Role-Based Access Control**: Admin and Resident permissions
- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure cookie handling

### Data Protection
- **Input Validation**: Prevents SQL injection and XSS
- **CORS Security**: Controlled cross-origin requests
- **Rate Limiting**: API abuse prevention
- **Audit Logging**: Complete security event tracking

## 📈 Monitoring & Logging

### Structured Logging
```json
{
  "timestamp": "2025-07-09T20:00:16.589240",
  "level": "INFO",
  "message": "Application starting on port 5001",
  "service": "lataupe_bunker_tech",
  "version": "1.0.0",
  "request_id": "req_123456",
  "user_id": "user_789",
  "performance": {
    "duration_ms": 150,
    "memory_mb": 45.2
  }
}
```

### Health Monitoring
- **Application Health**: Real-time status monitoring
- **Database Health**: Connection and performance tracking
- **Service Health**: Individual microservice status
- **Performance Metrics**: Response time and resource usage

## 🎮 Story Mode

Experience the immersive survival narrative with:
- **Interactive Chapters**: Multi-part survival story
- **Background Slides**: Visual storytelling with slide presentations
- **Multilingual Content**: Available in English and French
- **Dynamic Content**: Story adapts to current bunker conditions

## 🌍 Internationalization

### Supported Languages
- **English** (en) - Default
- **French** (fr) - Complete translation

### Adding New Languages
1. Create translation file in `translations/{lang}.json`
2. Add language option to UI
3. Update language switcher component

## 📁 Project Structure

```
lataupe-bunker-tech/
├── src/                          # Source code
│   ├── main.py                   # Application entry point
│   ├── main_microservices.py     # Enhanced microservices app
│   ├── models/                   # Data models
│   │   ├── user.py               # User authentication models
│   │   └── bunker.py             # Bunker-specific models
│   ├── services/                 # Microservices
│   │   ├── auth_service.py       # Authentication service
│   │   ├── environmental_service.py # Environmental monitoring
│   │   ├── alert_service.py      # Alert management
│   │   └── logging_service.py    # Centralized logging
│   └── static/                   # Frontend assets
│       ├── index_enhanced.html   # Enhanced UI
│       ├── app_enhanced.js       # Enhanced frontend logic
│       ├── index.html            # Original UI (legacy)
│       └── app.js                # Original frontend (legacy)
├── tests/                        # Comprehensive test suite
│   ├── test_auth_service.py      # Authentication tests
│   ├── test_environmental_service.py # Environmental tests
│   ├── test_alert_service.py     # Alert tests
│   └── test_integration.py       # Integration tests
├── run_tests.py                  # Test runner with reporting
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── IMPROVEMENTS.md               # Detailed improvement documentation
├── README.md                     # This file
└── venv/                         # Virtual environment
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python run_tests.py`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use ES6+ features
- **Testing**: Maintain 85%+ code coverage
- **Documentation**: Update docs for new features
- **Logging**: Add appropriate logging for new functionality

## 📋 Roadmap

### Version 2.0 (Planned)
- [ ] Real IoT sensor integration
- [ ] WebSocket real-time updates
- [ ] Advanced analytics dashboard
- [ ] Multi-bunker network support
- [ ] Mobile app (React Native)

### Version 2.1 (Future)
- [ ] Machine learning predictive alerts
- [ ] Advanced reporting (PDF/Excel)
- [ ] API rate limiting
- [ ] Redis caching layer
- [ ] Kubernetes deployment

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Database Issues**
```bash
# Reset database
rm bunker.db
python src/main_microservices.py
```

**Port Conflicts**
```bash
# Check for running processes
lsof -i :5001
kill -9 <PID>
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Community** - Excellent web framework
- **Tailwind CSS** - Beautiful utility-first CSS
- **Chart.js** - Powerful data visualization
- **Font Awesome** - Comprehensive icon library
- **pytest** - Robust testing framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Kvnbbg/lataupe-bunker-tech/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Kvnbbg/lataupe-bunker-tech/discussions)
- **Email**: support@lataupe-bunker-tech.com

---

**🌟 Star this repository if you find it useful!**

**🚀 [Try the Live Demo](https://mzhyi8cqmo7w.manus.space)**

