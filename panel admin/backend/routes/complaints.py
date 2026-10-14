from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from backend import db
from backend.models import Complaint, User, StatusLog, ComplaintResponse, Notification
from sqlalchemy import text
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__, url_prefix='/complaints')


def get_complaint_stats():
    return {
        'total': Complaint.query.count(),
        'new': Complaint.query.filter_by(status='menunggu').count(),
        'progress': Complaint.query.filter_by(status='diproses').count(),
        'resolved': Complaint.query.filter_by(status='selesai').count(),
        'rejected': Complaint.query.filter_by(status='ditolak').count(),
    }


def _delete_complaint_with_deps(complaint):
    """Delete a complaint and all its related records (notifications, status_logs)."""
    # Remove related notifications (no ORM model, use raw SQL)
    db.session.execute(text('DELETE FROM notifications WHERE complaint_id = :cid'), {'cid': complaint.id})
    # Remove related status_logs if they have a FK
    db.session.execute(text('DELETE FROM status_logs WHERE complaint_id = :cid'), {'cid': complaint.id})
    db.session.delete(complaint)


@complaints_bp.route('/')
@complaints_bp.route('')
@login_required
def index():
    query = Complaint.query

    # Search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (Complaint.title.ilike(f'%{search}%')) |
            (Complaint.ticket_number.ilike(f'%{search}%'))
        )

    # Status filter
    status = request.args.get('status', '').strip().lower()
    if status and status != 'semua status':
        status_map = {
            'baru': 'menunggu',
            'diproses': 'diproses',
            'selesai': 'selesai',
            'ditolak': 'ditolak',
        }
        mapped_status = status_map.get(status, status)
        query = query.filter_by(status=mapped_status)

    # Category filter
    category = request.args.get('category', '').strip().lower()
    if category and category != 'semua kategori':
        cat_map = {
            'akademik': 'akademik',
            'dosen & pengajaran': 'dosen',
            'dosen': 'dosen',
            'fasilitas & lab': 'fasilitas',
            'fasilitas': 'fasilitas',
            'administrasi': 'administrasi',
            'saran & kritik': 'saran',
            'saran': 'saran',
            'lainnya': 'lainnya',
        }
        mapped_cat = cat_map.get(category, category)
        query = query.filter_by(category=mapped_cat)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    stats = get_complaint_stats()

    return render_template(
        'complaints/index.html',
        complaints=complaints,
        stats=stats,
        current_search=search,
        current_status=status,
        current_category=category,
    )


@complaints_bp.route('/<int:id>')
@login_required
def detail(id):
    complaint = Complaint.query.get_or_404(id)
    return render_template('complaints/detail.html', complaint=complaint)


