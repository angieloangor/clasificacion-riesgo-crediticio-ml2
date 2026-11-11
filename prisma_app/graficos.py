"""Gráficos Plotly con un estilo uniforme.

Cada función recibe datos ya calculados (del dataset, de los archivos de
resultados o del Pipeline) y solo se ocupa de la presentación.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import config as C
from .esquema import VARIABLES, etiqueta

FUENTE = "Instrument Sans, system-ui, -apple-system, Segoe UI, sans-serif"
GRID = "#EEF1F0"
CONFIG = {"displaylogo": False, "responsive": True,
          "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines"]}
GRIS = "#B4BDCA"
NEGATIVO = "#DDE3EB"  # barras que alejan de la clase: claras, con borde, distinguibles incluso para Standard
SERIE_A, SERIE_B = "#A7D7CF", C.ACENTO


def tema(fig: go.Figure, alto: int = 380, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        height=alto, margin=dict(l=12, r=20, t=28, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FUENTE, size=13, color=C.TINTA_2),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=C.LINEA, font=dict(family=FUENTE, color=C.TINTA, size=13)),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text="",
                    font=dict(size=12.5, color=C.TINTA_2)),
        bargap=0.32,
        separators=",.",  # coma decimal y punto de miles, como en el resto de la interfaz
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor="#C9D2DE", linecolor=C.LINEA, tickfont=dict(color=C.TINTA_3),
                     title_font=dict(size=12.5, color=C.TINTA_2))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor="#C9D2DE", linecolor=C.LINEA, tickfont=dict(color=C.TINTA_2),
                     title_font=dict(size=12.5, color=C.TINTA_2))
    return fig


def _eje_valor(var: str) -> str:
    v = VARIABLES.get(var)
    return f"{etiqueta(var)} ({v.unidad})" if v and v.unidad else etiqueta(var)


# ---------------- Resultado ----------------

def barras_probabilidad(probs: dict, predicha: str) -> go.Figure:
    clases = C.ORDEN_CLASES[::-1]
    vals = [probs[c] for c in clases]
    fig = go.Figure(go.Bar(
        x=vals, y=clases, orientation="h",
        marker=dict(color=[C.COLOR_CLASE[c] for c in clases],
                    opacity=[1 if c == predicha else 0.5 for c in clases],
                    line=dict(width=0), cornerradius=4),
        text=[f"{v * 100:.2f} %".replace(".", ",") + ("  ← mayor" if c == predicha else "") for c, v in zip(clases, vals)],
        textposition="outside", textfont=dict(color=C.TINTA, size=13),
        hovertemplate="%{y}: %{x:.4f}<extra>predict_proba</extra>", cliponaxis=False))
    fig.update_xaxes(range=[0, max(vals) * 1.35 + 0.02], tickformat=".0%", title="Probabilidad (predict_proba)")
    tema(fig, alto=230, leyenda=False)
    fig.update_layout(margin=dict(l=12, r=34, t=28, b=12))
    return fig


def contribuciones(tabla: pd.DataFrame, clase: str, n: int = 10) -> go.Figure:
    t = tabla[tabla["clase"] == clase].copy()
    t["abs"] = t["contribucion"].abs()
    t = t.sort_values("abs", ascending=False).head(n).sort_values("contribucion")
    color = C.COLOR_CLASE[clase]
    fig = go.Figure(go.Bar(
        x=t["contribucion"], y=[etiqueta(v) for v in t["variable"]], orientation="h",
        marker=dict(color=[color if v > 0 else NEGATIVO for v in t["contribucion"]], cornerradius=4,
                    line=dict(color=["rgba(0,0,0,0)" if v > 0 else "#8D99AB" for v in t["contribucion"]], width=1)),
        hovertemplate="%{y}: %{x:+.4f}<extra>contribución al logit</extra>"))
    fig.add_vline(x=0, line_color="#9AA6B6", line_width=1)
    fig.update_xaxes(title=f"Contribución a la puntuación lineal de {clase} (vs. perfil promedio)")
    return tema(fig, alto=max(300, 34 * len(t) + 80), leyenda=False)


def comparar_probabilidades(pa: dict, pb: dict, na: str, nb: str) -> go.Figure:
    fig = go.Figure()
    for nombre, p, col in [(na, pa, SERIE_A), (nb, pb, SERIE_B)]:
        fig.add_bar(name=nombre, x=C.ORDEN_CLASES, y=[p[c] for c in C.ORDEN_CLASES],
                    marker=dict(color=col, cornerradius=4, line=dict(color="#FFFFFF", width=2)),
                    text=[f"{p[c] * 100:.1f} %".replace(".", ",") for c in C.ORDEN_CLASES],
                    textposition="outside", textfont=dict(color=C.TINTA),
                    hovertemplate="%{x}: %{y:.4f}<extra>" + nombre + "</extra>", cliponaxis=False)
    fig.update_yaxes(tickformat=".0%", title="Probabilidad", rangemode="tozero")
    fig.update_layout(barmode="group", bargroupgap=0.08)
    return tema(fig, alto=340)


# ---------------- Datos ----------------

def caja_por_clase(df: pd.DataFrame, var: str) -> go.Figure:
    """Boxplot por clase: caja rellena con el color de la clase, mediana marcada y media punteada."""
    from .esquema import formato_valor
    fig = go.Figure()
    for c in C.ORDEN_CLASES:
        y = df.loc[df[C.OBJETIVO] == c, var]
        fig.add_box(y=y, name=c, boxpoints=False, boxmean=True, width=0.5, whiskerwidth=0.4,
                    fillcolor=C.SUAVE_CLASE[c], line=dict(color=C.COLOR_CLASE[c], width=2.2),
                    hovertemplate=f"<b>{c}</b><br>%{{y:,.3~f}}<extra></extra>")
        med = float(y.median())
        fig.add_annotation(x=c, y=float(y.quantile(0.75)), text=f"mediana {formato_valor(var, med)}",
                           showarrow=False, yshift=16, bgcolor="#FFFFFF", borderpad=3,
                           bordercolor=C.LINEA, borderwidth=1, font=dict(size=12, color=C.TINTA))
    fig.update_yaxes(title=_eje_valor(var), gridcolor=GRID, zeroline=False)
    fig.update_xaxes(showgrid=False, tickfont=dict(size=14, color=C.TINTA))
    return tema(fig, alto=400, leyenda=False)


def promedio_por_clase(df: pd.DataFrame, var: str) -> go.Figure:
    """Promedio de una variable numérica en cada clase (barras horizontales con el valor escrito)."""
    from .esquema import formato_valor
    g = df.groupby(C.OBJETIVO)[var]
    media, mediana, n = g.mean(), g.median(), g.size()
    clases = C.ORDEN_CLASES[::-1]
    fig = go.Figure(go.Bar(
        x=[media[c] for c in clases], y=clases, orientation="h",
        marker=dict(color=[C.COLOR_CLASE[c] for c in clases], cornerradius=8, line=dict(width=0)),
        text=[formato_valor(var, media[c]) for c in clases], textposition="outside", cliponaxis=False,
        textfont=dict(color=C.TINTA, size=15, family="Sora, " + FUENTE),
        customdata=[[formato_valor(var, mediana[c]), f"{n[c]:,}".replace(",", ".")] for c in clases],
        hovertemplate="%{y}<br>Promedio: %{text}<br>Mediana: %{customdata[0]}<br>Perfiles: %{customdata[1]}<extra></extra>"))
    fig.update_xaxes(range=[0, media.max() * 1.28], showticklabels=False, showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=14, color=C.TINTA))
    tema(fig, alto=260, leyenda=False)
    fig.update_layout(bargap=0.48, margin=dict(l=12, r=60, t=10, b=10))
    fig.update_xaxes(showgrid=False, showticklabels=False)
    return fig


def composicion_categorica(df: pd.DataFrame, var: str) -> go.Figure:
    tab = pd.crosstab(df[var], df[C.OBJETIVO], normalize="index")[C.ORDEN_CLASES]
    n = df[var].value_counts()
    tab = tab.loc[tab["Poor"].sort_values().index]
    fig = go.Figure()
    for c in C.ORDEN_CLASES:
        fig.add_bar(name=c, y=[f"{i} (n={n[i]:,})".replace(",", ".") for i in tab.index], x=tab[c], orientation="h",
                    marker=dict(color=C.COLOR_CLASE[c], line=dict(color="#FFFFFF", width=2), cornerradius=6),
                    text=[f"{v * 100:.0f} %" if v >= 0.07 else "" for v in tab[c]], textposition="inside",
                    insidetextanchor="middle", textfont=dict(color=C.TEXTO_SOBRE_CLASE[c], size=12.5),
                    hovertemplate="%{y}<br>" + c + ": %{x:.1%}<extra></extra>")
    fig.update_layout(barmode="stack", bargap=0.42, legend_traceorder="normal")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], title="Proporción de perfiles dentro de la categoría",
                     showgrid=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=13.5, color=C.TINTA))
    return tema(fig, alto=max(260, 54 * len(tab) + 110))


def promedio_por_grupo(df: pd.DataFrame, var: str, bins: int = 8) -> go.Figure:
    """Proporción de cada clase por intervalos (cuantiles) de una variable numérica."""
    x = df[var]
    q = pd.qcut(x, q=bins, duplicates="drop")
    tab = pd.crosstab(q, df[C.OBJETIVO], normalize="index")[C.ORDEN_CLASES]
    def _f(v):
        return f"{v:,.3g}".replace(",", "_").replace(".", ",").replace("_", ".")
    # el primer límite de qcut queda levemente bajo el mínimo; se muestra el mínimo real
    etiquetas = [f"{_f(max(iv.left, float(x.min())))} – {_f(iv.right)}" for iv in tab.index]
    fig = go.Figure()
    for c in C.ORDEN_CLASES:
        fig.add_scatter(x=etiquetas, y=tab[c], name=c, mode="lines+markers",
                        line=dict(color=C.COLOR_CLASE[c], width=3, shape="spline", smoothing=0.6),
                        marker=dict(size=10, color=C.COLOR_CLASE[c], line=dict(color="#fff", width=2.5)),
                        hovertemplate="%{x}<br>" + c + ": %{y:.1%}<extra></extra>")
        fig.add_annotation(x=etiquetas[-1], y=float(tab[c].iloc[-1]), text=f"<b>{c}</b>", showarrow=False,
                           xanchor="left", xshift=12, font=dict(color=C.TINTA, size=12.5))
    fig.update_yaxes(tickformat=".0%", title="Proporción de perfiles en el tramo", rangemode="tozero", gridcolor=GRID)
    fig.update_xaxes(title=f"Tramos de {_eje_valor(var)} (cada uno con un número similar de perfiles)",
                     type="category", showgrid=False)
    tema(fig, alto=400)
    fig.update_layout(margin=dict(l=12, r=80, t=28, b=12), hovermode="x unified")
    return fig


# ---------------- Modelo ----------------

def matriz_confusion(cm: pd.DataFrame, normalizar: bool) -> go.Figure:
    m = cm.loc[C.ORDEN_CLASES, C.ORDEN_CLASES].astype(float)
    filas = m.sum(axis=1).values[:, None]
    porc = m.values / filas
    z = porc if normalizar else m.values
    texto = [[f"{int(m.values[i, j])}<br><span style='font-size:11px'>{porc[i, j] * 100:.1f} %</span>".replace(".", ",")
              for j in range(3)] for i in range(3)]
    fig = go.Figure(go.Heatmap(
        z=z, x=C.ORDEN_CLASES, y=C.ORDEN_CLASES, text=texto, texttemplate="%{text}",
        colorscale=[[0, "#F0F7F5"], [0.5, "#7CC1B6"], [1, "#0B5A54"]], showscale=False, xgap=3, ygap=3,
        hovertemplate="Real %{y} → Predicha %{x}<extra></extra>"))
    fig.update_traces(textfont=dict(size=15))  # Plotly elige texto claro/oscuro según el fondo
    fig.update_yaxes(title="Clase real", autorange="reversed", showgrid=False)
    fig.update_xaxes(title="Clase predicha", side="top", showgrid=False)
    return tema(fig, alto=400, leyenda=False)


def importancia(df: pd.DataFrame, n: int = 23) -> go.Figure:
    t = df.sort_values("importance", ascending=False).head(n).sort_values("importance")
    fig = go.Figure(go.Bar(
        x=t["importance"], y=[etiqueta(v) for v in t["feature"]], orientation="h",
        error_x=dict(type="data", array=t["sd"], color="#9AA6B6", thickness=1.2, width=3),
        marker=dict(color=[C.TURQUESA if v > 0 else GRIS for v in t["importance"]], cornerradius=3),
        hovertemplate="%{y}<br>ΔF1 macro: %{x:+.4f}<extra></extra>"))
    fig.add_vline(x=0, line_color="#9AA6B6", line_width=1)
    fig.update_xaxes(title="Disminución media del F1 macro al permutar la variable (± desv.)")
    return tema(fig, alto=max(360, 24 * len(t) + 90), leyenda=False)


def pdp(x, curvas: dict, var: str) -> go.Figure:
    fig = go.Figure()
    for c in C.ORDEN_CLASES:
        if c in curvas:
            fig.add_scatter(x=x, y=curvas[c], name=c, mode="lines", line=dict(color=C.COLOR_CLASE[c], width=2.4),
                            hovertemplate=f"{etiqueta(var)} = %{{x:,.3~f}}<br>{c}: %{{y:.3f}}<extra></extra>")
    fig.update_xaxes(title=_eje_valor(var))
    fig.update_yaxes(title="Probabilidad media predicha", tickformat=".0%")
    fig.update_layout(hovermode="x unified")
    return tema(fig, alto=380)


def coeficientes(df: pd.DataFrame, clase: str, n: int = 36) -> go.Figure:
    t = df[df["clase"] == clase].copy()
    t["nombre"] = [etiqueta(v) + (f": {lv}" if lv else "") for v, lv in zip(t["variable"], t["nivel"])]
    t = t.reindex(t["coeficiente"].abs().sort_values(ascending=False).index).head(n).sort_values("coeficiente")
    fig = go.Figure(go.Bar(
        x=t["coeficiente"], y=t["nombre"], orientation="h",
        marker=dict(color=[C.COLOR_CLASE[clase] if v > 0 else NEGATIVO for v in t["coeficiente"]], cornerradius=3,
                    line=dict(color=["rgba(0,0,0,0)" if v > 0 else "#8D99AB" for v in t["coeficiente"]], width=1)),
        customdata=np.stack([t["tipo"]], axis=-1),
        hovertemplate="%{y}<br>coeficiente: %{x:+.4f}<br>%{customdata[0]}<extra></extra>"))
    fig.add_vline(x=0, line_color="#9AA6B6", line_width=1)
    fig.update_xaxes(title=f"Coeficiente en la puntuación de {clase} (numéricas: por 1 desv. estándar)")
    return tema(fig, alto=max(380, 22 * len(t) + 90), leyenda=False)


FAMILIA = {
    "Logistic Regression": "Lineal", "Naive Bayes": "Probabilístico simple", "Decision Tree": "Árbol único",
    "SVM": "Kernel", "Random Forest": "Ensamble", "Gradient Boosting": "Ensamble", "XGBoost": "Ensamble",
    "LightGBM": "Ensamble", "AdaBoost": "Ensamble", "Baseline": "Referencia",
}


def comparacion_modelos(df: pd.DataFrame, col: str, err: str | None, final: str, titulo_x: str,
                        referencia: float | None = None) -> go.Figure:
    t = df.sort_values(col)
    colores = [C.ACENTO if m == final else ("#E5E7EB" if m == "Baseline" else "#A8B3AF") for m in t["Modelo"]]
    fig = go.Figure(go.Bar(
        x=t[col], y=t["Modelo"], orientation="h",
        error_x=dict(type="data", array=t[err], color="#6B7A90", thickness=1.2, width=3) if err else None,
        marker=dict(color=colores, cornerradius=4),
        text=[f"{v:.3f}".replace(".", ",") for v in t[col]], textposition="inside", insidetextanchor="start",
        textfont=dict(color=["#4B5563" if m == "Baseline" else "#FFFFFF" for m in t["Modelo"]], size=12),
        customdata=[FAMILIA.get(m, "") for m in t["Modelo"]], cliponaxis=False,
        hovertemplate="%{y} · %{customdata}<br>F1 macro: %{x:.4f}<extra></extra>"))
    if referencia is not None:
        fig.add_vline(x=referencia, line_dash="dot", line_color=C.TINTA_3, line_width=1,
                      annotation_text="Baseline", annotation_position="top", annotation_font_color=C.TINTA_3)
    fig.update_xaxes(title=titulo_x, range=[0, max(t[col]) * 1.15])
    return tema(fig, alto=max(280, 38 * len(t) + 80), leyenda=False)


def pesos_generacion(filas) -> go.Figure:
    t = pd.DataFrame(filas, columns=["senal", "variable", "grupo", "peso", "signo"])
    t["valor"] = t["peso"] * t["signo"]
    t = t.sort_values("valor")
    fig = go.Figure(go.Bar(
        x=t["valor"], y=t["senal"], orientation="h",
        marker=dict(color=[C.COLOR_CLASE["Poor"] if v > 0 else C.COLOR_CLASE["Good"] for v in t["valor"]], cornerradius=3),
        text=[f"{abs(v) * 100:.2f} %".replace(".", ",") for v in t["valor"]], textposition="outside",
        textfont=dict(color=C.TINTA), customdata=t["grupo"], cliponaxis=False,
        hovertemplate="%{y}<br>Grupo FICO: %{customdata}<br>peso: %{x:+.4f}<extra></extra>"))
    fig.add_vline(x=0, line_color="#9AA6B6", line_width=1)
    fig.update_xaxes(title="Peso en el riesgo latente (negativo = protector)", range=[-0.22, 0.22], tickformat=".0%")
    return tema(fig, alto=380, leyenda=False)
