# app/services/metadatos_service.py
#
# Módulo de análisis forense de metadatos (EXIF / XMP / PNG).
# Extrae campos, aplica reglas de severidad, clasifica y persiste el resultado.
#
# Cambios respecto de la versión anterior:
#  - extraer_exif() ahora devuelve también los nombres planos de los campos
#    (Make, Software, DateTimeOriginal...). Con "-G0:1" ExifTool antepone el
#    grupo ("EXIF:IFD0:Make") y los validadores, que buscan "Make", no
#    encontraban nada en JPEG/HEIC.
#  - validar_software() y validar_makernotes() convierten a str() antes de
#    .lower(): ExifTool devuelve números JSON para valores como "12".
#  - Las llamadas a ExifTool fuerzan encoding UTF-8 (Windows usa cp1252).

import subprocess
import json
import os
from datetime import datetime, timedelta

from PIL import Image

from app.repositories.analisis_repository import AnalisisRepository

# ============================================================
# Ruta al ejecutable de ExifTool
# ============================================================
# Si agregaste exiftool.exe al PATH del sistema, dejá simplemente "exiftool".
# Si lo dejaste dentro del proyecto (carpeta tools/), usá la ruta completa,
# calculada de forma relativa a este archivo para que funcione en cualquier PC.

EXIFTOOL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools", "exiftool.exe"
)

# ============================================================
# Configuración de reglas (listas y umbrales editables)
# ============================================================

SOFTWARE_CONOCIDO = [
    "photoshop", "gimp", "snapseed", "facetune", "lightroom",
    "midjourney", "dall-e", "dalle", "stable diffusion", "firefly",
    "canva", "picsart",
]

PALABRAS_CLAVE_GENERACION = [
    "prompt", "steps", "sampler", "cfg_scale", "seed", "negative_prompt",
]

MARCAS_CONOCIDAS = ["apple", "samsung", "xiaomi", "motorola", "huawei", "google"]

UMBRAL_MODIFYDATE_HORAS = 24

DIMENSIONES_TIPICAS_IA = {
    (512, 512), (768, 768), (1024, 1024), (1536, 1536), (2048, 2048),
}


# ============================================================
# Detección de formato
# ============================================================

def detectar_formato(imagen_path):
    """Lee los magic numbers del archivo para determinar el formato real."""
    with open(imagen_path, "rb") as f:
        cabecera = f.read(12)

    if cabecera.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if cabecera.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if cabecera[4:8] == b"ftyp" and (b"heic" in cabecera or b"heix" in cabecera):
        return "heic"
    return "desconocido"


# ============================================================
# Extracción
# ============================================================

def extraer_exif(imagen_path):
    """
    Ejecuta ExifTool sobre el archivo y devuelve un diccionario.

    Con "-G0:1" las claves llegan con grupo ("EXIF:IFD0:Make"). Se conservan
    esas claves (el chequeo de MakerNotes las necesita) y se agregan además los
    nombres planos ("Make") para que los validadores los encuentren. Si un
    nombre plano aparece en varios grupos, prevalece la primera aparición.

    Si no hay bloque EXIF, devuelve {} (no es un error).
    """
    try:
        resultado = subprocess.run(
            [EXIFTOOL_PATH, "-json", "-G0:1", imagen_path],
            capture_output=True, encoding="utf-8", errors="replace", timeout=15,
        )
        datos = json.loads(resultado.stdout)
        crudo = datos[0] if datos else {}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return {}

    plano = dict(crudo)
    for clave, valor in crudo.items():
        plano.setdefault(clave.split(":")[-1], valor)
    return plano


def extraer_xmp(imagen_path):
    """Extrae CreatorTool y History del bloque XMP (cualquier formato)."""
    try:
        resultado = subprocess.run(
            [EXIFTOOL_PATH, "-json", "-XMP:CreatorTool", "-XMP:History", imagen_path],
            capture_output=True, encoding="utf-8", errors="replace", timeout=15,
        )
        datos = json.loads(resultado.stdout)
        return datos[0] if datos else {}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return {}


