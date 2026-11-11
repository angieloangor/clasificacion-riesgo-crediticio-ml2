import pandas as pd
import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos
from prisma_app.prediccion import predecir
from prisma_app.validacion import validar_lote

art = datos.cargar_artefactos()
MAX_FILAS = 50_000

ui.encabezado("Predicción por lotes",
              "Sube un CSV con las 23 columnas del modelo y descarga las probabilidades de cada fila. "
              "Se usa el mismo Pipeline y las mismas validaciones del simulador.", ficha=ui.FICHA_MODELO)

with st.expander("Formato requerido y plantilla", expanded=False):
    st.markdown("- Una fila por perfil y **las 23 columnas con sus nombres exactos** (el orden no importa).\n"
                "- Las columnas adicionales se conservan en la salida pero el modelo no las usa. Si el archivo trae "
                "`Credit_Score`, se informa la coincidencia con la etiqueta sintética.\n"
                "- Categorías válidas: " + "; ".join(f"`{k}`: {', '.join(v)}" for k, v in art.categorias.items()) + ".\n"
                f"- Máximo {MAX_FILAS:,} filas.".replace(",", "."))
    _, X_te, _, y_te = datos.particion()
    plantilla = X_te.head(10)[art.columnas]
    st.download_button("Descargar plantilla (10 perfiles de prueba)", plantilla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="plantilla_prisma.csv", mime="text/csv", icon=":material/download:")

c1, c2 = st.columns([3, 1])
archivo = c1.file_uploader("Archivo CSV", type=["csv"])
decimal = c2.radio("Separador decimal", [".", ","], horizontal=True,
                   help="Usa ',' si el CSV viene de Excel en español (normalmente con ';' entre columnas).")

if archivo is None:
    st.info("Sube un archivo para empezar. Puedes probar con la plantilla.", icon=":material/upload_file:")
    st.stop()

try:
    datos_csv = pd.read_csv(archivo, sep=None, engine="python", decimal=decimal, encoding="utf-8-sig")
except Exception as exc:  # noqa: BLE001 — se muestra el motivo al usuario
    st.error(f"No se pudo leer el archivo como CSV: {exc}")
    st.stop()

if datos_csv.empty:
    st.error("El archivo no tiene filas.")
    st.stop()
if len(datos_csv) > MAX_FILAS:
    st.error(f"El archivo tiene {len(datos_csv):,} filas; el máximo es {MAX_FILAS:,}.")
    st.stop()

datos_csv.columns = [str(c).strip() for c in datos_csv.columns]
datos_csv = datos_csv.reset_index(drop=True)
errores, informe, listo, validos = validar_lote(datos_csv, art.columnas, datos.rangos(), art.categorias,
                                               datos.tipos_columnas())
if errores:
    for e in errores:
        st.error(e)
    st.stop()

n_err = int((informe["estado"] == "error").sum())
n_adv = int((informe["estado"] == "advertencia").sum())
ui.cifras([(f"{len(datos_csv):,}".replace(",", "."), "filas leídas", ""),
           (f"{len(validos):,}".replace(",", "."), "filas evaluadas", "pasaron la validación"),
           (str(n_adv), "con advertencias", "fuera de las reglas del generador"),
           (str(n_err), "con errores", "no se evaluaron")])

if n_err or n_adv:
    with st.expander(f"Ver {n_err + n_adv} filas con observaciones"):
        st.dataframe(informe[informe["estado"] != "válida"], hide_index=True, width="stretch")

if listo is None:
    st.warning("Ninguna fila es válida; revisa las observaciones.")
    st.stop()

pred = predecir(art, listo)
salida = datos_csv.copy()
for col in pred.columns:
    salida.loc[pred.index, col] = pred[col]
salida["Validacion"] = informe["estado"].values
salida["Observaciones"] = informe["mensajes"].values
primeras = ["Validacion", "Clase_predicha"] + [f"Prob_{c}" for c in C.ORDEN_CLASES]
salida = salida[primeras + [c for c in salida.columns if c not in primeras]]

ui.seccion("Distribución de las clases predichas")
dist = pred["Clase_predicha"].value_counts(normalize=True).reindex(C.ORDEN_CLASES, fill_value=0).to_dict()
cnt = pred["Clase_predicha"].value_counts().reindex(C.ORDEN_CLASES, fill_value=0)
ui.espectro(dist, sufijo_leyenda={c: f"{cnt[c]} filas" for c in C.ORDEN_CLASES})
if C.OBJETIVO in datos_csv.columns:
    real = datos_csv.loc[pred.index, C.OBJETIVO].astype(str)
    acierto = (real == pred["Clase_predicha"]).mean()
    st.caption(f"El archivo incluye `{C.OBJETIVO}`: la clase predicha coincide con la etiqueta sintética en "
               f"{ui.pct(acierto)} de las {len(pred)} filas evaluadas.")

ui.seccion("Resultados")
st.dataframe(salida, hide_index=True, width="stretch", column_config={
    f"Prob_{c}": st.column_config.ProgressColumn(f"Prob {c}", format="%.4f", min_value=0.0, max_value=1.0)
    for c in C.ORDEN_CLASES})
st.download_button("Descargar resultados (CSV)", salida.to_csv(index=False).encode("utf-8-sig"),
                   file_name="prisma_predicciones.csv", mime="text/csv", type="primary", icon=":material/download:")
ui.aviso(ui.AVISO_SINTETICO, alerta=True)
