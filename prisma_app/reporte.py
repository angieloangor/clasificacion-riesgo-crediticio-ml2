"""Resumen descargable de una predicción (HTML autocontenido y CSV)."""
from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import sklearn

from . import config as C
from .componentes import AVISO_SINTETICO, espectro_html, pct
from .esquema import GRUPOS, etiqueta, formato_valor


def html_prediccion(perfil: dict, probs: dict, clase: str, origen: str, advertencias: list,
                    contrib_top: list[tuple[str, float]] | None = None) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    filas = ""
    for _, titulo, cols in GRUPOS:
        filas += f'<tr><th colspan="2" class="g">{html.escape(titulo)}</th></tr>'
        for c in cols:
            filas += (f"<tr><td>{html.escape(etiqueta(c))}<br><code>{c}</code></td>"
                      f"<td class='v'>{html.escape(formato_valor(c, perfil[c]))}</td></tr>")
    probs_tabla = "".join(
        f"<tr><td>{c}</td><td class='v'>{probs[c]:.6f}</td><td class='v'>{pct(probs[c], 2)}</td></tr>"
        for c in C.ORDEN_CLASES)
    adv = ("<ul>" + "".join(f"<li>{html.escape(a)}</li>" for a in advertencias) + "</ul>") if advertencias else "<p>Ninguna.</p>"
    contrib = ""
    if contrib_top:
        contrib = ("<h2>Variables con mayor contribución a la puntuación de " + clase + "</h2><table>"
                   + "".join(f"<tr><td>{html.escape(etiqueta(v))}</td><td class='v'>{x:+.4f}</td></tr>" for v, x in contrib_top)
                   + "</table><p class='n'>Descomposición exacta del logit de la regresión logística frente al perfil "
                     "promedio del entrenamiento. Es una asociación del modelo, no un efecto causal.</p>")
    estilos = f"""
    body{{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;color:{C.TINTA};max-width:760px;margin:40px auto;padding:0 20px;line-height:1.5}}
    h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:16px;margin:28px 0 8px}}
    .meta{{color:{C.TINTA_2};font-size:13px}} table{{width:100%;border-collapse:collapse;font-size:13.5px}}
    td,th{{border-bottom:1px solid {C.LINEA};padding:6px 4px;text-align:left;vertical-align:top}}
    th.g{{background:#F4F6F9;font-size:12.5px;color:{C.TINTA_2}}} td.v{{text-align:right;font-variant-numeric:tabular-nums}}
    code{{font-size:11px;color:{C.TINTA_3}}} .aviso{{border-left:3px solid {C.TURQUESA};background:#EAF6F5;padding:10px 14px;font-size:13.5px}}
    .pr-espectro{{display:flex;height:40px;border-radius:10px;overflow:hidden;gap:2px}}
    .pr-espectro div{{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:13px}}
    .pr-espectro div.pr-tenue{{opacity:.4}} .pr-espectro-leyenda{{display:flex;justify-content:space-between;font-size:12.5px;margin-top:6px}}
    .pr-espectro-leyenda i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px}} .n{{font-size:12.5px;color:{C.TINTA_2}}}
    """
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Prisma · resumen de predicción</title>
<style>{estilos}</style></head><body>
<h1>Resumen de predicción — clase {html.escape(clase)}</h1>
<p class="meta">Generado: {fecha} · Modelo: regresión logística (C = 0.001) en Pipeline de scikit-learn {sklearn.__version__} ·
Origen del perfil: {html.escape(origen)}</p>
<div class="aviso">{AVISO_SINTETICO}</div>
<h2>Probabilidades (predict_proba)</h2>
{espectro_html(probs, clase, alto=40)}
<table style="margin-top:12px"><tr><th>Clase</th><th class="v">Probabilidad</th><th class="v">%</th></tr>{probs_tabla}</table>
<p class="n">Suma: {sum(probs.values()):.6f}. Clase predicha = mayor probabilidad.</p>
{contrib}
<h2>Advertencias de coherencia</h2>{adv}
<h2>Perfil evaluado (23 predictores)</h2><table>{filas}</table>
<p class="n">Proyecto académico Machine Learning II — Nicolás Barrera y Angie Loango. Datos y etiquetas sintéticos.</p>
</body></html>"""


def csv_prediccion(perfil: dict, probs: dict, clase: str, columnas: list) -> bytes:
    fila = {c: perfil[c] for c in columnas}
    fila.update({f"Prob_{c}": probs[c] for c in C.ORDEN_CLASES})
    fila["Clase_predicha"] = clase
    return pd.DataFrame([fila]).to_csv(index=False).encode("utf-8-sig")
