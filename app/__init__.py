from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

from app.config import obtener_config

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(obtener_config(config_name))

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        from app import models  # noqa: F401  pylint: disable=unused-import
        db.create_all()

        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)

        from app.routes.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp)

        from app.routes.casos import casos_bp
        app.register_blueprint(casos_bp)

    @app.route("/")
    def hello():
        return "Sistema funcionando correctamente"

    return app
