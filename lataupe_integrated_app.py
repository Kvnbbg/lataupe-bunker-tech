# Copied from DATA/lataupe_integrated_app.py
# (Full content is already present in DATA/lataupe_integrated_app.py)
# This file is now the main backend entrypoint for the improved app.

# To run: python3 lataupe_integrated_app.py

# For full code, see DATA/lataupe_integrated_app.py

from flask import send_from_directory

# Serve static files and index.html
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
