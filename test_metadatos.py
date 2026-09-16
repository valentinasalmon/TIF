# test_metadatos.py
#
# Script de prueba rápida del módulo de metadatos, sin pasar por rutas web.
# Corré desde la raíz del proyecto: python test_metadatos.py "ruta/a/imagen.jpg"
#
# NOTA: este script prueba solo la EXTRACCIÓN y VALIDACIÓN (no guarda en la
# base de datos, para no necesitar un caso/imagen real creados de antemano).

import sys
import json

sys.path.insert(0, ".")  # para que encuentre el paquete app/

from app.services.metadatos_service import (
    detectar_formato,
    extraer_exif,
    extraer_xmp,
    extraer_chunks_png,
    obtener_dimensiones,
    obtener_fecha_creacion_sistema,
    validar_software,
    validar_historial_xmp,
    validar_chunks_generacion,
    validar_makernotes,
    validar_cronologia,
    validar_bloque_captura,
    validar_dimensiones,
    clasificar,
)


def main(imagen_path):
    print(f"\n=== Analizando: {imagen_path} ===\n")

    formato = detectar_formato(imagen_path)
    print(f"Formato detectado: {formato}")

    datos_exif = {}
    chunks_png = {}

    if formato in ("jpeg", "heic"):
        datos_exif = extraer_exif(imagen_path)
        print(f"\nCampos EXIF encontrados: {len(datos_exif)}")

    if formato == "png":
        chunks_png = extraer_chunks_png(imagen_path)
        print(f"\nChunks PNG encontrados: {list(chunks_png.keys())}")

    datos_xmp = extraer_xmp(imagen_path)
    ancho, alto = obtener_dimensiones(imagen_path)
    fecha_sistema = obtener_fecha_creacion_sistema(imagen_path)

    print(f"Dimensiones: {ancho}x{alto}")
    print(f"Fecha creación (sistema): {fecha_sistema}")
    print(f"Datos XMP crudos: {datos_xmp}")

    anomalias = []
    anomalias += validar_software(datos_exif, datos_xmp)
    anomalias += validar_historial_xmp(datos_xmp)
    if formato == "png":
        anomalias += validar_chunks_generacion(chunks_png)
    if formato in ("jpeg", "heic"):
        anomalias += validar_makernotes(datos_exif)
        anomalias += validar_cronologia(datos_exif, fecha_sistema)
        anomalias += validar_bloque_captura(datos_exif)
    anomalias += validar_dimensiones(ancho, alto)

    clasificacion = clasificar(anomalias)

    print(f"\n=== RESULTADO ===")
    print(f"Clasificación: {clasificacion.upper()}")
    print(f"\nAnomalías encontradas ({len(anomalias)}):")
    for a in anomalias:
        print(f"  [{a['severidad'].upper()}] {a['campo_afectado']}: {a['descripcion']}")

    if not anomalias:
        print("  (ninguna)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_metadatos.py \"ruta/a/imagen.jpg\"")
        sys.exit(1)
    main(sys.argv[1])