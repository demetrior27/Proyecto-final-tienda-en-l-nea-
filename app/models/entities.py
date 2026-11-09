from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    password: str
    rol: str = Field(default="cliente")  # "cliente" o "admin"

    carrito: Optional["Carrito"] = Relationship(back_populates="usuario")
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    descripcion: str

    productos: List["Producto"] = Relationship(back_populates="categoria")

class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    precio: float
    stock: int
    imagen: str  # Ruta local ej: "/Assets/prod1.svg"
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")

    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    carrito_items: List["CarritoItem"] = Relationship(back_populates="producto")
    pedido_items: List["PedidoItem"] = Relationship(back_populates="producto")

class Carrito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(unique=True, foreign_key="usuario.id")

    usuario: Optional[Usuario] = Relationship(back_populates="carrito")
    items: List["CarritoItem"] = Relationship(back_populates="carrito")

class CarritoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    carrito_id: int = Field(foreign_key="carrito.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int

    carrito: Optional[Carrito] = Relationship(back_populates="items")
    producto: Optional[Producto] = Relationship(back_populates="carrito_items")

class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    total: float
    estado: str = Field(default="pendiente")  # pendiente, procesando, enviado, entregado

    usuario: Optional[Usuario] = Relationship(back_populates="pedidos")
    items: List["PedidoItem"] = Relationship(back_populates="pedido")

class PedidoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int
    precio_unitario: float

    pedido: Optional[Pedido] = Relationship(back_populates="items")
    producto: Optional[Producto] = Relationship(back_populates="pedido_items")