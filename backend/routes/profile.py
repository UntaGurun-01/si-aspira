import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models import User, db
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@profile_bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html')


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        semester = request.form.get('semester', current_user.semester)

        errors = []
        if not full_name:
            errors.append('Nama lengkap wajib diisi.')

        # Handle avatar upload
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename and allowed_image(avatar_file.filename):
            ext = avatar_file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            avatar_file.save(save_path)
            # Delete old avatar
            if current_user.avatar:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)
            current_user.avatar = unique_name

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            current_user.full_name = full_name
            current_user.phone = phone
            current_user.semester = int(semester)
            db.session.commit()
            flash('Profil berhasil diperbarui!', 'success')
            return redirect(url_for('profile.index'))

    return render_template('profile/edit.html')


@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not current_user.check_password(current_password):
            errors.append('Kata sandi saat ini tidak benar.')
        if len(new_password) < 8:
            errors.append('Kata sandi baru minimal 8 karakter.')
        if new_password != confirm_password:
            errors.append('Konfirmasi kata sandi tidak cocok.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Kata sandi berhasil diubah!', 'success')
            return redirect(url_for('profile.index'))

    return render_template('profile/change_password.html')
