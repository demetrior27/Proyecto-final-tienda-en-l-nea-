from fastapi import APIRouter, Depends
from sqlmodel import Session
from db.session import get_session
from dependencies.auth_dep import get_current_user, get_admin_user
from models.entities import Usuario
from schemas.dtos import (
    UsuarioCreate, LoginRequest, UsuarioRead, CategoriaCreate,
    ProductoCreate, CarritoAdd, CarritoUpdateCant, EstadoPedidoUpdate
)
from services import store_service

router = APIRouter()

# --- AUTH ---
@router.post("/auth/register", response_model=UsuarioRead, tags=["Autenticación"])
def registrar(datos: UsuarioCreate, session: Session = Depends(get_session)):
    return store_service.register_user(session, datos)

@router.post("/auth/login", tags=["Autenticación"])
def login(datos: LoginRequest, session: Session = Depends(get_session)):
    return store_service.login_user(session, datos)

@router.get("/auth/me", response_model=UsuarioRead, tags=["Autenticación"])
def perfil(user: Usuario = Depends(get_current_user)):
    return user

# --- CATEGORÍAS ---
@router.get("/categorias/", tags=["Categorías"])
def obtener_categorias(session: Session = Depends(get_session)):
    return store_service.list_categorias(session)

@router.post("/categorias/", tags=["Categorías"])
def crear_categoria(datos: CategoriaCreate, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.create_categoria(session, datos)

@router.put("/categorias/{id}", tags=["Categorías"])
def actualizar_categoria(id: int, datos: CategoriaCreate, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.update_categoria(session, id, datos)

@router.delete("/categorias/{id}", tags=["Categorías"])
def eliminar_categoria(id: int, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.delete_categoria(session, id)

# --- PRODUCTOS ---
@router.get("/productos/", tags=["Productos"])
def listar_productos(buscar: str | None = None, categoria_id: int | None = None, session: Session = Depends(get_session)):
    return store_service.list_productos(session, buscar, categoria_id)

@router.get("/productos/aleatorios", tags=["Productos"])
def productos_aleatorios(session: Session = Depends(get_session)):
    return store_service.random_productos(session, 4)

@router.get("/productos/{id}", tags=["Productos"])
def detalle_producto(id: int, session: Session = Depends(get_session)):
    return store_service.get_producto(session, id)

@router.post("/productos/", tags=["Productos"])
def crear_producto(datos: ProductoCreate, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.create_producto(session, datos)

@router.put("/productos/{id}", tags=["Productos"])
def actualizar_producto(id: int, datos: ProductoCreate, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.update_producto(session, id, datos)

@router.delete("/productos/{id}", tags=["Productos"])
def eliminar_producto(id: int, session: Session = Depends(get_session), admin: Usuario = Depends(get_admin_user)):
    return store_service.delete_producto(session, id)

# --- CARRITO ---
@router.get("/carrito/", tags=["Carrito"])
def ver_carrito(user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.view_cart(session, user.id)

@router.post("/carrito/items", tags=["Carrito"])
def agregar_al_carrito(datos: CarritoAdd, user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.add_to_cart(session, user.id, datos)

@router.put("/carrito/items/{item_id}", tags=["Carrito"])
def modificar_cantidad_carrito(item_id: int, datos: CarritoUpdateCant, user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.update_cart_item(session, user.id, item_id, datos.cantidad)

@router.delete("/carrito/items/{item_id}", tags=["Carrito"])
def eliminar_del_carrito(item_id: int, user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.remove_cart_item(session, user.id, item_id)

# --- PEDIDOS ---
@router.post("/pedidos/", tags=["Pedidos"])
def confirmar_pedido(user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.create_order(session, user.id)

@router.get("/pedidos/mis-pedidos", tags=["Pedidos"])
def mis_pedidos(user: Usuario = Depends(get_current_user), session: Session = Depends(get_session)):
    return store_service.list_user_orders(session, user.id)

@router.get("/pedidos/admin", tags=["Pedidos"])
def todos_los_pedidos(admin: Usuario = Depends(get_admin_user), session: Session = Depends(get_session)):
    return store_service.list_all_orders(session)

@router.put("/pedidos/{id}/estado", tags=["Pedidos"])
def cambiar_estado_pedido(id: int, datos: EstadoPedidoUpdate, admin: Usuario = Depends(get_admin_user), session: Session = Depends(get_session)):
    return store_service.update_order_status(session, id, datos.estado)