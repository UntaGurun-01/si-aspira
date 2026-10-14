import os
import uuid
import platform
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from backend import db
from backend.models import Admin, Complaint, User, StatusLog

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def allowed_audio(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


@settings_bp.route('/')
@settings_bp.route('')
@login_required
def index():
    # Category statistics from DB
    categories_info = [
        ('Akademik', 'Nilai, KRS, jadwal kuliah, dan kurikulum', 'akademik'),
        ('Dosen & Pengajaran', 'Kehadiran dan kualitas pengajaran dosen', 'dosen'),
        ('Fasilitas & Lab', 'Sarana prasarana kampus dan laboratorium', 'fasilitas'),
        ('Administrasi', 'Surat menyurat, beasiswa, dan administrasi fakultas', 'administrasi'),
        ('Saran & Kritik', 'Usulan dan kritik membangun untuk kampus', 'saran'),
        ('Lainnya', 'Pengaduan umum di luar kategori utama', 'lainnya'),
    ]
    categories_data = []
    for name, desc, key in categories_info:
        count = Complaint.query.filter_by(category=key).count()
        categories_data.append({
            'name': name,
            'desc': desc,
            'count': count,
            'active': True
        })

    # Recent activity logs from DB
    activity_logs = StatusLog.query.order_by(StatusLog.created_at.desc()).limit(10).all()

    # Program studi statistics
    prodi_names = [
        'Teknik Informatika',
        'Sistem Informasi',
        'Teknik Elektro',
        'Teknik Mesin',
        'Teknik Sipil'
    ]
    prodi_data = []
    for p in prodi_names:
        count = User.query.filter_by(program_studi=p).count()
        prodi_data.append({'name': p, 'count': count})

    # System Information
    system_info = {
        'os': f"{platform.system()} {platform.release()}",
        'python_version': platform.python_version(),
        'framework': 'Flask 3.x (Modular Blueprint)',
        'database': 'MySQL (si_pengaduan)',
        'server_port': '5001',
        'status': 'Aktif / Berjalan Normal'
    }

    # Audio file info
    sound_file = current_user.notif_sound_file or 'default_chime.mp3'
    sound_url = f"/static/uploads/audio/{sound_file}"

    return render_template(
        'settings/index.html',
        admin=current_user,
        categories=categories_data,
        activity_logs=activity_logs,
        prodi_data=prodi_data,
        system_info=system_info,
        sound_file=sound_file,
        sound_url=sound_url,
    )


@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
    else:
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

    if not name:
        return jsonify({'success': False, 'message': 'Nama lengkap tidak boleh kosong.'}), 400
    if not username:
        return jsonify({'success': False, 'message': 'Username tidak boleh kosong.'}), 400
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Format alamat email tidak valid.'}), 400

    existing_user = Admin.query.filter(Admin.username == username, Admin.id != current_user.id).first()
    if existing_user:
        return jsonify({'success': False, 'message': f'Username "{username}" sudah digunakan akun lain.'}), 400

    existing_email = Admin.query.filter(Admin.email == email, Admin.id != current_user.id).first()
    if existing_email:
        return jsonify({'success': False, 'message': f'Email "{email}" sudah terdaftar pada akun lain.'}), 400

    avatar_url = None
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename != '' and allowed_image(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"admin_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
            static_dir = os.path.join(current_app.root_path, '../frontend/static/uploads/avatars')
            os.makedirs(static_dir, exist_ok=True)
            file_path = os.path.join(static_dir, filename)
            file.save(file_path)
            current_user.avatar = filename
            avatar_url = f"/static/uploads/avatars/{filename}"

    current_user.name = name
    current_user.username = username
    current_user.email = email
    current_user.phone = phone

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Perubahan profil admin berhasil disimpan!',
        'admin': {
            'name': current_user.name,
            'username': current_user.username,
            'email': current_user.email,
            'phone': current_user.phone or '',
            'avatar': current_user.avatar or '',
            'avatar_url': avatar_url,
            'initial': current_user.name[0].upper() if current_user.name else 'A'
        }
    })


