# 🎵 Gamified Music Manager

A fun and interactive way to manage your music collection with gamification elements, animations, and sound effects!

## ✨ Features

### 🎮 Gamification Elements
- **Level System**: Gain experience points and level up as you add more music
- **Achievements**: Unlock badges for various milestones
- **Streak System**: Build daily upload streaks for bonus points
- **Progress Tracking**: Visual progress bars and statistics

### 🎵 Music Management
- **Drag & Drop Upload**: Simply drag music files to the upload zone
- **Multiple Format Support**: MP3, WAV, FLAC, AAC, OGG, WMA, M4A, OPUS
- **File Organization**: Automatic file management in the `music/` folder
- **Music Library**: Browse and manage your uploaded songs
- **File Playback**: Click to play songs directly in the browser

### 🎨 Visual & Audio Experience
- **Animated Interface**: Smooth animations and transitions
- **Sound Effects**: Different sounds for success, victory, launch, and error events
- **Background Music**: Optional ambient background music
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Glass Morphism UI**: Modern, translucent design elements

### 🏆 Achievement System
- **First Beat**: Upload your first song (10 XP)
- **Music Lover**: Upload 10 songs (50 XP)
- **Collector**: Upload 50 songs (200 XP)
- **Audiophile**: Upload 100 songs (500 XP)
- **Streak Master**: Upload songs for 7 days in a row (100 XP)
- **Size Master**: Upload over 1GB of music (150 XP)

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the application**:
   ```bash
   # If you have the files, navigate to the directory
   cd music_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python music_manager.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5002
   ```

## 📁 Project Structure

```
music_app/
├── music_manager.py          # Main Flask application
├── requirements.txt          # Python dependencies
├── music/                   # Music files storage (auto-created)
├── static/
│   └── audio/              # Sound effects and background music
│       ├── background.mp3  # Background music
│       ├── success.wav     # Success sound effect
│       ├── victory.wav     # Victory/level up sound
│       ├── lauch.wav       # Launch/startup sound
│       └── error.wav       # Error sound effect
└── README.md               # This documentation
```

## 🎯 How to Use

### 1. Upload Music
- **Drag & Drop**: Drag music files from your computer to the upload zone
- **Click to Browse**: Click the upload zone to open file browser
- **Multiple Files**: Select multiple files at once for batch upload
- **Progress Tracking**: Watch the upload progress bar

### 2. Manage Your Library
- **View Files**: Browse your uploaded music in the library section
- **Play Music**: Click the play button to listen to songs
- **Delete Files**: Remove unwanted songs with the delete button
- **File Information**: See file size, format, and upload date

### 3. Track Your Progress
- **Level Up**: Gain experience points and level up
- **Achievements**: Unlock badges for various milestones
- **Statistics**: Monitor your songs count, experience, and streak
- **Visual Feedback**: Enjoy animations and sound effects

### 4. Audio Controls
- **Background Music**: Toggle ambient background music on/off
- **Sound Effects**: Automatic sound effects for different actions
- **Music Playback**: Play your uploaded songs directly in the browser

## 🔧 Technical Details

### Backend (Flask)
- **Framework**: Flask 2.3.3 with CORS support
- **File Handling**: Secure file uploads with validation
- **Data Storage**: JSON-based statistics and file metadata
- **API Endpoints**: RESTful API for frontend communication

### Frontend (HTML/CSS/JavaScript)
- **Styling**: Tailwind CSS with custom animations
- **Icons**: Font Awesome for beautiful icons
- **Animations**: CSS animations and Animate.css library
- **Responsive**: Mobile-first responsive design

### Audio Integration
- **HTML5 Audio**: Native browser audio playback
- **Multiple Formats**: Support for all major audio formats
- **Sound Effects**: Contextual audio feedback
- **Background Music**: Optional ambient audio

## 🎨 Customization

### Adding New Achievements
Edit the `ACHIEVEMENTS` dictionary in `music_manager.py`:

```python
ACHIEVEMENTS = {
    'your_achievement': {
        'name': 'Achievement Name',
        'description': 'Achievement description',
        'icon': '🎵',
        'points': 50
    }
}
```

