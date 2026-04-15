from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, Usuario, InventarioActual, Producto

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para continuar.'
    login_manager.login_message_category = 'info'

    from routes.auth import auth_bp
    from routes.productos import productos_bp
    from routes.inventario import inventario_bp
    from routes.reportes import reportes_bp
    from routes.usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)

    from flask import Blueprint
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    @login_required
    def dashboard():
        total_productos = Producto.query.filter_by(activo=True).count()
        items = (InventarioActual.query
                 .join(InventarioActual.producto)
                 .filter(Producto.activo == True)
                 .all())
        valor_total = sum(i.valor_total for i in items)
        alertas = [i for i in items if i.stock <= i.producto.stock_minimo and i.producto.stock_minimo > 0]
        return render_template('dashboard.html',
                               total_productos=total_productos,
                               valor_total=valor_total,
                               alertas=alertas)

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


app = create_app()

# Inicializar BD y datos al arrancar (funciona con gunicorn y python directo)
with app.app_context():
    from seed import seed
    seed()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
