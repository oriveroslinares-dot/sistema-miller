"""Datos iniciales: categorías, empresas y 3 usuarios."""
from app import app
from models import db, Categoria, Empresa, Usuario


def seed():
    with app.app_context():
        db.create_all()

        # Categorías
        for nombre in ['Electrodomésticos', 'Muebles', 'Otros']:
            if not Categoria.query.filter_by(nombre=nombre).first():
                db.session.add(Categoria(nombre=nombre))

        # Empresas
        empresas = [
            ('Electrodomésticos Miller S.A.S', '901201234-5'),
            ('ElectroMiller', '901201234-5'),
        ]
        for nombre, nit in empresas:
            if not Empresa.query.filter_by(nombre=nombre).first():
                db.session.add(Empresa(nombre=nombre, nit=nit))

        db.session.commit()

        # Usuarios
        usuarios = [
            ('admin',      'Administrador',  'admin123',   'admin'),
            ('bodeguero',  'Bodeguero',       'miller456',  'bodeguero'),
            ('vendedor',   'Vendedor',        'miller789',  'vendedor'),
        ]
        for username, nombre, pwd, rol in usuarios:
            if not Usuario.query.filter_by(username=username).first():
                u = Usuario(username=username, nombre=nombre, rol=rol, activo=True)
                u.set_password(pwd)
                db.session.add(u)

        db.session.commit()
        print("Base de datos inicializada correctamente.")
        print("\nUsuarios creados:")
        print("  admin     / admin123   (Administrador)")
        print("  bodeguero / miller456  (Bodeguero)")
        print("  vendedor  / miller789  (Vendedor)")


if __name__ == '__main__':
    seed()
