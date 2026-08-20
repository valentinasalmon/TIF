from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.services.caso_service import CasoService, CasoDuplicadoError, PermisoDenegadoError

casos_bp = Blueprint("casos", __name__, url_prefix="/casos")
caso_service = CasoService()


@casos_bp.route("/")
@login_required
def listar():
    casos = caso_service.listar_casos_de_usuario(current_user.id)
    return render_template("casos/listar.html", casos=casos)


@casos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        try:
            caso_service.crear_caso(
                usuario_id=current_user.id,
                numero_expediente=request.form.get("numero_expediente"),
                titulo=request.form.get("titulo"),
                descripcion=request.form.get("descripcion"),
                tipo=request.form.get("tipo"),
            )
        except CasoDuplicadoError as error:
            flash(str(error))
            return redirect(url_for("casos.crear"))

        flash("Caso creado correctamente")
        return redirect(url_for("casos.listar"))

    return render_template("casos/crear.html")


@casos_bp.route("/<int:caso_id>")
@login_required
def detalle(caso_id):
    caso = caso_service.obtener_caso(caso_id)
    if not caso_service.puede_acceder(caso, current_user):
        flash("No tenés permiso para ver este caso")
        return redirect(url_for("casos.listar"))
    return render_template("casos/detalle.html", caso=caso)


@casos_bp.route("/<int:caso_id>/editar", methods=["GET", "POST"])
@login_required
def editar(caso_id):
    caso = caso_service.obtener_caso(caso_id)
    if not caso_service.puede_acceder(caso, current_user):
        flash("No tenés permiso para editar este caso")
        return redirect(url_for("casos.listar"))

    if request.method == "POST":
        try:
            caso_service.actualizar_caso(
                caso,
                current_user,
                titulo=request.form.get("titulo"),
                descripcion=request.form.get("descripcion"),
                tipo=request.form.get("tipo"),
                estado=request.form.get("estado"),
            )
        except PermisoDenegadoError as error:
            flash(str(error))
            return redirect(url_for("casos.listar"))

        flash("Caso actualizado")
        return redirect(url_for("casos.detalle", caso_id=caso.id))

    return render_template("casos/editar.html", caso=caso)
