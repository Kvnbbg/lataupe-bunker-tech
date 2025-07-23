#!/usr/bin/env python3
"""
Système complet d'optimisation mobile et responsive design pour lataupe-bunker-tech
Crée tous les fichiers nécessaires pour une expérience mobile exceptionnelle
"""

import os
import json
from pathlib import Path

def create_responsive_css():
    """Crée le CSS responsive avancé"""
    
    css_content = """/* 
 * CSS Responsive Avancé pour Lataupe Bunker Tech
 * Mobile-first approach avec breakpoints optimisés
 */

/* ===== VARIABLES CSS ===== */
:root {
  /* Couleurs thème bunker */
  --primary-color: #2c3e50;
  --secondary-color: #34495e;
  --accent-color: #e74c3c;
  --success-color: #27ae60;
  --warning-color: #f39c12;
  --danger-color: #e74c3c;
  --info-color: #3498db;
  
  /* Couleurs neutres */
  --dark-bg: #1a1a1a;
  --medium-bg: #2d2d2d;
  --light-bg: #f8f9fa;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --text-muted: #6c757d;
  
  /* Espacements */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-xxl: 3rem;
  
  /* Typographie */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Tailles de police responsive */
  --font-size-xs: clamp(0.75rem, 2vw, 0.875rem);
  --font-size-sm: clamp(0.875rem, 2.5vw, 1rem);
  --font-size-base: clamp(1rem, 3vw, 1.125rem);
  --font-size-lg: clamp(1.125rem, 3.5vw, 1.25rem);
  --font-size-xl: clamp(1.25rem, 4vw, 1.5rem);
  --font-size-2xl: clamp(1.5rem, 5vw, 2rem);
  --font-size-3xl: clamp(2rem, 6vw, 2.5rem);
  
  /* Rayons de bordure */
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 0.75rem;
  --border-radius-xl: 1rem;
  
  /* Ombres */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition-fast: 0.15s ease-in-out;
  --transition-normal: 0.3s ease-in-out;
  --transition-slow: 0.5s ease-in-out;
  
  /* Z-index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}

/* ===== RESET ET BASE ===== */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
}

body {
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--dark-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

/* ===== BREAKPOINTS ===== */
/* Mobile first approach */
/* xs: 0px - 575px (mobile) */
/* sm: 576px - 767px (mobile large) */
/* md: 768px - 991px (tablet) */
/* lg: 992px - 1199px (desktop) */
/* xl: 1200px - 1399px (desktop large) */
/* xxl: 1400px+ (desktop extra large) */

/* ===== LAYOUT RESPONSIVE ===== */
.container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

@media (min-width: 576px) {
  .container {
    max-width: 540px;
    padding: 0 var(--spacing-lg);
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 720px;
  }
}

@media (min-width: 992px) {
  .container {
    max-width: 960px;
  }
}

@media (min-width: 1200px) {
  .container {
    max-width: 1140px;
  }
}

@media (min-width: 1400px) {
  .container {
    max-width: 1320px;
  }
}

/* ===== GRILLE RESPONSIVE ===== */
.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 calc(-1 * var(--spacing-md));
}

.col {
  flex: 1;
  padding: 0 var(--spacing-md);
  min-width: 0;
}

/* Colonnes mobiles */
.col-12 { flex: 0 0 100%; max-width: 100%; }
.col-11 { flex: 0 0 91.666667%; max-width: 91.666667%; }
.col-10 { flex: 0 0 83.333333%; max-width: 83.333333%; }
.col-9 { flex: 0 0 75%; max-width: 75%; }
.col-8 { flex: 0 0 66.666667%; max-width: 66.666667%; }
.col-7 { flex: 0 0 58.333333%; max-width: 58.333333%; }
.col-6 { flex: 0 0 50%; max-width: 50%; }
.col-5 { flex: 0 0 41.666667%; max-width: 41.666667%; }
.col-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
.col-3 { flex: 0 0 25%; max-width: 25%; }
.col-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
.col-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }

/* Colonnes tablet */
@media (min-width: 768px) {
  .col-md-12 { flex: 0 0 100%; max-width: 100%; }
  .col-md-11 { flex: 0 0 91.666667%; max-width: 91.666667%; }
  .col-md-10 { flex: 0 0 83.333333%; max-width: 83.333333%; }
  .col-md-9 { flex: 0 0 75%; max-width: 75%; }
  .col-md-8 { flex: 0 0 66.666667%; max-width: 66.666667%; }
  .col-md-7 { flex: 0 0 58.333333%; max-width: 58.333333%; }
  .col-md-6 { flex: 0 0 50%; max-width: 50%; }
  .col-md-5 { flex: 0 0 41.666667%; max-width: 41.666667%; }
  .col-md-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
  .col-md-3 { flex: 0 0 25%; max-width: 25%; }
  .col-md-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
  .col-md-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }
}

/* Colonnes desktop */
@media (min-width: 992px) {
  .col-lg-12 { flex: 0 0 100%; max-width: 100%; }
  .col-lg-11 { flex: 0 0 91.666667%; max-width: 91.666667%; }
  .col-lg-10 { flex: 0 0 83.333333%; max-width: 83.333333%; }
  .col-lg-9 { flex: 0 0 75%; max-width: 75%; }
  .col-lg-8 { flex: 0 0 66.666667%; max-width: 66.666667%; }
  .col-lg-7 { flex: 0 0 58.333333%; max-width: 58.333333%; }
  .col-lg-6 { flex: 0 0 50%; max-width: 50%; }
  .col-lg-5 { flex: 0 0 41.666667%; max-width: 41.666667%; }
  .col-lg-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
  .col-lg-3 { flex: 0 0 25%; max-width: 25%; }
  .col-lg-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
  .col-lg-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }
}

/* ===== NAVIGATION MOBILE ===== */
.navbar {
  background-color: var(--primary-color);
  padding: var(--spacing-sm) 0;
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  box-shadow: var(--shadow-md);
}

.navbar-brand {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.navbar-nav {
  display: none;
  list-style: none;
  margin: 0;
  padding: 0;
}

.navbar-toggler {
  display: block;
  background: none;
  border: 2px solid var(--text-primary);
  color: var(--text-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.navbar-toggler:hover {
  background-color: var(--text-primary);
  color: var(--primary-color);
}

.navbar-collapse {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-md);
}

.navbar-collapse.show {
  display: block;
}

.nav-link {
  display: block;
  color: var(--text-primary);
  text-decoration: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
  margin-bottom: var(--spacing-xs);
}

.nav-link:hover,
.nav-link.active {
  background-color: var(--accent-color);
  color: var(--text-primary);
}

/* Navigation desktop */
@media (min-width: 992px) {
  .navbar-toggler {
    display: none;
  }
  
  .navbar-nav {
    display: flex;
    gap: var(--spacing-sm);
  }
  
  .navbar-collapse {
    display: block !important;
    position: static;
    background: none;
    box-shadow: none;
    padding: 0;
  }
  
  .nav-link {
    margin-bottom: 0;
  }
}

/* ===== COMPOSANTS MOBILES ===== */

/* Boutons tactiles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  min-height: 44px; /* Taille tactile minimum */
  min-width: 44px;
}

.btn:focus {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

.btn-primary {
  color: var(--text-primary);
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-danger {
  color: var(--text-primary);
  background-color: var(--danger-color);
  border-color: var(--danger-color);
}

.btn-success {
  color: var(--text-primary);
  background-color: var(--success-color);
  border-color: var(--success-color);
}

.btn-lg {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-lg);
  min-height: 48px;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
  min-height: 36px;
}

/* Formulaires mobiles */
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  display: block;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--medium-bg);
  border: 1px solid var(--text-muted);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  min-height: 44px; /* Taille tactile */
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.25);
}

.form-control::placeholder {
  color: var(--text-muted);
}

/* Cartes responsives */
.card {
  background-color: var(--medium-bg);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.card-header {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--primary-color);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-body {
  padding: var(--spacing-lg);
}

.card-footer {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.card-text {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
}

/* Alertes */
.alert {
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  position: relative;
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.alert-warning {
  color: #856404;
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.alert-info {
  color: #0c5460;
  background-color: #d1ecf1;
  border-color: #bee5eb;
}

/* ===== COMPOSANTS SPÉCIFIQUES BUNKER ===== */

/* Dashboard mobile */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Métriques bunker */
.metric-card {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: var(--text-primary);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s;
}

.metric-card:hover::before {
  transform: translateX(100%);
}

.metric-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
}

.metric-label {
  font-size: var(--font-size-sm);
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Status indicators */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-xl);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.status-indicator::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-online {
  background-color: rgba(39, 174, 96, 0.2);
  color: var(--success-color);
}

.status-online::before {
  background-color: var(--success-color);
}

.status-offline {
  background-color: rgba(231, 76, 60, 0.2);
  color: var(--danger-color);
}

.status-offline::before {
  background-color: var(--danger-color);
}

.status-warning {
  background-color: rgba(243, 156, 18, 0.2);
  color: var(--warning-color);
}

.status-warning::before {
  background-color: var(--warning-color);
}

/* Quiz mobile */
.quiz-container {
  max-width: 100%;
  margin: 0 auto;
  padding: var(--spacing-md);
}

.quiz-question {
  background-color: var(--medium-bg);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  margin-bottom: var(--spacing-lg);
  text-align: center;
}

.quiz-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

@media (min-width: 768px) {
  .quiz-options {
    grid-template-columns: repeat(2, 1fr);
  }
}

.quiz-option {
  padding: var(--spacing-md);
  background-color: var(--dark-bg);
  border: 2px solid var(--text-muted);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-option:hover {
  border-color: var(--accent-color);
  background-color: rgba(231, 76, 60, 0.1);
}

.quiz-option.selected {
  border-color: var(--accent-color);
  background-color: var(--accent-color);
  color: var(--text-primary);
}

/* Progress bar */
.progress {
  width: 100%;
  height: 8px;
  background-color: var(--medium-bg);
  border-radius: var(--border-radius-xl);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-color), var(--success-color));
  border-radius: var(--border-radius-xl);
  transition: width var(--transition-normal);
  position: relative;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

/* ===== ANIMATIONS ===== */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Classes d'animation */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

.slide-in-left {
  animation: slideInLeft 0.6s ease-out;
}

.slide-in-right {
  animation: slideInRight 0.6s ease-out;
}

/* ===== UTILITAIRES RESPONSIVE ===== */

/* Visibilité */
.d-none { display: none !important; }
.d-block { display: block !important; }
.d-flex { display: flex !important; }
.d-grid { display: grid !important; }

@media (min-width: 768px) {
  .d-md-none { display: none !important; }
  .d-md-block { display: block !important; }
  .d-md-flex { display: flex !important; }
  .d-md-grid { display: grid !important; }
}

@media (min-width: 992px) {
  .d-lg-none { display: none !important; }
  .d-lg-block { display: block !important; }
  .d-lg-flex { display: flex !important; }
  .d-lg-grid { display: grid !important; }
}

/* Espacement */
.m-0 { margin: 0 !important; }
.m-1 { margin: var(--spacing-xs) !important; }
.m-2 { margin: var(--spacing-sm) !important; }
.m-3 { margin: var(--spacing-md) !important; }
.m-4 { margin: var(--spacing-lg) !important; }
.m-5 { margin: var(--spacing-xl) !important; }

.p-0 { padding: 0 !important; }
.p-1 { padding: var(--spacing-xs) !important; }
.p-2 { padding: var(--spacing-sm) !important; }
.p-3 { padding: var(--spacing-md) !important; }
.p-4 { padding: var(--spacing-lg) !important; }
.p-5 { padding: var(--spacing-xl) !important; }

/* Texte */
.text-center { text-align: center !important; }
.text-left { text-align: left !important; }
.text-right { text-align: right !important; }

.text-primary { color: var(--primary-color) !important; }
.text-secondary { color: var(--text-secondary) !important; }
.text-success { color: var(--success-color) !important; }
.text-danger { color: var(--danger-color) !important; }
.text-warning { color: var(--warning-color) !important; }
.text-info { color: var(--info-color) !important; }

/* ===== OPTIMISATIONS PERFORMANCE ===== */

/* Lazy loading */
.lazy-load {
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.lazy-load.loaded {
  opacity: 1;
}

/* Optimisation images */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

.img-responsive {
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Optimisation vidéos */
video {
  max-width: 100%;
  height: auto;
}

/* ===== ACCESSIBILITÉ ===== */

/* Focus visible */
*:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

/* Réduction des mouvements */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Mode sombre forcé */
@media (prefers-color-scheme: dark) {
  :root {
    --light-bg: #1a1a1a;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
  }
}

/* ===== PRINT STYLES ===== */
@media print {
  * {
    background: transparent !important;
    color: black !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }
  
  .navbar,
  .btn,
  .alert {
    display: none !important;
  }
  
  .container {
    max-width: none !important;
  }
}
"""
    
    return css_content

