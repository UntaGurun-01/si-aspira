from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from backend.models import Complaint
from sqlalchemy import func, extract
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@dashboard_bp.route('')
@login_required
def index():
    stats = {
        'total': Complaint.query.count(),
        'new': Complaint.query.filter_by(status='menunggu').count(),
        'in_progress': Complaint.query.filter_by(status='diproses').count(),
        'resolved': Complaint.query.filter_by(status='selesai').count(),
        'rejected': Complaint.query.filter_by(status='ditolak').count(),
    }

    # Recent complaints from DB (real data)
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(6).all()

    # Priority complaints: oldest unresolved complaints (menunggu or diproses)
    # Sorted by created_at ascending (oldest = highest priority / longest waiting)
    priority_complaints = (
        Complaint.query
        .filter(Complaint.status.in_(['menunggu', 'diproses']))
        .order_by(Complaint.created_at.asc())
        .limit(3)
        .all()
    )

    # Monthly trend data for current year
    current_year = datetime.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    trend_pengaduan = []
    trend_selesai = []
    for m in range(1, 13):
        count = Complaint.query.filter(
            extract('year', Complaint.created_at) == current_year,
            extract('month', Complaint.created_at) == m
        ).count()
        resolved = Complaint.query.filter(
            extract('year', Complaint.created_at) == current_year,
            extract('month', Complaint.created_at) == m,
            Complaint.status == 'selesai'
        ).count()
        trend_pengaduan.append(count)
        trend_selesai.append(resolved)

    # Category distribution from DB
    category_map = {
        'Akademik': 'akademik',
        'Dosen': 'dosen',
        'Fasilitas': 'fasilitas',
        'Laboratorium': 'laboratorium',
        'Administrasi': 'administrasi',
        'Saran': 'saran',
        'Lainnya': 'lainnya',
    }
    category_counts = {}
    for label, key in category_map.items():
        cnt = Complaint.query.filter_by(category=key).count()
        category_counts[label] = cnt

    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_complaints=recent_complaints,
        priority_complaints=priority_complaints,
        months=months,
        trend_pengaduan=trend_pengaduan,
        trend_selesai=trend_selesai,
        category_counts=category_counts,
    )
