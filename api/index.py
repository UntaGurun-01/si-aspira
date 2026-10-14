import os
import sys

# Add project root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend import create_app
from flask import redirect, url_for

flask_app = create_app()

@flask_app.route('/api/index')
def vercel_entry_fallback():
    return redirect(url_for('auth.login'))

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Restore real request path if rewritten by Vercel
        raw_path = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('HTTP_X_MATCHED_PATH') or 
            environ.get('HTTP_X_NOW_ROUTE_MATCHES')
        )
        if raw_path and environ.get('PATH_INFO') in ('/api/index', '/api/index.py'):
            clean_path = raw_path.split('?')[0]
            if clean_path:
                environ['PATH_INFO'] = clean_path
        return self.wsgi_app(environ, start_response)

app = VercelPathMiddleware(flask_app)
handler = app
