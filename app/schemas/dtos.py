from typing import Optional
from sqlmodel import SQLModel

class UsuarioCreate(SQLModel):
    nombre: str
    email: str
    password: str
    rol: str = "cliente"

class LoginRequest(SQLModel):
    email: str
    password: str

class UsuarioRead(SQLModel):
    id: int
    nombre: str
    email: str
    rol: str

class CategoriaCreate(SQLModel):
    nombre: str
    descripcion: str

class ProductoCreate(SQLModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    imagen: str
    categoria_id: int

class CarritoAdd(SQLModel):
    producto_id: int
    cantidad: int

class CarritoUpdateCant(SQLModel):
    cantidad: int

class EstadoPedidoUpdate(SQLModel):
    estado: str