/**
 * Lataupe Bunker Tech - Frontend Application
 * Comprehensive underground survival system with gamification, music, themes, and more
 * Author: Kevin Marville
 * Version: 2.0.0
 */

class LataupeApp {
    constructor() {
        this.currentUser = null;
        this.currentLanguage = 'en';
        this.currentTheme = 'blue-night';
        this.isAuthenticated = false;
        this.environmentalData = {};
        this.alerts = [];
        this.gamificationData = {
            level: 1,
            xp: 250,
            nextLevelXP: 1000,
            badges: []
        };
        this.musicEnabled = true;
        this.audioManager = null;
        this.slideIndex = 0;
        this.totalSlides = 5;
        
        // Initialize the application
        this.init();
    }

    init() {
        console.log('🚀 Initializing Lataupe Bunker Tech...');
        
        // Initialize components
        this.initializeAudioManager();
        this.initializeThemeSystem();
        this.initializeLanguageSystem();
        this.initializeEventListeners();
        this.initializeAnimations();
        this.detectDeviceAndSetDefaultTheme();
        this.loadUserSettings();
        
        // Check if user is already authenticated
        this.checkAuthStatus();
    }

    initializeAudioManager() {
        this.audioManager = {
            backgroundMusic: document.getElementById('backgroundMusic'),
            successSound: document.getElementById('successSound'),
            errorSound: document.getElementById('errorSound'),
            launchSound: document.getElementById('launchSound'),
            victorySound: document.getElementById('victorySound'),
            isMuted: false,
            volume: 0.5
        };

        // Set initial volume
        Object.values(this.audioManager).forEach(audio => {
            if (audio instanceof HTMLAudioElement) {
                audio.volume = this.audioManager.volume;
            }
        });
    }

    initializeThemeSystem() {
        const themeSelector = document.getElementById('themeSelector');
        const savedTheme = localStorage.getItem('lataupe_theme');
        
        if (savedTheme) {
            this.currentTheme = savedTheme;
        }
        
        this.applyTheme(this.currentTheme);
        
        if (themeSelector) {
            themeSelector.value = this.currentTheme;
        }
    }

    initializeLanguageSystem() {
        const languageSelector = document.getElementById('languageSelector');
        const savedLanguage = localStorage.getItem('lataupe_language');
        
        if (savedLanguage) {
            this.currentLanguage = savedLanguage;
        }
        
        this.loadTranslations();
        
        if (languageSelector) {
            languageSelector.value = this.currentLanguage;
        }
    }

