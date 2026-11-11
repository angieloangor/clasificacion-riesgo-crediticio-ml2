import json

import pandas as pd
import streamlit as st

from prisma_app import componentes as ui
from prisma_app import datos, graficos

m = datos.metricas_prueba()
cv = datos.cv_inicial()
aj = datos.ajuste_hiperparametros()
an = datos.validacion_anidada()
ev = datos.evaluacion_final()
FINAL = "Logistic Regression"

ui.encabezado("Comparación de modelos",
              "Diez clasificadores, de una línea base trivial a ensambles de boosting, evaluados con F1 macro. "
              "La selección siguió tres etapas sobre los 4.000 perfiles de entrenamiento; la prueba se usó una sola vez.")

cifras = [("C = 0,001", "regresión logística (modelo final)", "regularización L2 · solver lbfgs"),
          (ui.num(m["f1_macro"]), "F1 macro en prueba",
           f"IC 95 %: {ui.num(ev['ic95_f1_bootstrap'][0])} – {ui.num(ev['ic95_f1_bootstrap'][1])}" if ev else "")]
if an is not None:
    lr = an.set_index("Modelo").loc[FINAL]
    cifras.append((ui.num(lr["F1_macro_nested"]), "F1 macro anidado", f"± {ui.num(lr['Desviacion'])} (3 folds externos)"))
if ev:
    cifras.append((ui.num(ev["oraculo_f1_macro"]), "techo teórico (oráculo)", "conoce las probabilidades reales"))
ui.cifras(cifras)

# ---------------- Etapa 1 ----------------
ui.seccion("Etapa 1 · Comparación inicial", "CV estratificada de 3 folds, hiperparámetros por defecto")
if cv is None:
    st.warning("No se encontró `resultados/comparacion_modelos_cv.csv`.")
else:
    ui.pregunta("Con configuraciones por defecto, ¿qué tan lejos están los modelos complejos de uno lineal?")
    base = float(cv.loc[cv.Modelo == "Baseline", "F1_macro_CV"].iloc[0])
    st.plotly_chart(graficos.comparacion_modelos(cv, "F1_macro_CV", "Desviacion", FINAL,
                                                 "F1 macro (media ± desv. de 3 folds)", referencia=base),
                    config=graficos.CONFIG, width="stretch")
    ens = cv[cv.Modelo.isin(["XGBoost", "AdaBoost", "Random Forest", "Gradient Boosting", "LightGBM"])]
    mejor_ens = ens.sort_values("F1_macro_CV").iloc[-1]
    f_lr = float(cv.loc[cv.Modelo == FINAL, "F1_macro_CV"].iloc[0])
    ui.aviso(f"<b>Simple frente a complejo.</b> El mejor ensamble ({mejor_ens.Modelo}, {ui.num(mejor_ens.F1_macro_CV, 4)}) "
             f"queda {ui.num(f_lr - mejor_ens.F1_macro_CV, 4)} por debajo de la regresión logística ({ui.num(f_lr, 4)}), "
             "una diferencia menor que la desviación entre folds. Tiene sentido: la etiqueta se generó con una "
             "combinación casi lineal de señales normalizadas más ruido, así que los modelos no lineales tienen poca "
             f"estructura adicional que capturar. Todos superan con holgura a la línea base ({ui.num(base)}).")
    ui.fuente("Fuente: <code>resultados/comparacion_modelos_cv.csv</code>")

# ---------------- Etapa 2 ----------------
ui.seccion("Etapa 2 · Ajuste de hiperparámetros", "GridSearchCV, 3 folds, solo entrenamiento")
REJILLAS = {
    "Logistic Regression": {"C": [0.0001, 0.001, 0.005, 0.01]},
    "Gradient Boosting": {"n_estimators": [50, 100], "learning_rate": [0.03, 0.05], "max_depth": [2]},
    "SVM": {"C": [0.1, 0.5], "gamma": ["scale", "auto"]},
    "XGBoost": {"n_estimators": [50, 100], "max_depth": [2], "learning_rate": [0.01, 0.03], "subsample": [0.8], "colsample_bytree": [0.8]},
    "Random Forest": {"n_estimators": [100], "max_depth": [4, 8], "min_samples_leaf": [1, 3], "max_features": ["sqrt"]},
    "AdaBoost": {"n_estimators": [50, 100], "learning_rate": [0.1, 0.3]},
}
if aj is None:
    st.warning("No se encontraron resultados del ajuste de hiperparámetros en el proyecto.")
