from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Usuario

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


def _solo_admin():
    return current_user.rol == 'admin'


@usuarios_bp.route('/')
@login_required
def lista():
    if not _solo_admin():
        flash('Solo el administrador puede gestionar usuarios.', 'warning')
        return redirect(url_for('main.dashboard'))
    usuarios = Usuario.query.order_by(Usuario.id).all()
    return render_template('usuarios/lista.html', usuarios=usuarios)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not _solo_admin():
        flash('No tiene permisos.', 'warning')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        nombre = request.form.get('nombre', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', 'vendedor')
        if Usuario.query.filter_by(username=username).first():
            flash(f'El usuario "{username}" ya existe.', 'danger')
            return render_template('usuarios/form.html', accion='Nuevo')
        u = Usuario(username=username, nombre=nombre, rol=rol, activo=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash(f'Usuario {username} creado.', 'success')
        return redirect(url_for('usuarios.lista'))
    return render_template('usuarios/form.html', accion='Nuevo')


@usuarios_bp.route('/editar/<int:uid>', methods=['GET', 'POST'])
@login_required
def editar(uid):
    if not _solo_admin():
        flash('No tiene permisos.', 'warning')
        return redirect(url_for('main.dashboard'))
    u = Usuario.query.get_or_404(uid)
    if request.method == 'POST':
        u.nombre = request.form.get('nombre', '').strip()
        u.rol = request.form.get('rol', 'vendedor')
        u.activo = bool(request.form.get('activo'))
        password = request.form.get('password', '')
        if password:
            u.set_password(password)
        db.session.commit()
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('usuarios.lista'))
    return render_template('usuarios/form.html', usuario=u, accion='Editar')
