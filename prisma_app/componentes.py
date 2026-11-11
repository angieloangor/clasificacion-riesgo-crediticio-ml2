"""Componentes visuales reutilizables (HTML ligero sobre Streamlit)."""
from __future__ import annotations

import html

import streamlit as st

from . import config as C


def _e(t) -> str:
    return html.escape(str(t))


def pct(x: float, dec: int = 1) -> str:
    return f"{100 * x:.{dec}f} %".replace(".", ",")


def num(x: float, dec: int = 3) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


LOGO_SVG = '<img src="/app/static/prisma.svg" width="34" height="34" alt="">'


def marca_lateral() -> None:
    with st.sidebar:
        st.html(f"""<div class="pr-marca">{LOGO_SVG}
        <div><b>Prisma</b><small>Laboratorio de riesgo crediticio sintético</small></div></div>""")


def nota_lateral() -> None:
    with st.sidebar:
        st.html("""<div class="pr-lateral-nota"><b>Nicolás Barrera · Angie Loango</b><br>
        Proyecto académico de Machine Learning II.
        Datos y etiquetas sintéticos: los resultados no sirven para aprobar o negar créditos reales.</div>""")


FICHA_MODELO = "Modelo activo: regresión logística · C = 0,001"


def encabezado(titulo: str, texto: str = "", ficha: str | None = None) -> None:
    """Título de página. `ficha` muestra a la derecha qué modelo responde."""
    cuerpo = f"<div><h1>{_e(titulo)}</h1>" + (f"<p>{texto}</p>" if texto else "") + "</div>"
    if ficha:
        st.html(f'<div class="pr-encabezado pr-con-ficha">{cuerpo}<span class="pr-ficha"><i></i>{_e(ficha)}</span></div>')
    else:
        st.html(f'<div class="pr-encabezado">{cuerpo}</div>')


def seccion(titulo: str, nota: str = "") -> None:
    st.html(f'<div class="pr-seccion"><h3>{_e(titulo)}</h3><span>{_e(nota)}</span></div>')


def pregunta(texto: str) -> None:
    st.html(f'<p class="pr-pregunta">{texto}</p>')


def fuente(texto: str) -> None:
    st.html(f'<div class="pr-fuente">{texto}</div>')


def aviso(texto: str, alerta: bool = False) -> None:
    st.html(f'<div class="pr-aviso{" pr-alerta" if alerta else ""}">{texto}</div>')


def espectro_html(probs: dict, resaltar: str | None = None, etiquetas: bool = True,
                  alto: int = 46, sufijo_leyenda: dict | None = None, leyenda_compacta: bool = False) -> str:
    """Barra de tres bandas proporcional a las probabilidades (o proporciones)."""
    bandas = []
    for c in C.ORDEN_CLASES:
        p = float(probs[c])
        txt = pct(p, 1) if (etiquetas and p >= 0.09) else ""
        tenue = " pr-tenue" if (resaltar and c != resaltar) else ""
        bandas.append(f'<div class="{tenue.strip()}" style="flex-grow:{p:.6f};flex-basis:0;'
                      f'background:{C.COLOR_CLASE[c]};color:{C.TEXTO_SOBRE_CLASE[c]}" title="{c}: {pct(p, 2)}">{txt}</div>')
    ley = "".join(
        f'<span class="{"pr-mayor" if c == resaltar else ""}"><i style="background:{C.COLOR_CLASE[c]}"></i>{c}'
        + (f" · {sufijo_leyenda[c]}" if sufijo_leyenda else "")
        + (" · mayor probabilidad" if (c == resaltar and not leyenda_compacta) else "") + "</span>"
        for c in C.ORDEN_CLASES)
    return (f'<div class="pr-espectro" style="height:{alto}px" role="img" aria-label="'
            + ", ".join(f"{c} {pct(float(probs[c]), 1)}" for c in C.ORDEN_CLASES)
            + f'">{"".join(bandas)}</div><div class="pr-espectro-leyenda">{ley}</div>')


def espectro(probs: dict, resaltar: str | None = None, **kw) -> None:
    st.html(espectro_html(probs, resaltar, **kw))


def cifras(items: list[tuple[str, str, str]]) -> None:
    """items: (valor, etiqueta, nota)."""
    cel = "".join(f'<div class="pr-cifra"><b>{v}</b><span>{_e(e)}</span>'
                  + (f"<small>{n}</small>" if n else "") + "</div>" for v, e, n in items)
    st.html(f'<div class="pr-cifras">{cel}</div>')


def resultado_principal(probs: dict, clase: str) -> None:
    """Tarjeta oscura con la clase predicha, las tres probabilidades y el espectro."""
    tres = "".join(
        f'<div class="{"pr-res-max" if c == clase else ""}" style="border-color:{C.COLOR_CLASE[c]}">'
        f'<span>{c}</span><b>{pct(probs[c], 2)}</b></div>' for c in C.ORDEN_CLASES)
    st.html(f"""<section class="pr-resultado" aria-label="Resultado de la predicción">
      <div><span class="pr-res-etiqueta">Clase predicha</span>
        <div class="pr-res-clase"><i style="background:{C.COLOR_CLASE[clase]}"></i>{_e(clase)}</div>
        <p>Probabilidad asignada por el modelo: <b>{pct(probs[clase], 1)}</b> · {C.DESCRIPCION_CLASE[clase]}</p></div>
      <div class="pr-res-tres">{tres}</div>
      <div class="pr-res-banda">{espectro_html(probs, clase, alto=50)}</div>
    </section>""")


def veredicto(clase: str, prob: float) -> None:
    st.html(f"""<div class="pr-veredicto">
      <div class="pr-sello" style="background:{C.COLOR_CLASE[clase]}">{_e(clase)}</div>
      <div><h2>Clase predicha: {_e(clase)}</h2>
      <p>Probabilidad asignada por el modelo: <b class="pr-num">{pct(prob, 1)}</b> · {C.DESCRIPCION_CLASE[clase]}</p></div>
    </div>""")


def pasos(actual: int, visitados: set, total: int) -> None:
    barras = "".join(
        f'<div class="{"pr-actual" if i == actual else ("pr-hecho" if i in visitados else "")}"></div>'
        for i in range(total))
    st.html(f'<div class="pr-pasos" aria-hidden="true">{barras}</div>')


def etiqueta_estado(ok: bool, si: str = "Verificado", no: str = "No verificado") -> str:
    return f'<span class="pr-etiqueta {"pr-ok" if ok else "pr-no"}">{si if ok else no}</span>'


AVISO_SINTETICO = ("Resultado de un modelo entrenado con <b>etiquetas sintéticas</b>. Las probabilidades indican "
                   "a qué clase simulada se parece el perfil; no son probabilidades de incumplimiento ni una "
                   "recomendación financiera, y no deben usarse para aprobar o negar créditos.")
