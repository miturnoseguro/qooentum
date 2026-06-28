#!/usr/bin/env python3
"""
patch_map_style.py
==================
Descarga el estilo "bright" de OpenFreeMap y reemplaza todos los valores
null en expresiones numéricas de paint/layout por 0, eliminando el error:
  "Expected value to be of type number, but found null instead"

Uso:
    python3 patch_map_style.py

Genera: bright_patched.json  (servir este archivo en tu proyecto)
"""

import json, urllib.request, sys, copy

STYLE_URL = "https://tiles.openfreemap.org/styles/bright"
OUTPUT    = "bright_patched.json"

# Propiedades de paint/layout que esperan número y pueden recibir null
NUMBER_PROPS = {
    # line
    "line-width", "line-opacity", "line-blur", "line-gap-width",
    "line-offset", "line-dasharray",
    # fill
    "fill-opacity",
    # symbol / text
    "text-size", "text-opacity", "text-halo-width", "text-halo-blur",
    "text-letter-spacing", "text-line-height", "text-max-width",
    "text-padding", "text-rotate", "text-offset",
    # icon
    "icon-size", "icon-opacity", "icon-halo-width", "icon-halo-blur",
    "icon-rotate", "icon-padding",
    # circle
    "circle-radius", "circle-opacity", "circle-stroke-width", "circle-blur",
    # heatmap
    "heatmap-weight", "heatmap-intensity", "heatmap-radius", "heatmap-opacity",
    # raster
    "raster-opacity", "raster-brightness-min", "raster-brightness-max",
    "raster-saturation", "raster-contrast", "raster-hue-rotate",
    # background
    "background-opacity",
}

def patch_value(val, prop_name=""):
    """Reemplaza null por 0 en valores numéricos, recursivamente en expresiones."""
    if val is None:
        return 0
    if isinstance(val, list):
        return [patch_value(v) for v in val]
    if isinstance(val, dict):
        return {k: patch_value(v, k) for k, v in val.items()}
    return val

def patch_layer(layer):
    layer = copy.deepcopy(layer)
    for block in ("paint", "layout"):
        if block not in layer:
            continue
        for prop, val in layer[block].items():
            if prop in NUMBER_PROPS:
                layer[block][prop] = patch_value(val, prop)
    return layer

def main():
    print(f"Descargando estilo desde {STYLE_URL} ...")
    try:
        with urllib.request.urlopen(STYLE_URL, timeout=20) as r:
            style = json.loads(r.read().decode())
    except Exception as e:
        print(f"ERROR al descargar: {e}", file=sys.stderr)
        sys.exit(1)

    original_layers = len(style.get("layers", []))
    style["layers"] = [patch_layer(l) for l in style.get("layers", [])]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(style, f, ensure_ascii=False, separators=(",", ":"))

    print(f"✅ Listo. {original_layers} capas parcheadas → {OUTPUT}")
    print()
    print("Próximo paso: copiá bright_patched.json a la raíz de tu proyecto")
    print("y cambiá en index.html:")
    print()
    print("  ANTES:  style: 'https://tiles.openfreemap.org/styles/bright'")
    print("  DESPUÉS: style: './bright_patched.json'")

if __name__ == "__main__":
    main()
