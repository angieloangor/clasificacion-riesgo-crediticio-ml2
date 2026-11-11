import json
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Riesgo crediticio — ML II", layout="wide")
st.title("Clasificación de riesgo crediticio — FICO adaptado a Colombia")
st.warning("Prototipo académico entrenado con etiquetas sintéticas. No utilizar para conceder o denegar créditos reales.")
root = Path(__file__).parent
artefactos = root / "artefactos"
modelo = joblib.load(artefactos / "modelo_credito.joblib")
encoder = joblib.load(artefactos / "encoder_etiquetas.joblib")
esquema = json.loads((artefactos / "esquema.json").read_text(encoding="utf-8"))
ejemplo = json.loads((artefactos / "ejemplo_entrada.json").read_text(encoding="utf-8"))[0]
categorias = json.loads((root / "categorias_validas.json").read_text(encoding="utf-8"))
st.write("Introduce las características de un perfil sintético. Las categorías están restringidas a los valores usados en el entrenamiento.")
with st.form("evaluar"):
    columnas_ui = st.columns(2)
    valores = {}
    for i, nombre in enumerate(esquema["columnas"]):
        with columnas_ui[i % 2]:
            if nombre in esquema["categoricas"]:
                opciones = categorias[nombre]
                inicial = opciones.index(str(ejemplo[nombre])) if str(ejemplo[nombre]) in opciones else 0
                valores[nombre] = st.selectbox(nombre, opciones, index=inicial)
            else:
                valores[nombre] = st.number_input(nombre, value=float(ejemplo[nombre]), format="%.4f")
    enviado = st.form_submit_button("Calcular clasificación", type="primary")
if enviado:
    entrada = pd.DataFrame([valores], columns=esquema["columnas"])
    pred = int(modelo.predict(entrada)[0])
    clase = str(encoder.inverse_transform([pred])[0])
    st.subheader(f"Clase predicha: {clase}")
    if hasattr(modelo, "predict_proba"):
        probabilidades = modelo.predict_proba(entrada)[0]
        clases = encoder.inverse_transform(modelo.classes_.astype(int))
        tabla = pd.DataFrame({"Clase":clases, "Probabilidad":probabilidades})
        st.bar_chart(tabla.set_index("Clase"))
        st.dataframe(tabla.style.format({"Probabilidad":"{:.1%}"}), hide_index=True)
    st.info("Las probabilidades corresponden a clases simuladas y no son probabilidades reales de incumplimiento.")