@settings_bp.route('/password', methods=['POST'])
@login_required
def update_password():
    data = request.get_json(silent=True) or request.form
    old_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not old_password:
        return jsonify({'success': False, 'message': 'Password saat ini wajib diisi.'}), 400

    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': 'Password saat ini tidak cocok.'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password baru minimal 6 karakter.'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Konfirmasi password baru tidak cocok.'}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Password admin berhasil diperbarui!'})


@settings_bp.route('/notifications', methods=['POST'])
@login_required
def update_notifications():
    """Save admin notification preferences and custom mp3 sound file."""
    # Check switches
    sound_enabled = request.form.get('sound_enabled') in ['1', 'true', 'on', True]
    notif_email = request.form.get('notif_email') in ['1', 'true', 'on', True]
    notif_status = request.form.get('notif_status') in ['1', 'true', 'on', True]
    notif_pending = request.form.get('notif_pending') in ['1', 'true', 'on', True]

    # Handle custom mp3 audio upload
    sound_filename = current_user.notif_sound_file
    sound_url = None

    if 'sound_file' in request.files:
        file = request.files['sound_file']
        if file and file.filename != '':
            if not allowed_audio(file.filename):
                return jsonify({
                    'success': False,
                    'message': 'Format audio tidak valid! Hanya file berekstensi .mp3 yang diperbolehkan.'
                }), 400

            ext = 'mp3'
            clean_name = f"custom_notif_{current_user.id}_{uuid.uuid4().hex[:6]}.{ext}"
            audio_dir = os.path.join(current_app.root_path, '../frontend/static/uploads/audio')
            os.makedirs(audio_dir, exist_ok=True)
            target_path = os.path.join(audio_dir, clean_name)
            file.save(target_path)
            sound_filename = clean_name
            current_user.notif_sound_file = clean_name

    current_user.notif_sound_enabled = sound_enabled
    current_user.notif_email = notif_email
    current_user.notif_status = notif_status
    current_user.notif_pending = notif_pending

    db.session.commit()

    sound_url = f"/static/uploads/audio/{sound_filename}" if sound_filename else "/static/uploads/audio/default_chime.mp3"

    return jsonify({
        'success': True,
        'message': 'Pengaturan notifikasi dan nada suara berhasil disimpan!',
        'settings': {
            'sound_enabled': current_user.notif_sound_enabled,
            'sound_file': sound_filename or 'default_chime.mp3',
            'sound_url': sound_url,
            'notif_email': current_user.notif_email,
            'notif_status': current_user.notif_status,
            'notif_pending': current_user.notif_pending
        }
    })


@settings_bp.route('/notifications/reset-sound', methods=['POST'])
@login_required
def reset_notification_sound():
    """Reset custom sound to default chime."""
    current_user.notif_sound_file = None
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Nada notifikasi berhasil dikembalikan ke nada standar.',
        'sound_url': '/static/uploads/audio/default_chime.mp3',
        'sound_file': 'default_chime.mp3'
    })


@settings_bp.route('/notifications/feed', methods=['GET'])
@login_required
def notifications_feed():
    """Live notification feed for topbar bell and audio alerts."""
    # Count new complaints
    new_count = Complaint.query.filter_by(status='menunggu').count()

    # Recent complaints for bell dropdown
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(7).all()
    items = []
    for c in recent_complaints:
        items.append({
            'id': c.id,
            'ticket_number': c.ticket_number,
            'title': c.title,
            'category': c.category_label,
            'status': c.status,
            'status_label': c.status_label,
            'user_name': c.user.full_name if c.user else 'Mahasiswa',
            'time': c.created_at.strftime('%d %b %H:%M') if c.created_at else '-',
            'is_new': (c.status == 'menunggu')
        })

    sound_file = current_user.notif_sound_file or 'default_chime.mp3'
    sound_url = f"/static/uploads/audio/{sound_file}"

    return jsonify({
        'total_new': new_count,
        'sound_enabled': bool(current_user.notif_sound_enabled),
        'sound_url': sound_url,
        'sound_file': sound_file,
        'items': items
    })
