from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Producto, Categoria, InventarioActual

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')


def _generar_codigo(categoria_id):
    cat = Categoria.query.get(categoria_id)
    prefijos = {'Electrodomésticos': 'ELE', 'Muebles': 'MUE', 'Otros': 'OTR'}
    prefijo = prefijos.get(cat.nombre, 'PRO') if cat else 'PRO'
    ultimo = (Producto.query
              .filter(Producto.codigo.like(f'{prefijo}%'))
              .order_by(Producto.id.desc())
              .first())
    if ultimo:
        try:
            num = int(ultimo.codigo[3:]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f'{prefijo}{num:04d}'


@productos_bp.route('/')
@login_required
def lista():
    categoria_id = request.args.get('categoria', type=int)
    query = Producto.query.filter_by(activo=True)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    productos = query.order_by(Producto.codigo).all()
    categorias = Categoria.query.all()
    return render_template('productos/lista.html', productos=productos,
                           categorias=categorias, categoria_sel=categoria_id)


@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if current_user.rol not in ('admin', 'bodeguero'):
        flash('No tiene permisos para esta acción.', 'warning')
        return redirect(url_for('productos.lista'))
    categorias = Categoria.query.all()
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id', type=int)
        codigo = request.form.get('codigo', '').strip() or _generar_codigo(categoria_id)
        if Producto.query.filter_by(codigo=codigo).first():
            flash(f'El código {codigo} ya existe.', 'danger')
            return render_template('productos/form.html', categorias=categorias, accion='Nuevo')
        p = Producto(
            codigo=codigo,
            nombre=request.form.get('nombre', '').strip(),
            descripcion=request.form.get('descripcion', '').strip(),
            categoria_id=categoria_id,
            unidad=request.form.get('unidad', 'UND'),
            stock_minimo=float(request.form.get('stock_minimo', 0) or 0),
            proveedor=request.form.get('proveedor', '').strip() or None,
            precio_venta=float(request.form.get('precio_venta', 0) or 0),
        )
        db.session.add(p)
        db.session.flush()
        inv = InventarioActual(producto_id=p.id, stock=0, costo_promedio=0, valor_total=0)
        db.session.add(inv)
        db.session.commit()
        flash(f'Producto {p.codigo} creado correctamente.', 'success')
        return redirect(url_for('productos.lista'))
    return render_template('productos/form.html', categorias=categorias, accion='Nuevo')


@productos_bp.route('/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def editar(pid):
    if current_user.rol not in ('admin', 'bodeguero'):
        flash('No tiene permisos para esta acción.', 'warning')
        return redirect(url_for('productos.lista'))
    p = Producto.query.get_or_404(pid)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        p.nombre = request.form.get('nombre', '').strip()
        p.descripcion = request.form.get('descripcion', '').strip()
        p.categoria_id = request.form.get('categoria_id', type=int)
        p.unidad = request.form.get('unidad', 'UND')
        p.stock_minimo = float(request.form.get('stock_minimo', 0) or 0)
        p.proveedor = request.form.get('proveedor', '').strip() or None
        p.precio_venta = float(request.form.get('precio_venta', 0) or 0)
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('productos.lista'))
    return render_template('productos/form.html', producto=p, categorias=categorias, accion='Editar')


@productos_bp.route('/desactivar/<int:pid>', methods=['POST'])
@login_required
def desactivar(pid):
    if current_user.rol != 'admin':
        flash('Solo el administrador puede desactivar productos.', 'warning')
        return redirect(url_for('productos.lista'))
    p = Producto.query.get_or_404(pid)
    p.activo = False
    db.session.commit()
    flash(f'Producto {p.codigo} desactivado.', 'info')
    return redirect(url_for('productos.lista'))