def extraer_chunks_png(imagen_path):
    """Extrae los chunks de texto (tEXt/iTXt/zTXt) de un PNG vía Pillow."""
    try:
        with Image.open(imagen_path) as img:
            return dict(img.info)  # Pillow expone los chunks de texto acá
    except Exception:
        return {}


def obtener_dimensiones(imagen_path):
    with Image.open(imagen_path) as img:
        return img.width, img.height


def obtener_fecha_creacion_sistema(imagen_path):
    timestamp = os.path.getctime(imagen_path)
    return datetime.fromtimestamp(timestamp)


# ============================================================
# Validaciones (cada una devuelve una lista de anomalías, puede ser vacía)
# ============================================================

def validar_software(datos_exif, datos_xmp):
    software = str(datos_exif.get("Software") or "").lower()
    creator_tool = str(datos_xmp.get("CreatorTool") or "").lower()

    for nombre in SOFTWARE_CONOCIDO:
        if nombre in software or nombre in creator_tool:
            valor = datos_exif.get("Software") or datos_xmp.get("CreatorTool")
            return [{
                "campo_afectado": "Software/CreatorTool",
                "valor_detectado": valor,
                "descripcion": f'El archivo indica procesamiento con "{valor}".',
                "severidad": "directo",
            }]
    return []


def validar_historial_xmp(datos_xmp):
    history = datos_xmp.get("History")
    if history:
        return [{
            "campo_afectado": "xmpMM:History",
            "valor_detectado": str(history),
            "descripcion": "El archivo tiene un historial de edición registrado en XMP.",
            "severidad": "directo",
        }]
    return []


def validar_chunks_generacion(chunks_png):
    texto_completo = " ".join(str(v).lower() for v in chunks_png.values())
    encontradas = [p for p in PALABRAS_CLAVE_GENERACION if p in texto_completo]
    if encontradas:
        return [{
            "campo_afectado": "PNG:tEXt/iTXt",
            "valor_detectado": ", ".join(encontradas),
            "descripcion": (
                f"Se encontraron parámetros de generación de IA en los metadatos "
                f"del PNG: {', '.join(encontradas)}."
            ),
            "severidad": "directo",
        }]
    return []


def validar_makernotes(datos_exif):
    make = str(datos_exif.get("Make") or "").lower()
    tiene_makernotes = any(
        k for k in datos_exif.keys() if "makernotes" in k.lower()
    )
    if any(m in make for m in MARCAS_CONOCIDAS) and not tiene_makernotes:
        return [{
            "campo_afectado": "MakerNotes",
            "valor_detectado": "ausente",
            "descripcion": (
                f'El dispositivo declarado es "{datos_exif.get("Make")}", pero '
                f"no se encontró el bloque de datos propietario (MakerNotes) "
                f"que ese fabricante suele incluir."
            ),
            "severidad": "fuerte",
        }]
    return []


