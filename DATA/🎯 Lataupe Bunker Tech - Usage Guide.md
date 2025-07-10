# 🎯 Lataupe Bunker Tech - Usage Guide

## 🚀 Quick Start (30 seconds)

### **Step 1: Download & Run**
```bash
# Download the integrated application
curl -O https://raw.githubusercontent.com/your-repo/lataupe_integrated_app.py

# Run immediately (auto-installs dependencies)
python3 lataupe_integrated_app.py
```

### **Step 2: Access the Application**
```
🌐 Open: http://localhost:5001
👤 Login: admin / admin123 (or resident / resident123)
```

### **Step 3: Explore Features**
- **Dashboard**: Real-time environmental monitoring
- **Alerts**: Active system alerts and warnings
- **Premium**: Upgrade options and Stripe integration
- **Telegram**: Web app integration for mobile

## 📱 **User Interface Guide**

### **Main Dashboard**
```
┌─────────────────────────────────────────┐
│ 🏠 Lataupe Bunker Tech                 │
├─────────────────────────────────────────┤
│ Temperature: 22.1°C  │ Oxygen: 20.8%    │
│ Radiation: 0.2 mSv/h │ Alerts: 0        │
├─────────────────────────────────────────┤
│ [Environmental Chart] [Status Chart]    │
├─────────────────────────────────────────┤
│ Premium Tiers: Free | Pro+ | Ultra      │
└─────────────────────────────────────────┘
```

### **Mobile Interface**
- **Swipe Navigation**: Left/right to navigate sections
- **Pull to Refresh**: Pull down to update data
- **Touch Menu**: Tap hamburger menu for navigation
- **Responsive Cards**: Auto-adjusting layout

## 🔐 **Authentication Flow**

### **Login Process**
1. **Access**: Navigate to the main page
2. **Click Login**: Use the login button in navigation
3. **Enter Credentials**: Use default or create new account
4. **JWT Token**: Automatically managed for API access

### **User Roles**
```
Admin (admin/admin123):
✅ Full system access
✅ Premium Ultra features
✅ Alert management
✅ System configuration

Resident (resident/resident123):
✅ Basic monitoring
✅ Personal alerts
✅ Free tier features
❌ System administration
```

## 📊 **Environmental Monitoring**

### **Real-time Data**
The system monitors these parameters:
- **Temperature**: Optimal range 18-24°C
- **Humidity**: Target 40-60%
- **Oxygen Level**: Critical below 18%
- **CO2 Level**: Warning above 1000 ppm
- **Radiation**: Alert above 1.0 mSv/h
- **Air Quality**: Index 0-300

### **Alert Thresholds**
```
🟢 Normal: All parameters within safe ranges
🟡 Warning: One parameter approaching limits
🔴 Critical: Multiple parameters dangerous
🚨 Emergency: Life-threatening conditions
```

## 💰 **Premium Features**

### **Tier Comparison**
```
Free (€0/month):
- Basic monitoring
- Standard alerts
- Community support

Taupe Pro+ (€3/month):
- Beta access
- Priority requests
- Advanced tools
- Premium support

Taupe Ultra (€27/month):
- All Pro+ features
- Secret tools
- VIP status
- Personal mention
```

### **Upgrade Process**
1. **Click Premium**: Navigate to premium section
2. **Select Tier**: Choose your preferred tier
3. **Stripe Payment**: Secure payment via Stripe
4. **Instant Access**: Features unlock immediately

## 🤖 **Telegram Integration**

### **Music Bunker Bot**
```
🎵 Bot: @musicbunkerbot
🌐 Web App: /api/telegram/webapp
📱 Features:
   - Real-time bunker status
   - Quick alerts
   - Premium upgrade
   - Music streaming
```

### **Web App Usage**
1. **Open Telegram**: Start @musicbunkerbot
2. **Launch Web App**: Tap the web app button
3. **View Status**: See real-time bunker data
4. **Interact**: Use touch gestures for navigation

## 🔧 **API Usage**

### **Authentication**
```bash
# Login to get JWT token
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5001/api/premium/status
```

### **Common Endpoints**
```bash
# Health check
curl http://localhost:5001/api/health

# Current environmental data
curl http://localhost:5001/api/environmental/current

# Active alerts
curl http://localhost:5001/api/alerts/active

# Premium tiers
curl http://localhost:5001/api/premium/tiers

# Run tests
curl http://localhost:5001/api/test/run
```

## 🧪 **Testing & Development**

### **Run Tests**
```bash
# Command line testing
python3 lataupe_integrated_app.py --test

# API testing
curl http://localhost:5001/api/test/run

# Expected output:
# test_authentication ... ok
# test_environmental_data ... ok  
# test_health_check ... ok
# test_premium_features ... ok
# Ran 4 tests in 0.694s - OK
```

### **Development Mode**
```bash
# Enable debug mode
export ENVIRONMENT=development
python3 lataupe_integrated_app.py

# Features:
# - Auto-reload on changes
# - Detailed error messages
# - Debug toolbar
# - Verbose logging
```

## 🚀 **Deployment Guide**

### **Railway (Recommended)**
```bash
# One-click deployment
https://railway.com/deploy/lzsD1L?referralCode=74Ni9C

# Manual deployment
1. Fork the repository
2. Connect to Railway
3. Deploy automatically
4. Access via provided URL
```

### **Docker Deployment**
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
COPY lataupe_integrated_app.py /app/
WORKDIR /app
RUN pip install Flask Flask-SQLAlchemy Flask-CORS PyJWT bcrypt
EXPOSE 5001
CMD ["python3", "lataupe_integrated_app.py"]
EOF

