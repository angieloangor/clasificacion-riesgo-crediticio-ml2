import numpy as np
import streamlit as st

from prisma_app import config as C
from prisma_app import componentes as ui
from prisma_app import datos, estado
from prisma_app.esquema import GRUPOS, GRUPOS_CORTOS, VARIABLES, etiqueta, formato_valor
from prisma_app.validacion import ratio_derivado, utilizacion_derivada, validar_perfil

art = datos.cargar_artefactos()
rangos = datos.rangos()
tipos = datos.tipos_columnas()
df = datos.cargar_dataset()
perfil = st.session_state.perfil
N = len(GRUPOS)

# Derivadas con la fórmula exacta del notebook (antes de dibujar los campos).
if st.session_state.derivar:
    perfil["Utilizacion_Credito"] = utilizacion_derivada(float(perfil["Saldo_Tarjeta"]), float(perfil["Limite_Tarjeta"]))
    perfil["Ratio_Deuda_Ingreso"] = ratio_derivado(float(perfil["Deuda_Pendiente"]), float(perfil["Ingreso_Mensual"]))


def _sync(nombre: str, key: str) -> None:
    v = st.session_state[key]
    t = VARIABLES[nombre].tipo
    if t == "binaria":
        v = int(bool(v))
    elif tipos[nombre].startswith("int"):
        v = int(v)
    elif t != "categorica":
        v = float(v)
    st.session_state.perfil[nombre] = v


def campo(nombre: str) -> None:
    v = VARIABLES[nombre]
    lo, hi = rangos.get(nombre, (None, None))
    etiqueta_ui = f"{v.etiqueta} ({v.unidad})" if v.unidad and v.tipo not in ("binaria",) else v.etiqueta
    ayuda = v.ayuda + (f" Rango observado en el dataset: {lo:,.6g} – {hi:,.6g}." if lo is not None else "")
    key = f"in_{nombre}_v{st.session_state.version}"
    val = perfil[nombre]
    if v.derivada and st.session_state.derivar:
        st.number_input(etiqueta_ui, value=float(val), format="%.3f", disabled=True,
                        help=ayuda + " Calculada automáticamente con la fórmula del notebook.")
        return
    if v.tipo == "categorica":
        ops = art.categorias[nombre]
        st.selectbox(etiqueta_ui, ops, index=ops.index(str(val)), key=key, help=ayuda,
                     on_change=_sync, args=(nombre, key))
    elif v.tipo == "binaria":
        st.toggle(etiqueta_ui, value=bool(int(val)), key=key, help=ayuda, on_change=_sync, args=(nombre, key))
    elif tipos[nombre].startswith("int"):
        st.number_input(etiqueta_ui, min_value=int(lo), max_value=int(hi), value=int(val), step=1,
                        key=key, help=ayuda, on_change=_sync, args=(nombre, key))
    else:
        fmt = "%.0f" if v.tipo == "dinero" else ("%.1f" if v.tipo == "decimal" else "%.3f")
        st.number_input(etiqueta_ui, min_value=float(lo), max_value=float(hi), value=float(val),
                        step=float(v.paso or 0.01), format=fmt, key=key, help=ayuda,
                        on_change=_sync, args=(nombre, key))
        if v.tipo == "dinero":
            st.caption(formato_valor(nombre, val))


def ir(paso: int) -> None:
    st.session_state.paso = paso


def corregir() -> None:
    p = st.session_state.perfil
    if int(p["Tiene_Tarjeta_Credito"]) == 0:
        p.update(Limite_Tarjeta=0.0, Saldo_Tarjeta=0.0, Monto_Pagado_Tarjeta=0.0, Comportamiento_Pago_Tarjeta="No aplica")
    if int(p["Numero_Retrasos_12M"]) == 0:
        p["Dias_Mora_Promedio"] = 0.0
    if p["Tipo_Cotizante"] == "Sin cotizacion":
        p["Meses_Cotizados_12M"] = 0
    if int(p["Meses_Cotizados_12M"]) == 0:
        p["IBC_Aproximado"] = 0.0
    if p["Saldo_Tarjeta"] > p["Limite_Tarjeta"]:
        p["Saldo_Tarjeta"] = float(p["Limite_Tarjeta"])
    if p["Monto_Pagado_Tarjeta"] > p["Saldo_Tarjeta"]:
        p["Monto_Pagado_Tarjeta"] = float(p["Saldo_Tarjeta"])
    estado.limpiar_widgets()


def cargar_registro(idx: int) -> None:
    fila = df.loc[idx]
    conjunto = "entrenamiento" if idx in datos.indices_entrenamiento() else "prueba"
    estado.fijar_perfil({c: fila[c] for c in art.columnas},
                        f"Registro #{idx} del dataset (conjunto de {conjunto}; etiqueta sintética: {fila[C.OBJETIVO]})")
    st.session_state.etiqueta_real = (idx, str(fila[C.OBJETIVO]), conjunto)