def create_mobile_javascript():
    """Crée le JavaScript pour les fonctionnalités mobiles"""
    
    js_content = """/**
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
            const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
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
            { message: 'Niveau d\'eau optimal', type: 'info' },
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
"""
    
    return js_content

def create_pwa_files():
    """Crée les fichiers PWA (Progressive Web App)"""
    
    pwa_files = {}
    
    # Manifest PWA
    pwa_files['manifest.json'] = """{
  "name": "Lataupe Bunker Tech",
  "short_name": "Bunker Tech",
  "description": "Système de gestion de bunker de survie intelligent",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#2c3e50",
  "orientation": "portrait-primary",
  "categories": ["productivity", "utilities", "lifestyle"],
  "lang": "fr",
  "dir": "ltr",
  "scope": "/",
  "icons": [
    {
      "src": "/static/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/static/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "shortcuts": [
    {
      "name": "Dashboard",
      "short_name": "Dashboard",
      "description": "Accéder au tableau de bord",
      "url": "/dashboard",
      "icons": [
        {
          "src": "/static/icons/dashboard-96x96.png",
          "sizes": "96x96"
        }
      ]
    },
    {
      "name": "Quiz Survie",
      "short_name": "Quiz",
      "description": "Lancer un quiz de survie",
      "url": "/quiz",
      "icons": [
        {
          "src": "/static/icons/quiz-96x96.png",
          "sizes": "96x96"
        }
      ]
    },
    {
      "name": "Alertes",
      "short_name": "Alertes",
      "description": "Voir les alertes système",
      "url": "/alerts",
      "icons": [
        {
          "src": "/static/icons/alert-96x96.png",
          "sizes": "96x96"
        }
      ]
    }
  ],
  "screenshots": [
    {
      "src": "/static/screenshots/desktop-dashboard.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide",
      "label": "Dashboard principal sur desktop"
    },
    {
      "src": "/static/screenshots/mobile-dashboard.png",
      "sizes": "375x667",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "Dashboard principal sur mobile"
    }
  ],
  "related_applications": [],
  "prefer_related_applications": false,
  "edge_side_panel": {
    "preferred_width": 400
  }
}"""
    
    # Service Worker
    pwa_files['sw.js'] = """/**
 * Service Worker pour Lataupe Bunker Tech
 * Gestion du cache et fonctionnalités hors ligne
 */

const CACHE_NAME = 'bunker-tech-v2.0.0';
const STATIC_CACHE = 'bunker-static-v2.0.0';
const DYNAMIC_CACHE = 'bunker-dynamic-v2.0.0';

// Fichiers à mettre en cache immédiatement
const STATIC_FILES = [
  '/',
  '/static/css/responsive.css',
  '/static/js/mobile.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/offline.html'
];

// Fichiers à mettre en cache dynamiquement
const DYNAMIC_FILES = [
  '/dashboard',
  '/quiz',
  '/profile',
  '/settings'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installation');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Mise en cache des fichiers statiques');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activation');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Suppression ancien cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// Interception des requêtes
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorer les requêtes non-HTTP
  if (!request.url.startsWith('http')) {
    return;
  }
  
  // Stratégie Cache First pour les ressources statiques
  if (isStaticResource(request)) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Stratégie Network First pour les API
  if (isApiRequest(request)) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Stratégie Stale While Revalidate pour les pages
  if (isPageRequest(request)) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }
  
  // Par défaut, essayer le réseau puis le cache
  event.respondWith(networkFirst(request));
});

// Vérifier si c'est une ressource statique
function isStaticResource(request) {
  const url = new URL(request.url);
  return url.pathname.includes('/static/') || 
         url.pathname.includes('/icons/') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.jpg') ||
         url.pathname.endsWith('.svg');
}

// Vérifier si c'est une requête API
function isApiRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api/') || 
         url.pathname.startsWith('/auth/');
}

// Vérifier si c'est une requête de page
function isPageRequest(request) {
  return request.method === 'GET' && 
         request.headers.get('accept').includes('text/html');
}

// Stratégie Cache First
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Cache First Error:', error);
    return caches.match('/offline.html');
  }
}

// Stratégie Network First
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network First Error:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Retourner une page hors ligne pour les requêtes de page
    if (isPageRequest(request)) {
      return caches.match('/offline.html');
    }
    
    // Retourner une réponse d'erreur pour les API
    return new Response(
      JSON.stringify({ error: 'Pas de connexion réseau' }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Stratégie Stale While Revalidate
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    // En cas d'erreur réseau, retourner la version en cache
    return cachedResponse || caches.match('/offline.html');
  });
  
  // Retourner immédiatement la version en cache si disponible
  return cachedResponse || fetchPromise;
}

// Gestion des messages du client
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_CACHE_SIZE':
      getCacheSize().then((size) => {
        event.ports[0].postMessage({ type: 'CACHE_SIZE', payload: size });
      });
      break;
      
    case 'CLEAR_CACHE':
      clearCache().then(() => {
        event.ports[0].postMessage({ type: 'CACHE_CLEARED' });
      });
      break;
      
    case 'SYNC_DATA':
      // Synchroniser les données hors ligne
      syncOfflineData(payload);
      break;
  }
});

// Obtenir la taille du cache
async function getCacheSize() {
  const cacheNames = await caches.keys();
  let totalSize = 0;
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();
    
    for (const request of requests) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        totalSize += blob.size;
      }
    }
  }
  
  return totalSize;
}

// Vider le cache
async function clearCache() {
  const cacheNames = await caches.keys();
  
  return Promise.all(
    cacheNames.map((cacheName) => {
      if (cacheName !== STATIC_CACHE) {
        return caches.delete(cacheName);
      }
    })
  );
}

// Synchroniser les données hors ligne
async function syncOfflineData(data) {
  try {
    // Ici, vous enverriez les données au serveur
    const response = await fetch('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      // Notifier le client que la synchronisation est terminée
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'SYNC_COMPLETE',
          payload: { success: true }
        });
      });
    }
  } catch (error) {
    console.log('Sync Error:', error);
    
    // Notifier le client de l'erreur
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_ERROR',
        payload: { error: error.message }
      });
    });
  }
}

// Gestion des notifications push
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: data.data,
    actions: [
      {
        action: 'view',
        title: 'Voir',
        icon: '/static/icons/view-24x24.png'
      },
      {
        action: 'dismiss',
        title: 'Ignorer',
        icon: '/static/icons/dismiss-24x24.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Gestion des clics sur les notifications
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const { action, data } = event;
  
  if (action === 'view') {
    // Ouvrir l'application à la page appropriée
    event.waitUntil(
      clients.openWindow(data.url || '/')
    );
  } else if (action === 'dismiss') {
    // Ne rien faire, la notification est déjà fermée
    return;
  } else {
    // Clic sur la notification elle-même
    event.waitUntil(
      clients.openWindow(data.url || '/')
    );
  }
});

// Synchronisation en arrière-plan
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  try {
    // Récupérer les données à synchroniser depuis IndexedDB
    const dataToSync = await getDataToSync();
    
    if (dataToSync.length > 0) {
      // Envoyer les données au serveur
      await syncDataToServer(dataToSync);
      
      // Nettoyer les données synchronisées
      await clearSyncedData();
    }
  } catch (error) {
    console.log('Background Sync Error:', error);
  }
}

async function getDataToSync() {
  // Ici, vous récupéreriez les données depuis IndexedDB
  return [];
}

async function syncDataToServer(data) {
  // Ici, vous enverriez les données au serveur
  return fetch('/api/sync', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
}

async function clearSyncedData() {
  // Ici, vous supprimeriez les données synchronisées d'IndexedDB
}
"""
    
    return pwa_files

