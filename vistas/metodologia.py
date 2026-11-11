import pandas as pd
import streamlit as st

from prisma_app import componentes as ui
from prisma_app import datos, graficos
from prisma_app.esquema import GRUPOS, PESOS_GENERACION, VARIABLES

df = datos.cargar_dataset()
art = datos.cargar_artefactos()

ui.encabezado("Metodología y documentación",
              "Resumen académico del proyecto, consistente con el notebook "
              "<code>ProyectoML2_EntregaFinal_FICO_Colombia.ipynb</code>. Nicolás Barrera y Angie Loango · Machine Learning II.")

tabs = st.tabs(["Objetivo y datos", "Generación de etiquetas", "Variables", "Preprocesamiento y entrenamiento",
                "Limitaciones", "Verificaciones"])

with tabs[0]:
    ui.seccion("Objetivo")
    st.markdown("Comparar clasificadores de distinta complejidad para recuperar una etiqueta crediticia multiclase "
                "(Good, Standard, Poor) a partir de señales financieras, laborales y de comportamiento de pago, con un "
                "procedimiento reproducible. La referencia metodológica es Koshti, Molia y Varia (2025): se retoma su "
                "comparación de algoritmos, no su población ni sus etiquetas. El ejercicio es experimental y no estima "
                "incumplimientos reales.")
    ui.seccion("Construcción sintética del dataset")
    st.markdown(f"- **{len(df):,} perfiles** generados con semilla 42 y **{df.shape[1]} columnas**: 23 predictores, "
                "`Antiguedad_Laboral_Años` (derivada de los meses y excluida del modelo por redundancia) y la etiqueta "
                "`Credit_Score`.".replace(",", ".") + "\n"
                "- Cuatro bloques encadenados, cada uno condicionado por los anteriores: perfil socioeconómico (edad con "
                "normal truncada 18–75, ocupación según edad, formalidad, antigüedad, ingreso lognormal, variabilidad "
                "beta); cotización (tipo de cotizante, meses cotizados, IBC); historial crediticio (antigüedad, "
                "productos, préstamos, tarjeta, cupo, saldo, utilización); y comportamiento (deuda, razón "
                "deuda/ingreso, comportamiento de pago, monto pagado, retrasos, mora y consultas).\n"
                "- Contexto colombiano tomado como referencia: GEIH del DANE (ingresos y condiciones laborales), UGPP "
                "(base de cotización de independientes), Superintendencia Financiera y Banca de las Oportunidades "
                "(acceso al crédito, cartera y mora). Las medias, desviaciones, probabilidades y límites concretos son "
                "**supuestos del equipo**, no estimaciones oficiales.\n"
                f"- Sin valores faltantes ({int(df.isna().sum().sum())}) ni filas duplicadas ({int(df.duplicated().sum())}).")

with tabs[1]:
    ui.seccion("Mecanismo de generación de Credit_Score")
    st.markdown("La etiqueta no es un dato observado. Se construye en cuatro pasos (celdas del Bloque 5 del notebook):")
    st.markdown("1. **Normalización** de nueve señales a [0, 1]: utilización (recorte 0–1), deuda/ingreso (0–1,5 ÷ 1,5), "
                "retrasos (0–6 ÷ 6), mora (0–60 ÷ 60), consultas (0–6 ÷ 6), variabilidad (0–1), meses sin cotizar "
                "(1 − meses/12), comportamiento de pago en escala ordinal supuesta (Pago total 0; superior al mínimo "
                "0,25; mínimo 0,65; irregular 1,0; No aplica 0,5 neutral) y antigüedad crediticia (0–240 ÷ 240) como "
                "señal protectora.\n"
                "2. **Riesgo latente**: suma ponderada de las señales más ruido normal (σ = 0,12), con la antigüedad "
                "restando.\n"
                "3. **Estandarización y softmax** con logits fijados por diseño:")
    st.latex(r"z=\frac{r-\bar r}{s_r},\quad \ell_{Good}=-1.25z-0.15,\quad \ell_{Std}=0.55-0.25|z|,\quad \ell_{Poor}=1.25z-0.25")
    st.markdown("4. **Muestreo**: la clase de cada perfil se sortea con esas tres probabilidades (generador "
                "independiente, semilla 142). Por eso incluso un clasificador perfecto se equivoca a veces.")
    ui.seccion("Justificación de los factores ponderados", "única sección donde se usa FICO")
    a, b = st.columns([1.25, 1], gap="large")
    with a:
        st.plotly_chart(graficos.pesos_generacion(PESOS_GENERACION), config=graficos.CONFIG, width="stretch")
    with b:
        st.markdown("Los pesos parten de los grupos generales que publica **FICO**: historial de pagos 35 %, montos "
                    "adeudados 30 %, antigüedad crediticia 15 %, crédito nuevo 10 % y mezcla crediticia 10 %.")
        st.markdown("- Se conserva la masa de los cuatro primeros grupos.\n"
                    "- La mezcla crediticia, no representada, se reasigna a dos señales laborales colombianas: "
                    "variabilidad del ingreso 6 % y meses sin cotizar 4 %.\n"
                    "- Dentro de pagos (3 señales) y deuda (2 señales) el reparto es equitativo.\n"
                    "- Los pesos absolutos suman 100 %.")
        ui.aviso("FICO publica porcentajes por grupo para su sistema general, no coeficientes colombianos por "
                 "variable. El reparto interno, el 6 %/4 % y los parámetros softmax son decisiones del equipo. La "
                 "pertinencia de capacidad de pago e ingreso se apoya conceptualmente en Gutiérrez-Rueda, Estrada y "
                 "Capera (2011), sin atribuirles pesos.", alerta=True)
    st.caption("Peso cero en la generación no significa que la variable no se use: las 23 entran al Pipeline y el "
               "modelo aprende sus coeficientes.")