# ---------------- Encabezado ----------------
ui.encabezado("Simulador", "Ajusta el perfil sección por sección. La vista previa cambia con cada valor.",
              ficha=ui.FICHA_MODELO)

izq, der = st.columns([2.15, 1], gap="large")

# ---------------- Formulario por pasos ----------------
with izq:
    paso = st.radio("Sección", list(range(N)), format_func=lambda i: GRUPOS_CORTOS[i], horizontal=True,
                    key="paso", label_visibility="collapsed")
    st.session_state.visitados.add(paso)
    ui.pasos(paso, st.session_state.visitados, N)  # progreso: secciones revisadas
    _, titulo, cols = GRUPOS[paso]
    with st.container(border=True, key=f"tarjeta_seccion_{paso}"):
        if paso == 2:
            st.toggle("Calcular utilización y deuda/ingreso automáticamente", value=st.session_state.derivar,
                      key="w_derivar", on_change=lambda: st.session_state.update(derivar=st.session_state.w_derivar),
                      help="Usa las mismas fórmulas del notebook: saldo ÷ cupo y deuda ÷ (ingreso × 12). "
                           "Desactívalo para escribir los valores manualmente.")
        ncol = 3 if len(cols) >= 6 else 2
        for inicio in range(0, len(cols), ncol):  # una fila de columnas por grupo para alinear los campos
            fila = st.columns(ncol)
            for j, nombre in enumerate(cols[inicio:inicio + ncol]):
                with fila[j]:
                    campo(nombre)
    a, b, _ = st.columns([1, 1, 2.2])
    a.button("Anterior", on_click=ir, args=(max(paso - 1, 0),), disabled=paso == 0, width="stretch",
             icon=":material/arrow_back:")
    b.button("Siguiente", on_click=ir, args=(min(paso + 1, N - 1),), disabled=paso == N - 1, width="stretch",
             icon=":material/arrow_forward:")

# ---------------- Panel lateral: vista previa y acciones ----------------
with der:
    errores, advertencias = validar_perfil(perfil, art.columnas, rangos, art.categorias, tipos)
    with st.container(border=True, key="tarjeta_vista_previa"):
        st.markdown("**Vista previa**")
        if errores:
            st.error("Corrige los campos marcados para ver la vista previa.")
        else:
            res, _ = estado.evaluar(perfil, st.session_state.origen)
            ui.espectro(res["probs"], res["clase"], alto=52, leyenda_compacta=True)
        if st.button("Calcular clasificación", type="primary", width="stretch", icon=":material/insights:",
                     disabled=bool(errores)):
            res, errs = estado.evaluar(perfil, st.session_state.origen)
            if res:
                et = st.session_state.get("etiqueta_real")
                res["etiqueta_real"] = et if et and st.session_state.origen.startswith(f"Registro #{et[0]} ") else None
                st.session_state.resultado = res
                st.switch_page("vistas/resultado.py")

        for e in errores:
            st.error(e, icon=":material/error:")
        if advertencias:
            with st.expander(f"{len(advertencias)} advertencia{'s' if len(advertencias) > 1 else ''} de coherencia",
                             icon=":material/warning:"):
                for a_ in advertencias:
                    st.caption(f"• {a_}")
                st.caption("El generador del notebook nunca produce estas combinaciones.")
                st.button("Corregir automáticamente", on_click=corregir, width="stretch",
                          help="Campos de tarjeta en 0 si no hay tarjeta, mora 0 sin retrasos, IBC 0 sin "
                               "cotización y saldo/pago dentro de sus límites.")
        elif not errores:
            st.html('<p class="pr-estado-ok">● Perfil coherente con los datos de entrenamiento</p>')

    st.caption(st.session_state.origen)
    with st.popover("Cargar perfil del dataset", icon=":material/dataset:", width="stretch"):
        st.markdown("**Perfil del dataset**")
        idx = st.number_input("Registro (0 – 4999)", 0, len(df) - 1, 0, 1)
        st.button("Cargar registro", on_click=cargar_registro, args=(int(idx),), width="stretch")
        st.divider()
        clase = st.selectbox("O uno al azar con etiqueta", C.ORDEN_CLASES)
        if st.button("Cargar al azar", width="stretch"):
            rng = np.random.default_rng()
            cargar_registro(int(rng.choice(df.index[df[C.OBJETIVO] == clase])))
            st.rerun()
    st.button("Restablecer perfil base", on_click=estado.restablecer, width="stretch", icon=":material/restart_alt:")
