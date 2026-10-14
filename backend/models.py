import uuid
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(20), unique=True, nullable=False)
    program_studi = db.Column(db.String(100), default='Teknik Informatika')
    semester = db.Column(db.Integer, default=1)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    complaints = db.relationship('Complaint', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def unread_notifications_count(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, diproses, selesai, ditolak
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attachments = db.relationship('Attachment', backref='complaint', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('ComplaintResponse', backref='complaint', lazy=True, cascade='all, delete-orphan')
    status_logs = db.relationship('StatusLog', backref='complaint', lazy=True, cascade='all, delete-orphan')

    STATUS_LABELS = {
        'menunggu': 'Menunggu',
        'diproses': 'Sedang Diproses',
        'selesai': 'Selesai',
        'ditolak': 'Ditolak',
    }
    STATUS_COLORS = {
        'menunggu': 'warning',
        'diproses': 'info',
        'selesai': 'success',
        'ditolak': 'danger',
    }
    CATEGORY_LABELS = {
        'akademik': 'Akademik',
        'dosen': 'Dosen & Pengajaran',
        'fasilitas': 'Fasilitas',
        'laboratorium': 'Laboratorium',
        'administrasi': 'Administrasi',
        'saran': 'Saran & Kritik',
        'lainnya': 'Lainnya',
    }
    CATEGORY_ICONS = {
        'akademik': 'bi-book-fill',
        'dosen': 'bi-person-video3',
        'fasilitas': 'bi-building',
        'laboratorium': 'bi-cpu-fill',
        'administrasi': 'bi-file-earmark-text-fill',
        'saran': 'bi-lightbulb-fill',
        'lainnya': 'bi-question-circle-fill',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def category_label(self):
        return self.CATEGORY_LABELS.get(self.category, self.category)

    @property
    def category_icon(self):
        return self.CATEGORY_ICONS.get(self.category, 'bi-tag-fill')

    def __repr__(self):
        return f'<Complaint {self.ticket_number}>'


class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attachment {self.filename}>'


class ComplaintResponse(db.Model):
    __tablename__ = 'complaint_responses'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    responder_name = db.Column(db.String(100), nullable=False, default='Petugas Prodi')
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ComplaintResponse {self.id}>'


class StatusLog(db.Model):
    __tablename__ = 'status_logs'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(200), nullable=True)
    changed_by = db.Column(db.String(100), default='Sistem')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StatusLog {self.id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id}>'


def generate_ticket_number():
    """Generate unique ticket number like TKT-20241013-XXXX"""
    date_str = datetime.utcnow().strftime('%Y%m%d')
    random_part = uuid.uuid4().hex[:4].upper()
    return f"TKT-{date_str}-{random_part}"


def seed_default_data():
    """Ensure demo user accounts exist for student portal"""
    # 1. Main demo user (NIM: 2455201016)
    if not User.query.filter_by(nim='2455201016').first():
        user1 = User(
            email='agamal2455201016.mhs@universitaspahlawan.ac.id',
            full_name='Agam Al Hakim Hasibuan',
            nim='2455201016',
            program_studi='Teknik Informatika',
            semester=5,
            phone='08123456789',
        )
        user1.set_password('password123')
        db.session.add(user1)

    # 2. Backup demo user (NIM: 2024001234)
    if not User.query.filter_by(nim='2024001234').first():
        user2 = User(
            email='agam@student.ti.ac.id',
            full_name='Agam Al Hakim Hasibuan',
            nim='2024001234',
            program_studi='Teknik Informatika',
            semester=5,
            phone='081234567890',
        )
        user2.set_password('password123')
        db.session.add(user2)

    db.session.commit()
