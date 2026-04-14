# Sistema de Inventario – Electrodomésticos Miller

Sistema web de inventario unificado para **Electrodomésticos Miller S.A.S** y **ElectroMiller** (Facatativá, Cundinamarca).

## Características

- Inventario unificado con clasificación: **Electrodomésticos**, **Muebles**, **Otros**
- Codificación automática de productos (ELE-XXXX / MUE-XXXX / OTR-XXXX)
- **Costo promedio ponderado** automático en cada movimiento
- Entradas, salidas y ajustes de inventario con kardex por producto
- Alertas de stock mínimo en el dashboard
- 3 usuarios con roles: Administrador, Bodeguero, Vendedor
- Reportes de stock actual y movimientos con filtros
- Soporte para ambas empresas (Electrodomésticos Miller SAS / ElectroMiller)

## Tecnología

- Python 3 + Flask
- SQLite (base de datos local)
- Bootstrap 5

## Instalación

```bash
pip install -r requirements.txt
python seed.py       # Crea la BD e inicializa datos
python app.py        # Inicia el servidor
```

Abre `http://localhost:5000` en tu navegador.

## Usuarios por defecto

| Usuario    | Contraseña  | Rol           |
|------------|-------------|---------------|
| admin      | admin123    | Administrador |
| bodeguero  | miller456   | Bodeguero     |
| vendedor   | miller789   | Vendedor      |

> **Cambia las contraseñas al primer ingreso.**
