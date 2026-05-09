"""
database.py
Configuración de conexión a PostgreSQL con SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ── Ajusta estos valores según tu entorno ──────────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "123456"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "superstor"
DB_SCHEMA   = "public"
# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_session():
    """Retorna una sesión lista para usar (ciérrala tú mismo)."""
    return SessionLocal()