@complaints_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    complaint = Complaint.query.get_or_404(id)
    new_status = request.form.get('status', '').strip().lower()
    note = request.form.get('note', '').strip()
    officer = request.form.get('officer', '').strip()

    valid_statuses = ['menunggu', 'diproses', 'selesai', 'ditolak']
    if new_status not in valid_statuses:
        flash('Status tidak valid.', 'danger')
        return redirect(url_for('complaints.detail', id=id))

    old_status = complaint.status
    responder = officer if officer else (current_user.name if hasattr(current_user, 'name') and current_user.name else 'Admin')

    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()

    # Build status log
    log_parts = []
    if officer:
        log_parts.append(f'Petugas: {officer}')
    if note:
        log_parts.append(note)
    full_note = ' | '.join(log_parts) if log_parts else f'Status diubah menjadi {complaint.status_label}'

    log = StatusLog(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        note=full_note,
        changed_by=responder
    )
    db.session.add(log)

    # Notify student
    status_titles = {
        'menunggu': 'Status Pengaduan Diperbarui',
        'diproses': 'Pengaduan Sedang Diproses',
        'selesai': 'Pengaduan Berhasil Diselesaikan',
        'ditolak': 'Pengaduan Ditolak'
    }
    status_types = {
        'menunggu': 'info',
        'diproses': 'warning',
        'selesai': 'success',
        'ditolak': 'danger'
    }
    notif_msg = f'Status pengaduan #{complaint.ticket_number} "{complaint.title}" diubah menjadi {complaint.status_label}.'
    if note:
        notif_msg += f' Catatan: {note}'

    notif = Notification(
        user_id=complaint.user_id,
        complaint_id=complaint.id,
        title=status_titles.get(new_status, 'Status Pengaduan Diperbarui'),
        message=notif_msg,
        type=status_types.get(new_status, 'info')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Status tiket #{complaint.ticket_number} berhasil diubah menjadi {complaint.status_label}. Notifikasi terkirim ke mahasiswa!', 'success')
    return redirect(url_for('complaints.detail', id=id))


@complaints_bp.route('/<int:id>/response', methods=['POST'])
@login_required
def add_response(id):
    complaint = Complaint.query.get_or_404(id)
    message = request.form.get('message', '').strip()
    mark_resolved = request.form.get('mark_resolved') == '1'

    if not message:
        flash('Pesan tanggapan tidak boleh kosong.', 'danger')
        return redirect(url_for('complaints.detail', id=id))

    responder = current_user.name if hasattr(current_user, 'name') and current_user.name else 'Admin'

    # Create response
    resp = ComplaintResponse(
        complaint_id=complaint.id,
        responder_name=responder,
        message=message
    )
    db.session.add(resp)

    old_status = complaint.status
    if mark_resolved:
        complaint.status = 'selesai'
        complaint.updated_at = datetime.utcnow()
        log = StatusLog(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status='selesai',
            note=f'Tanggapan diberikan: "{message[:60]}..." dan ditandai selesai.',
            changed_by=responder
        )
        db.session.add(log)
    elif complaint.status == 'menunggu':
        complaint.status = 'diproses'
        complaint.updated_at = datetime.utcnow()
        log = StatusLog(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status='diproses',
            note=f'Tanggapan pertama diberikan: "{message[:60]}..."',
            changed_by=responder
        )
        db.session.add(log)

    # Notify student
    notif = Notification(
        user_id=complaint.user_id,
        complaint_id=complaint.id,
        title='Tanggapan Baru dari Petugas' if not mark_resolved else 'Pengaduan Selesai & Diberi Tanggapan',
        message=f'{responder} memberikan tanggapan pada pengaduan #{complaint.ticket_number}: "{message[:100]}"',
        type='success' if mark_resolved else 'info'
    )
    db.session.add(notif)
    db.session.commit()

    flash('Tanggapan berhasil dikirim dan mahasiswa telah menerima notifikasi!', 'success')
    return redirect(url_for('complaints.detail', id=id))


@complaints_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_single(id):
    complaint = Complaint.query.get_or_404(id)
    ticket_number = complaint.ticket_number
    _delete_complaint_with_deps(complaint)
    db.session.commit()

    stats = get_complaint_stats()
    return jsonify({
        'success': True,
        'message': f'Pengaduan {ticket_number} berhasil dihapus permanen dari database.',
        'stats': stats,
    })


@complaints_bp.route('/delete-bulk', methods=['POST'])
@login_required
def delete_bulk():
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])

    if ids == 'all' or ids == ['all']:
        # Delete all complaints (and their dependencies)
        all_complaints = Complaint.query.all()
        deleted_count = len(all_complaints)
        # Bulk delete notifications & logs via raw SQL for speed
        db.session.execute(text('DELETE FROM notifications WHERE complaint_id IS NOT NULL'))
        db.session.execute(text('DELETE FROM status_logs WHERE complaint_id IS NOT NULL'))
        for c in all_complaints:
            db.session.delete(c)
        db.session.commit()
        msg = f'Seluruh {deleted_count} data pengaduan berhasil dihapus permanen.'
    elif isinstance(ids, list) and len(ids) > 0:
        complaints = Complaint.query.filter(Complaint.id.in_(ids)).all()
        deleted_count = len(complaints)
        for c in complaints:
            _delete_complaint_with_deps(c)
        db.session.commit()
        msg = f'{deleted_count} data pengaduan terpilih berhasil dihapus permanen.'
    else:
        return jsonify({'success': False, 'message': 'Tidak ada data yang dipilih untuk dihapus.'}), 400

    stats = get_complaint_stats()
    return jsonify({
        'success': True,
        'message': msg,
        'deleted_count': deleted_count,
        'stats': stats,
    })


@complaints_bp.route('/stats', methods=['GET'])
@login_required
def stats_api():
    return jsonify(get_complaint_stats())

