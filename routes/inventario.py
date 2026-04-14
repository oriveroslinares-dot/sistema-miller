from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Producto, Empresa, Kardex, InventarioActual, Categoria

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')


def _actualizar_inventario(producto_id, tipo, cantidad, costo_unitario):
    inv = InventarioActual.query.filter_by(producto_id=producto_id).first()
    if not inv:
        inv = InventarioActual(producto_id=producto_id, stock=0, costo_promedio=0, valor_total=0)
        db.session.add(inv)

    stock_ant = inv.stock
    costo_ant = inv.costo_promedio

    if tipo in ('ENTRADA', 'AJUSTE_MAS'):
        nuevo_stock = stock_ant + cantidad
        if nuevo_stock > 0:
            nuevo_promedio = (stock_ant * costo_ant + cantidad * costo_unitario) / nuevo_stock
        else:
            nuevo_promedio = costo_unitario
    else:  # SALIDA, AJUSTE_MENOS
        nuevo_stock = stock_ant - cantidad
        nuevo_promedio = costo_ant

    inv.stock = round(nuevo_stock, 4)
    inv.costo_promedio = round(nuevo_promedio, 4)
    inv.valor_total = round(inv.stock * inv.costo_promedio, 2)
    return inv.stock, inv.costo_promedio, inv.valor_total


# ─── ENTRADAS ───────────────────────────────────────────────────────────────

@inventario_bp.route('/entrada', methods=['GET', 'POST'])
@login_required
def entrada():
    if current_user.rol not in ('admin', 'bodeguero'):
        flash('No tiene permisos para registrar entradas.', 'warning')
        return redirect(url_for('main.dashboard'))

    productos = (Producto.query
                 .filter_by(activo=True)
                 .join(Producto.categoria)
                 .order_by(Producto.codigo)
                 .all())
    empresas = Empresa.query.all()

    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        empresa_id = request.form.get('empresa_id', type=int)
        cantidad = float(request.form.get('cantidad', 0) or 0)
        costo_unitario = float(request.form.get('costo_unitario', 0) or 0)
        documento = request.form.get('documento', '').strip()
        concepto = request.form.get('concepto', 'Entrada de inventario').strip()
        fecha_str = request.form.get('fecha', '')

        if cantidad <= 0 or costo_unitario <= 0:
            flash('Cantidad y costo deben ser mayores a cero.', 'danger')
            return render_template('inventario/entrada.html', productos=productos, empresas=empresas)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.utcnow()
        except ValueError:
            fecha = datetime.utcnow()

        saldo_cant, costo_prom, saldo_val = _actualizar_inventario(producto_id, 'ENTRADA', cantidad, costo_unitario)

        k = Kardex(
            producto_id=producto_id,
            empresa_id=empresa_id,
            fecha=fecha,
            tipo='ENTRADA',
            documento=documento,
            concepto=concepto,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            costo_total=round(cantidad * costo_unitario, 2),
            saldo_cantidad=saldo_cant,
            costo_promedio=costo_prom,
            saldo_valor=saldo_val,
            usuario_id=current_user.id,
        )
        db.session.add(k)
        db.session.commit()
        flash(f'Entrada registrada. Nuevo costo promedio: ${costo_prom:,.2f}', 'success')
        return redirect(url_for('inventario.entrada'))

    return render_template('inventario/entrada.html', productos=productos, empresas=empresas)


# ─── SALIDAS ────────────────────────────────────────────────────────────────

