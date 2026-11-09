import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.session import create_db_and_tables
from controller.routers import router

app = FastAPI(title="Proyecto Final - Tienda Virtual Full Stack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sos.makedirs("Assets", exist_ok=True)
app.mount("/Assets", StaticFiles(directory="Assets"), name="Assets")

@app.on_event("startup")
def on_startup():

    create_db_and_tables()

app.include_router(router)
