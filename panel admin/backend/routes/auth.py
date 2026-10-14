from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import Admin
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        raw_identifier = (request.form.get('username') or '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on' or request.form.get('remember') == '1' or bool(request.form.get('remember'))
        clean_user = raw_identifier.lstrip('@')
        admin = Admin.query.filter(
            (Admin.username == raw_identifier) | 
            (Admin.username == clean_user) | 
            (Admin.username == '@' + clean_user) | 
            (Admin.email == raw_identifier)
        ).first()
        if admin and admin.check_password(password) and admin.is_active:
            session.permanent = True
            admin.last_login = datetime.utcnow()
            from backend import db
            db.session.commit()
            login_user(admin, remember=remember)
            next_page = request.args.get('next') or request.form.get('next')
            if next_page and not next_page.startswith('/auth'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
def root():
    return redirect(url_for('auth.login'))
