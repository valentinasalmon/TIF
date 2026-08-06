from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.caso import Caso
from app import db

casos_bp = Blueprint("casos", __name__, url_prefix="/casos")

@casos_bp.route("/")
@login_required
def listar():
    casos = Caso.query.filter_by(usuario_id=current_user.id).order_by(Caso.fecha_creacion.desc()).all()
    return render_template("casos/listar.html", casos=casos)

@casos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        numero_expediente = request.form.get("numero_expediente")
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        tipo = request.form.get("tipo")

        existente = Caso.query.filter_by(numero_expediente=numero_expediente).first()
        if existente:
            flash("Ya existe un caso con ese número de expediente")
            return redirect(url_for("casos.crear"))

        nuevo_caso = Caso(
            numero_expediente=numero_expediente,
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            usuario_id=current_user.id
        )
        db.session.add(nuevo_caso)
        db.session.commit()
        flash("Caso creado correctamente")
        return redirect(url_for("casos.listar"))

    return render_template("casos/crear.html")

@casos_bp.route("/<int:caso_id>")
@login_required
def detalle(caso_id):
    caso = Caso.query.get_or_404(caso_id)
    if caso.usuario_id != current_user.id and current_user.rol != "administrador":
        flash("No tenés permiso para ver este caso")
        return redirect(url_for("casos.listar"))
    return render_template("casos/detalle.html", caso=caso)

@casos_bp.route("/<int:caso_id>/editar", methods=["GET", "POST"])
@login_required
def editar(caso_id):
    caso = Caso.query.get_or_404(caso_id)
    if caso.usuario_id != current_user.id and current_user.rol != "administrador":
        flash("No tenés permiso para editar este caso")
        return redirect(url_for("casos.listar"))

    if request.method == "POST":
        caso.titulo = request.form.get("titulo")
        caso.descripcion = request.form.get("descripcion")
        caso.tipo = request.form.get("tipo")
        caso.estado = request.form.get("estado")
        db.session.commit()
        flash("Caso actualizado")
        return redirect(url_for("casos.detalle", caso_id=caso.id))

    return render_template("casos/editar.html", caso=caso)