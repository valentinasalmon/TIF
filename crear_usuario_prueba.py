from app import create_app, db
from app.models.usuario import Usuario

app = create_app()

usuarios_prueba = [
    {"nombre": "Perito Prueba", "email": "perito@test.com", "rol": "perito"},
    {"nombre": "Abogado Prueba", "email": "abogado@test.com", "rol": "abogado"},
    {"nombre": "Aseguradora Prueba", "email": "aseguradora@test.com", "rol": "aseguradora"},
    {"nombre": "Admin Prueba", "email": "admin@test.com", "rol": "administrador"},
]

with app.app_context():
    for datos in usuarios_prueba:
        existente = Usuario.query.filter_by(email=datos["email"]).first()
        if not existente:
            nuevo = Usuario(nombre=datos["nombre"], email=datos["email"], rol=datos["rol"])
            nuevo.set_password("123456")
            db.session.add(nuevo)
            print(f"Usuario creado: {datos['email']} ({datos['rol']})")
        else:
            print(f"Ya existe: {datos['email']}")
    db.session.commit()