import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from ..models import Complaint, Attachment, StatusLog, Notification, db, generate_ticket_number
from werkzeug.utils import secure_filename

complaint_bp = Blueprint('complaint', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@complaint_bp.route('/complaints')
@login_required
def list_complaints():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', '')

    query = Complaint.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            db.or_(
                Complaint.title.ilike(f'%{search}%'),
                Complaint.ticket_number.ilike(f'%{search}%'),
            )
        )
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)

    complaints = query.order_by(Complaint.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'complaints/list.html',
        complaints=complaints,
        search=search,
        category=category,
        status=status,
        categories=Complaint.CATEGORY_LABELS,
    )


@complaint_bp.route('/complaints/create', methods=['GET', 'POST'])
@login_required
def create_complaint():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()

        errors = []
        if not title:
            errors.append('Judul pengaduan wajib diisi.')
        if not description or len(description) < 20:
            errors.append('Deskripsi minimal 20 karakter.')
        if not category:
            errors.append('Kategori wajib dipilih.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('complaints/create.html', categories=Complaint.CATEGORY_LABELS)

        # Create complaint
        ticket = generate_ticket_number()
        complaint = Complaint(
            ticket_number=ticket,
            title=title,
            description=description,
            category=category,
            status='menunggu',
            user_id=current_user.id,
        )
        db.session.add(complaint)
        db.session.flush()

        # Handle file uploads
        files = request.files.getlist('attachments')
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                ext = f.filename.rsplit('.', 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                f.save(save_path)
                file_size = os.path.getsize(save_path)
                att = Attachment(
                    complaint_id=complaint.id,
                    filename=unique_name,
                    original_filename=secure_filename(f.filename),
                    file_type=ext,
                    file_size=file_size,
                )
                db.session.add(att)

        # Status log
        log = StatusLog(
            complaint_id=complaint.id,
            old_status=None,
            new_status='menunggu',
            note='Pengaduan berhasil dibuat dan sedang menunggu penanganan.',
            changed_by='Sistem',
        )
        db.session.add(log)

        # Notification
        notif = Notification(
            user_id=current_user.id,
            title='Pengaduan Berhasil Dikirim',
            message=f'Pengaduan "{title}" dengan nomor tiket {ticket} berhasil dikirim. Tim kami akan segera meninjaunya.',
            type='success',
            complaint_id=complaint.id,
        )
        db.session.add(notif)

        db.session.commit()
        flash(f'Pengaduan berhasil dikirim! Nomor tiket: <strong>{ticket}</strong>', 'success')
        return redirect(url_for('complaint.detail', id=complaint.id))

    return render_template('complaints/create.html', categories=Complaint.CATEGORY_LABELS)


@complaint_bp.route('/complaints/<int:id>')
@login_required
def detail(id):
    complaint = Complaint.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('complaints/detail.html', complaint=complaint)


@complaint_bp.route('/complaints/<int:id>/status-check')
@login_required
def status_check(id):
    from flask import jsonify
    complaint = Complaint.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify({
        'status': complaint.status,
        'status_label': complaint.status_label,
        'responses_count': len(complaint.responses),
        'logs_count': len(complaint.status_logs)
    })


@complaint_bp.route('/complaints/<int:id>/delete', methods=['POST'])
@login_required
def delete_complaint(id):
    complaint = Complaint.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    ticket_number = complaint.ticket_number
    title = complaint.title

    # Remove attached physical files
    for att in complaint.attachments:
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], att.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

    # Clean up related notifications
    Notification.query.filter_by(complaint_id=complaint.id).delete()

    db.session.delete(complaint)
    db.session.commit()

    flash(f'Pengaduan <strong>{ticket_number}</strong> ({title}) berhasil dihapus.', 'success')
    return redirect(url_for('complaint.list_complaints'))

