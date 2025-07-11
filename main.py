#!/usr/bin/env python3
"""
Lataupe Bunker Tech - Entry Point

This file serves as the main entry point for the application.
The actual Flask application is in lataupe_integrated_app.py
"""

import os
import sys

def main():
    """Run the main integrated application."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the integrated app
    integrated_app = os.path.join(script_dir, 'lataupe_integrated_app.py')
    
    if not os.path.exists(integrated_app):
        print("Error: lataupe_integrated_app.py not found!")
        print("Please ensure the project structure is set up correctly.")
        sys.exit(1)
    
    # Add the project root to Python path
    sys.path.insert(0, script_dir)
    
    # Change to the project directory
    os.chdir(script_dir)
    
    try:
        # Import and run the integrated Flask app
        from lataupe_integrated_app import app, create_tables
        
        # Initialize database tables
        with app.app_context():
            create_tables()
        
        # Run the application
        port = int(os.environ.get('PORT', 5001))
        print(f"Starting Lataupe Bunker Tech on port {port}...")
        print(f"Access the application at: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
