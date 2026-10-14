from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from ..models import Notification, db

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/notifications')
@login_required
def index():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications/index.html', notifications=notifications)


@notification_bp.route('/notifications/count')
@login_required
def count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@notification_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})
