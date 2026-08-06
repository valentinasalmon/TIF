from app import db
from flask_login import UserMixin
from datetime import datetime
import bcrypt

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="perito")  # perito, abogado, aseguradora, administrador
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def generar_token_recuperacion(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.email, salt="recuperacion-password")

    @staticmethod
    def verificar_token_recuperacion(token, max_age=3600):
        from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(token, salt="recuperacion-password", max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None
        return Usuario.query.filter_by(email=email).first()



from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
