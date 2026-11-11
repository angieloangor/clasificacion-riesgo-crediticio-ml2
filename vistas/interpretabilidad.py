import numpy as np
import pandas as pd
import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos, graficos, prediccion
from prisma_app.esquema import etiqueta, formato_valor

art = datos.cargar_artefactos()
m = datos.metricas_prueba()

ui.encabezado("Interpretabilidad del modelo",
              "Cómo usa la regresión logística las 23 variables. Las explicaciones <b>globales</b> describen el "
              "modelo completo sobre el conjunto de prueba; la explicación <b>individual</b> descompone la "
              "predicción de un solo perfil y está en la página de resultado.")

t_imp, t_coef, t_pdp, t_cm, t_ind = st.tabs(["Importancia por permutación", "Coeficientes", "Dependencia parcial",
                                             "Matriz de confusión", "Explicación individual"])

# ---------------- Importancia por permutación ----------------
with t_imp:
    ui.pregunta("¿Cuánto empeora el F1 macro de prueba si se desordena aleatoriamente una variable?")
    opciones = {"5rep": "5 repeticiones · archivo del proyecto (citado en el informe)",
                "10rep": "10 repeticiones · configuración del notebook (reproducida)"}
    disponibles = [k for k in opciones if datos.importancias(k) is not None]
    if not disponibles:
        st.warning("No se encontraron archivos de importancia por permutación.")
    else:
        ver = st.radio("Versión", disponibles, format_func=opciones.get, horizontal=True, label_visibility="collapsed")
        imp = datos.importancias(ver)
        st.plotly_chart(graficos.importancia(imp), config=graficos.CONFIG, width="stretch")
        pos = imp[imp["importance"] > 0].sort_values("importance", ascending=False)
        top = ", ".join(f"{etiqueta(v)} ({x:+.4f})" for v, x in zip(pos.feature.head(3), pos.importance.head(3)))
        ui.aviso(f"Solo {len(pos)} de 23 variables reducen el F1 al permutarse; las tres principales son {top}. "
                 f"Incluso la mayor caída es pequeña frente al F1 macro de {ui.num(m['f1_macro'])}, y las "
                 f"{23 - len(pos)} variables con valor ≤ 0 no muestran aporte medible: su permutación no empeora "
                 "(o mejora levemente, dentro del ruido) el desempeño. Con predictores correlacionados la "
                 "importancia se reparte entre ellos, así que no debe leerse como efecto causal.")
        archivo = "resultados/interpretabilidad_importancias.csv" if ver == "5rep" else "resultados/reproduccion/importancia_permutacion_10rep.csv"
        ui.fuente(f"Fuente: <code>{archivo}</code> · scoring = F1 macro sobre las 1.000 filas de prueba.")

# ---------------- Coeficientes ----------------
with t_coef:
    coef = prediccion.coeficientes(art)
    ui.pregunta("¿En qué dirección y con qué fuerza mueve cada variable la puntuación de cada clase?")
    cl = st.radio("Clase", C.ORDEN_CLASES, horizontal=True, key="coef_clase", index=2)
    n = st.slider("Términos mostrados", 8, 36, 16)
    st.plotly_chart(graficos.coeficientes(coef, cl, n), config=graficos.CONFIG, width="stretch")
    sub = coef[coef.clase == cl].sort_values("coeficiente")
    sube = ", ".join(etiqueta(v) + (f" = {lv}" if lv else "") for v, lv in zip(sub.variable.tail(3)[::-1], sub.nivel.tail(3)[::-1]))
    baja = ", ".join(etiqueta(v) + (f" = {lv}" if lv else "") for v, lv in zip(sub.variable.head(3), sub.nivel.head(3)))
    ui.aviso(f"Para <b>{cl}</b>, los términos que más elevan la puntuación son {sube}; los que más la reducen, {baja}. "
             "En las variables numéricas el coeficiente es el cambio en la puntuación lineal por <b>una desviación "
             "estándar</b> (el Pipeline estandariza antes del modelo). En las categóricas, cada nivel tiene su propio "
             "coeficiente (one-hot sin categoría de referencia). La regresión usa C = 0,001, una regularización "
             "fuerte que encoge los coeficientes hacia cero: su tamaño es comparable entre variables, no su escala absoluta.")
    with st.expander("Tabla completa de coeficientes"):
        tabla = coef.pivot_table(index=["variable", "nivel"], columns="clase", values="coeficiente")[C.ORDEN_CLASES]
        sd = coef.drop_duplicates(["variable", "nivel"]).set_index(["variable", "nivel"])["desv_estandar"]
        tabla["1 desv. estándar (unidades originales)"] = sd
        st.dataframe(tabla.style.format("{:+.4f}", subset=C.ORDEN_CLASES).format("{:,.3f}", subset=tabla.columns[-1:], na_rep="—"),
                     width="stretch")
        st.caption("Los coeficientes de las tres clases suman cero en cada término; softmax solo depende de las "
                   "diferencias entre clases.")

