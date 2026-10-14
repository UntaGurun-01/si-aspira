import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend import create_app
from flask import request, render_template

flask_app = create_app()

@flask_app.route('/api/index')
def vercel_entry():
    # If Vercel rewrote request to /api/index, check original URI header
    # or render login directly instead of redirecting!
    original_uri = request.headers.get('x-forwarded-uri') or request.environ.get('REQUEST_URI') or ''
    if original_uri.startswith('/dashboard') or original_uri.startswith('/complaints') or original_uri.startswith('/profile'):
        # Pass to the proper view
        return flask_app.handle_url_adapter(request.environ)
    # Default to login page directly without redirecting!
    return render_template('auth/login.html')

app = flask_app
handler = flask_app
