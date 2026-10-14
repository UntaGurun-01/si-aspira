import os
import sys

# Ensure root directory is in sys.path for Vercel / serverless runtime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

@app.route('/api/index')
def vercel_entry_fallback():
    from flask import redirect, url_for
    return redirect(url_for('auth.login'))

handler = app

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
