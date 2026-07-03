"""
Punto de entrada de la aplicación FastAPI — AutoFinance Pro API.

Responsabilidades de este módulo (y sólo estas):
  1. Crear la instancia de FastAPI.
  2. Configurar middlewares transversales (CORS).
  3. Registrar manejadores globales de excepciones de dominio -> HTTP.
  4. Montar el router agregador de la API.
  5. Exponer un healthcheck.

Toda la lógica de negocio vive en app/services; toda la persistencia vive en
app/repositories y app/models. Este archivo no debería crecer con el tiempo.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.utils.exceptions import (
    CredencialesInvalidasError,
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El esquema de la base de datos se gestiona con Alembic
    # (`alembic upgrade head`), no con create_all(). Ver alembic/env.py.
    yield


tags_metadata = [
    {
        "name": "Autenticación",
        "description": "Registro, login (OAuth2 password flow) y datos del usuario autenticado.",
    },
    {
        "name": "Clientes",
        "description": "CRUD de clientes titulares de créditos vehiculares.",
    },
    {
        "name": "Vehículos",
        "description": "Catálogo de vehículos financiables (marca, modelo, precio, año).",
    },
    {
        "name": "Entidades Financieras",
        "description": "Bancos, cajas municipales y financieras que otorgan los créditos.",
    },
    {
        "name": "Simulador",
        "description": "Calcula cronograma e indicadores (VAN/TIR/TCEA) en memoria, sin persistir nada.",
    },
    {
        "name": "Créditos Vehiculares",
        "description": "Créditos ya registrados en base de datos: alta y consulta de detalle completo.",
    },
    {
        "name": "Reportes",
        "description": "Exportación en PDF del resumen y del cronograma de un crédito.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API REST para la simulación y gestión de créditos vehiculares bajo "
        "la modalidad de Compra Inteligente, método francés vencido "
        "ordinario (proyecto AutoFinance Pro)."
    ),
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción: restringir a los dominios del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Traducción de excepciones de dominio a respuestas HTTP -----------------
@app.exception_handler(RecursoNoEncontradoError)
async def handler_no_encontrado(request: Request, exc: RecursoNoEncontradoError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(RecursoDuplicadoError)
async def handler_duplicado(request: Request, exc: RecursoDuplicadoError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(CredencialesInvalidasError)
async def handler_credenciales(request: Request, exc: CredencialesInvalidasError):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(ReglaNegocioError)
async def handler_regla_negocio(request: Request, exc: ReglaNegocioError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.get("/health", tags=["Salud"])
def healthcheck():
    """Verifica que la API esté arriba (sin comprobar la conexión a la base de datos)."""
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse(url="/docs")


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
