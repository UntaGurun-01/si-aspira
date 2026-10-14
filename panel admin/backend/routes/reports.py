from flask import Blueprint, render_template, request
from flask_login import login_required
from backend import db
from backend.models import Complaint
from sqlalchemy import func, extract
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@reports_bp.route('')
@login_required
def index():
    selected_period = request.args.get('period', '30 Hari')

    now = datetime.utcnow()
    if selected_period == '7 Hari':
        cutoff = now - timedelta(days=7)
    elif selected_period == '30 Hari':
        cutoff = now - timedelta(days=30)
    elif selected_period == '3 Bulan':
        cutoff = now - timedelta(days=90)
    elif selected_period == '6 Bulan':
        cutoff = now - timedelta(days=180)
    elif selected_period == '1 Tahun':
        cutoff = now - timedelta(days=365)
    else:
        cutoff = now - timedelta(days=30)
        selected_period = '30 Hari'

    # Filter base query by cutoff date
    base_query = Complaint.query.filter(Complaint.created_at >= cutoff)
    total_complaints = base_query.count()

    # Complaints created in current month
    this_month_count = Complaint.query.filter(
        extract('year', Complaint.created_at) == now.year,
        extract('month', Complaint.created_at) == now.month
    ).count()

    # Resolution rate
    resolved_count = base_query.filter_by(status='selesai').count()
    if total_complaints > 0:
        resolution_rate = round((resolved_count / total_complaints) * 100, 1)
        resolution_rate_str = f"{int(resolution_rate)}%" if resolution_rate.is_integer() else f"{resolution_rate}%"
    else:
        resolution_rate_str = "0%"

    # Average resolution time in days (for complaints with status 'selesai')
    resolved_items = base_query.filter_by(status='selesai').all()
    if resolved_items:
        durations = [
            max(0.1, (c.updated_at - c.created_at).total_seconds() / 86400.0)
            for c in resolved_items
            if c.updated_at and c.created_at
        ]
        avg_days = round(sum(durations) / len(durations), 1) if durations else 0
    else:
        avg_days = 0

    # Rejection rate
    rejected_count = base_query.filter_by(status='ditolak').count()
    if total_complaints > 0:
        rejection_rate = round((rejected_count / total_complaints) * 100, 1)
        rejection_rate_str = f"{int(rejection_rate)}%" if rejection_rate.is_integer() else f"{rejection_rate}%"
    else:
        rejection_rate_str = "0%"

    stats = {
        'total': total_complaints,
        'this_month': this_month_count,
        'resolution_rate': resolution_rate_str,
        'resolved': resolved_count,
        'avg_days': f"{avg_days} Hari",
        'has_resolved': len(resolved_items) > 0,
        'rejection_rate': rejection_rate_str,
        'rejected': rejected_count,
    }

    # Monthly comparison (Masuk vs Selesai) for the current year
    current_year = now.year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    monthly_masuk = []
    monthly_selesai = []
    for m in range(1, 13):
        masuk = Complaint.query.filter(
            extract('year', Complaint.created_at) == current_year,
            extract('month', Complaint.created_at) == m
        ).count()
        selesai = Complaint.query.filter(
            extract('year', Complaint.created_at) == current_year,
            extract('month', Complaint.created_at) == m,
            Complaint.status == 'selesai'
        ).count()
        monthly_masuk.append(masuk)
        monthly_selesai.append(selesai)

    # Status distribution counts: Selesai, Diproses, Baru, Ditolak
    in_progress_count = base_query.filter_by(status='diproses').count()
    new_count = base_query.filter_by(status='menunggu').count()
    status_counts = [resolved_count, in_progress_count, new_count, rejected_count]

    # Category Statistics
    categories_config = [
        ('Akademik', ['akademik']),
        ('Fasilitas & Lab', ['fasilitas', 'laboratorium']),
        ('Dosen & Pengajaran', ['dosen']),
        ('Administrasi', ['administrasi']),
        ('Saran & Kritik', ['saran']),
        ('Lainnya', ['lainnya']),
    ]
    category_stats = []
    for label, cat_keys in categories_config:
        cat_query = base_query.filter(Complaint.category.in_(cat_keys))
        cat_total = cat_query.count()
        cat_resolved = cat_query.filter_by(status='selesai').count()
        if cat_total > 0:
            rate_num = round((cat_resolved / cat_total) * 100)
            rate_str = f"{rate_num}%"
            if rate_num >= 80:
                tren = '↑'
            elif rate_num >= 50:
                tren = '→'
            else:
                tren = '↓'
        else:
            rate_num = 0
            rate_str = "0%"
            tren = '-'
        category_stats.append({
            'name': label,
            'total': cat_total,
            'resolved': cat_resolved,
            'rate': rate_str,
            'rate_num': rate_num,
            'tren': tren
        })

    # Most frequently reported problems
    top_issues_rows = (
        db.session.query(Complaint.title, func.count(Complaint.id).label('total'))
        .filter(Complaint.created_at >= cutoff)
        .group_by(Complaint.title)
        .order_by(func.count(Complaint.id).desc())
        .limit(6)
        .all()
    )
    colors = ['blue', 'yellow', 'red', 'purple', 'cyan', 'green']
    max_count = top_issues_rows[0][1] if top_issues_rows else 1
    top_issues = []
    for i, row in enumerate(top_issues_rows):
        top_issues.append({
            'title': row[0],
            'count': row[1],
            'percentage': round((row[1] / max_count) * 100),
            'color': colors[i % len(colors)]
        })

    return render_template(
        'reports/index.html',
        selected_period=selected_period,
        stats=stats,
        months=months,
        monthly_masuk=monthly_masuk,
        monthly_selesai=monthly_selesai,
        status_counts=status_counts,
        category_stats=category_stats,
        top_issues=top_issues,
    )
