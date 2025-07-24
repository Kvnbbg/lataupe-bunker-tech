/**
 * JavaScript Mobile et Responsive pour Lataupe Bunker Tech
 * Fonctionnalités optimisées pour mobile et tactile
 */

class MobileBunkerApp {
    constructor() {
        this.init();
        this.bindEvents();
        this.setupServiceWorker();
        this.initializeComponents();
    }

    init() {
        console.log('🚀 Initialisation Lataupe Bunker Tech Mobile');
        
        // Détection du type d'appareil
        this.isMobile = this.detectMobile();
        this.isTablet = this.detectTablet();
        this.isTouch = this.detectTouch();
        
        // Configuration responsive
        this.breakpoints = {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        };
        
        // État de l'application
        this.state = {
            sidebarOpen: false,
            currentPage: 'dashboard',
            notifications: [],
            connectionStatus: 'online'
        };
        
        // Ajouter les classes CSS appropriées
        document.body.classList.add(
            this.isMobile ? 'is-mobile' : 'is-desktop',
            this.isTouch ? 'is-touch' : 'is-no-touch'
        );
    }

    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    detectTablet() {
        return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
    }

    detectTouch() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }

    bindEvents() {
        // Événements de redimensionnement
        window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
        
        // Événements tactiles
        if (this.isTouch) {
            this.setupTouchEvents();
        }
        
        // Événements de navigation
        this.setupNavigation();
        
        // Événements de formulaires
        this.setupForms();
        
        // Événements de connexion
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
        
        // Événements de visibilité
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }

    setupTouchEvents() {
        // Gestion des swipes
        let startX, startY, endX, endY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            this.handleSwipe(startX, startY, endX, endY);
        }, { passive: true });
        
        // Prévenir le zoom sur double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }

    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // Swipe horizontal
            if (Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
        } else {
            // Swipe vertical
            if (Math.abs(deltaY) > minSwipeDistance) {
                if (deltaY > 0) {
                    this.handleSwipeDown();
                } else {
                    this.handleSwipeUp();
                }
            }
        }
    }

    handleSwipeRight() {
        // Ouvrir la sidebar sur swipe droite
        if (this.isMobile && !this.state.sidebarOpen) {
            this.toggleSidebar();
        }
    }

    handleSwipeLeft() {
        // Fermer la sidebar sur swipe gauche
        if (this.isMobile && this.state.sidebarOpen) {
            this.toggleSidebar();
        }
    }

    handleSwipeDown() {
        // Rafraîchir la page sur swipe vers le bas
        if (window.scrollY === 0) {
            this.refreshData();
        }
    }

    handleSwipeUp() {
        // Actions sur swipe vers le haut
        console.log('Swipe up detected');
    }

    setupNavigation() {
        // Toggle mobile menu
        const navToggler = document.querySelector('.navbar-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');
        
        if (navToggler && navCollapse) {
            navToggler.addEventListener('click', () => {
                navCollapse.classList.toggle('show');
                navToggler.setAttribute('aria-expanded', 
                    navCollapse.classList.contains('show'));
            });
        }
        
        // Fermer le menu mobile lors du clic sur un lien
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (this.isMobile && navCollapse) {
                    navCollapse.classList.remove('show');
                    navToggler.setAttribute('aria-expanded', 'false');
                }
            });
        });
        
        // Navigation par historique
        window.addEventListener('popstate', this.handlePopState.bind(this));
    }

    setupForms() {
        // Amélioration des formulaires mobiles
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Validation en temps réel
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
            
            // Soumission de formulaire
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });
        
        // Auto-resize des textarea
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => this.autoResizeTextarea(textarea));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';
        
        // Validation required
        if (required && !value) {
            isValid = false;
            errorMessage = 'Ce champ est requis';
        }
        
        // Validation par type
        if (value && type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Adresse email invalide';
            }
        }
        
        if (value && type === 'password') {
            if (value.length < 8) {
                isValid = false;
                errorMessage = 'Le mot de passe doit contenir au moins 8 caractères';
            }
        }
        
        // Afficher/masquer l'erreur
        this.showFieldError(field, isValid ? null : errorMessage);
        
        return isValid;
    }

    showFieldError(field, message) {
        // Supprimer l'erreur existante
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        if (message) {
            // Ajouter la classe d'erreur
            field.classList.add('is-invalid');
            
            // Créer l'élément d'erreur
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error text-danger';
            errorElement.textContent = message;
            errorElement.style.fontSize = '0.875rem';
            errorElement.style.marginTop = '0.25rem';
            
            // Insérer après le champ
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        } else {
            field.classList.remove('is-invalid');
        }
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    handleFormSubmit(e) {
        const form = e.target;
        const inputs = form.querySelectorAll('input, textarea, select');
        let isFormValid = true;
        
        // Valider tous les champs
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            e.preventDefault();
            this.showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
            
            // Focus sur le premier champ invalide
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            // Afficher un indicateur de chargement
            this.showLoadingState(form);
        }
    }

    showLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Chargement...';
        }
    }

    hideLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.dataset.originalText || 'Envoyer';
        }
    }

    handleResize() {
        const width = window.innerWidth;
        
        // Mettre à jour les classes responsive
        document.body.classList.toggle('is-mobile', width < this.breakpoints.md);
        document.body.classList.toggle('is-tablet', width >= this.breakpoints.md && width < this.breakpoints.lg);
        document.body.classList.toggle('is-desktop', width >= this.breakpoints.lg);
        
        // Fermer la sidebar mobile si on passe en desktop
        if (width >= this.breakpoints.lg && this.state.sidebarOpen) {
            this.closeSidebar();
        }
        
        // Recalculer les hauteurs
        this.recalculateHeights();
    }

    recalculateHeights() {
        // Ajuster la hauteur des éléments full-height
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        // Ajuster les textarea auto-resize
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => this.autoResizeTextarea(textarea));
    }

    toggleSidebar() {
        this.state.sidebarOpen = !this.state.sidebarOpen;
        
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar) {
            sidebar.classList.toggle('show', this.state.sidebarOpen);
        }
        
        if (overlay) {
            overlay.classList.toggle('show', this.state.sidebarOpen);
        }
        
        // Prévenir le scroll du body quand la sidebar est ouverte
        document.body.classList.toggle('sidebar-open', this.state.sidebarOpen);
    }

    closeSidebar() {
        this.state.sidebarOpen = false;
        
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar) {
            sidebar.classList.remove('show');
        }
        
        if (overlay) {
            overlay.classList.remove('show');
        }
        
        document.body.classList.remove('sidebar-open');
    }

    handleOnline() {
        this.state.connectionStatus = 'online';
        this.showNotification('Connexion rétablie', 'success');
        this.syncOfflineData();
    }

    handleOffline() {
        this.state.connectionStatus = 'offline';
        this.showNotification('Mode hors ligne activé', 'warning');
    }

    handleVisibilityChange() {
        if (document.hidden) {
            // Page cachée - réduire l'activité
            this.pauseUpdates();
        } else {
            // Page visible - reprendre l'activité
            this.resumeUpdates();
            this.refreshData();
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };
        
        this.state.notifications.push(notification);
        this.renderNotification(notification);
        
        // Auto-suppression
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, duration);
    }

    renderNotification(notification) {
        const container = this.getNotificationContainer();
        
        const element = document.createElement('div');
        element.className = `notification alert alert-${notification.type} fade-in`;
        element.dataset.notificationId = notification.id;
        element.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${notification.message}</span>
                <button type="button" class="btn-close" onclick="app.removeNotification(${notification.id})"></button>
            </div>
        `;
        
        container.appendChild(element);
        
        // Animation d'entrée
        setTimeout(() => {
            element.classList.add('show');
        }, 10);
    }

    removeNotification(id) {
        const element = document.querySelector(`[data-notification-id="${id}"]`);
        if (element) {
            element.classList.add('fade-out');
            setTimeout(() => {
                element.remove();
            }, 300);
        }
        
        this.state.notifications = this.state.notifications.filter(n => n.id !== id);
    }

    getNotificationContainer() {
        let container = document.querySelector('.notification-container');
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1060;
                max-width: 350px;
                width: 100%;
            `;
            document.body.appendChild(container);
        }
        
        return container;
    }

    refreshData() {
        if (this.state.connectionStatus === 'offline') {
            this.showNotification('Impossible de rafraîchir en mode hors ligne', 'warning');
            return;
        }
        
        // Simuler le rafraîchissement des données
        this.showNotification('Données mises à jour', 'success', 2000);
        
        // Ici, vous ajouteriez les appels API réels
        this.loadDashboardData();
        this.loadNotifications();
    }

    loadDashboardData() {
        // Simulation du chargement des données du dashboard
        const metrics = document.querySelectorAll('.metric-value');
        metrics.forEach(metric => {
            const currentValue = parseInt(metric.textContent) || 0;
            const newValue = currentValue + Math.floor(Math.random() * 10) - 5;
            this.animateCounter(metric, currentValue, Math.max(0, newValue));
        });
    }

    animateCounter(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    loadNotifications() {
        // Simulation du chargement des notifications
        const notifications = [
            { message: 'Système de ventilation vérifié', type: 'success' },
            { message: 'Niveau d'eau optimal', type: 'info' },
            { message: 'Maintenance programmée dans 2 jours', type: 'warning' }
        ];
        
        // Afficher une notification aléatoire
        if (Math.random() > 0.7) {
            const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
            this.showNotification(randomNotification.message, randomNotification.type);
        }
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker enregistré:', registration);
                })
                .catch(error => {
                    console.log('Erreur Service Worker:', error);
                });
        }
    }

    initializeComponents() {
        // Initialiser les composants interactifs
        this.initializeQuiz();
        this.initializeDashboard();
        this.initializeCharts();
        this.setupLazyLoading();
    }

    initializeQuiz() {
        const quizContainer = document.querySelector('.quiz-container');
        if (!quizContainer) return;
        
        const options = quizContainer.querySelectorAll('.quiz-option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                // Désélectionner les autres options
                options.forEach(opt => opt.classList.remove('selected'));
                // Sélectionner l'option cliquée
                option.classList.add('selected');
                
                // Vibration tactile si supportée
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            });
        });
    }

    initializeDashboard() {
        // Initialiser les métriques du dashboard
        this.loadDashboardData();
        
        // Mise à jour périodique
        setInterval(() => {
            if (!document.hidden && this.state.connectionStatus === 'online') {
                this.loadDashboardData();
            }
        }, 30000); // Toutes les 30 secondes
    }

    initializeCharts() {
        // Initialiser les graphiques si Chart.js est disponible
        if (typeof Chart !== 'undefined') {
            const chartElements = document.querySelectorAll('.chart-container canvas');
            chartElements.forEach(canvas => {
                this.createChart(canvas);
            });
        }
    }

    createChart(canvas) {
        const ctx = canvas.getContext('2d');
        const type = canvas.dataset.chartType || 'line';
        
        new Chart(ctx, {
            type: type,
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
                datasets: [{
                    label: 'Données',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#b0b0b0'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#b0b0b0'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    setupLazyLoading() {
        const lazyElements = document.querySelectorAll('.lazy-load');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('loaded');
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            lazyElements.forEach(element => {
                observer.observe(element);
            });
        } else {
            // Fallback pour les navigateurs plus anciens
            lazyElements.forEach(element => {
                element.classList.add('loaded');
            });
        }
    }

    syncOfflineData() {
        // Synchroniser les données hors ligne quand la connexion revient
        const offlineData = this.getOfflineData();
        
        if (offlineData.length > 0) {
            this.showNotification(`Synchronisation de ${offlineData.length} éléments...`, 'info');
            
            // Ici, vous enverriez les données au serveur
            setTimeout(() => {
                this.clearOfflineData();
                this.showNotification('Synchronisation terminée', 'success');
            }, 2000);
        }
    }

    getOfflineData() {
        try {
            return JSON.parse(localStorage.getItem('offlineData') || '[]');
        } catch {
            return [];
        }
    }

    clearOfflineData() {
        localStorage.removeItem('offlineData');
    }

    pauseUpdates() {
        // Mettre en pause les mises à jour automatiques
        console.log('Mise en pause des mises à jour');
    }

    resumeUpdates() {
        // Reprendre les mises à jour automatiques
        console.log('Reprise des mises à jour');
    }

    handlePopState(event) {
        // Gérer la navigation par l'historique
        const state = event.state;
        if (state && state.page) {
            this.navigateToPage(state.page, false);
        }
    }

    navigateToPage(page, pushState = true) {
        this.state.currentPage = page;
        
        if (pushState) {
            history.pushState({ page }, '', `/${page}`);
        }
        
        // Ici, vous ajouteriez la logique de navigation
        console.log(`Navigation vers: ${page}`);
    }

    // Utilitaire debounce
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MobileBunkerApp();
});

// Export pour les modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileBunkerApp;
}
