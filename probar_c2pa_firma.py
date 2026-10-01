"""Sonda de firma C2PA: prueba c2pa-python sobre tus imagenes reales.

Instalacion (una vez, con el entorno virtual activado):
    pip install c2pa-python

Uso:
    python probar_c2pa_firma.py tests/imagenes_prueba/canales_gpt tests/imagenes_prueba/canales_gemini

Con la lista de confianza oficial de C2PA (descarga C2PA-TRUST-LIST.pem de GitHub):
    python probar_c2pa_firma.py --confianza tests/imagenes_prueba/canales_gpt tests/imagenes_prueba/canales_gemini

Para cada imagen muestra el estado de validacion que informa la libreria
(Invalid / Valid / Trusted), quien firmo y que fallos reporta. Guarda el
detalle completo en <carpeta>/resultados/<archivo>_firma.json.

No modifica nada del proyecto: es solo para decidir como interpretar la firma.
"""
import json
import sys
import urllib.request
from pathlib import Path

try:
    import c2pa
except ImportError:
    sys.exit("Falta la libreria. Ejecuta:  pip install c2pa-python")

EXTENSIONES = {".png", ".jpg", ".jpeg", ".webp"}
URL_LISTA_CONFIANZA = (
    "https://raw.githubusercontent.com/c2pa-org/conformance-public/"
    "main/trust-list/C2PA-TRUST-LIST.pem"
)
# Fallos que indican que el CONTENIDO del archivo cambio despues de firmarse
FALLOS_DE_CONTENIDO = ("mismatch", "claimSignature.", "dataHash", "hashedURI")


def crear_contexto(usar_confianza):
    """Devuelve un Context con la lista de confianza oficial, o None."""
    if not usar_confianza:
        return None
    with urllib.request.urlopen(URL_LISTA_CONFIANZA, timeout=30) as r:
        pem = r.read().decode("utf-8")
    ajustes = c2pa.Settings.from_dict({"trust": {"trust_anchors": pem}})
    return c2pa.Context(ajustes)


def sondear(ruta, contexto=None):
    """Devuelve un diccionario con lo que informa c2pa-python para un archivo."""
    try:
        lector = c2pa.Reader(str(ruta), context=contexto)
    except Exception as e:  # sin manifiesto o formato no soportado
        tipo = type(e).__name__
        sin_manifiesto = "ManifestNotFound" in tipo or "no JUMBF" in str(e)
        return {
            "resultado": "sin_manifiesto" if sin_manifiesto else "error",
            "excepcion": tipo,
            "mensaje": str(e),
        }

    try:
        estado = lector.get_validation_state()
        resultados = lector.get_validation_results()
        datos = json.loads(lector.json())
    finally:
        lector.close()

    activo = datos.get("manifests", {}).get(datos.get("active_manifest"), {})
    firma = activo.get("signature_info") or {}
    generadores = activo.get("claim_generator_info") or []

    activos = (resultados or {}).get("activeManifest", {})
    fallos_detalle = activos.get("failure", [])
    fallos = [f.get("code") for f in fallos_detalle]
    explicaciones = {f.get("code"): f.get("explanation") for f in fallos_detalle}
    toca_contenido = any(
        any(clave in (codigo or "") for clave in FALLOS_DE_CONTENIDO)
        for codigo in fallos
    )
    informativos = [f.get("code") for f in activos.get("informational", [])]

    return {
        "resultado": "con_manifiesto",
        "estado_validacion": str(estado),
        "firmante": firma.get("issuer"),
        "nombre_comun": firma.get("common_name"),
        "algoritmo": firma.get("alg"),
        "generador": [g.get("name") for g in generadores],
        "fallos": fallos,
        "explicaciones": explicaciones,
        "contenido_alterado": toca_contenido,
        "informativos": informativos,
        "json_completo": datos,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    args = sys.argv[1:]
    usar_confianza = "--confianza" in args
    args = [a for a in args if a != "--confianza"]
    print(f"Version del SDK de C2PA : {c2pa.sdk_version()}")
    print(f"Lista de confianza      : {'oficial C2PA' if usar_confianza else 'ninguna'}")
    contexto = crear_contexto(usar_confianza)

    resumen = []
    for arg in args:
        carpeta = Path(arg)
        archivos = sorted(
            p for p in carpeta.iterdir()
            if p.is_file() and p.suffix.lower() in EXTENSIONES
        )
        salida = carpeta / "resultados"
        salida.mkdir(exist_ok=True)

        print(f"\n##### {carpeta} #####")
        for ruta in archivos:
            r = sondear(ruta, contexto)
            (salida / f"{ruta.stem}_firma.json").write_text(
                json.dumps(r, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

            print(f"\n=== {ruta.name} ===")
            if r["resultado"] == "con_manifiesto":
                print(f"Estado de validacion : {r['estado_validacion']}")
                print(f"Firmante             : {r['firmante']}")
                print(f"Algoritmo            : {r['algoritmo']}")
                print(f"Generador            : {r['generador']}")
                print(f"Fallos               : {r['fallos'] or 'ninguno'}")
                for codigo, texto in r["explicaciones"].items():
                    print(f"    {codigo}: {texto}")
                print(f"Contenido alterado   : {'SI' if r['contenido_alterado'] else 'no'}")
                if r["informativos"]:
                    print(f"Informativos         : {r['informativos']}")
                resumen.append((carpeta.name, ruta.name, r["estado_validacion"], r["firmante"]))
            else:
                print(f"Resultado            : {r['resultado']}")
                print(f"Detalle              : {r['excepcion']}: {r['mensaje']}")
                resumen.append((carpeta.name, ruta.name, r["resultado"], "-"))

    print("\n--- Resumen ---")
    print(f"{'carpeta':18} {'archivo':30} {'estado':16} firmante")
    for c, a, e, f in resumen:
        print(f"{c:18} {a:30} {e:16} {f}")


if __name__ == "__main__":
    main()