@inventario_bp.route('/salida', methods=['GET', 'POST'])
@login_required
def salida():
    productos = (Producto.query
                 .filter_by(activo=True)
                 .join(Producto.categoria)
                 .order_by(Producto.codigo)
                 .all())
    empresas = Empresa.query.all()

    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        empresa_id = request.form.get('empresa_id', type=int)
        cantidad = float(request.form.get('cantidad', 0) or 0)
        documento = request.form.get('documento', '').strip()
        concepto = request.form.get('concepto', 'Salida de inventario').strip()
        fecha_str = request.form.get('fecha', '')

        inv = InventarioActual.query.filter_by(producto_id=producto_id).first()
        if not inv or inv.stock < cantidad:
            flash(f'Stock insuficiente. Disponible: {inv.stock if inv else 0}', 'danger')
            return render_template('inventario/salida.html', productos=productos, empresas=empresas)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.utcnow()
        except ValueError:
            fecha = datetime.utcnow()

        costo_unitario = inv.costo_promedio
        saldo_cant, costo_prom, saldo_val = _actualizar_inventario(producto_id, 'SALIDA', cantidad, costo_unitario)

        k = Kardex(
            producto_id=producto_id,
            empresa_id=empresa_id,
            fecha=fecha,
            tipo='SALIDA',
            documento=documento,
            concepto=concepto,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            costo_total=round(cantidad * costo_unitario, 2),
            saldo_cantidad=saldo_cant,
            costo_promedio=costo_prom,
            saldo_valor=saldo_val,
            usuario_id=current_user.id,
        )
        db.session.add(k)
        db.session.commit()
        flash('Salida registrada correctamente.', 'success')
        return redirect(url_for('inventario.salida'))

    return render_template('inventario/salida.html', productos=productos, empresas=empresas)


# ─── AJUSTES ────────────────────────────────────────────────────────────────

@inventario_bp.route('/ajuste', methods=['GET', 'POST'])
@login_required
def ajuste():
    if current_user.rol not in ('admin', 'bodeguero'):
        flash('No tiene permisos para registrar ajustes.', 'warning')
        return redirect(url_for('main.dashboard'))

    productos = (Producto.query
                 .filter_by(activo=True)
                 .join(Producto.categoria)
                 .order_by(Producto.codigo)
                 .all())
    empresas = Empresa.query.all()

    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        empresa_id = request.form.get('empresa_id', type=int)
        tipo_ajuste = request.form.get('tipo_ajuste')  # MAS o MENOS
        cantidad = float(request.form.get('cantidad', 0) or 0)
        costo_unitario = float(request.form.get('costo_unitario', 0) or 0)
        documento = request.form.get('documento', '').strip()
        concepto = request.form.get('concepto', 'Ajuste de inventario').strip()
        fecha_str = request.form.get('fecha', '')

        tipo = f'AJUSTE_{tipo_ajuste}'
        inv = InventarioActual.query.filter_by(producto_id=producto_id).first()

        if tipo == 'AJUSTE_MENOS':
            if not inv or inv.stock < cantidad:
                flash(f'Stock insuficiente para el ajuste. Disponible: {inv.stock if inv else 0}', 'danger')
                return render_template('inventario/ajuste.html', productos=productos, empresas=empresas)
            costo_unitario = inv.costo_promedio

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.utcnow()
        except ValueError:
            fecha = datetime.utcnow()

        saldo_cant, costo_prom, saldo_val = _actualizar_inventario(producto_id, tipo, cantidad, costo_unitario)

        k = Kardex(
            producto_id=producto_id,
            empresa_id=empresa_id,
            fecha=fecha,
            tipo=tipo,
            documento=documento,
            concepto=concepto,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            costo_total=round(cantidad * costo_unitario, 2),
            saldo_cantidad=saldo_cant,
            costo_promedio=costo_prom,
            saldo_valor=saldo_val,
            usuario_id=current_user.id,
        )
        db.session.add(k)
        db.session.commit()
        flash('Ajuste registrado correctamente.', 'success')
        return redirect(url_for('inventario.ajuste'))

    return render_template('inventario/ajuste.html', productos=productos, empresas=empresas)


# ─── KARDEX ─────────────────────────────────────────────────────────────────

@inventario_bp.route('/kardex/<int:pid>')
@login_required
def kardex(pid):
    producto = Producto.query.get_or_404(pid)
    inv = InventarioActual.query.filter_by(producto_id=pid).first()
    movimientos = (Kardex.query
                   .filter_by(producto_id=pid)
                   .order_by(Kardex.fecha.desc(), Kardex.id.desc())
                   .all())
    return render_template('inventario/kardex.html', producto=producto,
                           inv=inv, movimientos=movimientos)