# ---------------- Dependencia parcial ----------------
with t_pdp:
    ui.pregunta("Si se fija una variable en distintos valores para todos los perfiles, ¿cómo cambia la probabilidad "
                "media que predice el modelo?")
    _, X_te, _, _ = datos.particion()
    muestra = X_te.sample(min(250, len(X_te)), random_state=C.SEMILLA)  # misma muestra que el notebook
    opciones_pdp = [v for v in art.numericas if v != "Tiene_Tarjeta_Credito"]
    var = st.selectbox("Variable", opciones_pdp, index=opciones_pdp.index("Utilizacion_Credito"), format_func=etiqueta)

    @st.cache_data(show_spinner="Calculando dependencia parcial con el modelo…")
    def _pdp(variable: str):
        return prediccion.dependencia_parcial(datos.cargar_artefactos(), muestra, variable)

    x, curvas = _pdp(var)
    st.plotly_chart(graficos.pdp(x, curvas, var), config=graficos.CONFIG, width="stretch")
    cambio = " · ".join(f"{c}: {ui.pct(curvas[c][0])} → {ui.pct(curvas[c][-1])}" for c in C.ORDEN_CLASES)
    st.caption(f"De {formato_valor(var, x[0])} a {formato_valor(var, x[-1])} (percentiles 5–95 de la muestra): {cambio}.")
    guardada = datos.pdp_guardada()
    if guardada and var in guardada:
        ok = np.allclose(guardada[var]["y"], curvas["Poor"]) and np.allclose(guardada[var]["x"], x)
        st.html(f'<p class="pr-fuente">Comparado con <code>resultados/dependencia_parcial_datos.json</code> (clase Poor): '
                f'{ui.etiqueta_estado(ok, "coincide", "no coincide")}</p>')
    ui.fuente("Calculado en vivo con el Pipeline: 20 valores entre los percentiles 5 y 95, fijados en las mismas 250 "
              "filas de prueba del notebook (semilla 42), promediando predict_proba. Asociación del modelo con datos sintéticos, no efecto causal: al "
              "fijar una variable se crean combinaciones que pueden no existir en los datos.")

# ---------------- Matriz de confusión ----------------
with t_cm:
    ui.pregunta("¿Dónde acierta y dónde se confunde el modelo en los 1.000 perfiles de prueba?")
    norm = st.toggle("Colorear por porcentaje de la fila (recall)", value=True)
    a, b = st.columns([1.3, 1], gap="large")
    with a:
        st.plotly_chart(graficos.matriz_confusion(m["matriz"], norm), config=graficos.CONFIG, width="stretch")
    with b:
        cm = m["matriz"]
        st.dataframe(pd.DataFrame({"Precisión": m["precision_por_clase"], "Recall": m["recall_por_clase"],
                                   "F1": m["f1_por_clase"]}).loc[C.ORDEN_CLASES].style.format("{:.3f}"), width="stretch")
        ui.aviso(f"Standard es la clase más difícil (recall {ui.pct(m['recall_por_clase']['Standard'])}), porque por "
                 f"construcción ocupa la zona intermedia del riesgo latente. Los errores extremos son menos frecuentes: "
                 f"{cm.loc['Poor', 'Good']} perfiles Poor se predijeron Good y {cm.loc['Good', 'Poor']} Good se "
                 "predijeron Poor; el primero sería el error más costoso en un uso real.")
    ui.fuente("Recalculada en vivo y verificada contra <code>resultados/matriz_confusion_final.csv</code>.")

# ---------------- Individual ----------------
with t_ind:
    st.markdown("La explicación individual se calcula para el perfil que evalúas, con el modelo entrenado y el "
                "preprocesamiento real:")
    st.markdown("1. El perfil pasa por el `ColumnTransformer` del Pipeline (estandarización y one-hot).\n"
                "2. Para cada clase *k*, la puntuación lineal es `b_k + w_k · t(x)`.\n"
                "3. La diferencia frente al perfil promedio del entrenamiento se reparte exactamente entre variables: "
                "`Σ_j w_kj · (t_j(x) − t̄_j)`; las columnas one-hot se suman a su variable original.\n"
                "4. Softmax convierte las tres puntuaciones en las probabilidades de `predict_proba`.")
    st.caption("No se usan aproximaciones ni explicaciones genéricas: la suma de contribuciones reproduce el "
               "logit del modelo (se comprueba en las pruebas automáticas).")
    st.page_link("vistas/resultado.py", label="Ver la explicación del último resultado", icon=":material/insights:")