# Build and run
docker build -t lataupe-bunker .
docker run -p 5001:5001 lataupe-bunker
```

### **Heroku Deployment**
```bash
# Create required files
echo "web: python3 lataupe_integrated_app.py" > Procfile
echo "Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-CORS==6.0.0
PyJWT==2.8.0
bcrypt==4.1.2" > requirements.txt

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Required for production
export SECRET_KEY="your-super-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"
export ENVIRONMENT="production"

# Optional configurations
export DATABASE_URL="sqlite:///bunker.db"
export CORS_ORIGINS="https://yourdomain.com"
export PORT="5001"
```

### **Database Configuration**
```python
# SQLite (default)
DATABASE_URL = "sqlite:///lataupe_bunker.db"

# PostgreSQL (production)
DATABASE_URL = "postgresql://user:pass@host:port/db"

# MySQL (alternative)
DATABASE_URL = "mysql://user:pass@host:port/db"
```

## 📊 **Monitoring & Logs**

### **Log Files**
```bash
# Application logs
tail -f lataupe_bunker.log

# Structured JSON format
{
  "timestamp": "2025-07-09T23:39:02.227573",
  "level": "INFO",
  "message": "Health check completed",
  "service": "lataupe_bunker_tech",
  "version": "2.0.0"
}
```

### **Health Monitoring**
```bash
# Health check endpoint
curl http://localhost:5001/api/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-07-09T23:39:02.227573Z",
  "version": "2.0.0",
  "environment": "development",
  "database": "connected",
  "services": {
    "auth": "operational",
    "environmental": "operational", 
    "alerts": "operational",
    "logging": "operational",
    "premium": "operational"
  }
}
```

## 🔒 **Security Best Practices**

### **Production Security**
```bash
# Use strong secrets
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Enable HTTPS
export HTTPS=true

# Restrict CORS
export CORS_ORIGINS="https://yourdomain.com"

# Use secure database
export DATABASE_URL="postgresql://..."
```

### **User Management**
```bash
# Change default passwords immediately
# Create strong admin credentials
# Use role-based access control
# Monitor authentication logs
```

## 🎯 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use different port
export PORT=5002
```

#### **Database Issues**
```bash
# Reset database
rm lataupe_bunker.db
python3 lataupe_integrated_app.py

# Check database connectivity
curl http://localhost:5001/api/health
```

#### **Import Errors**
```bash
# Install missing dependencies
pip3 install Flask Flask-SQLAlchemy Flask-CORS PyJWT bcrypt

# Or let the app auto-install
python3 lataupe_integrated_app.py
```

#### **Permission Errors**
```bash
# Fix file permissions
chmod +x lataupe_integrated_app.py

# Run with proper permissions
sudo python3 lataupe_integrated_app.py
```

### **Debug Mode**
```bash
# Enable verbose logging
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG

# Run with debug output
python3 lataupe_integrated_app.py
```

## 📱 **Mobile Usage**

### **Touch Gestures**
- **Swipe Left/Right**: Navigate between sections
- **Pull Down**: Refresh data
- **Tap**: Select items
- **Long Press**: Context menu (where available)

### **Mobile Menu**
```
☰ Hamburger Menu:
├── Dashboard
├── Environmental  
├── Alerts
├── Premium
└── Settings
```

### **Responsive Breakpoints**
- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 1024px (two columns)
- **Desktop**: > 1024px (full layout)

## 🌐 **Social Integration**

### **Share Features**
```html
<!-- Embedded share buttons -->
<meta property="og:title" content="La Taupe Bunker Premium" />
<meta property="og:description" content="Underground survival system" />
<meta property="og:image" content="banner.jpg" />

<!-- Twitter card -->
<meta name="twitter:card" content="summary_large_image" />
```

### **Social Links**
- **All Links**: https://allmylinks.com/kevinmarville
- **GitHub**: https://github.com/Kvnbbg/
- **Telegram**: https://t.me/kevinmarville
- **Matrix**: https://matrix.to/#/@kvnbbg:matrix.org

## 💡 **Tips & Tricks**

### **Performance Optimization**
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 lataupe_integrated_app:app

# Enable caching
export CACHE_ENABLED=true

# Optimize database
export SQLALCHEMY_ENGINE_OPTIONS='{"pool_pre_ping": true}'
```

### **Customization**
```python
# Modify premium tiers
PREMIUM_TIERS = {
    'custom': {
        'name': 'Custom Tier',
        'price': 5.00,
        'features': ['Custom feature 1', 'Custom feature 2']
    }
}

# Add custom routes
@app.route('/api/custom')
def custom_endpoint():
    return jsonify({'message': 'Custom functionality'})
```

### **Integration Examples**
```javascript
// Frontend integration
fetch('/api/environmental/current')
  .then(response => response.json())
  .then(data => updateDashboard(data));

// Telegram bot integration
window.Telegram.WebApp.ready();
window.Telegram.WebApp.expand();
```

## 📞 **Support & Community**

### **Getting Help**
1. **Documentation**: Read this guide thoroughly
2. **GitHub Issues**: Report bugs or request features
3. **Telegram**: Join the community chat
4. **Email**: Contact via GitHub profile

### **Contributing**
1. **Fork**: Fork the repository
2. **Branch**: Create feature branch
3. **Test**: Run the test suite
4. **Submit**: Create pull request

### **Community Resources**
- **Telegram Group**: @lataupebunkertech
- **GitHub Discussions**: Community forum
- **Wiki**: Extended documentation
- **Blog**: Updates and tutorials

---

**🎉 You're now ready to use the Lataupe Bunker Tech integrated application! Enjoy exploring the underground survival system!**

