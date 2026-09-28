# tests/test_c2pa_service.py
#
# Correr desde la raíz del proyecto:  pytest tests/test_c2pa_service.py -v
#
# Tres grupos de pruebas:
#  1. Lógica de interpretación con diccionarios que reproducen lo que ExifTool
#     devolvió para las imágenes reales de ChatGPT y Gemini (sin archivos).
#  2. Un JPEG sin manifiesto generado al vuelo (usa ExifTool).
#  3. Regresión sobre las carpetas de la prueba de canales, si existen.

import shutil
from pathlib import Path

import pytest
from PIL import Image

from app.services import c2pa_service as c2pa

IMAGENES_PRUEBA = Path(__file__).parent / "imagenes_prueba"

# Lo que ExifTool devolvió para el original de ChatGPT (Prueba 3)
TAGS_CHATGPT = {
    "SourceFile": "01_original.png",
    "JUMBF:JUMDType": "(c2pa)-0011-0010-800000aa00389b71",
    "JUMBF:JUMDLabel": "c2pa",
    "CBOR:ActionsAction": ["c2pa.created", "c2pa.converted", "c2pa.watermarked.unbound"],
    "CBOR:ActionsSoftwareAgentName": "ChatGPT",
    "CBOR:ActionsDigitalSourceType":
        "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    "CBOR:Claim_Generator_InfoName": "OpenAI Media Service API",
}