def create_responsive_templates():
    """Crée les templates HTML responsives"""
    
    templates = {}
    
    # Template de base responsive
    templates['base_responsive.html'] = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="description" content="Système de gestion de bunker de survie intelligent">
    <meta name="keywords" content="bunker, survie, sécurité, monitoring, quiz">
    <meta name="author" content="Lataupe Bunker Tech">
    
    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#2c3e50">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Bunker Tech">
    <meta name="msapplication-TileColor" content="#2c3e50">
    <meta name="msapplication-TileImage" content="/static/icons/icon-144x144.png">
    
    <!-- Preconnect pour optimiser les performances -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Favicon et icônes -->
    <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/icons/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/icons/apple-touch-icon.png">
    <link rel="mask-icon" href="/static/icons/safari-pinned-tab.svg" color="#2c3e50">
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- CSS -->
    <link rel="stylesheet" href="/static/css/responsive.css">
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <title>{% block title %}Lataupe Bunker Tech{% endblock %}</title>
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- Navigation mobile -->
    <nav class="navbar">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center w-100">
                <a href="/" class="navbar-brand">
                    <img src="/static/icons/icon-32x32.png" alt="Logo" width="32" height="32">
                    Bunker Tech
                </a>
                
                <button class="navbar-toggler d-lg-none" type="button" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon">☰</span>
                </button>
                
                <div class="navbar-collapse">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/quiz">Quiz</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/monitoring">Monitoring</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/settings">Paramètres</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/profile">Profil</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Contenu principal -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer mobile -->
    <footer class="footer d-lg-none">
        <div class="container">
            <div class="row">
                <div class="col-3 text-center">
                    <a href="/dashboard" class="footer-link">
                        <div class="footer-icon">📊</div>
                        <div class="footer-text">Dashboard</div>
                    </a>
                </div>
                <div class="col-3 text-center">
                    <a href="/quiz" class="footer-link">
                        <div class="footer-icon">🧠</div>
                        <div class="footer-text">Quiz</div>
                    </a>
                </div>
                <div class="col-3 text-center">
                    <a href="/monitoring" class="footer-link">
                        <div class="footer-icon">📡</div>
                        <div class="footer-text">Monitoring</div>
                    </a>
                </div>
                <div class="col-3 text-center">
                    <a href="/profile" class="footer-link">
                        <div class="footer-icon">👤</div>
                        <div class="footer-text">Profil</div>
                    </a>
                </div>
            </div>
        </div>
    </footer>
    
    <!-- Scripts -->
    <script src="/static/js/mobile.js"></script>
    {% block extra_scripts %}{% endblock %}
    
    <!-- PWA Installation prompt -->
    <div id="pwa-install-prompt" class="pwa-prompt d-none">
        <div class="pwa-prompt-content">
            <h3>Installer l'application</h3>
            <p>Installez Bunker Tech sur votre appareil pour une meilleure expérience.</p>
            <div class="pwa-prompt-actions">
                <button id="pwa-install-btn" class="btn btn-primary">Installer</button>
                <button id="pwa-dismiss-btn" class="btn btn-secondary">Plus tard</button>
            </div>
        </div>
    </div>
    
    <style>
        /* Styles pour le footer mobile */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--primary-color);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: var(--spacing-sm) 0;
            z-index: var(--z-sticky);
        }
        
        .footer-link {
            color: var(--text-secondary);
            text-decoration: none;
            display: block;
            padding: var(--spacing-xs);
            border-radius: var(--border-radius-sm);
            transition: all var(--transition-fast);
        }
        
        .footer-link:hover,
        .footer-link.active {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .footer-icon {
            font-size: 1.2rem;
            margin-bottom: var(--spacing-xs);
        }
        
        .footer-text {
            font-size: var(--font-size-xs);
        }
        
        /* Ajuster le contenu principal pour le footer mobile */
        @media (max-width: 991px) {
            .main-content {
                padding-bottom: 80px;
            }
        }
        
        /* PWA Install Prompt */
        .pwa-prompt {
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background-color: var(--medium-bg);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-xl);
            z-index: var(--z-modal);
            padding: var(--spacing-lg);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .pwa-prompt h3 {
            margin-bottom: var(--spacing-sm);
            color: var(--text-primary);
        }
        
        .pwa-prompt p {
            margin-bottom: var(--spacing-md);
            color: var(--text-secondary);
        }
        
        .pwa-prompt-actions {
            display: flex;
            gap: var(--spacing-sm);
        }
        
        .pwa-prompt-actions .btn {
            flex: 1;
        }
    </style>
    
    <script>
        // PWA Installation
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Afficher le prompt personnalisé
            const prompt = document.getElementById('pwa-install-prompt');
            prompt.classList.remove('d-none');
        });
        
        document.getElementById('pwa-install-btn').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('PWA installée');
                }
                
                deferredPrompt = null;
                document.getElementById('pwa-install-prompt').classList.add('d-none');
            }
        });
        
        document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
            document.getElementById('pwa-install-prompt').classList.add('d-none');
        });
        
        // Marquer le lien actif dans le footer
        const currentPath = window.location.pathname;
        const footerLinks = document.querySelectorAll('.footer-link');
        
        footerLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    </script>
