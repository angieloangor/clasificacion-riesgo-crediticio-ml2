import pandas as pd
import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos, graficos, prediccion, reporte
from prisma_app.esquema import GRUPOS, etiqueta, formato_valor
from prisma_app.validacion import preparar_entrada

res = st.session_state.get("resultado")
if not res:
    ui.encabezado("Resultado de la predicción", "Todavía no hay una predicción en esta sesión.")
    with st.container(border=True, key="tarjeta_vacio"):
        st.markdown("Completa o ajusta un perfil en el simulador y pulsa **Calcular clasificación**. "
                    "El resultado aparecerá aquí con sus probabilidades exactas y una explicación individual.")
        st.page_link("vistas/simulador.py", label="Ir al simulador", icon=":material/tune:")
    st.stop()

art = datos.cargar_artefactos()
m = datos.metricas_prueba()
probs, clase, perfil = res["probs"], res["clase"], res["perfil"]
orden = sorted(probs, key=probs.get, reverse=True)
margen = probs[orden[0]] - probs[orden[1]]

ui.encabezado("Resultado de la predicción", f"Origen del perfil: {res['origen']}.", ficha=ui.FICHA_MODELO)

# ---------------- Veredicto y probabilidades ----------------
ui.resultado_principal(probs, clase)

pts = f"{margen * 100:.1f} puntos porcentuales".replace(".", ",")
if margen < 0.05:
    lectura = (f"Resultado ajustado: <b>{clase}</b> supera a <b>{orden[1]}</b> por solo {pts}. "
               "El perfil está cerca de la frontera entre ambas clases.")
elif margen < 0.15:
    lectura = f"<b>{clase}</b> supera a <b>{orden[1]}</b> por {pts}: una preferencia moderada."
else:
    lectura = f"<b>{clase}</b> domina con {pts} de ventaja sobre <b>{orden[1]}</b>."
prec = m["precision_por_clase"][clase]
lectura += (f"<br>En los datos de prueba, cuando el modelo predijo {clase} acertó el {ui.pct(prec)} de las veces.")

col_g, col_t = st.columns([1.5, 1], gap="large")
with col_g:
    ui.seccion("Probabilidades por clase", "predict_proba")
    st.plotly_chart(graficos.barras_probabilidad(probs, clase), config=graficos.CONFIG, width="stretch")
    with st.expander("Valores exactos"):
        tabla = pd.DataFrame({"Clase": C.ORDEN_CLASES, "Probabilidad": [probs[c] for c in C.ORDEN_CLASES]})
        st.dataframe(tabla, hide_index=True, width="stretch",
                     column_config={"Probabilidad": st.column_config.NumberColumn(format="%.6f")})
        st.caption(f"Suma: {sum(probs.values()):.6f}")
with col_t:
    ui.seccion("Cómo leerlo")
    ui.aviso(lectura)
    et = res.get("etiqueta_real")
    if et:
        coincide = et[1] == clase
        st.html(f'<p class="pr-pregunta" style="margin-top:.8rem">Registro #{et[0]} ({et[2]}): etiqueta sintética '
                f'<b>{et[1]}</b> {ui.etiqueta_estado(coincide, "coincide", "no coincide")}'
                + ("<br>El modelo ya vio este caso durante el entrenamiento." if et[2] == "entrenamiento" else "")
                + "</p>")

# ---------------- Explicación individual ----------------
ui.seccion("Explicación individual", "calculada con los coeficientes del modelo entrenado")
X_tr, *_ = datos.particion()


@st.cache_data(show_spinner=False)
def _ref():
    return prediccion.referencia(datos.cargar_artefactos(), X_tr)


x = preparar_entrada(perfil, art.columnas, datos.tipos_columnas())
exp = prediccion.explicar(art, x, _ref())
clase_exp = st.radio("Explicar la puntuación de", C.ORDEN_CLASES, index=C.ORDEN_CLASES.index(clase),
                     horizontal=True, key="clase_exp")
ui.pregunta(f"¿Qué variables acercan o alejan este perfil de <b>{clase_exp}</b> en comparación con el perfil "
            "promedio del entrenamiento? Barras de color (a la derecha): empujan hacia la clase; barras claras (a la izquierda): la alejan.")
st.plotly_chart(graficos.contribuciones(exp["tabla"], clase_exp, n=10), config=graficos.CONFIG, width="stretch")
suma = exp["tabla"].query("clase == @clase_exp")["contribucion"].sum()
st.caption(f"Puntuación lineal (logit) de {clase_exp}: perfil promedio {exp['z_ref'][clase_exp]:+.4f} + "
           f"suma de contribuciones {suma:+.4f} = {exp['z_x'][clase_exp]:+.4f}. La descomposición es exacta "
           "porque el modelo es lineal antes de softmax; describe cómo razona el modelo, no causas reales.")
with st.expander("Ver las 23 contribuciones"):
    t = (exp["tabla"].pivot(index="variable", columns="clase", values="contribucion")[C.ORDEN_CLASES]
         .assign(Variable=lambda d: [etiqueta(v) for v in d.index]).set_index("Variable")
         .sort_values(clase_exp, key=abs, ascending=False))
    st.dataframe(t.style.format("{:+.4f}"), width="stretch")

# ---------------- Advertencias, perfil y descargas ----------------
if res["advertencias"]:
    ui.seccion("Advertencias de coherencia")
    for a in res["advertencias"]:
        st.warning(a, icon=":material/warning:")

with st.expander("Perfil evaluado (23 predictores)"):
    filas = [{"Sección": t, "Variable": etiqueta(c), "Columna": c, "Valor": formato_valor(c, perfil[c])}
             for _, t, cols in GRUPOS for c in cols]
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")

ui.seccion("Descargar")
top = (exp["tabla"].query("clase == @clase").assign(a=lambda d: d.contribucion.abs())
       .sort_values("a", ascending=False).head(6))
d1, d2, d3 = st.columns([1, 1, 2])
d1.download_button("Resumen (HTML)", reporte.html_prediccion(perfil, probs, clase, res["origen"], res["advertencias"],
                                                             list(zip(top.variable, top.contribucion))),
                   file_name=f"prisma_prediccion_{clase}.html", mime="text/html", width="stretch",
                   icon=":material/description:")
d2.download_button("Datos (CSV)", reporte.csv_prediccion(perfil, probs, clase, art.columnas),
                   file_name=f"prisma_prediccion_{clase}.csv", mime="text/csv", width="stretch",
                   icon=":material/table_view:")
d3.page_link("vistas/comparar.py", label="Comparar con otro perfil", icon=":material/compare_arrows:")

st.write("")
ui.aviso(ui.AVISO_SINTETICO, alerta=True)