### Changing Sound Effects
Replace the audio files in `static/audio/` with your own:
- `background.mp3` - Background music
- `success.wav` - Success sound
- `victory.wav` - Level up sound
- `lauch.wav` - Startup sound
- `error.wav` - Error sound

### Modifying the UI
The entire UI is contained in the `MAIN_TEMPLATE` string in `music_manager.py`. You can modify:
- Colors and styling
- Layout and components
- Animations and effects
- Text and messaging

## 🌐 API Endpoints

### Statistics
- `GET /api/stats` - Get user statistics and progress
- `GET /api/achievements` - Get all achievements and unlock status

### Music Management
- `GET /api/music` - Get list of uploaded music files
- `POST /api/upload` - Upload new music files
- `DELETE /api/delete/<filename>` - Delete a specific music file

### File Serving
- `GET /static/audio/<filename>` - Serve sound effect files
- `GET /music/<filename>` - Serve uploaded music files

## 🎵 Supported Audio Formats

The application supports all major audio formats:
- **MP3** - Most common format
- **WAV** - Uncompressed audio
- **FLAC** - Lossless compression
- **AAC** - Advanced Audio Coding
- **OGG** - Open source format
- **WMA** - Windows Media Audio
- **M4A** - MPEG-4 Audio
- **OPUS** - Modern codec

## 🔒 Security Features

- **Secure Filenames**: Automatic filename sanitization
- **File Validation**: Extension and type checking
- **Size Limits**: 100MB maximum file size
- **CORS Protection**: Controlled cross-origin requests
- **Path Security**: Prevents directory traversal attacks

## 🚀 Deployment

### Local Development
```bash
python music_manager.py
```

### Production Deployment
For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 music_manager:app
```

### Environment Variables
- `PORT` - Server port (default: 5002)
- `ENVIRONMENT` - Set to 'production' for production mode

## 🎮 Gamification Mechanics

### Experience Points (XP)
- **Base XP**: 10 points per song uploaded
- **Size Bonus**: 2 points per MB of music
- **Achievement Bonus**: Varies by achievement (10-500 XP)

### Level Calculation
Level = √(Experience ÷ 100) + 1

### Streak System
- **Daily Uploads**: Upload songs on consecutive days
- **Streak Bonus**: Special achievement for 7-day streaks
- **Reset Logic**: Streak resets if you skip a day

## 🎨 Visual Design

### Color Scheme
- **Primary**: Purple gradient background (#667eea to #764ba2)
- **Glass Cards**: Translucent white with backdrop blur
- **Accents**: Green for success, red for errors, yellow for warnings

### Animations
- **Floating Elements**: Gentle up-down motion
- **Music Notes**: Rotating and scaling animations
- **Hover Effects**: Smooth transitions and transforms
- **Progress Bars**: Animated width changes

### Typography
- **Headers**: Large, bold fonts for impact
- **Body Text**: Clean, readable sans-serif
- **Icons**: Font Awesome for consistency

## 🐛 Troubleshooting

### Common Issues

1. **Files not uploading**
   - Check file format is supported
   - Ensure file size is under 100MB
   - Verify browser supports drag & drop

2. **Sound effects not playing**
   - Check browser audio permissions
   - Ensure audio files are present in `static/audio/`
   - Try clicking to enable audio context

3. **Application not starting**
   - Verify Python version (3.7+)
   - Install all requirements: `pip install -r requirements.txt`
   - Check port 5002 is not in use

4. **Music files not playing**
   - Ensure browser supports the audio format
   - Check file is properly uploaded
   - Verify file permissions

### Debug Mode
The application runs in debug mode by default for development. Check the console for detailed error messages.

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to contribute to this project by:
- Adding new features
- Improving the UI/UX
- Fixing bugs
- Adding more sound effects
- Creating new achievements

## 🎵 Credits

- **Sound Effects**: Custom audio files for enhanced user experience
- **Icons**: Font Awesome icon library
- **Styling**: Tailwind CSS framework
- **Animations**: CSS animations and Animate.css

---

**Enjoy managing your music collection in a fun, gamified way! 🎵🎮**