# Lo que ExifTool devolvió para el original de Gemini (Prueba 4)
TAGS_GEMINI = {
    "SourceFile": "01_original.jpg",
    "JUMBF:JUMDType": "(c2pa)-0011-0010-800000aa00389b71",
    "JUMBF:JUMDLabel": "c2pa",
    "CBOR:Claim_Generator_InfoName": "Google C2PA Core Generator Library",
    "CBOR:ActionsAction": ["c2pa.created", "c2pa.edited"],
    "CBOR:ActionsDigitalSourceType": [
        "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    ],
}


# ------------------------------------------------------------
# 1. Lógica de interpretación
# ------------------------------------------------------------

def test_chatgpt_declara_ia():
    r = c2pa.interpretar_tags(TAGS_CHATGPT)
    assert r["estado"] == "evaluada"
    assert r["clasificacion"] == "fuerte"
    assert r["detalle"]["declara_ia"] is True
    assert r["detalle"]["generador"] == "OpenAI Media Service API"
    assert r["detalle"]["agente_software"] == "ChatGPT"
    assert "trainedAlgorithmicMedia" in r["detalle"]["tipos_fuente"]
    assert r["detalle"]["firma_verificada"] is None
    assert [a["severidad"] for a in r["anomalias"]] == ["fuerte"]


def test_gemini_declara_ia_sin_nombre_de_producto():
    r = c2pa.interpretar_tags(TAGS_GEMINI)
    assert r["estado"] == "evaluada"
    assert r["clasificacion"] == "fuerte"
    assert r["detalle"]["generador"] == "Google C2PA Core Generator Library"
    assert r["detalle"]["agente_software"] is None
    assert r["detalle"]["acciones"] == ["c2pa.created", "c2pa.edited"]


def test_sin_manifiesto_es_no_evaluable():
    r = c2pa.interpretar_tags({"SourceFile": "x.jpg", "EXIF:Make": "Apple"})
    assert r["estado"] == "no_evaluable"
    assert r["clasificacion"] == "no_evaluable"
    assert r["anomalias"] == []


def test_manifiesto_sin_declaracion_de_ia_no_es_indicio():
    tags = {
        "JUMBF:JUMDLabel": "c2pa",
        "CBOR:ActionsAction": ["c2pa.created"],
        "CBOR:ActionsDigitalSourceType":
            "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture",
    }
    r = c2pa.interpretar_tags(tags)
    assert r["estado"] == "evaluada"
    assert r["clasificacion"] == "sin_indicios"
    assert r["anomalias"] == []
    assert r["detalle"]["declara_ia"] is False


def test_composicion_con_ia_tambien_cuenta():
    tags = {
        "JUMBF:JUMDLabel": "c2pa",
        "CBOR:ActionsDigitalSourceType":
            "http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia",
    }
    r = c2pa.interpretar_tags(tags)
    assert r["clasificacion"] == "fuerte"


def test_etiquetas_repetidas_con_sufijo_se_unifican():
    tags = {
        "JUMBF:JUMDLabel": "c2pa",
        "CBOR:ActionsDigitalSourceType": "trainedAlgorithmicMedia",
        "CBOR:ActionsDigitalSourceType (1)":
            "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    }
    r = c2pa.interpretar_tags(tags)
    assert r["detalle"]["tipos_fuente"] == ["trainedAlgorithmicMedia"]
    assert len(r["anomalias"]) == 1


def test_deteccion_por_jumdtype_si_falta_la_etiqueta():
    tags = {"JUMBF:JUMDType": "(c2pa)-0011-0010-800000aa00389b71"}
    assert c2pa.interpretar_tags(tags)["estado"] == "evaluada"


# ------------------------------------------------------------
# 2. Archivo real sin manifiesto (requiere ExifTool)
# ------------------------------------------------------------

def _exiftool_disponible():
    return c2pa.EXIFTOOL_PATH != "exiftool" or shutil.which("exiftool")


@pytest.mark.skipif(not _exiftool_disponible(), reason="ExifTool no disponible")
def test_jpeg_comun_es_no_evaluable(tmp_path):
    ruta = tmp_path / "foto.jpg"
    Image.new("RGB", (64, 48), (120, 80, 40)).save(ruta)
    r = c2pa.analizar_c2pa_archivo(str(ruta))
    assert r["estado"] == "no_evaluable"


def test_error_si_exiftool_no_existe(monkeypatch, tmp_path):
    monkeypatch.setattr(c2pa, "EXIFTOOL_PATH", str(tmp_path / "no_existe.exe"))
    r = c2pa.analizar_c2pa_archivo(str(tmp_path / "x.jpg"))
    assert r["estado"] == "error"


# ------------------------------------------------------------
# 3. Regresión sobre la prueba de canales (archivos reales)
# ------------------------------------------------------------
# Resultado esperado según las Pruebas 3 y 4 (ChatGPT y Gemini):
#   original, WhatsApp como documento y mail -> manifiesto presente
#   WhatsApp como foto y captura de pantalla  -> manifiesto perdido

ESPERADO_POR_PREFIJO = {
    "01_": True,
    "02_": False,
    "03_": True,
    "04_": True,
    "05_": False,
}
EXTENSIONES = {".png", ".jpg", ".jpeg"}


def _buscar(carpeta, prefijo):
    for ruta in sorted(carpeta.glob(prefijo + "*")):
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES:
            return ruta
    return None


@pytest.mark.skipif(not _exiftool_disponible(), reason="ExifTool no disponible")
@pytest.mark.parametrize("carpeta", ["canales", "canales_gemini"])
@pytest.mark.parametrize("prefijo,con_manifiesto", ESPERADO_POR_PREFIJO.items())
def test_regresion_prueba_de_canales(carpeta, prefijo, con_manifiesto):
    base = IMAGENES_PRUEBA / carpeta
    if not base.exists():
        pytest.skip(f"No existe {base}")
    ruta = _buscar(base, prefijo)
    if ruta is None:
        pytest.skip(f"No hay archivo {prefijo}* en {base}")

    r = c2pa.analizar_c2pa_archivo(str(ruta))

    if con_manifiesto:
        assert r["estado"] == "evaluada", ruta.name
        assert r["detalle"]["declara_ia"] is True, ruta.name
    else:
        assert r["estado"] == "no_evaluable", ruta.name


# ------------------------------------------------------------
# Persistencia (con el repositorio reemplazado por un doble)
# ------------------------------------------------------------

def test_persistencia_guarda_tipo_c2pa(monkeypatch):
    llamadas = []

    class _Registro:
        id = 7

    class _RepoFalso:
        @staticmethod
        def crear_resultado(imagen_id, tipo_analisis, clasificacion):
            llamadas.append(("crear", imagen_id, tipo_analisis, clasificacion))
            return _Registro()

        @staticmethod
        def guardar_anomalias(resultado_id, anomalias):
            llamadas.append(("anomalias", resultado_id, len(anomalias)))

    import app.repositories.analisis_repository as modulo_repo
    monkeypatch.setattr(modulo_repo, "AnalisisRepository", _RepoFalso)
    monkeypatch.setattr(
        c2pa, "analizar_c2pa_archivo",
        lambda ruta: c2pa.interpretar_tags(TAGS_CHATGPT),
    )

    resultado = c2pa.analizar_c2pa(42, "cualquiera.png")

    assert resultado["clasificacion"] == "fuerte"
    assert llamadas == [("crear", 42, "c2pa", "fuerte"), ("anomalias", 7, 1)]