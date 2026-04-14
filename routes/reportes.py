from flask import Blueprint, render_template, request
from flask_login import login_required
from models import Producto, InventarioActual, Kardex, Categoria
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')


@reportes_bp.route('/stock')
@login_required
def stock():
    categoria_id = request.args.get('categoria', type=int)
    alertas = request.args.get('alertas', type=int)

    query = (InventarioActual.query
             .join(InventarioActual.producto)
             .filter(Producto.activo == True))

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    items = query.order_by(Producto.codigo).all()

    if alertas:
        items = [i for i in items if i.stock <= i.producto.stock_minimo]

    categorias = Categoria.query.all()
    total_valor = sum(i.valor_total for i in items)

    return render_template('reportes/stock.html', items=items,
                           categorias=categorias, categoria_sel=categoria_id,
                           total_valor=total_valor, alertas=alertas)


@reportes_bp.route('/movimientos')
@login_required
def movimientos():
    desde = request.args.get('desde', '')
    hasta = request.args.get('hasta', '')
    tipo = request.args.get('tipo', '')
    categoria_id = request.args.get('categoria', type=int)

    query = Kardex.query.join(Kardex.producto)

    if desde:
        query = query.filter(Kardex.fecha >= desde)
    if hasta:
        query = query.filter(Kardex.fecha <= hasta + ' 23:59:59')
    if tipo:
        query = query.filter(Kardex.tipo == tipo)
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    movs = query.order_by(Kardex.fecha.desc(), Kardex.id.desc()).limit(500).all()
    categorias = Categoria.query.all()

    return render_template('reportes/movimientos.html', movimientos=movs,
                           categorias=categorias, categoria_sel=categoria_id,
                           desde=desde, hasta=hasta, tipo_sel=tipo)
