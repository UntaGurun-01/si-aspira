from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from backend import db
from backend.models import User, Complaint

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@users_bp.route('')
@login_required
def index():
    search = request.args.get('search', '').strip()
    prodi = request.args.get('prodi', '').strip()

    query = User.query
    if search:
        query = query.filter((User.full_name.ilike(f'%{search}%')) | (User.nim.ilike(f'%{search}%')))
    if prodi and prodi != 'Semua Program Studi':
        query = query.filter_by(program_studi=prodi)

    users = query.order_by(User.created_at.desc()).all()
    user_count = User.query.count()

    return render_template(
        'users/index.html',
        users=users,
        user_count=user_count,
        current_search=search,
        current_prodi=prodi,
    )


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_single(id):
    user = User.query.get_or_404(id)
    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'Akun mahasiswa {name} berhasil dihapus permanen dari database.',
        'remaining_count': User.query.count(),
    })


@users_bp.route('/delete-bulk', methods=['POST'])
@login_required
def delete_bulk():
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])

    if ids == 'all' or ids == ['all']:
        count = User.query.count()
        users = User.query.all()
        for u in users:
            db.session.delete(u)
        db.session.commit()
        msg = f'Seluruh {count} akun mahasiswa berhasil dihapus permanen.'
    elif isinstance(ids, list) and len(ids) > 0:
        users = User.query.filter(User.id.in_(ids)).all()
        count = len(users)
        for u in users:
            db.session.delete(u)
        db.session.commit()
        msg = f'{count} akun mahasiswa terpilih berhasil dihapus permanen.'
    else:
        return jsonify({'success': False, 'message': 'Tidak ada akun yang dipilih.'}), 400

    return jsonify({
        'success': True,
        'message': msg,
        'remaining_count': User.query.count(),
    })
