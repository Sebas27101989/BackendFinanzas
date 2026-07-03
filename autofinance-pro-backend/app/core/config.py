"""
Configuración central de la aplicación.

Toda constante de configuración (conexión a BD, llaves de seguridad, parámetros
por defecto del motor financiero, etc.) vive aquí y se expone a través de una
única instancia `settings`, siguiendo el patrón de "single source of truth"
recomendado para separar configuración de lógica de negocio.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Metadatos de la aplicación -----------------------------------
    PROJECT_NAME: str = "AutoFinance Pro API"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"

    # --- Base de datos ---------------------------------------------------
    # PostgreSQL es el motor de la aplicación. Los tests de integración usan
    # su propio engine SQLite en memoria (ver tests/test_api_integracion.py),
    # por lo que no dependen de esta variable.
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/autofinance_pro"

    # --- Seguridad / JWT ---------------------------------------------------
    SECRET_KEY: str = "CHANGE_ME_super_secret_key_autofinance_pro"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 horas

    # --- Parámetros financieros por defecto (sección 6 del informe) -----
    # Frecuencias de capitalización admitidas para tasas nominales (TNA)
    FRECUENCIAS_CAPITALIZACION: dict = {
        "Diaria": 360,
        "Mensual": 12,
        "Bimestral": 6,
        "Trimestral": 4,
        "Cuatrimestral": 3,
        "Semestral": 2,
        "Anual": 1,
    }
    DIAS_ANIO_COMERCIAL: int = 360
    DIAS_MES_COMERCIAL: int = 30

    # Tasa de descuento (COK) por defecto utilizada para el cálculo del VAN
    # cuando la entidad financiera no especifica una propia.
    TASA_DESCUENTO_DEFECTO: float = 0.10  # 10% efectiva anual

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de Settings (evita releer .env)."""
    return Settings()


settings = get_settings()
