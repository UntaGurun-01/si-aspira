from flask import Blueprint, render_template
from flask_login import login_required, current_user

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@settings_bp.route('')
@login_required
def index():
    return render_template('settings/index.html')
