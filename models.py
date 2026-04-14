from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256))
    rol = db.Column(db.String(20), default='vendedor')  # admin, bodeguero, vendedor
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'


class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20))

    def __repr__(self):
        return f'<Empresa {self.nombre}>'


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    unidad = db.Column(db.String(20), default='UND')
    stock_minimo = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)

    categoria = db.relationship('Categoria', backref='productos')

    def __repr__(self):
        return f'<Producto {self.codigo} - {self.nombre}>'


class Kardex(db.Model):
    __tablename__ = 'kardex'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(20), nullable=False)  # ENTRADA, SALIDA, AJUSTE_MAS, AJUSTE_MENOS
    documento = db.Column(db.String(50))
    concepto = db.Column(db.String(200))
    cantidad = db.Column(db.Float, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Float)
    saldo_cantidad = db.Column(db.Float)
    costo_promedio = db.Column(db.Float)
    saldo_valor = db.Column(db.Float)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    producto = db.relationship('Producto', backref='movimientos')
    empresa = db.relationship('Empresa')
    usuario = db.relationship('Usuario')

    def __repr__(self):
        return f'<Kardex {self.tipo} {self.producto_id} {self.cantidad}>'


class InventarioActual(db.Model):
    __tablename__ = 'inventario_actual'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), unique=True, nullable=False)
    stock = db.Column(db.Float, default=0)
    costo_promedio = db.Column(db.Float, default=0)
    valor_total = db.Column(db.Float, default=0)

    producto = db.relationship('Producto', backref='inventario_actual', uselist=False)

    def __repr__(self):
        return f'<Inventario {self.producto_id} stock={self.stock}>'
