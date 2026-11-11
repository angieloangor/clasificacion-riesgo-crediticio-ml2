import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos, graficos
from prisma_app.esquema import etiqueta, formato_valor
from prisma_app.estado import evaluar

df = datos.cargar_dataset()
art = datos.cargar_artefactos()
m = datos.metricas_prueba()
ev = datos.evaluacion_final()
base, idx_base = datos.perfil_base()
demo, _ = evaluar(base, "base")

# ---------- Portada: demostración en vivo con el perfil base ----------
st.html(f"""
<section class="pr-hero">
  <div class="pr-hero-texto">
    <div class="pr-autores">
      <span><i>NB</i>Nicolás Barrera</span>
      <span><i>AL</i>Angie Loango</span>
    </div>
    <h1>Riesgo crediticio con Machine Learning</h1>
    <p>Clasificamos perfiles crediticios sintéticos colombianos en Good, Standard o Poor con una
    regresión logística. Cambia un perfil y mira cómo responde el modelo.</p>
  </div>
  <div class="pr-demo">
    <div class="pr-demo-titulo">Predicción en vivo · perfil típico del entrenamiento</div>
    <div class="pr-demo-clase"><i style="background:{C.COLOR_CLASE[demo["clase"]]}"></i>{demo["clase"]}</div>
    {ui.espectro_html(demo["probs"], demo["clase"], alto=54)}
  </div>
</section>""")

st.write("")
if st.button("Abrir el simulador", type="primary", icon=":material/tune:"):
    st.switch_page("vistas/simulador.py")

# ---------- Cifras verificadas ----------
st.write("")
ic = f"IC 95 %: {ui.num(ev['ic95_f1_bootstrap'][0])} – {ui.num(ev['ic95_f1_bootstrap'][1])}" if ev else ""
ui.cifras([
    (f"{len(df):,}".replace(",", "."), "perfiles sintéticos", "sin faltantes ni duplicados"),
    (str(len(art.columnas)), "variables predictoras", f"{len(art.numericas)} numéricas · {len(art.categoricas)} categóricas"),
    (ui.num(m["f1_macro"]), "F1 macro en prueba", ic),
    (ui.num(m["accuracy"]), "accuracy en prueba", f"{m['n']:,} perfiles reservados".replace(",", ".")),
])
ui.fuente("Métricas recalculadas en vivo con el modelo entrenado sobre la partición de prueba del notebook.")

# ---------- Explorar los datos ----------
ui.seccion("Explora los datos", "5.000 perfiles sintéticos")
conteo = df[C.OBJETIVO].value_counts()
ui.espectro((conteo / conteo.sum()).to_dict(), alto=40,
            sufijo_leyenda={c: f"{conteo[c]:,}".replace(",", ".") for c in C.ORDEN_CLASES})
st.write("")

NUMERICAS = ["Utilizacion_Credito", "Dias_Mora_Promedio", "Antiguedad_Crediticia_Meses", "Ratio_Deuda_Ingreso",
             "Numero_Retrasos_12M", "Consultas_Credito_6M", "Ingreso_Mensual", "Deuda_Pendiente",
             "Variabilidad_Ingreso", "Limite_Tarjeta", "Saldo_Tarjeta", "Meses_Cotizados_12M"]
t1, t2, t3 = st.tabs(["Distribución por clase", "Proporción por tramos", "Variables categóricas"])
with t1:
    var = st.selectbox("Variable", NUMERICAS, format_func=etiqueta, key="ini_var")
    st.plotly_chart(graficos.caja_por_clase(df, var), config=graficos.CONFIG, width="stretch")
    st.caption("La caja va del percentil 25 al 75; la línea sólida es la mediana y la punteada, la media.")
with t2:
    var2 = st.selectbox("Variable", [v for v in NUMERICAS if df[v].nunique() > 8], format_func=etiqueta, key="ini_var2")
    st.plotly_chart(graficos.promedio_por_grupo(df, var2), config=graficos.CONFIG, width="stretch")
    st.caption(f"A medida que aumenta {etiqueta(var2).lower()}, ¿qué proporción de perfiles es Good, Standard o Poor?")
with t3:
    var3 = st.selectbox("Variable", art.categoricas, format_func=etiqueta, key="ini_var3")
    st.plotly_chart(graficos.composicion_categorica(df, var3), config=graficos.CONFIG, width="stretch")
    st.caption("Proporción de cada clase dentro de cada categoría, ordenada por la proporción de Poor.")

# ---------- Cómo funciona ----------
ui.seccion("Cómo responde el modelo")
st.html(f"""<div class="pr-flujo">
  <div class="pr-nodo"><small>1</small><b>Perfil</b><p>23 variables validadas.</p></div>
  <div class="pr-flecha" aria-hidden="true">→</div>
  <div class="pr-nodo"><small>2</small><b>Preprocesamiento</b><p>Escalado y codificación del Pipeline.</p></div>
  <div class="pr-flecha" aria-hidden="true">→</div>
  <div class="pr-nodo"><small>3</small><b>Regresión logística</b><p>Una puntuación por clase (C = 0,001).</p></div>
  <div class="pr-flecha" aria-hidden="true">→</div>
  <div class="pr-nodo pr-nodo-final"><small>4</small><b>Tres probabilidades</b>
    {ui.espectro_html(demo["probs"], demo["clase"], alto=30).split('<div class="pr-espectro-leyenda">')[0]}</div>
</div>""")
