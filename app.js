// Application JavaScript pour Lataupe Bunker Tech
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

