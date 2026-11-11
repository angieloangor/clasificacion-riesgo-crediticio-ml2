import pandas as pd
import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos, estado, graficos
from prisma_app.esquema import GRUPOS, etiqueta, formato_valor

art = datos.cargar_artefactos()
df = datos.cargar_dataset()

ui.encabezado("Comparar dos perfiles",
              "Elige dos perfiles sintéticos y observa en qué variables difieren y cómo cambia la respuesta del modelo.",
              ficha=ui.FICHA_MODELO)

FUENTES = ["Perfil actual del simulador", "Registro del dataset"]


def selector(col, clave: str, defecto: int, idx_defecto: int):
    with col:
        with st.container(border=True, key=f"tarjeta_perfil_{clave}"):
            st.markdown(f"**Perfil {clave}**")
            fuente = st.radio("Fuente", FUENTES, index=defecto, key=f"cmp_f_{clave}", horizontal=True,
                              label_visibility="collapsed")
            if fuente == FUENTES[0]:
                return dict(st.session_state.perfil), st.session_state.origen
            idx = st.number_input("Registro (0 – 4999)", 0, len(df) - 1, idx_defecto, 1, key=f"cmp_i_{clave}")
            fila = df.loc[int(idx)]
            conj = "entrenamiento" if int(idx) in datos.indices_entrenamiento() else "prueba"
            return ({c: fila[c] for c in art.columnas},
                    f"Registro #{int(idx)} ({conj}; etiqueta sintética {fila[C.OBJETIVO]})")


ca, cb = st.columns(2, gap="large")
pa, oa = selector(ca, "A", 0, 0)
# Por defecto B es un registro Poor del conjunto de prueba, para que la comparación sea informativa.
_, X_te, _, y_te = datos.particion()
idx_poor = int(y_te[y_te == "Poor"].index[0])
pb, ob = selector(cb, "B", 1, idx_poor)

ra, ea = estado.evaluar(pa, oa)
rb, eb = estado.evaluar(pb, ob)
if ea or eb:
    for e in ea + eb:
        st.error(e)
    st.stop()

with ca:
    st.caption(oa)
    ui.espectro(ra["probs"], ra["clase"], alto=44)
with cb:
    st.caption(ob)
    ui.espectro(rb["probs"], rb["clase"], alto=44)

ui.seccion("¿Cuánto cambian las probabilidades?", "predict_proba de cada perfil")
st.plotly_chart(graficos.comparar_probabilidades(ra["probs"], rb["probs"], "Perfil A", "Perfil B"),
                config=graficos.CONFIG, width="stretch")
delta = pd.DataFrame({"Clase": C.ORDEN_CLASES,
                      "Perfil A": [ra["probs"][c] for c in C.ORDEN_CLASES],
                      "Perfil B": [rb["probs"][c] for c in C.ORDEN_CLASES]})
delta["B − A (puntos)"] = (delta["Perfil B"] - delta["Perfil A"]) * 100
st.dataframe(delta, hide_index=True, width="stretch", column_config={
    "Perfil A": st.column_config.NumberColumn(format="%.4f"),
    "Perfil B": st.column_config.NumberColumn(format="%.4f"),
    "B − A (puntos)": st.column_config.NumberColumn(format="%+.2f")})

ui.seccion("¿En qué variables difieren?")
filas = []
for _, grupo, cols in GRUPOS:
    for c in cols:
        if str(ra["perfil"][c]) != str(rb["perfil"][c]):
            filas.append({"Sección": grupo, "Variable": etiqueta(c),
                          "Perfil A": formato_valor(c, ra["perfil"][c]), "Perfil B": formato_valor(c, rb["perfil"][c])})
if filas:
    st.caption(f"{len(filas)} de 23 variables tienen valores distintos.")
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
else:
    st.info("Los dos perfiles son idénticos.")

csv = pd.DataFrame([{**ra["perfil"], **{f"Prob_{c}": ra["probs"][c] for c in C.ORDEN_CLASES}, "Clase_predicha": ra["clase"], "Perfil": "A"},
                    {**rb["perfil"], **{f"Prob_{c}": rb["probs"][c] for c in C.ORDEN_CLASES}, "Clase_predicha": rb["clase"], "Perfil": "B"}])
st.download_button("Descargar comparación (CSV)", csv.to_csv(index=False).encode("utf-8-sig"),
                   file_name="prisma_comparacion.csv", mime="text/csv", icon=":material/download:")
ui.aviso(ui.AVISO_SINTETICO, alerta=True)
