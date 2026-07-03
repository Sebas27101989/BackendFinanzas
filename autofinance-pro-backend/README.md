# AutoFinance Pro — Backend

Backend en **Python + FastAPI** para *AutoFinance Pro*, el sistema de simulación
y gestión de créditos vehiculares (modalidad **Compra Inteligente**, método
francés vencido ordinario) descrito en el informe *"Trabajo Parcial —
Finanzas e Ingeniería Económica"* (UPC, 2026).

Este proyecto es el resultado de traducir ese informe (arquitectura,
definiciones financieras, casos de prueba y modelo de base de datos) en un
backend ejecutable, en capas, con separación clara de responsabilidades.
Ver también `AutoFinance_Pro_Arquitectura_Backend.docx` para el documento de
diseño completo (arquitectura, estructura, modelos y responsabilidades).

## Requisitos

- Python 3.11+
- pip
- PostgreSQL corriendo localmente (o accesible por red)

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # ajustar SECRET_KEY y DATABASE_URL
```

`DATABASE_URL` debe apuntar a una base de datos PostgreSQL existente, p. ej.:

```
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/autofinance_pro
```

Si la contraseña contiene caracteres especiales (`/`, `@`, `#`, etc.), deben
ir percent-encoded en la URL (ej. `/` → `%2F`).

Crear la base de datos si no existe (una vez, con `psql` o cualquier cliente):

```sql
CREATE DATABASE autofinance_pro;
```

## Migraciones (Alembic)

El esquema de la base de datos se gestiona con **Alembic**, no con
`create_all()`. La URL de conexión la toma de `app.core.config.settings`
(o sea, de `.env`) — no hace falta configurarla por separado en `alembic.ini`.

```bash
alembic upgrade head              # aplica todas las migraciones pendientes
alembic revision --autogenerate -m "descripción del cambio"   # tras modificar un modelo
alembic downgrade -1               # revertir la última migración
```

La migración inicial (`alembic/versions/d0c2f5902e02_esquema_inicial.py`)
crea las 7 tablas del modelo de datos (usuarios, clientes, vehículos,
entidades financieras, créditos vehiculares, cuotas, indicadores
financieros). Cualquier cambio futuro a un modelo en `app/models/` requiere
generar y aplicar una nueva migración con los comandos de arriba.

## Ejecutar la API

```bash
alembic upgrade head              # asegurar que el esquema esté al día
uvicorn app.main:app --reload
```

- Documentación interactiva (Swagger): http://localhost:8000/docs
- Documentación alternativa (ReDoc): http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/health

## Ejecutar las pruebas

```bash
pytest -v
```

Las pruebas de `tests/test_amortizacion_service.py` validan el motor de
amortización directamente contra los **3 Casos de Prueba** documentados en
la sección 7 del informe original (crédito estándar, gracia parcial y
gracia total), con tolerancias pequeñas para absorber el redondeo de las
tasas capturadas en las imágenes del informe. `tests/test_api_integracion.py`
corre un flujo end-to-end completo (registro → login → simulación → registro
de crédito → reporte PDF) sobre una base de datos SQLite en memoria.

## Estructura del proyecto

```
app/
├── main.py                  # arranque de FastAPI, CORS, manejo global de errores
├── core/                    # configuración, conexión a BD, seguridad (JWT/hash)
├── models/                  # entidades ORM (SQLAlchemy) — el "qué se guarda"
├── schemas/                 # DTOs Pydantic de entrada/salida — el "qué viaja por la API"
├── repositories/            # acceso a datos (SQL/ORM) — el "cómo se guarda"
├── services/                # lógica de negocio y motor financiero — el "cómo se calcula"
└── api/v1/                  # routers HTTP — el "cómo se expone"
tests/                       # pruebas unitarias e de integración
```

Ver el documento de arquitectura para el detalle de cada capa, el diagrama
de flujo de una petición y la justificación de la separación de
responsabilidades.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/registro` | Crea usuario + perfil de cliente |
| POST | `/api/v1/auth/login` | Devuelve JWT (`access_token`) |
| GET/POST | `/api/v1/clientes` | CRUD de clientes |
| GET/POST | `/api/v1/vehiculos` | CRUD del catálogo de vehículos |
| GET/POST | `/api/v1/entidades-financieras` | CRUD de entidades financieras |
| POST | `/api/v1/simulador/simular` | Simula un crédito (no persiste) |
| POST | `/api/v1/creditos` | Simula **y** persiste un crédito completo |
| GET | `/api/v1/creditos/{id}` | Detalle: crédito + cronograma + indicadores |
| GET | `/api/v1/reportes/creditos/{id}/resumen.pdf` | Reporte PDF de resumen |
| GET | `/api/v1/reportes/creditos/{id}/cronograma.pdf` | Reporte PDF del cronograma |

Todos los endpoints (excepto `/health`, `/auth/registro` y `/auth/login`)
requieren el header `Authorization: Bearer <token>`.

## Notas de diseño

- El motor financiero (`app/services/tasas_service.py`,
  `amortizacion_service.py`, `indicadores_service.py`) es **puro**: no
  importa FastAPI ni SQLAlchemy, por lo que se puede probar y reutilizar
  de forma aislada (incluso desde un script de línea de comandos).
- La cuota balón se calcula reduciendo el capital amortizable en
  `cuota_balon_pct` % antes de aplicar la fórmula francesa, y liquidando el
  saldo remanente (que incluye el interés compuesto de esa porción durante
  todo el plazo) como pago final — ver el docstring de
  `generar_cronograma()` para el detalle matemático completo.
- El VAN/TIR/TCEA se calculan con un resolutor Newton-Raphson (con
  respaldo por bisección) implementado sin dependencias externas, siguiendo
  al pie de la letra las fórmulas de las secciones 6.10 y 6.11 del informe.
