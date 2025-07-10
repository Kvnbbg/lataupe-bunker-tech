#!/usr/bin/env python3
"""
Gamified Music Manager - A fun way to manage your music collection!
Features: Drag & drop uploads, animations, sound effects, and gamification elements.

Author: Kevin Marville
Version: 1.0.0
License: MIT
"""

import os
import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Flask and extensions
from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'music-manager-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music')

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {
    'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus'
}

# User stats for gamification
user_stats = {
    'songs_added': 0,
    'total_size': 0,
    'level': 1,
    'experience': 0,
    'achievements': [],
    'streak': 0,
    'last_upload': None
}

# Achievement definitions
ACHIEVEMENTS = {
    'first_song': {
        'name': 'First Beat',
        'description': 'Upload your first song',
        'icon': '🎵',
        'points': 10
    },
    'music_lover': {
        'name': 'Music Lover',
        'description': 'Upload 10 songs',
        'icon': '🎶',
        'points': 50
    },
    'collector': {
        'name': 'Collector',
        'description': 'Upload 50 songs',
        'icon': '💿',
        'points': 200
    },
    'audiophile': {
        'name': 'Audiophile',
        'description': 'Upload 100 songs',
        'icon': '🎧',
        'points': 500
    },
    'streak_master': {
        'name': 'Streak Master',
        'description': 'Upload songs for 7 days in a row',
        'icon': '🔥',
        'points': 100
    },
    'size_master': {
        'name': 'Size Master',
        'description': 'Upload over 1GB of music',
        'icon': '💾',
        'points': 150
    }
}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0

def calculate_experience(songs_count: int, total_size_mb: float) -> int:
    """Calculate user experience points"""
    base_exp = songs_count * 10
    size_bonus = int(total_size_mb * 2)
    return base_exp + size_bonus

def check_level_up(experience: int) -> int:
    """Calculate user level based on experience"""
    # Level formula: level = sqrt(experience / 100) + 1
    import math
    return int(math.sqrt(experience / 100)) + 1

def check_achievements(stats: Dict) -> List[str]:
    """Check for new achievements"""
    new_achievements = []
    
    # First song achievement
    if stats['songs_added'] >= 1 and 'first_song' not in stats['achievements']:
        new_achievements.append('first_song')
    
    # Music lover achievement
    if stats['songs_added'] >= 10 and 'music_lover' not in stats['achievements']:
        new_achievements.append('music_lover')
    
    # Collector achievement
    if stats['songs_added'] >= 50 and 'collector' not in stats['achievements']:
        new_achievements.append('collector')
    
    # Audiophile achievement
    if stats['songs_added'] >= 100 and 'audiophile' not in stats['achievements']:
        new_achievements.append('audiophile')
    
    # Size master achievement
    if stats['total_size'] >= 1024 and 'size_master' not in stats['achievements']:
        new_achievements.append('size_master')
    
    return new_achievements

def update_streak(stats: Dict) -> Dict:
    """Update user streak"""
    today = datetime.now().date()
    
    if stats['last_upload']:
        last_date = datetime.fromisoformat(stats['last_upload']).date()
        days_diff = (today - last_date).days
        
        if days_diff == 1:
            # Consecutive day
            stats['streak'] += 1
        elif days_diff > 1:
            # Streak broken
            stats['streak'] = 1
        # Same day uploads don't change streak
    else:
        # First upload
        stats['streak'] = 1
    
    stats['last_upload'] = today.isoformat()
    
    # Check streak achievement
    if stats['streak'] >= 7 and 'streak_master' not in stats['achievements']:
        return ['streak_master']
    
    return []

