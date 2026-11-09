import random
from fastapi import HTTPException
from sqlmodel import Session, select
from models.entities import Usuario, Categoria, Producto, Carrito, CarritoItem, Pedido, PedidoItem
from schemas.dtos import UsuarioCreate, LoginRequest, CategoriaCreate, ProductoCreate, CarritoAdd
from core.security import get_password_hash, verify_password, create_access_token

# --- AUTENTICACIÓN ---
def register_user(session: Session, datos: UsuarioCreate):
    if session.exec(select(Usuario).where(Usuario.email == datos.email)).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password=get_password_hash(datos.password),
        rol=datos.rol
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    carrito = Carrito(usuario_id=user.id)
    session.add(carrito)
    session.commit()
    return user

def login_user(session: Session, datos: LoginRequest):
    user = session.exec(select(Usuario).where(Usuario.email == datos.email)).first()
    if not user or not verify_password(datos.password, user.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    token = create_access_token({"sub": user.email, "rol": user.rol})
    return {"access_token": token, "token_type": "bearer", "usuario": {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}}

# --- CATEGORÍAS ---
def list_categorias(session: Session):
    return session.exec(select(Categoria)).all()

def create_categoria(session: Session, datos: CategoriaCreate):
    cat = Categoria.model_validate(datos)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat

def update_categoria(session: Session, id: int, datos: CategoriaCreate):
    cat = session.get(Categoria, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat.nombre = datos.nombre
    cat.descripcion = datos.descripcion
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat

def delete_categoria(session: Session, id: int):
    cat = session.get(Categoria, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    session.delete(cat)
    session.commit()
    return {"mensaje": "Categoría eliminada"}

# --- PRODUCTOS ---
def format_prod(p: Producto, session: Session):
    cat = session.get(Categoria, p.categoria_id) if p.categoria_id else None
    return {
        "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
        "precio": p.precio, "stock": p.stock, "imagen": p.imagen,
        "categoria_id": p.categoria_id,
        "categoria_nombre": cat.nombre if cat else "Sin categoría"
    }

def list_productos(session: Session, buscar: str | None = None, categoria_id: int | None = None):
    prods = session.exec(select(Producto)).all()
    if categoria_id:
        prods = [p for p in prods if p.categoria_id == categoria_id]
    if buscar:
        q = buscar.lower()
        prods = [p for p in prods if q in p.nombre.lower() or q in p.descripcion.lower()]
    return [format_prod(p, session) for p in prods]

def random_productos(session: Session, limite: int = 4):
    prods = session.exec(select(Producto)).all()
    seleccion = random.sample(prods, min(len(prods), limite))
    return [format_prod(p, session) for p in seleccion]

def get_producto(session: Session, id: int):
    p = session.get(Producto, id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return format_prod(p, session)

def create_producto(session: Session, datos: ProductoCreate):
    if datos.precio < 0 or datos.stock < 0:
        raise HTTPException(status_code=400, detail="Precio y stock deben ser positivos")
    p = Producto.model_validate(datos)
    session.add(p)
    session.commit()
    session.refresh(p)
    return format_prod(p, session)

def update_producto(session: Session, id: int, datos: ProductoCreate):
    p = session.get(Producto, id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.nombre = datos.nombre
    p.descripcion = datos.descripcion
    p.precio = datos.precio
    p.stock = datos.stock
    p.imagen = datos.imagen
    p.categoria_id = datos.categoria_id
    session.add(p)
    session.commit()
    session.refresh(p)
    return format_prod(p, session)

def delete_producto(session: Session, id: int):
    p = session.get(Producto, id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    session.delete(p)
    session.commit()
    return {"mensaje": "Producto eliminado"}

# --- CARRITO ---
def get_or_create_cart(session: Session, user_id: int) -> Carrito:
    cart = session.exec(select(Carrito).where(Carrito.usuario_id == user_id)).first()
    if not cart:
        cart = Carrito(usuario_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart

def view_cart(session: Session, user_id: int):
    cart = get_or_create_cart(session, user_id)
    items = session.exec(select(CarritoItem).where(CarritoItem.carrito_id == cart.id)).all()
    detalle = []
    total = 0.0
    for item in items:
        prod = session.get(Producto, item.producto_id)
        if prod:
            subtotal = round(prod.precio * item.cantidad, 2)
            total += subtotal
            detalle.append({
                "item_id": item.id,
                "producto_id": prod.id,
                "nombre": prod.nombre,
                "precio": prod.precio,
                "imagen": prod.imagen,
                "cantidad": item.cantidad,
                "stock_disponible": prod.stock,
                "subtotal": subtotal
            })
    return {"carrito_id": cart.id, "items": detalle, "total": round(total, 2)}

def add_to_cart(session: Session, user_id: int, datos: CarritoAdd):
    prod = session.get(Producto, datos.producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if datos.cantidad <= 0 or prod.stock < datos.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    cart = get_or_create_cart(session, user_id)
    item = session.exec(
        select(CarritoItem).where(CarritoItem.carrito_id == cart.id, CarritoItem.producto_id == prod.id)
    ).first()

    if item:
        if prod.stock < (item.cantidad + datos.cantidad):
            raise HTTPException(status_code=400, detail="La cantidad supera el stock disponible")
        item.cantidad += datos.cantidad
        session.add(item)
    else:
        nuevo = CarritoItem(carrito_id=cart.id, producto_id=prod.id, cantidad=datos.cantidad)
        session.add(nuevo)
    session.commit()
    return view_cart(session, user_id)

def update_cart_item(session: Session, user_id: int, item_id: int, cantidad: int):
    item = session.get(CarritoItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    prod = session.get(Producto, item.producto_id)
    if cantidad <= 0:
        session.delete(item)
    else:
        if prod.stock < cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        item.cantidad = cantidad
        session.add(item)
    session.commit()
    return view_cart(session, user_id)

def remove_cart_item(session: Session, user_id: int, item_id: int):
    item = session.get(CarritoItem, item_id)
    if item:
        session.delete(item)
        session.commit()
    return view_cart(session, user_id)

# --- PEDIDOS ---
def create_order(session: Session, user_id: int):
    cart_data = view_cart(session, user_id)
    if not cart_data["items"]:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # Validar stock antes de procesar
    for it in cart_data["items"]:
        prod = session.get(Producto, it["producto_id"])
        if not prod or prod.stock < it["cantidad"]:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {it['nombre']}")

    pedido = Pedido(usuario_id=user_id, total=cart_data["total"], estado="pendiente")
    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    for it in cart_data["items"]:
        prod = session.get(Producto, it["producto_id"])
        prod.stock -= it["cantidad"]  # Descontar stock
        session.add(prod)
        p_item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=prod.id,
            cantidad=it["cantidad"],
            precio_unitario=prod.precio
        )
        session.add(p_item)

    # Vaciar carrito
    cart_items = session.exec(select(CarritoItem).where(CarritoItem.carrito_id == cart_data["carrito_id"])).all()
    for ci in cart_items:
        session.delete(ci)

    session.commit()
    return format_order(session, pedido)

def format_order(session: Session, pedido: Pedido):
    user = session.get(Usuario, pedido.usuario_id)
    items = session.exec(select(PedidoItem).where(PedidoItem.pedido_id == pedido.id)).all()
    detalles = []
    for i in items:
        prod = session.get(Producto, i.producto_id)
        detalles.append({
            "producto_id": i.producto_id,
            "nombre": prod.nombre if prod else "Producto eliminado",
            "cantidad": i.cantidad,
            "precio_unitario": i.precio_unitario,
            "subtotal": round(i.cantidad * i.precio_unitario, 2)
        })
    return {
        "id": pedido.id,
        "usuario_email": user.email if user else "",
        "fecha": pedido.fecha,
        "total": pedido.total,
        "estado": pedido.estado,
        "items": detalles
    }

def list_user_orders(session: Session, user_id: int):
    pedidos = session.exec(select(Pedido).where(Pedido.usuario_id == user_id)).all()
    return [format_order(session, p) for p in pedidos]

def list_all_orders(session: Session):
    pedidos = session.exec(select(Pedido)).all()
    return [format_order(session, p) for p in pedidos]

def update_order_status(session: Session, pedido_id: int, nuevo_estado: str):
    estados_validos = ["pendiente", "procesando", "enviado", "entregado"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no válido")
    pedido = session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = nuevo_estado
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return format_order(session, pedido)