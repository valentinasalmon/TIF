from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Email o contraseña incorrectos")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

from app.services.decoradores import requiere_rol

@auth_bp.route("/admin-test")
@login_required
@requiere_rol("administrador")
def admin_test():
    return "Acceso concedido: sos administrador"

@auth_bp.route("/recuperar-password", methods=["GET", "POST"])
def recuperar_password():
    if request.method == "POST":
        email = request.form.get("email")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = usuario.generar_token_recuperacion()
            enlace = url_for("auth.resetear_password", token=token, _external=True)
            # Por ahora lo mostramos en consola, más adelante se envía por email real
            print(f"[SIMULACIÓN DE EMAIL] Enlace de recuperación para {email}: {enlace}")

        flash("Si el email existe en el sistema, se envió un enlace de recuperación")
        return redirect(url_for("auth.login"))

    return render_template("recuperar_password.html")

@auth_bp.route("/resetear-password/<token>", methods=["GET", "POST"])
def resetear_password(token):
    usuario = Usuario.verificar_token_recuperacion(token)

    if not usuario:
        flash("El enlace es inválido o expiró")
        return redirect(url_for("auth.recuperar_password"))

    if request.method == "POST":
        nueva_password = request.form.get("password")
        usuario.set_password(nueva_password)
        from app import db
        db.session.commit()
        flash("Contraseña actualizada correctamente")
        return redirect(url_for("auth.login"))

    return render_template("resetear_password.html")
