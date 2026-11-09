import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from db.session import engine, create_db_and_tables
from models.entities import Usuario, Categoria, Producto, Carrito
from core.security import get_password_hash
from controller.routers import router

app = FastAPI(title="Proyecto Final - Tienda Virtual Full Stack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asegurar que la carpeta Assets exista y generar imágenes SVG locales para los productos
os.makedirs("Assets", exist_ok=True)
app.mount("/Assets", StaticFiles(directory="Assets"), name="Assets")

def generar_svg_locales():
    svgs = {
        "laptop.svg": ("#1e3a8a", "Laptop Pro 15"),
        "mouse.svg": ("#065f46", "Mouse Gamer RGB"),
        "teclado.svg": ("#3730a3", "Teclado Mecanico"),
        "monitor.svg": ("#0f766e", "Monitor 27 UHD"),
        "auriculares.svg": ("#7c2d12", "Audifonos Studio"),
        "silla.svg": ("#4c1d95", "Silla Ergonomica"),
    }
    for filename, (color, texto) in svgs.items():
        path = os.path.join("Assets", filename)
        if not os.path.exists(path):
            contenido = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="280">
                <rect width="100%" height="100%" fill="{color}"/>
                <text x="50%" y="50%" fill="#ffffff" font-family="sans-serif" font-size="24" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{texto}</text>
            </svg>'''
            with open(path, "w", encoding="utf-8") as f:
                f.write(contenido)

def seed_initial_data():
    generar_svg_locales()
    with Session(engine) as session:
        if not session.exec(select(Usuario)).first():
            admin = Usuario(nombre="Administrador", email="admin@tienda.com", password=get_password_hash("admin123"), rol="admin")
            cliente = Usuario(nombre="Cliente Demo", email="cliente@tienda.com", password=get_password_hash("cliente123"), rol="cliente")
            session.add(admin)
            session.add(cliente)
            session.commit()
            session.refresh(admin)
            session.refresh(cliente)
            session.add(Carrito(usuario_id=admin.id))
            session.add(Carrito(usuario_id=cliente.id))

            cat1 = Categoria(nombre="Computadoras", descripcion="Equipos portátiles y monitores")
            cat2 = Categoria(nombre="Periféricos", descripcion="Teclados, ratones y audio")
            cat3 = Categoria(nombre="Mobiliario", descripcion="Sillas y accesorios de oficina")
            session.add_all([cat1, cat2, cat3])
            session.commit()
            session.refresh(cat1)
            session.refresh(cat2)
            session.refresh(cat3)

            productos_iniciales = [
                Producto(nombre="Laptop Pro 15", descripcion="Portátil 16GB RAM 512GB SSD", precio=850.00, stock=10, imagen="/Assets/laptop.svg", categoria_id=cat1.id),
                Producto(nombre="Monitor 27 UHD", descripcion="Monitor IPS 4K 144Hz", precio=320.00, stock=8, imagen="/Assets/monitor.svg", categoria_id=cat1.id),
                Producto(nombre="Mouse Gamer RGB", descripcion="Sensor óptico 16000 DPI", precio=35.50, stock=25, imagen="/Assets/mouse.svg", categoria_id=cat2.id),
                Producto(nombre="Teclado Mecánico", descripcion="Switches rojos silenciosos", precio=65.00, stock=15, imagen="/Assets/teclado.svg", categoria_id=cat2.id),
                Producto(nombre="Audífonos Studio", descripcion="Cancelación activa de ruido", precio=110.00, stock=12, imagen="/Assets/auriculares.svg", categoria_id=cat2.id),
                Producto(nombre="Silla Ergonómica", descripcion="Soporte lumbar ajustable", precio=195.00, stock=5, imagen="/Assets/silla.svg", categoria_id=cat3.id),
            ]
            session.add_all(productos_iniciales)
            session.commit()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_initial_data()

app.include_router(router)