</body>
</html>"""
    
    # Dashboard mobile
    templates['dashboard_mobile.html'] = """{% extends "base_responsive.html" %}

{% block title %}Dashboard - Bunker Tech{% endblock %}

{% block content %}
<div class="container">
    <!-- En-tête du dashboard -->
    <div class="dashboard-header mb-4">
        <h1 class="h2 mb-2">Dashboard Bunker</h1>
        <div class="d-flex justify-content-between align-items-center">
            <div class="status-indicator status-online">
                Système en ligne
            </div>
            <button class="btn btn-sm btn-primary" onclick="app.refreshData()">
                🔄 Actualiser
            </button>
        </div>
    </div>
    
    <!-- Métriques principales -->
    <div class="dashboard-grid mb-4">
        <div class="metric-card">
            <div class="metric-value" data-value="98">98</div>
            <div class="metric-label">Niveau Oxygène (%)</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" data-value="21">21</div>
            <div class="metric-label">Température (°C)</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" data-value="45">45</div>
            <div class="metric-label">Humidité (%)</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" data-value="87">87</div>
            <div class="metric-label">Énergie (%)</div>
        </div>
    </div>
    
    <!-- Alertes récentes -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Alertes Récentes</h3>
        </div>
        <div class="card-body">
            <div class="alert alert-success">
                <strong>✅ Système de ventilation</strong><br>
                Fonctionnement normal - Dernière vérification: il y a 5 min
            </div>
            
            <div class="alert alert-warning">
                <strong>⚠️ Niveau d'eau</strong><br>
                Réservoir à 75% - Rechargement recommandé dans 2 jours
            </div>
            
            <div class="alert alert-info">
                <strong>ℹ️ Maintenance programmée</strong><br>
                Vérification des filtres prévue demain à 14h00
            </div>
        </div>
    </div>
    
    <!-- Actions rapides -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Actions Rapides</h3>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-6 col-md-3 mb-3">
                    <button class="btn btn-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center" style="min-height: 80px;">
                        <div class="mb-2" style="font-size: 1.5rem;">🚨</div>
                        <div>Alerte</div>
                    </button>
                </div>
                
                <div class="col-6 col-md-3 mb-3">
                    <button class="btn btn-success w-100 h-100 d-flex flex-column align-items-center justify-content-center" style="min-height: 80px;">
                        <div class="mb-2" style="font-size: 1.5rem;">🔒</div>
                        <div>Verrouiller</div>
                    </button>
                </div>
                
                <div class="col-6 col-md-3 mb-3">
                    <button class="btn btn-warning w-100 h-100 d-flex flex-column align-items-center justify-content-center" style="min-height: 80px;">
                        <div class="mb-2" style="font-size: 1.5rem;">💡</div>
                        <div>Éclairage</div>
                    </button>
                </div>
                
                <div class="col-6 col-md-3 mb-3">
                    <button class="btn btn-info w-100 h-100 d-flex flex-column align-items-center justify-content-center" style="min-height: 80px;">
                        <div class="mb-2" style="font-size: 1.5rem;">📊</div>
                        <div>Rapports</div>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Graphique de tendance -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Tendances (24h)</h3>
        </div>
        <div class="card-body">
            <div class="chart-container" style="position: relative; height: 200px;">
                <canvas id="trendsChart" data-chart-type="line"></canvas>
            </div>
        </div>
    </div>
    
    <!-- Quiz du jour -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Quiz du Jour</h3>
        </div>
        <div class="card-body">
            <p class="card-text">Testez vos connaissances en survie avec notre quiz quotidien.</p>
            <div class="d-flex justify-content-between align-items-center">
                <div class="text-muted">
                    <small>Dernière tentative: 85% (Excellent)</small>
                </div>
                <a href="/quiz" class="btn btn-primary">Commencer</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Initialiser le graphique de tendances
    document.addEventListener('DOMContentLoaded', function() {
        const ctx = document.getElementById('trendsChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                datasets: [
                    {
                        label: 'Température (°C)',
                        data: [20, 19, 21, 23, 22, 21, 20],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Humidité (%)',
                        data: [45, 48, 42, 40, 43, 46, 45],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            usePointStyle: true
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
    });
</script>
{% endblock %}"""
    
    return templates

def main():
    """Fonction principale pour créer le système mobile responsive"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("📱 Création du système mobile et responsive...")
    print("=" * 55)
    
    # Créer les dossiers nécessaires
    css_dir = os.path.join(project_path, 'src', 'static', 'css')
    js_dir = os.path.join(project_path, 'src', 'static', 'js')
    templates_dir = os.path.join(project_path, 'src', 'templates')
    icons_dir = os.path.join(project_path, 'src', 'static', 'icons')
    
    for directory in [css_dir, js_dir, templates_dir, icons_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Créer le CSS responsive
    css_file = os.path.join(css_dir, 'responsive.css')
    with open(css_file, 'w') as f:
        f.write(create_responsive_css())
    
    # Créer le JavaScript mobile
    js_file = os.path.join(js_dir, 'mobile.js')
    with open(js_file, 'w') as f:
        f.write(create_mobile_javascript())
    
    # Créer les fichiers PWA
    pwa_files = create_pwa_files()
    for filename, content in pwa_files.items():
        filepath = os.path.join(project_path, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # Créer les templates responsives
    templates = create_responsive_templates()
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # Créer une page hors ligne
    offline_html = os.path.join(project_path, 'offline.html')
    with open(offline_html, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hors ligne - Bunker Tech</title>
    <link rel="stylesheet" href="/static/css/responsive.css">
</head>
<body>
    <div class="container">
        <div class="text-center" style="padding: 2rem;">
            <h1>📡 Mode Hors Ligne</h1>
            <p>Vous êtes actuellement hors ligne. Certaines fonctionnalités peuvent être limitées.</p>
            <button onclick="window.location.reload()" class="btn btn-primary">
                Réessayer
            </button>
        </div>
    </div>
</body>
</html>""")
    
    print("\\n✅ Système mobile et responsive créé avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • CSS responsive: {css_file}")
    print(f"   • JavaScript mobile: {js_file}")
    print(f"   • Fichiers PWA: {len(pwa_files)} fichiers")
    print(f"   • Templates responsives: {len(templates)} fichiers")
    print(f"   • Page hors ligne: {offline_html}")
    
    print("\\n📱 Fonctionnalités mobiles:")
    print("   • Design mobile-first responsive")
    print("   • Navigation tactile optimisée")
    print("   • PWA avec installation native")
    print("   • Mode hors ligne complet")
    print("   • Gestion des swipes et gestures")
    print("   • Notifications push")
    print("   • Auto-scaling et performance")
    
    print("\\n🎨 Fonctionnalités design:")
    print("   • Système de grille responsive")
    print("   • Variables CSS personnalisées")
    print("   • Animations et transitions fluides")
    print("   • Thème sombre optimisé bunker")
    print("   • Composants tactiles (44px minimum)")
    print("   • Accessibilité complète")
    
    print("\\n⚡ Optimisations performance:")
    print("   • Lazy loading des images")
    print("   • Service Worker avec cache intelligent")
    print("   • Compression et minification")
    print("   • Preload des ressources critiques")
    print("   • Debouncing des événements")
    
    print("\\n🚀 Utilisation:")
    print("   1. Intégrer les fichiers CSS/JS dans les templates")
    print("   2. Configurer le Service Worker")
    print("   3. Tester sur différents appareils")
    print("   4. Optimiser selon les métriques")
    
    return True

if __name__ == "__main__":
    main()

