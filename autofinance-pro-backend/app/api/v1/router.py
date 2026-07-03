"""Agregador de todos los routers de la versión 1 de la API."""
from fastapi import APIRouter

from app.api.v1 import auth, clientes, creditos, entidades, reportes, simulador, vehiculos

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(clientes.router)
api_router.include_router(vehiculos.router)
api_router.include_router(entidades.router)
api_router.include_router(simulador.router)
api_router.include_router(creditos.router)
api_router.include_router(reportes.router)