else:
    st.plotly_chart(graficos.comparacion_modelos(aj, "Mejor_F1_macro_CV", None, FINAL, "Mejor F1 macro CV del GridSearch"),
                    config=graficos.CONFIG, width="stretch")
    tabla = aj.copy()
    tabla["Rejilla evaluada"] = tabla.Modelo.map(lambda k: json.dumps(REJILLAS.get(k, {}), ensure_ascii=False))
    tabla["Mejores_parametros"] = tabla["Mejores_parametros"].str.replace('"', "")
    tabla["Rejilla evaluada"] = tabla["Rejilla evaluada"].str.replace('"', "")
    st.dataframe(tabla, hide_index=True, width="stretch",
                 column_config={"Mejor_F1_macro_CV": st.column_config.NumberColumn("F1 macro CV", format="%.4f"),
                                "Mejores_parametros": "Mejores parámetros"})
    st.caption("Decision Tree, LightGBM y Naive Bayes no se ajustaron por su menor desempeño inicial. Estos scores "
               "son optimistas porque se obtienen dentro del mismo proceso que elige los hiperparámetros.")
    ui.fuente("Fuente: <code>resultados/reproduccion/ajuste_hiperparametros.csv</code> — reproducido al re-ejecutar el "
              "notebook; dataset y modelo regenerados idénticos byte a byte a los entregados (ver REPRODUCCION.md).")

# ---------------- Etapa 3 ----------------
ui.seccion("Etapa 3 · Validación cruzada anidada", "3 folds externos × 2 internos, los dos finalistas")
if an is None:
    st.warning("No se encontraron resultados de validación anidada en el proyecto. No se muestran cifras para esta etapa.")
else:
    a, b = st.columns([1.2, 1], gap="large")
    with a:
        st.plotly_chart(graficos.comparacion_modelos(an, "F1_macro_nested", "Desviacion", FINAL, "F1 macro anidado (± desv.)"),
                        config=graficos.CONFIG, width="stretch")
    with b:
        st.dataframe(an, hide_index=True, width="stretch", column_config={
            "F1_macro_nested": st.column_config.NumberColumn("F1 anidado", format="%.4f"),
            "Desviacion": st.column_config.NumberColumn("Desviación", format="%.4f")})
        mejor = an.sort_values("F1_macro_nested").iloc[-1]
        dif = float(mejor.F1_macro_nested - an.set_index("Modelo").loc[FINAL, "F1_macro_nested"])
        st.markdown(f"**Regla del notebook:** se elige la regresión logística si su F1 anidado queda a ≤ 0,01 del mejor "
                    f"finalista. Mejor finalista: {mejor.Modelo}; diferencia: {dif:+.4f}.")
    ui.fuente("Fuente: <code>resultados/reproduccion/validacion_anidada.csv</code> (reproducido, ver REPRODUCCION.md).")

# ---------------- Decisión ----------------
ui.seccion("Por qué se eligió la regresión logística")
razones = ["Mejor F1 macro en la comparación inicial y en el ajuste de hiperparámetros, aunque con diferencias pequeñas."]
if an is not None:
    razones.append("Mejor F1 en la validación anidada, que estima el desempeño sin el sesgo de elegir hiperparámetros "
                   "y evaluar con los mismos datos.")
razones += ["Menor complejidad: una puntuación lineal por clase, sin interacciones que interpretar.",
            "Coeficientes directamente interpretables y explicaciones individuales exactas.",
            "Regularización fuerte (C = 0,001) que reduce la varianza con 4.000 perfiles de entrenamiento."]
for r in razones:
    st.markdown(f"- {r}")

ui.seccion("Evaluación final en prueba", "1.000 perfiles nunca usados en la selección")
met = pd.DataFrame({"Métrica": ["Accuracy", "Precisión macro", "Recall macro", "F1 macro"],
                    "Valor": [m["accuracy"], m["precision_macro"], m["recall_macro"], m["f1_macro"]]})
a, b = st.columns([1, 1.4], gap="large")
a.dataframe(met, hide_index=True, width="stretch", column_config={"Valor": st.column_config.NumberColumn(format="%.4f")})
with b:
    texto = (f"El F1 macro de prueba ({ui.num(m['f1_macro'])}) es coherente con la validación cruzada. ")
    if ev:
        texto += (f"Como las etiquetas se sortearon a partir de probabilidades, ni siquiera un clasificador que conoce "
                  f"esas probabilidades acierta siempre: su F1 macro es {ui.num(ev['oraculo_f1_macro'])}. Ese es el techo "
                  "teórico de esta simulación; el modelo recupera alrededor de "
                  f"{ui.pct(m['f1_macro'] / ev['oraculo_f1_macro'], 0)} de él.")
    ui.aviso(texto)
if ev:
    with st.expander("Otras pruebas del notebook"):
        st.markdown(f"- **SVM con log1p en variables monetarias:** F1 macro CV {ui.num(ev['svm_log1p_f1_cv'], 4)} "
                    f"(± {ui.num(ev['svm_log1p_desv'], 4)}). Prueba de sensibilidad; no cambió la selección.\n"
                    f"- **Oráculo:** accuracy {ui.num(ev['oraculo_accuracy'])}, F1 macro {ui.num(ev['oraculo_f1_macro'], 4)}.\n"
                    f"- **IC bootstrap 95 % del F1 macro:** 1.000 remuestreos del conjunto de prueba.")
        ui.fuente("Fuente: <code>resultados/reproduccion/evaluacion_final.json</code>")
