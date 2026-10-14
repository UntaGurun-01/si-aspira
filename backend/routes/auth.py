from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        # Mendukung login menggunakan Username (NIM terdaftar) atau Email
        identifier = (request.form.get('username') or request.form.get('nim') or request.form.get('email') or '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') in ['on', 'true', '1', True]

        if not identifier or not password:
            flash('Harap masukkan Username (NIM) dan kata sandi Anda.', 'danger')
            return render_template('auth/login.html')

        clean_id = identifier.strip()

        # Cari user berdasarkan NIM persis, Email persis, atau awalan email
        user = User.query.filter(
            (User.nim == clean_id) | 
            (User.email == clean_id) |
            (User.email.ilike(f"{clean_id}@%"))
        ).first()

        if user and user.check_password(password):
            session.permanent = True
            login_user(user, remember=remember)
            next_page = request.args.get('next') or request.form.get('next')
            if next_page and not next_page.startswith('/auth') and not next_page.startswith('/login'):
                return redirect(next_page)
            flash(f'Selamat datang kembali, {user.full_name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Username (NIM) atau kata sandi salah. Silakan periksa kembali.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        nim = request.form.get('nim', '').strip()
        semester = request.form.get('semester', 1)
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not full_name:
            errors.append('Nama lengkap wajib diisi.')
        if not email:
            errors.append('Email wajib diisi.')
        if not nim:
            errors.append('NIM wajib diisi.')
        if len(password) < 8:
            errors.append('Kata sandi minimal 8 karakter.')
        if password != confirm_password:
            errors.append('Konfirmasi kata sandi tidak cocok.')
        if User.query.filter_by(email=email).first():
            errors.append('Email sudah terdaftar.')
        if User.query.filter_by(nim=nim).first():
            errors.append('NIM sudah terdaftar.')

        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            user = User(
                full_name=full_name,
                email=email,
                nim=nim,
                semester=int(semester),
                program_studi='Teknik Informatika',
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Pendaftaran berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.login'))
