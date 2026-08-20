import os


class Config:
    """Configuración base. Strategy compartida por todos los entornos."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "clave-de-testing"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


CONFIG_POR_NOMBRE = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def obtener_config(nombre_entorno=None):
    """Resuelve la clase de configuración a partir del nombre de entorno o de FLASK_ENV."""
    nombre_entorno = nombre_entorno or os.getenv("FLASK_ENV", "development")
    return CONFIG_POR_NOMBRE.get(nombre_entorno, DevelopmentConfig)