def _parsear_fecha_exif(valor):
    """EXIF suele usar formato 'YYYY:MM:DD HH:MM:SS'."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y:%m:%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def validar_cronologia(datos_exif, fecha_creacion_sistema):
    anomalias = []

    fecha_original = _parsear_fecha_exif(datos_exif.get("DateTimeOriginal"))
    fecha_modificacion = _parsear_fecha_exif(datos_exif.get("ModifyDate"))

    if fecha_original and fecha_creacion_sistema < fecha_original:
        anomalias.append({
            "campo_afectado": "CreateDate (sistema) / DateTimeOriginal",
            "valor_detectado": (
                f"sistema={fecha_creacion_sistema.isoformat()}, "
                f"exif={fecha_original.isoformat()}"
            ),
            "descripcion": (
                "El archivo aparece creado en el sistema antes de la fecha de "
                "captura declarada en EXIF, lo cual es cronológicamente imposible."
            ),
            "severidad": "fuerte",
        })

    if fecha_original and fecha_modificacion:
        diferencia = fecha_modificacion - fecha_original
        if diferencia > timedelta(hours=UMBRAL_MODIFYDATE_HORAS):
            anomalias.append({
                "campo_afectado": "ModifyDate / DateTimeOriginal",
                "valor_detectado": f"diferencia={diferencia}",
                "descripcion": (
                    f"La fecha de última modificación es posterior a la fecha de "
                    f"captura por más de {UMBRAL_MODIFYDATE_HORAS} horas "
                    f"({diferencia})."
                ),
                "severidad": "moderado",
            })

    return anomalias


def validar_bloque_captura(datos_exif):
    campos_captura = [
        "ExposureTime", "FNumber", "ISO", "FocalLength",
        "Flash", "ExposureProgram", "MeteringMode",
    ]
    tiene_dispositivo = datos_exif.get("Make") or datos_exif.get("Model")
    todos_vacios = all(not datos_exif.get(c) for c in campos_captura)

    if tiene_dispositivo and todos_vacios:
        return [{
            "campo_afectado": "Bloque de parámetros de captura",
            "valor_detectado": "vacío",
            "descripcion": (
                "El dispositivo está declarado, pero no se encontró ninguno de "
                "los parámetros técnicos de captura esperables de una cámara real "
                "(exposición, ISO, distancia focal, etc.)."
            ),
            "severidad": "moderado",
        }]
    return []


def validar_dimensiones(ancho, alto):
    if (ancho, alto) in DIMENSIONES_TIPICAS_IA:
        return [{
            "campo_afectado": "ImageWidth/ImageHeight",
            "valor_detectado": f"{ancho}x{alto}",
            "descripcion": (
                f"La imagen mide {ancho}x{alto} px, una resolución típica de "
                f"salida de modelos generativos de IA."
            ),
            "severidad": "debil",
        }]
    return []


# ============================================================
# Clasificación
# ============================================================

def clasificar(anomalias):
    severidades = [a["severidad"] for a in anomalias]

    n_directo = severidades.count("directo")
    n_fuerte = severidades.count("fuerte")
    n_moderado = severidades.count("moderado")
    n_debil = severidades.count("debil")

    if n_directo >= 1:
        return "fuerte"
    if n_fuerte >= 2 or (n_fuerte >= 1 and n_moderado >= 1):
        return "fuerte"
    if n_fuerte == 1 or n_moderado >= 2:
        return "moderado"
    if n_debil >= 1:
        return "debil"
    return "sin_indicios"


# ============================================================
# Orquestador
# ============================================================

def analizar_metadatos(imagen_id, imagen_path):
    formato = detectar_formato(imagen_path)

    datos_exif = {}
    chunks_png = {}

    if formato in ("jpeg", "heic"):
        datos_exif = extraer_exif(imagen_path)

    if formato == "png":
        chunks_png = extraer_chunks_png(imagen_path)

    datos_xmp = extraer_xmp(imagen_path)
    ancho, alto = obtener_dimensiones(imagen_path)
    fecha_creacion_sistema = obtener_fecha_creacion_sistema(imagen_path)

    anomalias = []
    anomalias += validar_software(datos_exif, datos_xmp)
    anomalias += validar_historial_xmp(datos_xmp)
    if formato == "png":
        anomalias += validar_chunks_generacion(chunks_png)
    if formato in ("jpeg", "heic"):
        anomalias += validar_makernotes(datos_exif)
        anomalias += validar_cronologia(datos_exif, fecha_creacion_sistema)
        anomalias += validar_bloque_captura(datos_exif)
    anomalias += validar_dimensiones(ancho, alto)

    clasificacion = clasificar(anomalias)

    resultado = AnalisisRepository.crear_resultado(
        imagen_id=imagen_id,
        tipo_analisis="metadatos",
        clasificacion=clasificacion,
    )
    AnalisisRepository.guardar_anomalias(resultado.id, anomalias)

    return clasificacion, anomalias