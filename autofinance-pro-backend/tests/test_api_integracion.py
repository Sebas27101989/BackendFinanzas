"""
Prueba de integración end-to-end sobre la API REST completa: registro de
usuario -> login -> creación de vehículo/entidad -> simulación -> registro
de crédito persistido -> consulta del detalle. Usa una base de datos SQLite
en memoria aislada por test (no toca autofinance_pro.db).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    from app import models  # noqa: F401 registra los modelos antes de crear tablas

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def _obtener_token(client: TestClient) -> str:
    client.post(
        "/api/v1/auth/registro",
        json={
            "username": "jperez",
            "password": "clave12345",
            "nombre": "Juan",
            "apellidos": "Pérez",
            "dni": "74859632",
            "telefono": "999999999",
            "correo": "juan.perez@example.com",
            "direccion": "Av. Siempre Viva 123",
            "ingresos_mensuales": 5000,
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "jperez", "password": "clave12345"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_flujo_completo_simular_y_registrar_credito(client: TestClient):
    token = _obtener_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload_simulacion = {
        "precio_vehiculo": 85000,
        "cuota_inicial": 17000,
        "moneda": "PEN",
        "tasa_interes": 10.7,
        "tipo_tasa": "Efectiva",
        "plazo_meses": 60,
        "cuota_balon_pct": 25,
        "tipo_gracia": "Ninguno",
        "meses_gracia": 0,
        "seguro_vehicular_mensual": 150,
        "seguro_desgravamen_mensual": 45,
        "gastos_administrativos": 200,
        "fecha_inicio": "2026-05-14",
    }

    resp_sim = client.post("/api/v1/simulador/simular", json=payload_simulacion, headers=headers)
    assert resp_sim.status_code == 200, resp_sim.text
    resultado = resp_sim.json()
    assert len(resultado["cronograma"]) == 60
    assert resultado["indicadores"]["cuota_regular"] == pytest.approx(1088.84, abs=1.0)

    vehiculo = client.post(
        "/api/v1/vehiculos",
        json={"marca": "Toyota", "modelo": "Corolla", "anio": 2024, "precio": 85000, "moneda": "PEN", "estado": "Nuevo"},
        headers=headers,
    ).json()
    entidad = client.post(
        "/api/v1/entidades-financieras",
        json={"nombre": "Banco Demo", "tipo_entidad": "Banco", "tasa_base": 10.7, "estado": "Activo"},
        headers=headers,
    ).json()
    cliente = client.get("/api/v1/clientes", headers=headers).json()[0]

    payload_credito = {**payload_simulacion, "id_cliente": cliente["id_cliente"], "id_vehiculo": vehiculo["id_vehiculo"], "id_entidad": entidad["id_entidad"]}
    resp_credito = client.post("/api/v1/creditos", json=payload_credito, headers=headers)
    assert resp_credito.status_code == 201, resp_credito.text
    detalle = resp_credito.json()
    id_credito = detalle["credito"]["id_credito"]

    resp_get = client.get(f"/api/v1/creditos/{id_credito}", headers=headers)
    assert resp_get.status_code == 200
    assert len(resp_get.json()["cronograma"]) == 60

    resp_pdf = client.get(f"/api/v1/reportes/creditos/{id_credito}/resumen.pdf", headers=headers)
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
