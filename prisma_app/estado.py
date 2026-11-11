"""Estado de sesión compartido entre páginas."""
from __future__ import annotations

import streamlit as st

from . import datos
from .esquema import VARIABLES
from .validacion import preparar_entrada, validar_perfil


def iniciar() -> None:
    if "perfil" not in st.session_state:
        base, idx = datos.perfil_base()
        st.session_state.perfil = dict(base)
        st.session_state.origen = f"Perfil base: registro #{idx} del entrenamiento (el más cercano a la mediana)"
    st.session_state.setdefault("paso", 0)
    st.session_state.setdefault("visitados", {0})
    st.session_state.setdefault("derivar", True)
    st.session_state.setdefault("version", 0)


def limpiar_widgets() -> None:
    """Invalida los campos del formulario.

    Además de borrar sus claves, cambia la versión que forma parte de cada clave:
    así el navegador crea widgets nuevos y no reenvía valores del perfil anterior.
    """
    st.session_state.version = st.session_state.get("version", 0) + 1
    for k in [k for k in st.session_state.keys() if str(k).startswith("in_")]:
        del st.session_state[k]


def fijar_perfil(perfil: dict, origen: str) -> None:
    st.session_state.perfil = dict(perfil)
    st.session_state.origen = origen
    limpiar_widgets()


def restablecer() -> None:
    base, idx = datos.perfil_base()
    fijar_perfil(base, f"Perfil base: registro #{idx} del entrenamiento (el más cercano a la mediana)")
    st.session_state.paso = 0
    st.session_state.visitados = {0}


def evaluar(perfil: dict, origen: str):
    """Valida y predice un perfil. Devuelve (resultado | None, errores)."""
    from .prediccion import predecir
    art = datos.cargar_artefactos()
    errores, advertencias = validar_perfil(perfil, art.columnas, datos.rangos(), art.categorias, datos.tipos_columnas())
    if errores:
        return None, errores
    X = preparar_entrada(perfil, art.columnas, datos.tipos_columnas())
    pred = predecir(art, X).iloc[0]
    probs = {c: float(pred[f"Prob_{c}"]) for c in ("Good", "Standard", "Poor")}
    return {"perfil": X.iloc[0].to_dict(), "probs": probs, "clase": str(pred["Clase_predicha"]),
            "origen": origen, "advertencias": advertencias}, []


def tipo_widget(nombre: str) -> str:
    return VARIABLES[nombre].tipo
