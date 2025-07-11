// Lataupe Bunker Tech - Enhanced UI/UX Application
// Enterprise-grade microservices architecture with security and monitoring

class BunkerTechApp {
    constructor() {
        this.currentUser = null;
        this.currentLanguage = 'en';
        this.currentSection = 'dashboard';
        this.translations = {};
        this.storyData = {};
        this.environmentalChart = null;
        this.backgroundSlides = ['vanishing_shield', 'scorched_earth', 'underground_living', 'technology_failure', 'call_to_action'];
        this.currentSlideIndex = 0;
        this.slideInterval = null;
        
        this.init();
    }

    async init() {
        console.log('🏠 Initializing Lataupe Bunker Tech...');
        
        // Load translations and story data
        await this.loadTranslations();
        await this.loadStoryData();
        
        // Check authentication status
        await this.checkAuthStatus();
        
        // Start background slide rotation
        this.startSlideRotation();
        
        // Initialize real-time monitoring
        this.startRealTimeMonitoring();
        
        console.log('✅ Application initialized successfully');
    }

    // Authentication & Security
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.authenticated) {
                this.currentUser = data.user;
                this.showMainApp();
                await this.loadDashboardData();
            } else {
                this.showLoginScreen();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.showLoginScreen();
        }
    }

    async login(event) {
        event.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const loginBtn = event.target.querySelector('button[type="submit"]');
        const loginText = document.getElementById('loginText');
        const loginLoading = document.getElementById('loginLoading');
        const errorDiv = document.getElementById('loginError');
        
        // Show loading state
        loginText.classList.add('hidden');
        loginLoading.classList.remove('hidden');
        loginBtn.disabled = true;
        errorDiv.classList.add('hidden');
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentUser = data.user;
                this.showMainApp();
                await this.loadDashboardData();
                this.showSuccessMessage('Login successful! Welcome to the bunker.');
            } else {
                this.showError(errorDiv, data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError(errorDiv, 'Network error. Please try again.');
        } finally {
            // Reset loading state
            loginText.classList.remove('hidden');
            loginLoading.classList.add('hidden');
            loginBtn.disabled = false;
        }
    }

    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            
            this.currentUser = null;
            this.showLoginScreen();
            this.showSuccessMessage('Logged out successfully');
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    // Language & Internationalization
    async loadTranslations() {
        try {
            const response = await fetch(`/api/translations?lang=${this.currentLanguage}`);
            this.translations = await response.json();
            this.updateUITranslations();
        } catch (error) {
            console.error('Failed to load translations:', error);
        }
    }

    async switchLanguage(lang) {
        this.currentLanguage = lang;
        
        // Update language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.lang === lang) {
                btn.classList.add('active');
            }
        });
        
        await this.loadTranslations();
        await this.loadStoryData();
        
        if (this.currentSection === 'story') {
            this.loadStoryContent();
        }
    }

    updateUITranslations() {
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (this.translations[key]) {
                if (element.tagName === 'INPUT' && element.type !== 'submit') {
                    element.placeholder = this.translations[key];
                } else {
                    element.textContent = this.translations[key];
                }
            }
        });
    }

    // Story System
    async loadStoryData() {
        try {
            const response = await fetch(`/api/story?lang=${this.currentLanguage}`);
            this.storyData = await response.json();
        } catch (error) {
            console.error('Failed to load story data:', error);
        }
    }

    loadStoryContent() {
        const container = document.getElementById('storyContent');
        container.innerHTML = '';

        Object.keys(this.storyData).forEach(chapterKey => {
            const chapter = this.storyData[chapterKey];
            const chapterDiv = document.createElement('div');
            chapterDiv.className = 'story-chapter fade-in';
            chapterDiv.innerHTML = `
                <h3 class="story-title">${chapter.title}</h3>
                <p class="story-content">${chapter.content}</p>
            `;
            container.appendChild(chapterDiv);
        });
    }

    // Background Slides System
    startSlideRotation() {
        this.updateSlideBackground();
        
        this.slideInterval = setInterval(() => {
            this.currentSlideIndex = (this.currentSlideIndex + 1) % this.backgroundSlides.length;
            this.updateSlideBackground();
        }, 8000); // Change slide every 8 seconds
    }

    async updateSlideBackground() {
        const slideElement = document.getElementById('slideBackground');
        const slideName = this.backgroundSlides[this.currentSlideIndex];
        
        try {
            // For now, we'll use placeholder images. In production, these would load from /api/slides/
            const slideUrl = `/images/underground_bunker_view.webp`; // Fallback image
            slideElement.style.backgroundImage = `url('${slideUrl}')`;
            slideElement.style.opacity = '0.15';
        } catch (error) {
            console.error('Failed to load slide:', error);
        }
    }

    // UI Navigation
    showLoginScreen() {
        document.getElementById('loginScreen').classList.remove('hidden');
        document.getElementById('mainApp').classList.add('hidden');
    }

    showMainApp() {
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected section
        const section = document.getElementById(`${sectionName}Section`);
        if (section) {
            section.classList.remove('hidden');
            section.classList.add('fade-in');
        }
        
        // Update active button
        event.target.classList.add('active');
        this.currentSection = sectionName;
        
        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'dashboard':
                await this.loadDashboardData();
                break;
            case 'story':
                this.loadStoryContent();
                break;
            case 'environmental':
                await this.loadEnvironmentalData();
                break;
            case 'alerts':
                await this.loadAlerts();
                break;
            case 'emergency':
                await this.loadEmergencyData();
                break;
        }
    }

    // Dashboard System
    async loadDashboardData() {
        try {
            // Load system status
            const statusResponse = await fetch('/api/dashboard/system-status', {
                credentials: 'include'
            });
            const statusData = await statusResponse.json();
            
            this.updateSystemStatus(statusData);
            
            // Load environmental data for charts
            const envResponse = await fetch('/api/dashboard/environmental-data?hours=24', {
                credentials: 'include'
            });
            const envData = await envResponse.json();
            
            this.updateEnvironmentalDisplay(envData);
            this.createEnvironmentalChart(envData);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showErrorMessage('Failed to load dashboard data');
        }
    }

    updateSystemStatus(data) {
        // Update health score
        const healthScore = document.getElementById('healthScore');
        if (healthScore && data.health_score !== undefined) {
            healthScore.textContent = `${data.health_score}%`;
        }
        
        // Update resident count
        const residentCount = document.getElementById('residentCount');
        if (residentCount && data.total_residents !== undefined) {
            residentCount.textContent = data.total_residents;
        }
    }

    updateEnvironmentalDisplay(data) {
        const container = document.getElementById('environmentalData');
        if (!container || !data.length) return;
        
        const latest = data[0]; // Most recent data
        
        const envCards = [
            { key: 'temperature', label: this.translations.temperature || 'Temperature', value: `${latest.temperature?.toFixed(1) || 'N/A'}°C`, unit: '°C' },
            { key: 'humidity', label: this.translations.humidity || 'Humidity', value: `${latest.humidity?.toFixed(1) || 'N/A'}%`, unit: '%' },
            { key: 'oxygen_level', label: this.translations.oxygen || 'Oxygen', value: `${latest.oxygen_level?.toFixed(1) || 'N/A'}%`, unit: '%' },
            { key: 'co2_level', label: this.translations.co2 || 'CO2', value: `${latest.co2_level?.toFixed(0) || 'N/A'} ppm`, unit: 'ppm' },
            { key: 'radiation_level', label: this.translations.radiation || 'Radiation', value: `${latest.radiation_level?.toFixed(2) || 'N/A'} µSv/h`, unit: 'µSv/h' },
            { key: 'air_quality', label: 'Air Quality', value: `${latest.air_quality?.toFixed(0) || 'N/A'}`, unit: 'AQI' }
        ];
        
        container.innerHTML = envCards.map(card => `
            <div class="env-card">
                <div class="env-value">${card.value}</div>
                <div class="env-label">${card.label}</div>
            </div>
        `).join('');
    }

    createEnvironmentalChart(data) {
        const ctx = document.getElementById('environmentalChart');
        if (!ctx || !data.length) return;
        
        // Destroy existing chart
        if (this.environmentalChart) {
            this.environmentalChart.destroy();
        }
        
        const labels = data.reverse().map(item => {
            return new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });
        
        this.environmentalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: data.map(item => item.temperature),
                        borderColor: '#ff6b35',
                        backgroundColor: 'rgba(255, 107, 53, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Humidity (%)',
                        data: data.map(item => item.humidity),
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Oxygen (%)',
                        data: data.map(item => item.oxygen_level),
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                }
            }
        });
    }

    // Environmental Monitoring
    async loadEnvironmentalData() {
        try {
            const response = await fetch('/api/dashboard/environmental-data?hours=48', {
                credentials: 'include'
            });
            const data = await response.json();
            
            this.updateCurrentReadings(data);
            this.createHistoricalChart(data);
        } catch (error) {
            console.error('Failed to load environmental data:', error);
        }
    }

    updateCurrentReadings(data) {
        const container = document.getElementById('currentReadings');
        if (!container || !data.length) return;
        
        const latest = data[0];
        
        container.innerHTML = `
            <div class="space-y-4">
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>Temperature:</span>
                    <span class="font-bold text-orange-500">${latest.temperature?.toFixed(1) || 'N/A'}°C</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>Humidity:</span>
                    <span class="font-bold text-blue-400">${latest.humidity?.toFixed(1) || 'N/A'}%</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>Oxygen Level:</span>
                    <span class="font-bold text-green-400">${latest.oxygen_level?.toFixed(1) || 'N/A'}%</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>CO2 Level:</span>
                    <span class="font-bold text-yellow-400">${latest.co2_level?.toFixed(0) || 'N/A'} ppm</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>Radiation:</span>
                    <span class="font-bold text-red-400">${latest.radiation_level?.toFixed(2) || 'N/A'} µSv/h</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-800 rounded">
                    <span>Air Quality:</span>
                    <span class="font-bold text-purple-400">${latest.air_quality?.toFixed(0) || 'N/A'} AQI</span>
                </div>
            </div>
        `;
    }

    // Alerts System
    async loadAlerts() {
        try {
            const response = await fetch('/api/dashboard/alerts', {
                credentials: 'include'
            });
            const alerts = await response.json();
            
            this.displayAlerts(alerts);
        } catch (error) {
            console.error('Failed to load alerts:', error);
        }
    }

    displayAlerts(alerts) {
        const container = document.getElementById('alertsList');
        if (!container) return;
        
        if (!alerts.length) {
            container.innerHTML = '<div class="card text-center text-gray-400">No active alerts</div>';
            return;
        }
        
        container.innerHTML = alerts.map(alert => `
            <div class="card">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-semibold text-${this.getSeverityColor(alert.severity)}-400">
                            ${alert.alert_type.toUpperCase()}
                        </h3>
                        <p class="text-gray-300 mt-2">${alert.message}</p>
                        <p class="text-sm text-gray-400 mt-2">
                            ${new Date(alert.timestamp).toLocaleString()}
                        </p>
                    </div>
                    <span class="px-3 py-1 rounded text-sm bg-${this.getSeverityColor(alert.severity)}-600">
                        ${alert.severity.toUpperCase()}
                    </span>
                </div>
            </div>
        `).join('');
    }

    getSeverityColor(severity) {
        const colors = {
            low: 'blue',
            medium: 'yellow',
            high: 'orange',
            critical: 'red'
        };
        return colors[severity] || 'gray';
    }

    // Emergency Communications
    async loadEmergencyData() {
        try {
            const response = await fetch('/api/emergency/messages', {
                credentials: 'include'
            });
            const messages = await response.json();
            
            this.displayMessageHistory(messages);
        } catch (error) {
            console.error('Failed to load emergency data:', error);
        }
    }

    async sendEmergencyMessage(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const messageData = {
            message_type: formData.get('message_type'),
            recipient: formData.get('recipient'),
            subject: formData.get('subject'),
            content: formData.get('content')
        };
        
        try {
            const response = await fetch('/api/emergency/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(messageData),
                credentials: 'include'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccessMessage('Emergency message sent successfully!');
                event.target.reset();
                await this.loadEmergencyData();
            } else {
                this.showErrorMessage(result.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('Failed to send emergency message:', error);
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    displayMessageHistory(messages) {
        const container = document.getElementById('messageHistory');
        if (!container) return;
        
        if (!messages.length) {
            container.innerHTML = '<div class="text-gray-400 text-center">No messages found</div>';
            return;
        }
        
        container.innerHTML = messages.slice(0, 10).map(msg => `
            <div class="border-l-4 border-${this.getStatusColor(msg.status)}-500 pl-4 py-2 mb-3">
                <div class="font-semibold">${msg.message_type.toUpperCase()}</div>
                <div class="text-sm text-gray-400">To: ${msg.recipient}</div>
                <div class="text-sm text-gray-400">Status: ${msg.status}</div>
                <div class="text-xs text-gray-500 mt-1">
                    ${new Date(msg.timestamp).toLocaleString()}
                </div>
            </div>
        `).join('');
    }

    getStatusColor(status) {
        const colors = {
            pending: 'yellow',
            sent: 'blue',
            delivered: 'green',
            failed: 'red'
        };
        return colors[status] || 'gray';
    }

    // Real-time Monitoring
    startRealTimeMonitoring() {
        // Update dashboard data every 30 seconds
        setInterval(async () => {
            if (this.currentSection === 'dashboard' && this.currentUser) {
                await this.loadDashboardData();
            }
        }, 30000);
        
        // Health check every 5 minutes
        setInterval(async () => {
            try {
                await fetch('/api/health');
            } catch (error) {
                console.warn('Health check failed:', error);
            }
        }, 300000);
    }

    // Utility Functions
    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }

    showError(element, message) {
        element.textContent = message;
        element.classList.remove('hidden');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm fade-in ${
            type === 'success' ? 'bg-green-600' : 
            type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        } text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Global functions for event handlers
let app;

function login(event) {
    return app.login(event);
}

function logout() {
    return app.logout();
}

function showSection(section) {
    return app.showSection(section);
}

function switchLanguage(lang) {
    return app.switchLanguage(lang);
}

function sendEmergencyMessage(event) {
    return app.sendEmergencyMessage(event);
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app = new BunkerTechApp();
});

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
