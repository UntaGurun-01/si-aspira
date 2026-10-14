from backend import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')  # superadmin, admin, petugas
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255), nullable=True)
    notif_sound_enabled = db.Column(db.Boolean, default=True)
    notif_sound_file = db.Column(db.String(255), nullable=True)
    notif_email = db.Column(db.Boolean, default=True)
    notif_status = db.Column(db.Boolean, default=True)
    notif_pending = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


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

    def __repr__(self):
        return f'<User {self.email}>'


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
        'menunggu': 'Baru',
        'diproses': 'Diproses',
        'selesai': 'Selesai',
        'ditolak': 'Ditolak',
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

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status.capitalize())

    @property
    def category_label(self):
        return self.CATEGORY_LABELS.get(self.category, self.category.capitalize())

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


class ComplaintResponse(db.Model):
    __tablename__ = 'complaint_responses'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    responder_name = db.Column(db.String(100), nullable=False, default='Admin')
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StatusLog(db.Model):
    __tablename__ = 'status_logs'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(200), nullable=True)
    changed_by = db.Column(db.String(100), default='Admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')
    is_read = db.Column(db.Boolean, default=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def generate_ticket_number():
    date_str = datetime.utcnow().strftime('%Y%m%d')
    random_part = uuid.uuid4().hex[:4].upper()
    return f"TKT-{date_str}-{random_part}"


@login_manager.user_loader
def load_user(user_id):
    try:
        return Admin.query.get(int(user_id))
    except Exception:
        return None