def get_music_files() -> List[Dict]:
    """Get list of music files in the music folder"""
    music_files = []
    music_folder = app.config['UPLOAD_FOLDER']
    
    try:
        for filename in os.listdir(music_folder):
            if allowed_file(filename):
                file_path = os.path.join(music_folder, filename)
                file_stats = os.stat(file_path)
                
                music_files.append({
                    'name': filename,
                    'size': file_stats.st_size,
                    'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                })
    except Exception as e:
        logger.error(f"Error reading music folder: {e}")
    
    return sorted(music_files, key=lambda x: x['modified'], reverse=True)

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main application page"""
    return render_template_string(MAIN_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    """Get user statistics"""
    global user_stats
    
    # Recalculate stats based on actual files
    music_files = get_music_files()
    actual_count = len(music_files)
    actual_size = sum(f['size'] for f in music_files) / (1024 * 1024)  # MB
    
    # Update stats if they're out of sync
    if actual_count != user_stats['songs_added']:
        user_stats['songs_added'] = actual_count
        user_stats['total_size'] = actual_size
        user_stats['experience'] = calculate_experience(actual_count, actual_size)
        user_stats['level'] = check_level_up(user_stats['experience'])
    
    return jsonify(user_stats)

@app.route('/api/music')
def get_music():
    """Get list of music files"""
    music_files = get_music_files()
    return jsonify({
        'files': music_files,
        'count': len(music_files),
        'total_size_mb': round(sum(f['size'] for f in music_files) / (1024 * 1024), 2)
    })

@app.route('/api/upload', methods=['POST'])
def upload_music():
    """Upload music files"""
    global user_stats
    
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        new_achievements = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Secure the filename
                filename = secure_filename(file.filename)
                
                # Handle duplicate filenames
                counter = 1
                original_filename = filename
                while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    counter += 1
                
                # Save the file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Get file info
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                
                uploaded_files.append({
                    'name': filename,
                    'size': file_size,
                    'size_mb': round(file_size_mb, 2)
                })
                
                # Update stats
                user_stats['songs_added'] += 1
                user_stats['total_size'] += file_size_mb
                
                logger.info(f"Uploaded: {filename} ({file_size_mb:.2f} MB)")
        
        if not uploaded_files:
            return jsonify({'error': 'No valid music files uploaded'}), 400
        
        # Update experience and level
        user_stats['experience'] = calculate_experience(user_stats['songs_added'], user_stats['total_size'])
        old_level = user_stats['level']
        user_stats['level'] = check_level_up(user_stats['experience'])
        level_up = user_stats['level'] > old_level
        
        # Check for achievements
        new_achievements.extend(check_achievements(user_stats))
        new_achievements.extend(update_streak(user_stats))
        
        # Add new achievements to user stats
        for achievement in new_achievements:
            if achievement not in user_stats['achievements']:
                user_stats['achievements'].append(achievement)
        
        # Determine sound effect
        sound_effect = 'victory' if level_up else 'success'
        
        return jsonify({
            'success': True,
            'uploaded_files': uploaded_files,
            'stats': user_stats,
            'new_achievements': [ACHIEVEMENTS[a] for a in new_achievements],
            'level_up': level_up,
            'sound_effect': sound_effect,
            'message': f"Successfully uploaded {len(uploaded_files)} file(s)!"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            'error': 'Upload failed',
            'sound_effect': 'error',
            'message': str(e)
        }), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_music(filename):
    """Delete a music file"""
    global user_stats
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get file size before deletion
        file_size_mb = get_file_size_mb(file_path)
        
        # Delete the file
        os.remove(file_path)
        
        # Update stats
        user_stats['songs_added'] = max(0, user_stats['songs_added'] - 1)
        user_stats['total_size'] = max(0, user_stats['total_size'] - file_size_mb)
        user_stats['experience'] = calculate_experience(user_stats['songs_added'], user_stats['total_size'])
        user_stats['level'] = check_level_up(user_stats['experience'])
        
        logger.info(f"Deleted: {filename}")
        
        return jsonify({
            'success': True,
            'message': f"Deleted {filename}",
            'stats': user_stats,
            'sound_effect': 'success'
        })
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return jsonify({
            'error': 'Delete failed',
            'sound_effect': 'error',
            'message': str(e)
        }), 500

@app.route('/api/achievements')
def get_achievements():
    """Get all achievements"""
    user_achievements = user_stats['achievements']
    
    achievements_data = []
    for key, achievement in ACHIEVEMENTS.items():
        achievements_data.append({
            'key': key,
            'name': achievement['name'],
            'description': achievement['description'],
            'icon': achievement['icon'],
            'points': achievement['points'],
            'unlocked': key in user_achievements
        })
    
    return jsonify({
        'achievements': achievements_data,
        'total_unlocked': len(user_achievements),
        'total_available': len(ACHIEVEMENTS)
    })

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static', 'audio'),
        filename
    )

@app.route('/music/<filename>')
def serve_music(filename):
    """Serve music files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================================================
# HTML TEMPLATE
# ============================================================================

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Gamified Music Manager</title>
    
    <!-- Styles -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css" rel="stylesheet">
    
    <style>
        .music-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .drop-zone {
            border: 3px dashed #cbd5e0;
            transition: all 0.3s ease;
        }
        
        .drop-zone.dragover {
            border-color: #4299e1;
            background-color: rgba(66, 153, 225, 0.1);
            transform: scale(1.02);
        }
        
        .level-bar {
            background: linear-gradient(90deg, #48bb78, #38a169);
            height: 8px;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .achievement-badge {
            animation: bounce 1s infinite;
        }
        
        .pulse-ring {
            animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
        }
        
        @keyframes pulse-ring {
            0% {
                transform: scale(0.33);
            }
            80%, 100% {
                opacity: 0;
            }
        }
        
        .floating {
            animation: floating 3s ease-in-out infinite;
        }
        
        @keyframes floating {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .music-note {
            animation: musicNote 2s ease-in-out infinite;
        }
        
        @keyframes musicNote {
            0%, 100% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(-5deg) scale(1.1); }
            75% { transform: rotate(5deg) scale(1.1); }
        }
        
        .file-item {
            transition: all 0.3s ease;
        }
        
        .file-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body class="music-bg text-white">
    <!-- Background Audio -->
    <audio id="backgroundAudio" loop>
        <source src="/static/audio/background.mp3" type="audio/mpeg">
    </audio>
    
    <!-- Sound Effects -->
    <audio id="successSound" preload="auto">
        <source src="/static/audio/success.wav" type="audio/wav">
    </audio>
    <audio id="victorySound" preload="auto">
        <source src="/static/audio/victory.wav" type="audio/wav">
    </audio>
    <audio id="launchSound" preload="auto">
        <source src="/static/audio/lauch.wav" type="audio/wav">
    </audio>
    <audio id="errorSound" preload="auto">
        <source src="/static/audio/error.wav" type="audio/wav">
    </audio>
    
    <!-- Main Container -->
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <header class="text-center mb-8">
            <h1 class="text-5xl font-bold mb-4 floating">
                <i class="fas fa-music music-note mr-4"></i>
                Gamified Music Manager
                <i class="fas fa-headphones music-note ml-4"></i>
            </h1>
            <p class="text-xl opacity-90">Upload, organize, and level up your music collection!</p>
            
            <!-- Audio Controls -->
            <div class="mt-4">
                <button id="toggleBgMusic" class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition-colors">
                    <i class="fas fa-volume-up mr-2"></i>Background Music
                </button>
            </div>
        </header>
        
        <!-- Stats Dashboard -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <!-- Level Card -->
            <div class="glass-card rounded-xl p-6 text-center">
                <div class="text-3xl mb-2">🏆</div>
                <div class="text-2xl font-bold" id="userLevel">1</div>
                <div class="text-sm opacity-75">Level</div>
                <div class="mt-2 bg-gray-700 rounded-full h-2">
                    <div class="level-bar" id="levelBar" style="width: 0%"></div>
                </div>
            </div>
            
            <!-- Songs Card -->
            <div class="glass-card rounded-xl p-6 text-center">
                <div class="text-3xl mb-2">🎵</div>
                <div class="text-2xl font-bold" id="songsCount">0</div>
                <div class="text-sm opacity-75">Songs</div>
            </div>
            
            <!-- Experience Card -->
            <div class="glass-card rounded-xl p-6 text-center">
                <div class="text-3xl mb-2">⭐</div>
                <div class="text-2xl font-bold" id="experiencePoints">0</div>
                <div class="text-sm opacity-75">Experience</div>
            </div>
            
            <!-- Streak Card -->
            <div class="glass-card rounded-xl p-6 text-center">
                <div class="text-3xl mb-2">🔥</div>
                <div class="text-2xl font-bold" id="streakCount">0</div>
                <div class="text-sm opacity-75">Day Streak</div>
            </div>
        </div>
        
        <!-- Upload Zone -->
        <div class="glass-card rounded-xl p-8 mb-8">
            <div id="dropZone" class="drop-zone rounded-lg p-12 text-center cursor-pointer">
                <div class="text-6xl mb-4">
                    <i class="fas fa-cloud-upload-alt floating"></i>
                </div>
                <h3 class="text-2xl font-bold mb-2">Drop your music files here</h3>
                <p class="text-lg opacity-75 mb-4">or click to browse</p>
                <p class="text-sm opacity-60">Supports: MP3, WAV, FLAC, AAC, OGG, WMA, M4A, OPUS</p>
                <input type="file" id="fileInput" multiple accept="audio/*" class="hidden">
            </div>
            
            <!-- Upload Progress -->
            <div id="uploadProgress" class="mt-4 hidden">
                <div class="bg-gray-700 rounded-full h-3">
                    <div id="progressBar" class="bg-green-500 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
                <p id="progressText" class="text-center mt-2">Uploading...</p>
            </div>
        </div>
        
        <!-- Music Library -->
        <div class="glass-card rounded-xl p-8 mb-8">
            <h2 class="text-3xl font-bold mb-6">
                <i class="fas fa-music mr-3"></i>Your Music Library
            </h2>
            
            <div id="musicLibrary" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Music files will be loaded here -->
            </div>
            
            <div id="emptyLibrary" class="text-center py-12 hidden">
                <div class="text-6xl mb-4 opacity-50">🎵</div>
                <p class="text-xl opacity-75">Your music library is empty</p>
                <p class="opacity-60">Upload some songs to get started!</p>
            </div>
        </div>
        
        <!-- Achievements -->
        <div class="glass-card rounded-xl p-8">
            <h2 class="text-3xl font-bold mb-6">
                <i class="fas fa-trophy mr-3"></i>Achievements
            </h2>
            
            <div id="achievementsList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Achievements will be loaded here -->
            </div>
        </div>
    </div>
    
    <!-- Achievement Notification -->
    <div id="achievementNotification" class="fixed top-4 right-4 glass-card rounded-lg p-4 transform translate-x-full transition-transform duration-500 z-50">
        <div class="flex items-center">
            <div class="text-3xl mr-3" id="achievementIcon">🏆</div>
            <div>
                <div class="font-bold" id="achievementTitle">Achievement Unlocked!</div>
                <div class="text-sm opacity-75" id="achievementDesc">Description</div>
            </div>
        </div>
    </div>
    
    <!-- Level Up Notification -->
    <div id="levelUpNotification" class="fixed inset-0 flex items-center justify-center z-50 hidden">
        <div class="glass-card rounded-xl p-8 text-center animate__animated animate__bounceIn">
            <div class="text-6xl mb-4">🎉</div>
            <h2 class="text-4xl font-bold mb-2">LEVEL UP!</h2>
            <p class="text-xl">You reached level <span id="newLevel">2</span>!</p>
        </div>
    </div>
    
    <!-- JavaScript -->
    <script>
        // Global variables
        let userStats = {};
        let backgroundMusicPlaying = false;
        
        // Audio elements
        const backgroundAudio = document.getElementById('backgroundAudio');
        const successSound = document.getElementById('successSound');
        const victorySound = document.getElementById('victorySound');
        const launchSound = document.getElementById('launchSound');
        const errorSound = document.getElementById('errorSound');
        
        // DOM elements
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const musicLibrary = document.getElementById('musicLibrary');
        const emptyLibrary = document.getElementById('emptyLibrary');
        const achievementsList = document.getElementById('achievementsList');
        
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadMusicLibrary();
            loadAchievements();
            setupEventListeners();
            playSound('launch');
        });
        
        // Setup event listeners
        function setupEventListeners() {
            // Drop zone events
            dropZone.addEventListener('click', () => fileInput.click());
            dropZone.addEventListener('dragover', handleDragOver);
            dropZone.addEventListener('dragleave', handleDragLeave);
            dropZone.addEventListener('drop', handleDrop);
            
            // File input change
            fileInput.addEventListener('change', handleFileSelect);
            
            // Background music toggle
            document.getElementById('toggleBgMusic').addEventListener('click', toggleBackgroundMusic);
        }
        
        // Drag and drop handlers
        function handleDragOver(e) {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }
        
        function handleDragLeave(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            uploadFiles(files);
        }
        
        function handleFileSelect(e) {
            const files = e.target.files;
            uploadFiles(files);
        }
        
        // Upload files
        async function uploadFiles(files) {
            if (files.length === 0) return;
            
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            
            // Show progress
            uploadProgress.classList.remove('hidden');
            progressBar.style.width = '0%';
            progressText.textContent = 'Uploading...';
            
            try {
                // Simulate progress
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 30;
                    if (progress > 90) progress = 90;
                    progressBar.style.width = progress + '%';
                }, 200);
                
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(progressInterval);
                progressBar.style.width = '100%';
                
                const result = await response.json();
                
                if (result.success) {
                    // Play sound effect
                    playSound(result.sound_effect);
                    
                    // Show achievements
                    if (result.new_achievements && result.new_achievements.length > 0) {
                        for (let achievement of result.new_achievements) {
                            showAchievementNotification(achievement);
                        }
                    }
                    
                    // Show level up
                    if (result.level_up) {
                        showLevelUpNotification(result.stats.level);
                    }
                    
                    // Update UI
                    userStats = result.stats;
                    updateStatsDisplay();
                    loadMusicLibrary();
                    loadAchievements();
                    
                    progressText.textContent = result.message;
                } else {
                    playSound('error');
                    progressText.textContent = result.error || 'Upload failed';
                }
                
            } catch (error) {
                console.error('Upload error:', error);
                playSound('error');
                progressText.textContent = 'Upload failed';
            }
            
            // Hide progress after delay
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
                fileInput.value = '';
            }, 3000);
        }
        
        // Load user stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                userStats = await response.json();
                updateStatsDisplay();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Update stats display
        function updateStatsDisplay() {
            document.getElementById('userLevel').textContent = userStats.level || 1;
            document.getElementById('songsCount').textContent = userStats.songs_added || 0;
            document.getElementById('experiencePoints').textContent = userStats.experience || 0;
            document.getElementById('streakCount').textContent = userStats.streak || 0;
            
            // Update level progress bar
            const currentLevelExp = Math.pow(userStats.level - 1, 2) * 100;
            const nextLevelExp = Math.pow(userStats.level, 2) * 100;
            const progress = ((userStats.experience - currentLevelExp) / (nextLevelExp - currentLevelExp)) * 100;
            document.getElementById('levelBar').style.width = Math.min(progress, 100) + '%';
        }
        
        // Load music library
        async function loadMusicLibrary() {
            try {
                const response = await fetch('/api/music');
                const data = await response.json();
                
                if (data.files.length === 0) {
                    musicLibrary.innerHTML = '';
                    emptyLibrary.classList.remove('hidden');
                } else {
                    emptyLibrary.classList.add('hidden');
                    displayMusicFiles(data.files);
                }
            } catch (error) {
                console.error('Error loading music library:', error);
            }
        }
        
        // Display music files
        function displayMusicFiles(files) {
            musicLibrary.innerHTML = files.map(file => `
                <div class="file-item glass-card rounded-lg p-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center flex-1 min-w-0">
                            <div class="text-2xl mr-3">
                                ${getFileIcon(file.extension)}
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="font-semibold truncate" title="${file.name}">
                                    ${file.name}
                                </div>
                                <div class="text-sm opacity-75">
                                    ${file.size_mb} MB • ${file.extension.toUpperCase()}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2 ml-4">
                            <button onclick="playMusic('${file.name}')" class="text-green-400 hover:text-green-300 transition-colors">
                                <i class="fas fa-play"></i>
                            </button>
                            <button onclick="deleteMusic('${file.name}')" class="text-red-400 hover:text-red-300 transition-colors">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Get file icon based on extension
        function getFileIcon(extension) {
            const icons = {
                'mp3': '🎵',
                'wav': '🎶',
                'flac': '🎼',
                'aac': '🎤',
                'ogg': '🎧',
                'wma': '🎸',
                'm4a': '🎹',
                'opus': '🎺'
            };
            return icons[extension] || '🎵';
        }
        
        // Play music file
        function playMusic(filename) {
            const audio = new Audio(`/music/${encodeURIComponent(filename)}`);
            audio.play().catch(error => {
                console.error('Error playing music:', error);
                playSound('error');
            });
        }
        
        // Delete music file
        async function deleteMusic(filename) {
            if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/delete/${encodeURIComponent(filename)}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSound(result.sound_effect);
                    userStats = result.stats;
                    updateStatsDisplay();
                    loadMusicLibrary();
                } else {
                    playSound('error');
                    alert(result.error || 'Delete failed');
                }
            } catch (error) {
                console.error('Delete error:', error);
                playSound('error');
                alert('Delete failed');
            }
        }
        
        // Load achievements
        async function loadAchievements() {
            try {
                const response = await fetch('/api/achievements');
                const data = await response.json();
                displayAchievements(data.achievements);
            } catch (error) {
                console.error('Error loading achievements:', error);
            }
        }
        
        // Display achievements
        function displayAchievements(achievements) {
            achievementsList.innerHTML = achievements.map(achievement => `
                <div class="glass-card rounded-lg p-4 ${achievement.unlocked ? 'opacity-100' : 'opacity-50'}">
                    <div class="text-center">
                        <div class="text-3xl mb-2 ${achievement.unlocked ? 'achievement-badge' : ''}">
                            ${achievement.icon}
                        </div>
                        <div class="font-bold">${achievement.name}</div>
                        <div class="text-sm opacity-75 mb-2">${achievement.description}</div>
                        <div class="text-xs">
                            <span class="bg-yellow-600 px-2 py-1 rounded">
                                ${achievement.points} XP
                            </span>
                        </div>
                        ${achievement.unlocked ? 
                            '<div class="text-green-400 text-xs mt-1">✓ Unlocked</div>' : 
                            '<div class="text-gray-400 text-xs mt-1">🔒 Locked</div>'
                        }
                    </div>
                </div>
            `).join('');
        }
        
        // Show achievement notification
        function showAchievementNotification(achievement) {
            const notification = document.getElementById('achievementNotification');
            const icon = document.getElementById('achievementIcon');
            const title = document.getElementById('achievementTitle');
            const desc = document.getElementById('achievementDesc');
            
            icon.textContent = achievement.icon;
            title.textContent = achievement.name;
            desc.textContent = achievement.description;
            
            // Show notification
            notification.classList.remove('translate-x-full');
            
            // Hide after 5 seconds
            setTimeout(() => {
                notification.classList.add('translate-x-full');
            }, 5000);
        }
        
        // Show level up notification
        function showLevelUpNotification(level) {
            const notification = document.getElementById('levelUpNotification');
            const newLevel = document.getElementById('newLevel');
            
            newLevel.textContent = level;
            notification.classList.remove('hidden');
            
            // Hide after 3 seconds
            setTimeout(() => {
                notification.classList.add('hidden');
            }, 3000);
        }
        
        // Play sound effect
        function playSound(soundName) {
            try {
                let audio;
                switch(soundName) {
                    case 'success':
                        audio = successSound;
                        break;
                    case 'victory':
                        audio = victorySound;
                        break;
                    case 'launch':
                        audio = launchSound;
                        break;
                    case 'error':
                        audio = errorSound;
                        break;
                    default:
                        return;
                }
                
                audio.currentTime = 0;
                audio.play().catch(error => {
                    console.log('Sound play failed:', error);
                });
            } catch (error) {
                console.log('Sound error:', error);
            }
        }
        
        // Toggle background music
        function toggleBackgroundMusic() {
            const button = document.getElementById('toggleBgMusic');
            
            if (backgroundMusicPlaying) {
                backgroundAudio.pause();
                button.innerHTML = '<i class="fas fa-volume-mute mr-2"></i>Background Music';
                backgroundMusicPlaying = false;
            } else {
                backgroundAudio.play().then(() => {
                    button.innerHTML = '<i class="fas fa-volume-up mr-2"></i>Background Music';
                    backgroundMusicPlaying = true;
                }).catch(error => {
                    console.log('Background music play failed:', error);
                });
            }
        }
        
        // Auto-refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
"""

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Gamified Music Manager")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info("Features: Drag & Drop, Gamification, Sound Effects, Animations")
    
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)

