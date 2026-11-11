"""Prisma — laboratorio de riesgo crediticio sintético (Machine Learning II).

Ejecutar desde la carpeta del proyecto:
    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Prisma · Riesgo crediticio sintético", page_icon="◭",
                   layout="wide", initial_sidebar_state="auto")

from prisma_app import componentes as ui  # noqa: E402
from prisma_app import estado, estilos  # noqa: E402

estilos.aplicar()
ui.marca_lateral()

try:
    estado.iniciar()
except FileNotFoundError as exc:
    st.error(f"No se encontró un archivo necesario: `{exc.filename}`. Ejecuta la app desde la carpeta "
             "del proyecto y verifica que existan `artefactos/` y `dataset_credit_score_colombia.csv`.")
    st.stop()

paginas = {
    "Plataforma": [
        st.Page("vistas/inicio.py", title="Inicio", icon=":material/space_dashboard:", default=True),
        st.Page("vistas/simulador.py", title="Simulador", icon=":material/tune:"),
        st.Page("vistas/resultado.py", title="Resultado", icon=":material/insights:"),
        st.Page("vistas/comparar.py", title="Comparar perfiles", icon=":material/compare_arrows:"),
        st.Page("vistas/lotes.py", title="Predicción por lotes", icon=":material/upload_file:"),
    ],
    "Modelo": [
        st.Page("vistas/interpretabilidad.py", title="Interpretabilidad", icon=":material/psychology_alt:"),
        st.Page("vistas/modelos.py", title="Comparación de modelos", icon=":material/leaderboard:"),
        st.Page("vistas/metodologia.py", title="Metodología", icon=":material/menu_book:"),
    ],
}
nav = st.navigation(paginas, position="hidden")
with st.sidebar:
    for grupo, lista in paginas.items():
        st.html(f'<div class="pr-grupo-nav">{grupo}</div>')
        for pagina in lista:
            st.page_link(pagina)
ui.nota_lateral()
nav.run()
