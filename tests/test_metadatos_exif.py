# tests/test_metadatos_exif.py
#
# Regresión del arreglo de extraer_exif(): con "-G0:1" ExifTool devuelve las
# claves con grupo ("EXIF:IFD0:Make") y los validadores buscan "Make".
# Si se corre contra la versión anterior de metadatos_service.py, los tests
# que dependen de extraer_exif() deben fallar.
#
# Correr desde la raíz del proyecto:  pytest tests/test_metadatos_exif.py -v

import os
import shutil
import subprocess
from datetime import datetime

import pytest
from PIL import Image

from app.services import metadatos_service as ms


def _exiftool():
    ruta = ms.EXIFTOOL_PATH
    if os.path.exists(ruta):
        return ruta
    return shutil.which("exiftool")


@pytest.fixture
def jpeg_con_exif(tmp_path, monkeypatch):
    exiftool = _exiftool()
    if not exiftool:
        pytest.skip("ExifTool no disponible")
    monkeypatch.setattr(ms, "EXIFTOOL_PATH", exiftool)

    ruta = tmp_path / "foto.jpg"
    Image.new("RGB", (64, 48), (120, 80, 40)).save(ruta)
    subprocess.run(
        [
            exiftool, "-overwrite_original",
            "-Make=Apple", "-Model=iPhone 13", "-Software=Photoshop",
            "-DateTimeOriginal=2024:01:01 10:00:00",
            str(ruta),
        ],
        check=True, capture_output=True,
    )
    return str(ruta)


def test_extraer_exif_devuelve_nombres_planos(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    assert datos.get("Make") == "Apple"
    assert datos.get("Software") == "Photoshop"
    assert datos.get("DateTimeOriginal") == "2024:01:01 10:00:00"


def test_extraer_exif_conserva_las_claves_con_grupo(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    assert any(k.endswith(":Make") and ":" in k for k in datos)


def test_software_declarado_en_exif_se_detecta(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    anomalias = ms.validar_software(datos, {})
    assert [a["severidad"] for a in anomalias] == ["directo"]


def test_makernotes_ausente_con_marca_conocida(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    anomalias = ms.validar_makernotes(datos)
    assert [a["severidad"] for a in anomalias] == ["fuerte"]


def test_bloque_de_captura_vacio_con_dispositivo(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    anomalias = ms.validar_bloque_captura(datos)
    assert [a["severidad"] for a in anomalias] == ["moderado"]


def test_cronologia_imposible(jpeg_con_exif):
    datos = ms.extraer_exif(jpeg_con_exif)
    # Archivo "creado en el sistema" antes de la captura declarada (2024)
    anomalias = ms.validar_cronologia(datos, datetime(2023, 1, 1))
    assert [a["severidad"] for a in anomalias] == ["fuerte"]


def test_valores_numericos_no_rompen_los_validadores():
    # ExifTool puede devolver números JSON (por ejemplo Software = 12)
    assert ms.validar_software({"Software": 12}, {}) == []
    assert ms.validar_makernotes({"Make": 123}) == []