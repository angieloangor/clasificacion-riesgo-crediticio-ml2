"""Hoja de estilos de la plataforma (tema claro, paleta semáforo)."""
from __future__ import annotations

import streamlit as st

from . import config as C

_FUENTES = "\n".join(
    f"@font-face {{ font-family: '{fam}'; font-style: normal; font-weight: {w}; font-display: swap; "
    f"src: url('/app/static/fonts/{arch}-latin-{w}-normal.woff2') format('woff2'); }}"
    for fam, arch, pesos in [("Sora", "sora", (500, 600, 700)), ("Instrument Sans", "instrument-sans", (400, 500, 600))]
    for w in pesos)

_CSS = f"""
<style>
/* Fuentes empaquetadas en static/fonts (licencia SIL OFL): funcionan sin conexión. */
{_FUENTES}

:root {{
  --tinta: {C.TINTA}; --tinta-2: {C.TINTA_2}; --tinta-3: {C.TINTA_3};
  --linea: {C.LINEA}; --superficie: {C.SUPERFICIE}; --suave: {C.SUAVE}; --tarjeta: {C.TARJETA};
  --acento: {C.ACENTO}; --acento-claro: {C.ACENTO_CLARO}; --acento-oscuro: {C.ACENTO_OSCURO};
  --good: {C.COLOR_CLASE['Good']}; --standard: {C.COLOR_CLASE['Standard']}; --poor: {C.COLOR_CLASE['Poor']};
  --radio-l: 18px; --radio-m: 12px; --radio-s: 8px;
  --sombra: 0 1px 2px rgba(17,24,39,.04), 0 6px 20px -12px rgba(17,24,39,.14);
  --franja: linear-gradient(90deg, var(--good) 0 33.3%, var(--standard) 33.3% 66.6%, var(--poor) 66.6% 100%);
}}

/* ---------- Base ---------- */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button p,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] p {{
  font-family: 'Instrument Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }}
h1, h2, h3, h4, .pr-display {{ font-family: 'Sora', 'Instrument Sans', system-ui, sans-serif !important;
  letter-spacing: -0.02em; color: var(--tinta); }}
h1 {{ font-weight: 700 !important; }}
h2, h3 {{ font-weight: 600 !important; }}
.stApp {{ background: var(--superficie); }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1200px; }}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {{ background: var(--suave); border-right: 1px solid var(--linea); }}
.pr-marca {{ display:flex; align-items:center; gap:.65rem; padding:.2rem 0 1rem; }}
.pr-marca b {{ font-family:'Sora',sans-serif; font-size:1.25rem; color: var(--tinta); letter-spacing:-.02em; }}
.pr-marca small {{ display:block; font-size:.76rem; color: var(--tinta-3); line-height:1.25; }}
.pr-grupo-nav {{ font-size:.74rem; font-weight:600; color: var(--tinta-3); margin:1rem 0 .2rem .5rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{ border-radius: var(--radio-s); padding: .15rem .5rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{ background: rgba(17,24,39,.05); }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {{ background: var(--acento-claro);
  box-shadow: inset 3px 0 0 var(--acento); }}
[data-testid="stSidebar"] [data-testid="stPageLink"] p {{ color: var(--tinta-2) !important; font-size: .95rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] p {{ color: var(--acento-oscuro) !important; font-weight: 600; }}
.pr-lateral-nota {{ font-size:.78rem; line-height:1.5; color: var(--tinta-3); border-top:1px solid var(--linea);
  padding-top:.9rem; margin-top:.4rem; }}
.pr-lateral-nota b {{ color: var(--tinta); }}

/* ---------- Encabezados y secciones ---------- */
.pr-encabezado {{ margin: .2rem 0 1.4rem; }}
.pr-encabezado h1 {{ font-size: 2.05rem; margin: 0 0 .35rem; padding: 0; line-height: 1.15; }}
.pr-encabezado p {{ color: var(--tinta-2); font-size: 1.02rem; max-width: 72ch; margin: 0; line-height:1.5; }}
.pr-encabezado.pr-con-ficha {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem; flex-wrap: wrap; }}
.pr-encabezado.pr-con-ficha > div {{ flex: 1 1 520px; min-width: 0; }}
.pr-ficha {{ display: inline-flex; align-items: center; gap: .55rem; background: var(--tarjeta); border: 1px solid var(--linea);
  border-radius: 999px; padding: .4rem .9rem .4rem .7rem; font-size: .82rem; color: var(--tinta-2); white-space: nowrap; margin-top: .4rem; }}
.pr-ficha i {{ width: 8px; height: 8px; border-radius: 999px; background: var(--acento); display: inline-block; }}
.pr-seccion {{ display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:.3rem 1rem; margin: 2.4rem 0 .8rem; }}
.pr-seccion h3 {{ font-size: 1.2rem; margin: 0; padding:0; }}
.pr-seccion span {{ color: var(--tinta-3); font-size: .85rem; }}
.pr-pregunta {{ color: var(--tinta-2); font-size: .93rem; margin: -.4rem 0 .6rem; }}

/* ---------- Portada ---------- */
.pr-hero {{ position: relative; overflow: hidden; background: var(--suave); border: 1px solid var(--linea);
  border-radius: 24px; padding: 2.6rem 2.6rem 2.4rem; display: grid; grid-template-columns: 1.1fr 1fr;
  gap: 2.6rem; align-items: center; }}
.pr-hero::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px; background: var(--franja); }}
.pr-hero h1 {{ font-size: 2.9rem; line-height: 1.06; margin: 0 0 .9rem; padding: 0; letter-spacing: -.035em; }}
.pr-hero p {{ color: var(--tinta-2); font-size: 1.06rem; line-height: 1.55; margin: 0; max-width: 46ch; }}
.pr-autores {{ display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1.4rem; }}
.pr-autores span {{ display: inline-flex; align-items: center; gap: .55rem; padding: .3rem .9rem .3rem .3rem;
  border-radius: 999px; background: var(--tarjeta); border: 1px solid var(--linea); color: var(--tinta);
  font-size: .92rem; font-weight: 500; }}
.pr-autores i {{ font-style: normal; width: 28px; height: 28px; border-radius: 999px; display: inline-flex;
  align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-size: .72rem; font-weight: 600;
  background: var(--acento); color: #FFFFFF; }}
.pr-autores span + span i {{ background: var(--acento-oscuro); }}
.pr-autores em {{ font-style: normal; color: var(--tinta-3); font-size: .88rem; align-self: center; margin-left: .3rem; }}
.pr-demo {{ background: var(--tarjeta); border: 1px solid var(--linea); border-radius: 18px; padding: 1.3rem 1.4rem;
  box-shadow: var(--sombra); }}
.pr-demo-titulo {{ font-size: .84rem; color: var(--tinta-3); margin-bottom: .2rem; }}
.pr-demo-clase {{ font-family: 'Sora', sans-serif; font-size: 1.5rem; font-weight: 600; color: var(--tinta);
  margin: 0 0 .9rem; letter-spacing: -.02em; display: flex; align-items: center; gap: .5rem; }}
.pr-demo-clase i {{ width: 12px; height: 12px; border-radius: 4px; display: inline-block; }}
@media (max-width: 900px) {{ .pr-hero {{ grid-template-columns: 1fr; padding: 1.8rem 1.4rem; gap: 1.6rem; }}
  .pr-hero h1 {{ font-size: 2.1rem; }} }}

/* ---------- Espectro de probabilidades ---------- */
.pr-espectro {{ display:flex; width:100%; height: 46px; border-radius: 12px; overflow:hidden; gap: 3px; }}
.pr-espectro div {{ display:flex; align-items:center; justify-content:center; font-weight:600; font-size:.92rem;
  font-variant-numeric: tabular-nums; min-width: 0; white-space: nowrap; overflow: hidden; }}
.pr-espectro div:first-child {{ border-radius: 12px 4px 4px 12px; }}
.pr-espectro div:last-child {{ border-radius: 4px 12px 12px 4px; }}
.pr-espectro-leyenda {{ display:flex; justify-content:space-between; margin-top:.55rem; font-size:.86rem; gap:.5rem; flex-wrap: wrap; }}
.pr-espectro-leyenda span {{ display:inline-flex; align-items:center; gap:.4rem; color: var(--tinta-2); }}
.pr-espectro-leyenda span.pr-mayor {{ color: var(--tinta); font-weight: 600; }}
.pr-espectro-leyenda i {{ width:10px; height:10px; border-radius:3px; display:inline-block; }}

/* ---------- Cifras ---------- */
.pr-cifras {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); background: var(--tarjeta);
  border:1px solid var(--linea); border-radius: var(--radio-l); overflow:hidden; }}
.pr-cifra {{ padding: 1.1rem 1.3rem; border-right: 1px solid var(--linea); }}
.pr-cifra:last-child {{ border-right: none; }}
.pr-cifra b {{ display:block; font-family:'Sora',sans-serif; font-size:1.7rem; font-weight:600; color: var(--tinta);
  font-variant-numeric: tabular-nums; letter-spacing:-.02em; }}
.pr-cifra span {{ font-size:.86rem; color: var(--tinta-2); }}
.pr-cifra small {{ display:block; font-size:.76rem; color: var(--tinta-3); margin-top:.15rem; }}

/* ---------- Resultado ---------- */
.pr-resultado {{ position: relative; overflow: hidden; background: var(--tarjeta); border: 1px solid var(--linea);
  border-radius: 22px; padding: 1.9rem 2rem 1.6rem; box-shadow: var(--sombra);
  display: grid; grid-template-columns: 1fr 1.25fr; gap: 1.3rem 2.4rem; align-items: end; }}
.pr-resultado::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px; background: var(--franja); }}
.pr-res-etiqueta {{ font-size: .85rem; color: var(--tinta-3); }}
.pr-res-clase {{ display: flex; align-items: center; gap: .8rem; font-family: 'Sora', sans-serif; font-weight: 700;
  font-size: 3.1rem; line-height: 1.05; letter-spacing: -.03em; margin: .25rem 0 .45rem; color: var(--tinta); }}
.pr-res-clase i {{ width: 18px; height: 18px; border-radius: 6px; display: inline-block; flex-shrink: 0; }}
.pr-resultado p {{ margin: 0; color: var(--tinta-2); font-size: .98rem; }}
.pr-resultado p b {{ color: var(--tinta); }}
.pr-res-tres {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; }}
.pr-res-tres div {{ border-top: 4px solid; padding-top: .55rem; }}
.pr-res-tres span {{ font-size: .85rem; color: var(--tinta-3); }}
.pr-res-tres b {{ display: block; font-family: 'Sora', sans-serif; font-size: 1.65rem; font-weight: 600; color: var(--tinta);
  font-variant-numeric: tabular-nums; letter-spacing: -.02em; }}
.pr-res-tres div.pr-res-max span {{ color: var(--tinta); font-weight: 600; }}
.pr-res-banda {{ grid-column: 1 / -1; }}
@media (max-width: 900px) {{ .pr-resultado {{ grid-template-columns: 1fr; padding: 1.4rem; }} .pr-res-clase {{ font-size: 2.3rem; }} }}

/* ---------- Avisos y etiquetas ---------- */
.pr-aviso {{ border-left: 3px solid var(--acento); background: var(--acento-claro); border-radius: 0 var(--radio-m) var(--radio-m) 0;
  padding: .85rem 1rem; color: #0B3B37; font-size: .93rem; line-height:1.5; }}
.pr-aviso.pr-alerta {{ border-color: #D97706; background: #FFF7E8; color: #5C3D0B; }}
.pr-fuente {{ font-size: .78rem; color: var(--tinta-3); margin-top: .35rem; }}
.pr-fuente code {{ font-size: .76rem; background: #F1F3F2; color: var(--tinta-2); padding: .05rem .35rem; border-radius: 5px; }}
.pr-etiqueta {{ display:inline-block; font-size:.76rem; font-weight:600; padding:.18rem .55rem; border-radius: 999px;
  background:#F1F3F2; color: var(--tinta-2); }}
.pr-etiqueta.pr-ok {{ background:#E7F6EC; color:#15803D; }}
.pr-etiqueta.pr-no {{ background:#FDECEC; color:#B91C1C; }}
.pr-estado-ok {{ margin: .2rem 0 0; font-size: .84rem; color: #15803D; }}

/* ---------- Simulador: pasos ---------- */
.pr-pasos {{ display:flex; gap:.4rem; margin:.3rem 0 .4rem; }}
.pr-pasos div {{ flex:1; height:4px; border-radius: 4px; background: var(--linea); }}
.pr-pasos div.pr-hecho {{ background: #9FCFC8; }}
.pr-pasos div.pr-actual {{ background: var(--acento); }}
.st-key-paso {{ width: 100% !important; }}
.st-key-paso [data-testid="stWidgetLabel"] {{ display: none; }}
.st-key-paso [data-testid="stRadioGroup"] {{ display: grid !important; grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: .55rem; width: 100%; counter-reset: paso; align-items: stretch !important; }}
.st-key-paso [data-testid="stRadioGroup"] > div {{ counter-increment: paso; min-width: 0; display: flex; align-self: stretch; height: auto !important; }}
.st-key-paso [data-testid="stRadioOption"] {{ flex: 1 1 auto; width: 100%; margin: 0 !important; background: var(--tarjeta);
  border: 1px solid var(--linea); border-radius: 14px; padding: .7rem .85rem .75rem; cursor: pointer;
  display: flex; flex-direction: column; align-items: flex-start; gap: .35rem;
  transition: border-color .15s ease, background-color .15s ease; }}
.st-key-paso [data-testid="stRadioOption"]::before {{ content: counter(paso); display: inline-flex; align-items: center;
  justify-content: center; width: 24px; height: 24px; border-radius: 999px; font-family: 'Sora', sans-serif;
  font-size: .78rem; font-weight: 600; background: #F1F3F2; color: var(--tinta-2); }}
.st-key-paso [data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) {{ display: none; }}
.st-key-paso [data-testid="stRadioOption"] p {{ font-size: .88rem; font-weight: 600; color: var(--tinta-2);
  line-height: 1.25; margin: 0; overflow-wrap: normal; word-break: normal; hyphens: none; }}
.st-key-paso [data-testid="stRadioOption"]:hover {{ border-color: #A7B3AF; }}
.st-key-paso [data-testid="stRadioOption"][data-selected="true"] {{ background: var(--acento-claro); border-color: var(--acento); }}
.st-key-paso [data-testid="stRadioOption"][data-selected="true"]::before {{ background: var(--acento); color: #fff; }}
.st-key-paso [data-testid="stRadioOption"][data-selected="true"] p {{ color: var(--acento-oscuro); }}
@media (max-width: 900px) {{ .st-key-paso [data-testid="stRadioGroup"] {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

/* ---------- Pestañas como control segmentado ---------- */
[data-testid="stTabs"] [role="tablist"] {{ background: #F1F3F2; border-radius: 12px; padding: 4px; gap: 2px;
  border: none !important; width: fit-content; max-width: 100%; overflow-x: auto; }}
[data-testid="stTab"] {{ border-radius: 9px !important; padding: .42rem .9rem !important; border: none !important; }}
[data-testid="stTab"] p {{ font-weight: 600 !important; color: var(--tinta-2) !important; font-size: .9rem !important; white-space: nowrap; }}
[data-testid="stTab"][aria-selected="true"] {{ background: var(--tarjeta); box-shadow: 0 1px 2px rgba(17,24,39,.08), 0 2px 8px -2px rgba(17,24,39,.12); }}
[data-testid="stTab"][aria-selected="true"] p {{ color: var(--tinta) !important; }}
[data-testid="stTabs"] .react-aria-SelectionIndicator {{ display: none !important; }}
[data-testid="stTabs"] [role="tabpanel"] {{ padding-top: .9rem; }}

/* ---------- Tarjetas, gráficos y controles ---------- */
[class*="st-key-tarjeta"] {{ background: var(--tarjeta); border-radius: var(--radio-l) !important; box-shadow: var(--sombra); }}
div[data-testid="stPlotlyChart"] {{ background: var(--tarjeta); border:1px solid var(--linea); border-radius: var(--radio-l);
  padding: .7rem .6rem .3rem; }}
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
  border-radius: 10px; font-weight: 600; padding: .5rem 1.05rem; }}
.stButton > button[kind="primary"] {{ background: var(--acento); border-color: var(--acento); color: #fff; }}
.stButton > button[kind="primary"]:hover {{ background: var(--acento-oscuro); border-color: var(--acento-oscuro); }}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{ outline: 2px solid var(--acento); outline-offset: 2px; }}
[data-testid="stDataFrame"] {{ border-radius: var(--radio-m); overflow: hidden; }}
[data-testid="stExpander"] details {{ border-radius: var(--radio-m); background: var(--tarjeta); }}
[data-testid="stNumberInputContainer"] {{ border-radius: 10px; }}

/* ---------- Flujo del modelo (Inicio) ---------- */
.pr-flujo {{ display: grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1.15fr; align-items: stretch; gap: .6rem; }}
.pr-nodo {{ background: var(--tarjeta); border: 1px solid var(--linea); border-radius: 16px; padding: 1rem 1.1rem; }}
.pr-nodo small {{ display: inline-flex; width: 22px; height: 22px; border-radius: 999px; align-items: center; justify-content: center;
  background: #F1F3F2; color: var(--tinta-2); font-family: 'Sora', sans-serif; font-weight: 600; font-size: .74rem; }}
.pr-nodo b {{ display: block; font-family: 'Sora', sans-serif; font-weight: 600; color: var(--tinta); margin: .55rem 0 .3rem;
  font-size: 1rem; letter-spacing: -.01em; }}
.pr-nodo p {{ margin: 0; color: var(--tinta-2); font-size: .86rem; line-height: 1.45; }}
.pr-nodo.pr-nodo-final {{ background: var(--acento-claro); border-color: #B7DAD4; }}
.pr-nodo.pr-nodo-final small {{ background: var(--acento); color: #fff; }}
.pr-nodo.pr-nodo-final .pr-espectro {{ margin-top: .7rem; }}
.pr-flecha {{ display: flex; align-items: center; color: #9CA3AF; font-size: 1.2rem; }}
@media (max-width: 1000px) {{ .pr-flujo {{ grid-template-columns: 1fr; }} .pr-flecha {{ justify-content: center; transform: rotate(90deg); }} }}

/* ---------- Animación ----------
   Al aparecer un resultado, las bandas crecen desde cero y los textos suben.
   Se desactiva si el sistema tiene activado "reducir movimiento". */
@keyframes pr-subir {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes pr-crecer {{ from {{ flex-grow: 0; }} }}
@keyframes pr-texto {{ 0%, 55% {{ color: transparent; }} }}
.pr-espectro div {{ animation: pr-crecer 1.1s cubic-bezier(.2,.75,.15,1) both, pr-texto 1.1s ease both; }}
.pr-espectro div:nth-child(2) {{ animation-delay: .09s; }}
.pr-espectro div:nth-child(3) {{ animation-delay: .18s; }}
.pr-hero-texto, .pr-resultado > div:first-child {{ animation: pr-subir .7s cubic-bezier(.2,.75,.15,1) both; }}
.pr-hero .pr-demo {{ animation: pr-subir .7s .12s cubic-bezier(.2,.75,.15,1) both; }}
.pr-cifra {{ animation: pr-subir .6s cubic-bezier(.2,.75,.15,1) both; }}
.pr-cifra:nth-child(2) {{ animation-delay: .06s; }} .pr-cifra:nth-child(3) {{ animation-delay: .12s; }}
.pr-cifra:nth-child(4) {{ animation-delay: .18s; }}
.pr-res-tres div {{ animation: pr-subir .55s cubic-bezier(.2,.75,.15,1) both; }}
.pr-res-tres div:nth-child(1) {{ animation-delay: .15s; }} .pr-res-tres div:nth-child(2) {{ animation-delay: .22s; }}
.pr-res-tres div:nth-child(3) {{ animation-delay: .29s; }}
.pr-nodo {{ animation: pr-subir .6s cubic-bezier(.2,.75,.15,1) both; }}
.pr-flujo > :nth-child(3) {{ animation-delay: .08s; }} .pr-flujo > :nth-child(5) {{ animation-delay: .16s; }}
.pr-flujo > :nth-child(7) {{ animation-delay: .24s; }}
@media (prefers-reduced-motion: reduce) {{
  .pr-espectro div, .pr-hero-texto, .pr-hero .pr-demo, .pr-cifra, .pr-res-tres div, .pr-resultado > div,
  .pr-nodo {{ animation: none !important; }}
}}
</style>
"""


def aplicar() -> None:
    st.html(_CSS)
