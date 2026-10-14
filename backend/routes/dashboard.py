from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Complaint, Notification

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Stats
    total = Complaint.query.filter_by(user_id=current_user.id).count()
    menunggu = Complaint.query.filter_by(user_id=current_user.id, status='menunggu').count()
    diproses = Complaint.query.filter_by(user_id=current_user.id, status='diproses').count()
    selesai = Complaint.query.filter_by(user_id=current_user.id, status='selesai').count()

    # Recent complaints
    recent_complaints = (
        Complaint.query.filter_by(user_id=current_user.id)
        .order_by(Complaint.created_at.desc())
        .limit(5)
        .all()
    )

    # Unread notifications
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

    return render_template(
        'dashboard/index.html',
        total=total,
        menunggu=menunggu,
        diproses=diproses,
        selesai=selesai,
        recent_complaints=recent_complaints,
        unread_count=unread_count,
    )
