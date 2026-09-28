"""Prueba de canales: compara variantes de una misma imagen.

Uso:
    python probar_canales.py tests/imagenes_prueba/canales

La primera imagen (orden alfabetico, ej. 01_original.png) se toma como
referencia. Para cada archivo se calcula el SHA-256, se compara con la
referencia, se vuelca todo lo que lee ExifTool y se buscan indicios de
C2PA / procedencia de IA. No usa metadatos_service.py: es independiente.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

# Ajustar a la ruta real del ejecutable dentro del proyecto
EXIFTOOL = r"tools\exiftool.exe"

EXTENSIONES = {".png", ".jpg", ".jpeg", ".webp"}
PALABRAS = (
    "jumbf",
    "c2pa",
    "contentcredentials",
    "content credentials",
    "trainedalgorithmicmedia",
    "openai",
    "chatgpt",
    "claim_generator",
)
CLAVES_IGNORADAS = {"SourceFile", "FileName", "Directory"}


def calcular_sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def leer_exiftool(ruta):
    r = subprocess.run(
        [EXIFTOOL, "-a", "-G1", "-j", str(ruta)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0 or not r.stdout.strip():
        return {}, r.stderr.strip() or "ExifTool no devolvio datos"
    return json.loads(r.stdout)[0], ""


def buscar_indicios(tags):
    hallazgos = []
    for clave, valor in tags.items():
        if clave.split(":")[-1] in CLAVES_IGNORADAS:
            continue
        texto = f"{clave} {valor}".lower()
        if any(p in texto for p in PALABRAS):
            hallazgos.append(f"{clave}: {str(valor)[:80]}")
    return hallazgos


def formato_y_dimensiones(ruta):
    try:
        with Image.open(ruta) as img:
            return img.format, f"{img.width}x{img.height}"
    except Exception:
        return "?", "?"


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return
    carpeta = Path(sys.argv[1])
    archivos = sorted(
        p for p in carpeta.iterdir() if p.suffix.lower() in EXTENSIONES
    )
    if not archivos:
        print(f"No hay imagenes en {carpeta}")
        return

    salida = carpeta / "resultados"
    salida.mkdir(exist_ok=True)
    referencia = None
    resumen = []

    for ruta in archivos:
        huella = calcular_sha256(ruta)
        if referencia is None:
            referencia = huella
        igual = "SI" if huella == referencia else "NO"
        formato, dims = formato_y_dimensiones(ruta)
        kb = ruta.stat().st_size / 1024
        tags, error = leer_exiftool(ruta)
        indicios = buscar_indicios(tags)

        (salida / f"{ruta.stem}.json").write_text(
            json.dumps(tags, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"\n=== {ruta.name} ===")
        print(f"Formato / dimensiones : {formato} {dims}")
        print(f"Tamano                : {kb:.1f} KB")
        print(f"Igual a la referencia : {igual}")
        print(f"Campos de ExifTool    : {len(tags)}")
        if error:
            print(f"Error ExifTool        : {error}")
        if indicios:
            print("Indicios C2PA / IA    :")
            for h in indicios:
                print(f"    - {h}")
        else:
            print("Indicios C2PA / IA    : ninguno")

        resumen.append((ruta.name, formato, f"{kb:.0f}", igual, len(tags), len(indicios)))

    print("\n--- Resumen ---")
    print(f"{'archivo':32} {'fmt':6} {'KB':>6} {'igual':6} {'campos':>6} {'indicios':>8}")
    for fila in resumen:
        print(f"{fila[0]:32} {fila[1]:6} {fila[2]:>6} {fila[3]:6} {fila[4]:>6} {fila[5]:>8}")
    print(f"\nVolcados completos en: {salida}")


if __name__ == "__main__":
    main()
