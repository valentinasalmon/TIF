# app/services/c2pa_service.py
#
# Capa de análisis de procedencia: lectura de Content Credentials (C2PA).
#
# Nivel 1 (este archivo): lee el manifiesto con ExifTool e interpreta sus campos.
#   Verificado con imágenes reales de ChatGPT y Gemini (grupos JUMBF y CBOR).
# Nivel 2 (pendiente): verificar la firma criptográfica con c2pa-python.
#   Hasta que exista, "firma_verificada" queda en None y la severidad del
#   indicio es "fuerte" en lugar de "directo".
#
# Estados que devuelve cada análisis:
#   evaluada     -> la capa pudo mirar el archivo (haya o no indicios)
#   no_evaluable -> no hay manifiesto C2PA: no aporta ni resta (puede haberse
#                   perdido al recodificar o capturar la pantalla)
#   error        -> falló la ejecución de ExifTool

import json
import os
import re
import subprocess

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_EXIFTOOL_LOCAL = os.path.join(_RAIZ, "tools", "exiftool.exe")
# Si no está en tools/, se intenta con el PATH del sistema.
EXIFTOOL_PATH = _EXIFTOOL_LOCAL if os.path.exists(_EXIFTOOL_LOCAL) else "exiftool"

# Tipos de fuente digital (vocabulario IPTC) que declaran contenido generado o
# compuesto con IA. Se comparan en minúsculas.
TIPOS_FUENTE_IA = {
    "trainedalgorithmicmedia",
    "compositewithtrainedalgorithmicmedia",
}

_RE_SUFIJO_DUPLICADO = re.compile(r"\s*\(\d+\)$")


# ============================================================
# Lectura con ExifTool
# ============================================================

def ejecutar_exiftool(imagen_path):
    """Devuelve (tags, error). Con -a se conservan las etiquetas repetidas."""
    try:
        resultado = subprocess.run(
            [EXIFTOOL_PATH, "-a", "-G1", "-json", imagen_path],
            capture_output=True, encoding="utf-8", errors="replace", timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {}, f"No se pudo ejecutar ExifTool: {e}"

    if not resultado.stdout.strip():
        return {}, resultado.stderr.strip() or "ExifTool no devolvió datos"
    try:
        datos = json.loads(resultado.stdout)
    except json.JSONDecodeError:
        return {}, "La salida de ExifTool no es un JSON válido"
    return (datos[0] if datos else {}), ""


# ============================================================
# Interpretación (funciones puras, sin ExifTool ni base de datos)
# ============================================================

def _nombre_tag(clave):
    """'CBOR:ActionsAction (1)' -> 'ActionsAction'."""
    return _RE_SUFIJO_DUPLICADO.sub("", clave.split(":")[-1])


def _valores(tags, nombre):
    """Todos los valores (como texto) de las etiquetas con ese nombre."""
    encontrados = []
    for clave, valor in tags.items():
        if _nombre_tag(clave) != nombre:
            continue
        if isinstance(valor, list):
            encontrados.extend(str(v) for v in valor)
        else:
            encontrados.append(str(valor))
    return encontrados


def _unicos(valores):
    return list(dict.fromkeys(valores))


def _hay_manifiesto(tags):
    etiquetas = [v.lower() for v in _valores(tags, "JUMDLabel")]
    tipos = [v.lower() for v in _valores(tags, "JUMDType")]
    return "c2pa" in etiquetas or any("(c2pa)" in t for t in tipos)


def _nombre_tipo_fuente(valor):
    """'http://cv.iptc.org/.../trainedAlgorithmicMedia' -> 'trainedAlgorithmicMedia'."""
    return valor.rstrip("/").split("/")[-1]


def interpretar_tags(tags):
    """
    Convierte los tags de ExifTool en el resultado de la capa C2PA.

    Devuelve un diccionario con: estado, clasificacion, anomalias y detalle.
    """
    if not _hay_manifiesto(tags):
        return {
            "estado": "no_evaluable",
            "clasificacion": "no_evaluable",
            "anomalias": [],
            "detalle": {"manifiesto": False},
        }

    generadores = _valores(tags, "Claim_Generator_InfoName") or _valores(tags, "Claim_Generator")
    agentes = _valores(tags, "ActionsSoftwareAgentName")
    acciones = _unicos(_valores(tags, "ActionsAction"))
    tipos_fuente = _unicos(_nombre_tipo_fuente(v) for v in _valores(tags, "ActionsDigitalSourceType"))
    tipos_ia = [t for t in tipos_fuente if t.lower() in TIPOS_FUENTE_IA]

    generador = generadores[0] if generadores else None
    agente = agentes[0] if agentes else None

    detalle = {
        "manifiesto": True,
        "generador": generador,
        "agente_software": agente,
        "acciones": acciones,
        "tipos_fuente": tipos_fuente,
        "declara_ia": bool(tipos_ia),
        "firma_verificada": None,  # nivel 2 pendiente (c2pa-python)
    }

    anomalias = []
    if tipos_ia:
        origen = generador or "generador no informado"
        if agente:
            origen += f" (agente: {agente})"
        anomalias.append({
            "campo_afectado": "C2PA:DigitalSourceType",
            "valor_detectado": ", ".join(tipos_ia),
            "descripcion": (
                "El archivo contiene un manifiesto de Content Credentials (C2PA) "
                f"que declara contenido generado por IA. Generador declarado: {origen}. "
                "La firma criptográfica del manifiesto no fue verificada por el sistema."
            ),
            "severidad": "fuerte",
        })

    return {
        "estado": "evaluada",
        "clasificacion": "fuerte" if anomalias else "sin_indicios",
        "anomalias": anomalias,
        "detalle": detalle,
    }


# ============================================================
# Análisis
# ============================================================

def analizar_c2pa_archivo(imagen_path):
    """Analiza un archivo sin tocar la base de datos."""
    tags, error = ejecutar_exiftool(imagen_path)
    if error:
        return {
            "estado": "error",
            "clasificacion": "error",
            "anomalias": [],
            "detalle": {"error": error},
        }
    return interpretar_tags(tags)


def analizar_c2pa(imagen_id, imagen_path):
    """
    Analiza y persiste el resultado, con el mismo circuito que metadatos.

    Los resultados "error" no se guardan. Los "no_evaluable" sí, con
    clasificacion="no_evaluable": si la columna tiene una restricción de
    valores, hay que agregarlo antes (ver instrucciones de la entrega).
    """
    resultado = analizar_c2pa_archivo(imagen_path)
    if resultado["estado"] == "error":
        return resultado

    from app.repositories.analisis_repository import AnalisisRepository

    registro = AnalisisRepository.crear_resultado(
        imagen_id=imagen_id,
        tipo_analisis="c2pa",
        clasificacion=resultado["clasificacion"],
    )
    AnalisisRepository.guardar_anomalias(registro.id, resultado["anomalias"])
    return resultado