    initializeEventListeners() {
        // Authentication forms
        this.setupAuthenticationEvents();
        
        // Theme selector
        const themeSelector = document.getElementById('themeSelector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.changeTheme(e.target.value);
            });
        }

        // Language selector
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }

        // Music player controls
        this.setupMusicPlayerEvents();
        
        // Navigation tabs
        this.setupNavigationEvents();
        
        // Premium upgrade button
        const upgradeBtn = document.getElementById('upgradeBtn');
        if (upgradeBtn) {
            upgradeBtn.addEventListener('click', () => this.handlePremiumUpgrade());
        }

        // Story mode controls
        this.setupStoryModeEvents();

        // Modal events
        this.setupModalEvents();
    }

    setupAuthenticationEvents() {
        // Auth tab switching
        const authTabs = document.querySelectorAll('.auth-tab');
        authTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchAuthTab(e.target.dataset.tab);
            });
        });

        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister();
            });
        }
    }

    setupMusicPlayerEvents() {
        const playPauseBtn = document.getElementById('playPauseBtn');
        const muteBtn = document.getElementById('muteBtn');
        const volumeControl = document.getElementById('volumeControl');

        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.toggleBackgroundMusic());
        }

        if (muteBtn) {
            muteBtn.addEventListener('click', () => this.toggleMute());
        }

        if (volumeControl) {
            volumeControl.addEventListener('input', (e) => {
                this.setVolume(e.target.value / 100);
            });
        }
    }

    setupNavigationEvents() {
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchDashboardSection(e.target.dataset.screen);
            });
        });
    }

    setupStoryModeEvents() {
        const prevSlide = document.getElementById('prevSlide');
        const nextSlide = document.getElementById('nextSlide');

        if (prevSlide) {
            prevSlide.addEventListener('click', () => this.previousSlide());
        }

        if (nextSlide) {
            nextSlide.addEventListener('click', () => this.nextSlide());
        }
    }

    setupModalEvents() {
        const modal = document.getElementById('modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    initializeAnimations() {
        // Initialize AOS (Animate On Scroll)
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true
            });
        }
    }

    detectDeviceAndSetDefaultTheme() {
        // Detect if it's mobile or desktop
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // Default to blue-night theme
        if (!localStorage.getItem('lataupe_theme')) {
            this.currentTheme = 'blue-night';
            localStorage.setItem('lataupe_theme', this.currentTheme);
        }
    }

    // Authentication Methods
    switchAuthTab(tab) {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const authTabs = document.querySelectorAll('.auth-tab');

        authTabs.forEach(t => t.classList.remove('active'));
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        if (tab === 'login') {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        } else {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        }
    }

    async handleLogin() {
        const username = this.sanitizeInput(document.getElementById('loginUsername').value);
        const password = document.getElementById('loginPassword').value;
        const loadingEl = document.getElementById('loginLoading');

        if (!this.validateCredentials(username, password)) {
            this.showErrorAnimation(document.getElementById('loginForm'));
            this.playSound('error');
            return;
        }

        loadingEl.style.display = 'inline-block';

        try {
            const response = await this.apiCall('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            if (response.success) {
                this.currentUser = response.user;
                this.isAuthenticated = true;
                this.showSuccessAnimation(document.getElementById('loginForm'));
                this.playSound('success');
                this.switchToMain();
                this.loadDashboardData();
            } else {
                throw new Error(response.message || 'Login failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
            this.showErrorAnimation(document.getElementById('loginForm'));
            this.playSound('error');
        } finally {
            loadingEl.style.display = 'none';
        }
    }

    async handleRegister() {
        const username = this.sanitizeInput(document.getElementById('registerUsername').value);
        const email = this.sanitizeInput(document.getElementById('registerEmail').value);
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;
        const loadingEl = document.getElementById('registerLoading');

        if (!this.validateRegistration(username, email, password, confirmPassword)) {
            this.showErrorAnimation(document.getElementById('registerForm'));
            this.playSound('error');
            return;
        }

        loadingEl.style.display = 'inline-block';

        try {
            const response = await this.apiCall('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });

            if (response.success) {
                this.showSuccessAnimation(document.getElementById('registerForm'));
                this.playSound('success');
                this.showNotification('Account created successfully! Please login.', 'success');
                this.switchAuthTab('login');
            } else {
                throw new Error(response.message || 'Registration failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
            this.showErrorAnimation(document.getElementById('registerForm'));
            this.playSound('error');
        } finally {
            loadingEl.style.display = 'none';
        }
    }

    // Input Sanitization
    sanitizeInput(input) {
        if (typeof input !== 'string') return '';
        
        return input
            .trim()
            .replace(/[<>'"&]/g, (char) => {
                const entityMap = {
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;',
                    '&': '&amp;'
                };
                return entityMap[char];
            });
    }

    validateCredentials(username, password) {
        if (!username || username.length < 3) {
            this.showNotification('Username must be at least 3 characters', 'error');
            return false;
        }
        if (!password || password.length < 6) {
            this.showNotification('Password must be at least 6 characters', 'error');
            return false;
        }
        return true;
    }

    validateRegistration(username, email, password, confirmPassword) {
        if (!this.validateCredentials(username, password)) return false;
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return false;
        }
        
        if (password !== confirmPassword) {
            this.showNotification('Passwords do not match', 'error');
            return false;
        }
        
        return true;
    }

    // Theme System
    changeTheme(theme) {
        this.currentTheme = theme;
        this.applyTheme(theme);
        localStorage.setItem('lataupe_theme', theme);
        this.playSound('success');
    }

    applyTheme(theme) {
        const body = document.body;
        const themes = ['theme-dark', 'theme-light', 'theme-blue-night', 'theme-cyberpunk'];
        
        // Remove all existing theme classes
        themes.forEach(t => body.classList.remove(t));
        
        // Add new theme class
        body.classList.add(`theme-${theme}`);
    }

    // Language System
    changeLanguage(language) {
        this.currentLanguage = language;
        localStorage.setItem('lataupe_language', language);
        this.loadTranslations();
        this.playSound('success');
    }

    loadTranslations() {
        const translations = this.getTranslations();
        const elements = document.querySelectorAll('[data-translate]');
        
        elements.forEach(element => {
            const key = element.dataset.translate;
            if (translations[this.currentLanguage] && translations[this.currentLanguage][key]) {
                element.textContent = translations[this.currentLanguage][key];
            }
        });
    }

    getTranslations() {
        return {
            en: {
                'app.title': 'Lataupe Bunker Tech',
                'auth.login': 'Login',
                'auth.register': 'Register',
                'auth.username': 'Username',
                'auth.email': 'Email',
                'auth.password': 'Password',
                'auth.confirm_password': 'Confirm Password',
                'nav.dashboard': 'Dashboard',
                'nav.environmental': 'Environmental',
                'nav.alerts': 'Alerts',
                'nav.premium': 'Premium',
                'nav.story': 'Story Mode',
                'gamification.title': 'Your Progress',
                'gamification.level': 'Level',
                'dashboard.temperature': 'Temperature',
                'dashboard.air_quality': 'Air Quality',
                'dashboard.radiation': 'Radiation',
                'dashboard.power': 'Power Level',
                'status.optimal': 'Optimal',
                'status.excellent': 'Excellent',
                'status.safe': 'Safe',
                'status.good': 'Good',
                'alerts.recent': 'Recent Alerts',
                'alerts.title': 'Alert Management',
                'environmental.title': 'Environmental Monitoring',
                'premium.title': 'Upgrade to Premium',
                'premium.description': 'Unlock advanced features and enhanced monitoring capabilities',
                'premium.upgrade': 'Upgrade Now',
                'premium.advanced_analytics': 'Advanced Analytics',
                'premium.analytics_desc': 'Detailed historical data and predictive analysis',
                'premium.custom_alerts': 'Custom Alerts',
                'premium.alerts_desc': 'Personalized alert thresholds and notifications',
                'premium.mobile_access': 'Mobile Access',
                'premium.mobile_desc': 'Full mobile app with offline capabilities',
                'badges.first_login': 'First Login',
                'badges.environmental_monitor': 'Environmental Monitor',
                'badges.alert_responder': 'Alert Responder',
                'badges.premium_member': 'Premium Member',
                'charts.environmental_trends': 'Environmental Trends (24h)',
                'theme.dark': 'Dark',
                'theme.light': 'Light',
                'theme.blue_night': 'Blue Night',
                'theme.cyberpunk': 'Cyberpunk'
            },
            fr: {
                'app.title': 'Lataupe Bunker Tech',
                'auth.login': 'Connexion',
                'auth.register': 'S\'inscrire',
                'auth.username': 'Nom d\'utilisateur',
                'auth.email': 'Email',
                'auth.password': 'Mot de passe',
                'auth.confirm_password': 'Confirmer le mot de passe',
                'nav.dashboard': 'Tableau de bord',
                'nav.environmental': 'Environnemental',
                'nav.alerts': 'Alertes',
                'nav.premium': 'Premium',
                'nav.story': 'Mode Histoire',
                'gamification.title': 'Votre Progression',
                'gamification.level': 'Niveau',
                'dashboard.temperature': 'Température',
                'dashboard.air_quality': 'Qualité de l\'air',
                'dashboard.radiation': 'Radiation',
                'dashboard.power': 'Niveau d\'énergie',
                'status.optimal': 'Optimal',
                'status.excellent': 'Excellent',
                'status.safe': 'Sûr',
                'status.good': 'Bon',
                'alerts.recent': 'Alertes récentes',
                'alerts.title': 'Gestion des alertes',
                'environmental.title': 'Surveillance environnementale',
                'premium.title': 'Passer à Premium',
                'premium.description': 'Débloquez des fonctionnalités avancées et des capacités de surveillance améliorées',
                'premium.upgrade': 'Mettre à niveau maintenant',
                'premium.advanced_analytics': 'Analyses avancées',
                'premium.analytics_desc': 'Données historiques détaillées et analyse prédictive',
                'premium.custom_alerts': 'Alertes personnalisées',
                'premium.alerts_desc': 'Seuils d\'alerte personnalisés et notifications',
                'premium.mobile_access': 'Accès mobile',
                'premium.mobile_desc': 'Application mobile complète avec capacités hors ligne',
                'badges.first_login': 'Première connexion',
                'badges.environmental_monitor': 'Moniteur environnemental',
                'badges.alert_responder': 'Répondeur d\'alerte',
                'badges.premium_member': 'Membre premium',
                'charts.environmental_trends': 'Tendances environnementales (24h)',
                'theme.dark': 'Sombre',
                'theme.light': 'Clair',
                'theme.blue_night': 'Nuit bleue',
                'theme.cyberpunk': 'Cyberpunk'
            }
        };
    }

    // Audio/Music System
    toggleBackgroundMusic() {
        const music = this.audioManager.backgroundMusic;
        const playPauseBtn = document.getElementById('playPauseBtn');
        
        if (music.paused) {
            music.play().catch(e => console.log('Audio play failed:', e));
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            music.pause();
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }

    toggleMute() {
        const muteBtn = document.getElementById('muteBtn');
        this.audioManager.isMuted = !this.audioManager.isMuted;
        
        Object.values(this.audioManager).forEach(audio => {
            if (audio instanceof HTMLAudioElement) {
                audio.muted = this.audioManager.isMuted;
            }
        });
        
        muteBtn.innerHTML = this.audioManager.isMuted ? 
            '<i class="fas fa-volume-mute"></i>' : 
            '<i class="fas fa-volume-up"></i>';
    }

    setVolume(volume) {
        this.audioManager.volume = volume;
        Object.values(this.audioManager).forEach(audio => {
            if (audio instanceof HTMLAudioElement) {
                audio.volume = volume;
            }
        });
    }

    playSound(type) {
        if (!this.musicEnabled || this.audioManager.isMuted) return;
        
        const sound = this.audioManager[`${type}Sound`];
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound play failed:', e));
        }
    }

    // Animation System
    showSuccessAnimation(element) {
        element.classList.add('success-animation');
        setTimeout(() => element.classList.remove('success-animation'), 500);
    }

    showErrorAnimation(element) {
        element.classList.add('error-animation');
        setTimeout(() => element.classList.remove('error-animation'), 500);
    }

    // Navigation System
    switchToMain() {
        document.getElementById('authScreen').classList.remove('active');
        document.getElementById('dashboardScreen').classList.add('active');
        
        // Show user menu
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userNameDisplay = document.getElementById('userNameDisplay');
        
        if (userMenuBtn && userNameDisplay && this.currentUser) {
            userNameDisplay.textContent = this.currentUser.username;
            userMenuBtn.style.display = 'block';
        }
        
        // Start background music
        setTimeout(() => {
            if (!this.audioManager.backgroundMusic.paused === false) {
                this.toggleBackgroundMusic();
            }
        }, 1000);
        
        this.playSound('launch');
    }

    switchDashboardSection(section) {
        // Hide all content sections
        const contents = document.querySelectorAll('.dashboard-content');
        contents.forEach(content => content.style.display = 'none');
        
        // Update nav tabs
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => tab.classList.remove('active'));
        
        // Show selected section
        const targetContent = document.getElementById(`${section}Content`);
        const targetTab = document.querySelector(`[data-screen="${section}"]`);
        
        if (targetContent) {
            targetContent.style.display = 'block';
        }
        
        if (targetTab) {
            targetTab.classList.add('active');
        }
        
        this.playSound('success');
    }

    // Data Management
    async loadDashboardData() {
        try {
            // Load environmental data
            const envResponse = await this.apiCall('/api/environmental/current');
            if (envResponse.success) {
                this.updateEnvironmentalData(envResponse.data);
            }
            
            // Load alerts
            const alertsResponse = await this.apiCall('/api/alerts/active');
            if (alertsResponse.success) {
                this.updateAlertsData(alertsResponse.data);
            }
            
            // Load gamification data
            this.updateGamificationData();
            
            // Initialize charts
            this.initializeEnvironmentalChart();
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showNotification('Failed to load dashboard data', 'error');
        }
    }

    updateEnvironmentalData(data) {
        this.environmentalData = data;
        
        // Update temperature
        const tempElement = document.getElementById('currentTemp');
        if (tempElement && data.temperature) {
            tempElement.textContent = data.temperature.toFixed(1);
        }
        
        // Update air quality
        const airElement = document.getElementById('currentAir');
        if (airElement && data.air_quality) {
            airElement.textContent = Math.round(data.air_quality);
        }
        
        // Update radiation
        const radiationElement = document.getElementById('currentRadiation');
        if (radiationElement && data.radiation) {
            radiationElement.textContent = data.radiation.toFixed(2);
        }
        
        // Update power
        const powerElement = document.getElementById('currentPower');
        if (powerElement && data.power_level) {
            powerElement.textContent = Math.round(data.power_level);
        }
    }

    updateAlertsData(alerts) {
        this.alerts = alerts;
        const alertsList = document.getElementById('alertsList');
        
        if (!alertsList) return;
        
        alertsList.innerHTML = '';
        
        if (alerts.length === 0) {
            alertsList.innerHTML = '<p class="text-gray-400">No active alerts</p>';
            return;
        }
        
        alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert ${alert.severity}`;
            alertElement.innerHTML = `
                <div>
                    <strong>${alert.title}</strong>
                    <p>${alert.message}</p>
                    <small>${new Date(alert.timestamp).toLocaleString()}</small>
                </div>
                <button class="btn btn-secondary btn-sm" onclick="app.dismissAlert('${alert.id}')">
                    Dismiss
                </button>
            `;
            alertsList.appendChild(alertElement);
        });
    }

    updateGamificationData() {
        // Update level
        const levelElement = document.getElementById('userLevel');
        if (levelElement) {
            levelElement.textContent = this.gamificationData.level;
        }
        
        // Update XP
        const currentXPElement = document.getElementById('currentXP');
        const nextLevelXPElement = document.getElementById('nextLevelXP');
        const xpBarElement = document.getElementById('xpBar');
        
        if (currentXPElement) {
            currentXPElement.textContent = this.gamificationData.xp;
        }
        
        if (nextLevelXPElement) {
            nextLevelXPElement.textContent = this.gamificationData.nextLevelXP;
        }
        
        if (xpBarElement) {
            const percentage = (this.gamificationData.xp / this.gamificationData.nextLevelXP) * 100;
            xpBarElement.style.width = `${percentage}%`;
        }
    }

    // Story Mode
    nextSlide() {
        if (this.slideIndex < this.totalSlides - 1) {
            this.slideIndex++;
            this.updateSlide();
            this.playSound('success');
        }
    }

    previousSlide() {
        if (this.slideIndex > 0) {
            this.slideIndex--;
            this.updateSlide();
            this.playSound('success');
        }
    }

    updateSlide() {
        const slides = this.getStorySlides();
        const currentSlide = slides[this.slideIndex];
        
        const titleElement = document.getElementById('slideTitle');
        const textElement = document.getElementById('slideText');
        const indicatorElement = document.getElementById('slideIndicator');
        
        if (titleElement) titleElement.textContent = currentSlide.title;
        if (textElement) textElement.textContent = currentSlide.text;
        if (indicatorElement) indicatorElement.textContent = `${this.slideIndex + 1} / ${this.totalSlides}`;
    }

    getStorySlides() {
        const slides = {
            en: [
                {
                    title: "Welcome to the Underground",
                    text: "The year is 2045. The surface world has become uninhabitable due to environmental collapse. Humanity has retreated underground, and you are the guardian of this bunker..."
                },
                {
                    title: "The Ozone Crisis",
                    text: "The ozone layer has been severely damaged, allowing deadly radiation to reach the surface. Your mission is to monitor environmental conditions and keep everyone safe."
                },
                {
                    title: "Technology Failure",
                    text: "Many surface technologies have failed due to the harsh conditions. You must rely on robust underground systems to survive."
                },
                {
                    title: "Underground Living",
                    text: "Life underground requires careful resource management. Monitor air quality, temperature, and power levels to ensure survival."
                },
                {
                    title: "Your Mission",
                    text: "As the bunker's environmental manager, your decisions will determine the fate of everyone inside. Stay vigilant, stay alive."
                }
            ],
            fr: [
                {
                    title: "Bienvenue dans le souterrain",
                    text: "Nous sommes en 2045. Le monde de surface est devenu inhabitable à cause de l'effondrement environnemental. L'humanité s'est réfugiée sous terre, et vous êtes le gardien de ce bunker..."
                },
                {
                    title: "La crise de l'ozone",
                    text: "La couche d'ozone a été gravement endommagée, permettant aux radiations mortelles d'atteindre la surface. Votre mission est de surveiller les conditions environnementales et de garder tout le monde en sécurité."
                },
                {
                    title: "Défaillance technologique",
                    text: "De nombreuses technologies de surface ont échoué en raison des conditions difficiles. Vous devez compter sur des systèmes souterrains robustes pour survivre."
                },
                {
                    title: "Vie souterraine",
                    text: "La vie souterraine nécessite une gestion minutieuse des ressources. Surveillez la qualité de l'air, la température et les niveaux d'énergie pour assurer la survie."
                },
                {
                    title: "Votre mission",
                    text: "En tant que gestionnaire environnemental du bunker, vos décisions détermineront le sort de tous ceux qui s'y trouvent. Restez vigilant, restez en vie."
                }
            ]
        };
        
        return slides[this.currentLanguage] || slides.en;
    }

    // Premium Features
    async handlePremiumUpgrade() {
        try {
            this.showModal(`
                <h3>Upgrade to Premium</h3>
                <p>Unlock advanced features:</p>
                <ul>
                    <li>Advanced analytics and predictions</li>
                    <li>Custom alert thresholds</li>
                    <li>Mobile app access</li>
                    <li>Priority support</li>
                    <li>Enhanced gamification</li>
                </ul>
                <div style="margin: 2rem 0;">
                    <button class="btn btn-primary" onclick="app.redirectToStripe()">
                        Upgrade for $9.99/month
                    </button>
                    <button class="btn btn-secondary" onclick="app.closeModal()">
                        Maybe later
                    </button>
                </div>
            `);
        } catch (error) {
            this.showNotification('Unable to load premium features', 'error');
        }
    }

    redirectToStripe() {
        // This would redirect to Stripe checkout
        window.open('https://checkout.stripe.com/c/pay/cs_live_b1UPk4dQH9c2uMFQZDaLsqPZfgF8I0rJHWGKzP1Gx85xPuOLhAvGnO6eK#fidkdWxOYHwnPyd1blppbHNgWjA0SX1pUWZPTGRpPTZLSGJ0b19sVUJtUTVfNzZCa0p8Q1I2ZGdBMTViQEpKNE52Ync8X2ZAZ2o2M3F2YnBkQ1Y9XWNfX05SbEFQPFVJNHFsPEFQVzBGQ0FXf1Y3N3M3cScpJ3VpbGtuQH11anZgYUxhJz8ncWB2cVdeaydomGhkZW1tYXBrcUNhKE01MnxnS1RxY3RLSktoY1xfZz90', '_blank');
        this.closeModal();
    }

    // Modal System
    showModal(content) {
        const modal = document.getElementById('modal');
        const modalContent = document.getElementById('modalContent');
        
        if (modal && modalContent) {
            modalContent.innerHTML = content;
            modal.classList.add('show');
        }
    }

    closeModal() {
        const modal = document.getElementById('modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    // Notification System
    showNotification(message, type = 'info') {
        // Create notification if it doesn't exist
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'fixed top-4 right-4 z-50 hidden';
            document.body.appendChild(notification);
        }
        
        notification.innerHTML = `
            <div class="p-4 rounded-lg shadow-lg ${
                type === 'error' ? 'bg-red-600' : 
                type === 'success' ? 'bg-green-600' : 
                'bg-blue-600'
            } text-white">
                ${message}
            </div>
        `;
        
        notification.classList.remove('hidden');
        
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 5000);
    }

    // Chart Initialization
    initializeEnvironmentalChart() {
        const canvas = document.getElementById('environmentalChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Generate sample data for the last 24 hours
        const hours = [];
        const temperatures = [];
        const airQuality = [];
        
        for (let i = 23; i >= 0; i--) {
            const hour = new Date();
            hour.setHours(hour.getHours() - i);
            hours.push(hour.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
            temperatures.push(20 + Math.random() * 10); // 20-30°C
            airQuality.push(80 + Math.random() * 20); // 80-100%
        }
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: '#4299e1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Air Quality (%)',
                    data: airQuality,
                    borderColor: '#48bb78',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    // Utility Methods
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': this.currentUser ? `Bearer ${this.currentUser.token}` : ''
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(endpoint, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'API call failed');
            }
            
            return data;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    checkAuthStatus() {
        const savedUser = localStorage.getItem('lataupe_user');
        if (savedUser) {
            try {
                this.currentUser = JSON.parse(savedUser);
                this.isAuthenticated = true;
                this.switchToMain();
                this.loadDashboardData();
            } catch (error) {
                localStorage.removeItem('lataupe_user');
            }
        }
    }

    loadUserSettings() {
        const settings = localStorage.getItem('lataupe_settings');
        if (settings) {
            try {
                const parsed = JSON.parse(settings);
                this.musicEnabled = parsed.musicEnabled !== false;
                if (parsed.volume !== undefined) {
                    this.audioManager.volume = parsed.volume;
                    this.setVolume(parsed.volume);
                }
            } catch (error) {
                console.error('Failed to load user settings:', error);
            }
        }
    }

    saveUserSettings() {
        const settings = {
            musicEnabled: this.musicEnabled,
            volume: this.audioManager.volume
        };
        localStorage.setItem('lataupe_settings', JSON.stringify(settings));
    }

    async dismissAlert(alertId) {
        try {
            await this.apiCall(`/api/alerts/${alertId}/dismiss`, { method: 'POST' });
            this.alerts = this.alerts.filter(alert => alert.id !== alertId);
            this.updateAlertsData(this.alerts);
            this.playSound('success');
        } catch (error) {
            this.showNotification('Failed to dismiss alert', 'error');
        }
    }
}

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new LataupeApp();
});

// Export for global access
window.app = app;
class BunkerApp {
    constructor() {
        this.currentUser = null;
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        // Vérifier le statut d'authentification au chargement
        await this.checkAuthStatus();
        
        // Initialiser les événements
        this.setupEventListeners();
        
        // Démarrer le rafraîchissement automatique si connecté
        if (this.currentUser) {
            this.startAutoRefresh();
        }
    }

    setupEventListeners() {
        // Navigation mobile
        document.addEventListener('DOMContentLoaded', () => {
            // Gestion responsive de la navigation
            const navButtons = document.querySelectorAll('.nav-btn');
            navButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    navButtons.forEach(b => b.classList.remove('bg-white', 'bg-opacity-20'));
                    e.target.classList.add('bg-white', 'bg-opacity-20');
                });
            });
        });
    }

    // === AUTHENTIFICATION ===
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.authenticated) {
                this.currentUser = data.user;
                this.showMainContent();
                this.updateUserInfo();
                await this.loadDashboard();
            } else {
                this.showLoginSection();
            }
        } catch (error) {
            console.error('Erreur lors de la vérification du statut:', error);
            this.showLoginSection();
        }
    }

    async login(event) {
        event.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentUser = data.user;
                this.showNotification('Connexion réussie', 'success');
                this.showMainContent();
                this.updateUserInfo();
                await this.loadDashboard();
                this.startAutoRefresh();
            } else {
                this.showNotification(data.error || 'Erreur de connexion', 'error');
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
            this.showNotification('Erreur de connexion au serveur', 'error');
        }
    }

    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            
            this.currentUser = null;
            this.stopAutoRefresh();
            this.showLoginSection();
            this.showNotification('Déconnexion réussie', 'success');
        } catch (error) {
            console.error('Erreur de déconnexion:', error);
        }
    }

    // === INTERFACE UTILISATEUR ===
    showLoginSection() {
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('main-content').classList.add('hidden');
    }

    showMainContent() {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('main-content').classList.remove('hidden');
        this.showSection('dashboard');
    }

    showSection(sectionName) {
        // Cacher toutes les sections
        const sections = ['dashboard-section', 'alerts-section', 'emergency-section'];
        sections.forEach(section => {
            document.getElementById(section).classList.add('hidden');
        });
        
        // Afficher la section demandée
        document.getElementById(sectionName + '-section').classList.remove('hidden');
        
        // Charger les données de la section
        switch(sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'alerts':
                this.loadAlerts();
                break;
            case 'emergency':
                this.loadMessages();
                break;
        }
    }

    updateUserInfo() {
        if (this.currentUser) {
            document.getElementById('user-info').textContent = 
                `${this.currentUser.username} (${this.currentUser.role})`;
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const content = document.getElementById('notification-content');
        
        content.textContent = message;
        
        // Couleurs selon le type
        const colors = {
            success: 'bg-green-600 border-green-500',
            error: 'bg-red-600 border-red-500',
            warning: 'bg-yellow-600 border-yellow-500',
            info: 'bg-blue-600 border-blue-500'
        };
        
        notification.className = `fixed top-4 right-4 z-50 ${colors[type] || colors.info} rounded-lg p-4 shadow-lg max-w-sm`;
        notification.classList.remove('hidden');
        
        // Masquer après 5 secondes
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 5000);
    }

    // === TABLEAU DE BORD ===
    async loadDashboard() {
        try {
            await Promise.all([
                this.loadSystemStatus(),
                this.loadEnvironmentalData(),
                this.loadActiveAlerts()
            ]);
        } catch (error) {
            console.error('Erreur lors du chargement du tableau de bord:', error);
            this.showNotification('Erreur lors du chargement des données', 'error');
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/dashboard/system-status', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (response.ok) {
                this.updateSystemStatus(data);
            }
        } catch (error) {
            console.error('Erreur lors du chargement du statut système:', error);
        }
    }

    updateSystemStatus(status) {
        const statusElement = document.getElementById('system-status');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('span:last-child');
        
        // Mise à jour de l'indicateur de statut
        indicator.className = 'status-indicator';
        switch(status.system_status) {
            case 'normal':
                indicator.classList.add('status-normal');
                text.textContent = 'Système Opérationnel';
                text.className = 'text-green-400 font-medium';
                break;
            case 'warning':
                indicator.classList.add('status-warning');
                text.textContent = 'Attention Requise';
                text.className = 'text-yellow-400 font-medium';
                break;
            case 'critical':
                indicator.classList.add('status-critical');
                text.textContent = 'Situation Critique';
                text.className = 'text-red-400 font-medium pulse-animation';
                break;
        }
        
        // Mise à jour des informations
        document.getElementById('last-update').textContent = 
            status.last_data_update ? new Date(status.last_data_update).toLocaleString('fr-FR') : 'Aucune';
        document.getElementById('critical-alerts-count').textContent = status.critical_alerts;
        
        const freshnessElement = document.getElementById('data-freshness');
        switch(status.data_freshness) {
            case 'fresh':
                freshnessElement.textContent = 'Récentes';
                freshnessElement.className = 'text-lg font-semibold text-green-400';
                break;
            case 'stale':
                freshnessElement.textContent = 'Anciennes';
                freshnessElement.className = 'text-lg font-semibold text-yellow-400';
                break;
            case 'outdated':
                freshnessElement.textContent = 'Obsolètes';
                freshnessElement.className = 'text-lg font-semibold text-red-400';
                break;
        }
    }

    async loadEnvironmentalData() {
        try {
            const response = await fetch('/api/dashboard/environmental-data/current', {
                credentials: 'include'
            });
            const result = await response.json();
            
            if (response.ok) {
                this.updateEnvironmentalDisplay(result.data, result.trends);
                await this.updateCharts();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des données environnementales:', error);
        }
    }

    updateEnvironmentalDisplay(data, trends) {
        // Mise à jour des valeurs
        document.getElementById('temperature-value').textContent = `${data.temperature}°C`;
        document.getElementById('humidity-value').textContent = `${data.humidity}%`;
        document.getElementById('air-quality-value').textContent = `${data.air_quality}/100`;
        document.getElementById('oxygen-value').textContent = `${data.oxygen_level}%`;
        document.getElementById('co2-value').textContent = `${data.co2_level} PPM`;
        
        // Mise à jour des tendances
        this.updateTrend('temperature-trend', trends.temperature);
        this.updateTrend('humidity-trend', trends.humidity);
        this.updateTrend('air-quality-trend', trends.air_quality);
        this.updateTrend('oxygen-trend', trends.oxygen_level);
        this.updateTrend('co2-trend', trends.co2_level);
    }

    updateTrend(elementId, trend) {
        const element = document.getElementById(elementId);
        const icons = {
            up: '📈 En hausse',
            down: '📉 En baisse',
            stable: '➡️ Stable'
        };
        
        const colors = {
            up: 'text-red-400',
            down: 'text-blue-400',
            stable: 'text-gray-400'
        };
        
        element.textContent = icons[trend] || '❓ Inconnu';
        element.className = `text-xs mt-1 ${colors[trend] || 'text-gray-400'}`;
    }

    async updateCharts() {
        try {
            const response = await fetch('/api/dashboard/environmental-data?hours=24', {
                credentials: 'include'
            });
            const result = await response.json();
            
            if (response.ok && result.data.length > 0) {
                this.createTemperatureHumidityChart(result.data);
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour des graphiques:', error);
        }
    }

    createTemperatureHumidityChart(data) {
        const ctx = document.getElementById('temp-humidity-chart').getContext('2d');
        
        // Destruction du graphique existant
        if (this.charts.tempHumidity) {
            this.charts.tempHumidity.destroy();
        }
        
        const labels = data.slice(-20).map(d => new Date(d.timestamp).toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'}));
        const temperatures = data.slice(-20).map(d => d.temperature);
        const humidities = data.slice(-20).map(d => d.humidity);
        
        this.charts.tempHumidity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Température (°C)',
                    data: temperatures,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: 'Humidité (%)',
                    data: humidities,
                    borderColor: 'rgb(6, 182, 212)',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: {
                            color: 'rgb(59, 130, 246)'
                        },
                        grid: {
                            color: 'rgba(59, 130, 246, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: {
                            color: 'rgb(6, 182, 212)'
                        },
                        grid: {
                            drawOnChartArea: false,
                            color: 'rgba(6, 182, 212, 0.1)'
                        }
                    }
                }
            }
        });
    }

    // === ALERTES ===
    async loadAlerts() {
        try {
            const response = await fetch('/api/dashboard/alerts/active', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (response.ok) {
                this.updateAlertsDisplay(data);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des alertes:', error);
        }
    }

    async loadActiveAlerts() {
        try {
            const response = await fetch('/api/dashboard/alerts/active', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('active-alerts-count').textContent = data.count;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des alertes actives:', error);
        }
    }

    updateAlertsDisplay(data) {
        // Mise à jour des compteurs
        document.getElementById('critical-count').textContent = data.summary.critical;
        document.getElementById('high-count').textContent = data.summary.high;
        document.getElementById('medium-count').textContent = data.summary.medium;
        document.getElementById('low-count').textContent = data.summary.low;
        
        // Mise à jour de la liste des alertes
        const alertsList = document.getElementById('alerts-list');
        alertsList.innerHTML = '';
        
        if (data.alerts.length === 0) {
            alertsList.innerHTML = '<div class="text-center text-gray-400 py-8">Aucune alerte active</div>';
            return;
        }
        
        data.alerts.forEach(alert => {
            const alertElement = this.createAlertElement(alert);
            alertsList.appendChild(alertElement);
        });
    }

    createAlertElement(alert) {
        const div = document.createElement('div');
        div.className = 'bg-gray-800 bg-opacity-50 rounded-lg p-4 fade-in';
        
        const severityColors = {
            critical: 'text-red-400 bg-red-900',
            high: 'text-orange-400 bg-orange-900',
            medium: 'text-yellow-400 bg-yellow-900',
            low: 'text-blue-400 bg-blue-900'
        };
        
        const severityColor = severityColors[alert.severity] || 'text-gray-400 bg-gray-900';
        
        div.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <div class="flex items-center mb-2">
                        <span class="px-2 py-1 rounded text-xs font-medium ${severityColor} bg-opacity-50">
                            ${alert.severity.toUpperCase()}
                        </span>
                        <span class="ml-2 text-sm text-gray-400">
                            ${new Date(alert.timestamp).toLocaleString('fr-FR')}
                        </span>
                    </div>
                    <div class="text-white font-medium mb-1">${alert.alert_type.replace('_', ' ').toUpperCase()}</div>
                    <div class="text-gray-300 text-sm">${alert.message}</div>
                    ${alert.value !== null ? `<div class="text-xs text-gray-400 mt-1">Valeur: ${alert.value} (Seuil: ${alert.threshold})</div>` : ''}
                </div>
                <button onclick="app.resolveAlert(${alert.id})" 
                        class="ml-4 bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm text-white transition-colors">
                    Résoudre
                </button>
            </div>
        `;
        
        return div;
    }

    async resolveAlert(alertId) {
        try {
            const response = await fetch(`/api/dashboard/alerts/${alertId}/resolve`, {
                method: 'POST',
                credentials: 'include'
            });
            
            if (response.ok) {
                this.showNotification('Alerte résolue avec succès', 'success');
                await this.loadAlerts();
                await this.loadSystemStatus();
            } else {
                const data = await response.json();
                this.showNotification(data.error || 'Erreur lors de la résolution', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la résolution de l\'alerte:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    // === MESSAGES D'URGENCE ===
    async loadMessages() {
        try {
            const response = await fetch('/api/emergency/messages?sender_only=true', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (response.ok) {
                this.updateMessagesDisplay(data.messages);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des messages:', error);
        }
    }

    updateMessagesDisplay(messages) {
        const messagesList = document.getElementById('messages-list');
        messagesList.innerHTML = '';
        
        if (messages.length === 0) {
            messagesList.innerHTML = '<div class="text-center text-gray-400 py-4">Aucun message envoyé</div>';
            return;
        }
        
        messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            messagesList.appendChild(messageElement);
        });
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = 'bg-gray-800 bg-opacity-50 rounded-lg p-3 fade-in';
        
        const statusColors = {
            sent: 'text-green-400',
            pending: 'text-yellow-400',
            failed: 'text-red-400'
        };
        
        const statusIcons = {
            sent: '✅',
            pending: '⏳',
            failed: '❌'
        };
        
        div.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <div class="text-sm font-medium text-white">${message.message_type.toUpperCase()}</div>
                <div class="flex items-center">
                    <span class="${statusColors[message.status]} text-sm">
                        ${statusIcons[message.status]} ${message.status.toUpperCase()}
                    </span>
                </div>
            </div>
            <div class="text-xs text-gray-400 mb-1">
                À: ${message.recipient} | ${new Date(message.timestamp).toLocaleString('fr-FR')}
            </div>
            ${message.subject ? `<div class="text-sm text-gray-300 font-medium mb-1">${message.subject}</div>` : ''}
            <div class="text-sm text-gray-300">${message.content.substring(0, 100)}${message.content.length > 100 ? '...' : ''}</div>
            ${message.status === 'failed' && message.error_message ? 
                `<div class="text-xs text-red-400 mt-1">Erreur: ${message.error_message}</div>` : ''}
        `;
        
        return div;
    }

    async sendEmergencyMessage(event) {
        event.preventDefault();
        
        const messageType = document.getElementById('message-type').value;
        const recipient = document.getElementById('recipient').value;
        const subject = document.getElementById('message-subject').value;
        const content = document.getElementById('message-content').value;
        
        try {
            const response = await fetch('/api/emergency/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    message_type: messageType,
                    recipient: recipient,
                    subject: subject || null,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Message d\'urgence envoyé', 'success');
                // Réinitialiser le formulaire
                event.target.reset();
                // Recharger la liste des messages
                await this.loadMessages();
            } else {
                this.showNotification(data.error || 'Erreur lors de l\'envoi', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de l\'envoi du message:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    // === ACTIONS ===
    async refreshData() {
        this.showNotification('Actualisation des données...', 'info');
        await this.loadDashboard();
        this.showNotification('Données actualisées', 'success');
    }

    async generateTestData() {
        try {
            const response = await fetch('/api/dashboard/environmental-data/generate', {
                method: 'POST',
                credentials: 'include'
            });
            
            if (response.ok) {
                this.showNotification('Données de test générées', 'success');
                await this.loadDashboard();
            } else {
                const data = await response.json();
                this.showNotification(data.error || 'Erreur lors de la génération', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la génération:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    async simulateEmergency(scenario) {
        try {
            const response = await fetch('/api/dashboard/environmental-data/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ scenario: scenario })
            });
            
            if (response.ok) {
                this.showNotification(`Scénario d'urgence simulé: ${scenario}`, 'warning');
                await this.loadDashboard();
            } else {
                const data = await response.json();
                this.showNotification(data.error || 'Erreur lors de la simulation', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la simulation:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    async refreshAlerts() {
        await this.loadAlerts();
        this.showNotification('Alertes actualisées', 'success');
    }

    async refreshMessages() {
        await this.loadMessages();
        this.showNotification('Messages actualisés', 'success');
    }

    // === RAFRAÎCHISSEMENT AUTOMATIQUE ===
    startAutoRefresh() {
        // Rafraîchissement toutes les 30 secondes
        this.refreshInterval = setInterval(async () => {
            if (document.getElementById('dashboard-section').classList.contains('hidden') === false) {
                await this.loadEnvironmentalData();
                await this.loadSystemStatus();
            }
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialisation de l'application
const app = new BunkerApp();

// Fonctions globales pour les événements HTML
function login(event) {
    app.login(event);
}

function logout() {
    app.logout();
}

function showSection(section) {
    app.showSection(section);
}

function refreshData() {
    app.refreshData();
}

function generateTestData() {
    app.generateTestData();
}

function simulateEmergency(scenario) {
    app.simulateEmergency(scenario);
}

function refreshAlerts() {
    app.refreshAlerts();
}

function refreshMessages() {
    app.refreshMessages();
}

function sendEmergencyMessage(event) {
    app.sendEmergencyMessage(event);
}