with tabs[2]:
    ui.seccion("Las 23 variables predictoras")
    peso = {v: p * s for _, v, _, p, s in PESOS_GENERACION}
    filas = []
    for _, grupo, cols in GRUPOS:
        for c in cols:
            v = VARIABLES[c]
            filas.append({"Columna": c, "Variable": v.etiqueta, "Sección": grupo,
                          "Tipo en el modelo": "categórica (one-hot)" if c in art.categoricas else "numérica (estandarizada)",
                          "Unidad": v.unidad or "—", "Peso en la etiqueta": peso.get(c, 0.0), "Descripción": v.ayuda})
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", height=560,
                 column_config={"Peso en la etiqueta": st.column_config.NumberColumn(format="%+.4f")})
    ui.fuente("Pesos de la celda <code>PESOS_FICO_CO</code> del notebook. Documentación ampliada en "
              "<code>DOCUMENTACION_23_VARIABLES.md</code>.")

with tabs[3]:
    ui.seccion("Preprocesamiento")
    st.markdown("- **Partición** estratificada 80/20 con semilla 42 antes de cualquier ajuste: 4.000 entrenamiento, 1.000 prueba.\n"
                "- **Pipeline** de scikit-learn con `ColumnTransformer`: `StandardScaler` para las 19 numéricas y "
                "`OneHotEncoder(handle_unknown='ignore')` para las 4 categóricas, ajustados dentro de cada partición "
                "para evitar fuga de información.\n"
                "- Sin balanceo: las clases tienen tamaños similares (Good 1.709, Standard 1.772, Poor 1.519).\n"
                "- Cambios frente al artículo: one-hot en lugar de label encoding, preprocesamiento dentro del "
                "Pipeline, F1 macro como métrica principal y 5.000 registros sintéticos frente a ~100.000.")
    ui.seccion("Entrenamiento, evaluación y selección")
    st.markdown("1. **Comparación inicial** de 9 clasificadores del artículo más un `DummyClassifier`, con CV "
                "estratificada de 3 folds.\n"
                "2. **Ajuste de hiperparámetros** con `GridSearchCV` (3 folds) para regresión logística, Gradient "
                "Boosting, SVM, XGBoost, Random Forest y AdaBoost.\n"
                "3. **Validación cruzada anidada** (3 externos × 2 internos) de los dos mejores.\n"
                "4. **Regla de selección**: regresión logística si su F1 anidado queda a ≤ 0,01 del mejor finalista.\n"
                "5. **Evaluación única** en prueba, IC bootstrap del F1 (1.000 remuestreos) y comparación con el oráculo.\n"
                "6. **Interpretabilidad**: importancia por permutación, dependencia parcial y análisis de errores.")
    st.page_link("vistas/modelos.py", label="Ver los resultados de cada etapa", icon=":material/leaderboard:")

with tabs[4]:
    ui.seccion("Limitaciones")
    st.markdown("1. **Validez externa**: datos y etiquetas sintéticos; el F1 no predice el desempeño en entidades reales.\n"
                "2. **Ponderación**: FICO aporta pesos por grupo, no coeficientes por variable; el reparto interno, el "
                "6 %/4 % y la escala de pagos son supuestos.\n"
                "3. **Calibración**: logits y ruido elegidos para generar clases plausibles, sin contrastar con "
                "prevalencias observadas en Colombia.\n"
                "4. **Dependencias**: deuda, pagos y retrasos están correlacionados; sus importancias no son causales.\n"
                "5. **Desempeño moderado**: F1 macro ≈ 0,45, con Standard como clase más difícil.\n"
                "6. **Ética**: faltan auditoría de sesgos (la edad es predictor), calibración probabilística y "
                "monitoreo de deriva.")
    ui.seccion("Posibles mejoras")
    st.markdown("- Datos colombianos autorizados y anonimizados para estimar parámetros y validar en el tiempo.\n"
                "- Análisis de sensibilidad de los pesos y de los parámetros softmax.\n"
                "- Calibración de probabilidades y evaluación de equidad por grupos.\n"
                "- Versionado y seguimiento MLOps; Deep Learning solo si aporta frente a modelos tabulares.")
    ui.aviso("Prototipo académico: no apto para otorgar o negar créditos.", alerta=True)

with tabs[5]:
    ui.seccion("Verificaciones automáticas en vivo", "se ejecutan al abrir esta pestaña")
    for titulo, ok, detalle in datos.verificaciones():
        st.html(f'<div style="display:flex;gap:.8rem;align-items:baseline;padding:.45rem 0;border-bottom:1px solid #E2E7EE">'
                f'{ui.etiqueta_estado(ok, "Correcto", "Falla")}<div><b>{titulo}</b><br>'
                f'<span class="pr-fuente">{detalle}</span></div></div>')
    ui.seccion("Fuentes")
    st.markdown("- FICO. *What's in your credit score?* https://www.myfico.com/credit-education/whats-in-your-credit-score\n"
                "- Gutiérrez-Rueda, J., Estrada, D. y Capera-Romero, L. (2011). *Un análisis del endeudamiento de los "
                "hogares*. Banco de la República. https://doi.org/10.32468/tef.61\n"
                "- Koshti, R. M., Molia, S. J. y Varia, D. J. (2025). *Improving Credit Score Classification Using "
                "Predictive Analysis and Machine Learning Techniques*. https://www.ijsat.org/research-paper.php?id=4759\n"
                "- DANE, GEIH; UGPP; Superintendencia Financiera y Banca de las Oportunidades (fuentes de contexto del notebook).")
    st.caption("Declaración de IA: se utilizó inteligencia artificial generativa como herramienta de apoyo en el proyecto.")
