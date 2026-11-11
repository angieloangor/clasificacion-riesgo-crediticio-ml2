"""Pruebas de integridad técnica de Prisma.

Ejecutar desde la carpeta del proyecto:  python -m pytest -q
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from prisma_app import config as C  # noqa: E402
from prisma_app import datos, prediccion  # noqa: E402
from prisma_app.esquema import GRUPOS, VARIABLES  # noqa: E402
from prisma_app.validacion import (preparar_entrada, ratio_derivado, reglas_coherencia,  # noqa: E402
                                   utilizacion_derivada, validar_lote, validar_perfil)


@pytest.fixture(scope="module")
def art():
    return datos.cargar_artefactos()


@pytest.fixture(scope="module")
def df():
    return datos.cargar_dataset()


@pytest.fixture(scope="module")
def X(df, art):
    return df[art.columnas]


# ---------- Modelo y esquema ----------

def test_modelo_carga_y_es_regresion_logistica(art):
    lr = art.modelo.named_steps["modelo"]
    assert type(lr).__name__ == "LogisticRegression"
    assert lr.C == 0.001
    assert list(art.modelo.named_steps.keys()) == ["preprocesamiento", "modelo"]


def test_23_variables_coinciden_con_el_pipeline(art, df):
    assert len(art.columnas) == 23
    assert list(art.modelo.feature_names_in_) == art.columnas
    esperadas = [c for c in df.columns if c not in (C.OBJETIVO, C.COLUMNA_EXCLUIDA)]
    assert art.columnas == esperadas
    assert set(art.categoricas) | set(art.numericas) == set(art.columnas)


def test_metadatos_y_grupos_cubren_las_23_variables_una_vez(art):
    assert set(VARIABLES) == set(art.columnas)
    en_grupos = [c for _, _, cols in GRUPOS for c in cols]
    assert sorted(en_grupos) == sorted(art.columnas)
    assert len(en_grupos) == len(set(en_grupos)) == 23


def test_categorias_validas_iguales_al_entrenamiento(art, df):
    archivo = json.loads(C.RUTA_CATEGORIAS.read_text(encoding="utf-8"))
    for c, cats in art.categorias.items():
        assert sorted(cats) == sorted(archivo[c]) == sorted(df[c].unique())


def test_dtypes_de_entrada_iguales_al_dataset(art, df):
    x = preparar_entrada(df.loc[0, art.columnas].to_dict(), art.columnas, datos.tipos_columnas())
    for c in art.columnas:
        assert x[c].dtype == df[c].dtype, c


# ---------- Clases y probabilidades ----------

def test_correspondencia_indice_clase_del_codificador(art):
    assert list(art.encoder.classes_) == ["Good", "Poor", "Standard"]
    assert list(art.modelo.classes_) == [0, 1, 2]
    assert art.clases_modelo == ["Good", "Poor", "Standard"]


def test_prediccion_de_ejemplo_igual_a_la_registrada(art):
    ej = json.loads(C.RUTA_EJEMPLO.read_text(encoding="utf-8"))[0]
    x = preparar_entrada(ej, art.columnas, datos.tipos_columnas())
    r = prediccion.predecir(art, x).iloc[0]
    # PRUEBAS_APLICACION.txt: Poor, {Good 0.17896, Poor 0.49462, Standard 0.32642}
    assert r["Clase_predicha"] == "Poor"
    assert r["Prob_Good"] == pytest.approx(0.17896, abs=1e-5)
    assert r["Prob_Poor"] == pytest.approx(0.49462, abs=1e-5)
    assert r["Prob_Standard"] == pytest.approx(0.32642, abs=1e-5)


def test_probabilidades_suman_uno_y_son_las_de_predict_proba(art, X):
    p = prediccion.predecir(art, X)
    directo = art.modelo.predict_proba(X)
    for i, c in enumerate(art.clases_modelo):
        np.testing.assert_array_equal(p[f"Prob_{c}"].values, directo[:, i])
    np.testing.assert_allclose(p[[f"Prob_{c}" for c in C.ORDEN_CLASES]].sum(axis=1), 1.0, atol=1e-12)
    esperado = art.encoder.inverse_transform(art.modelo.predict(X).astype(int))
    assert (p["Clase_predicha"].values == esperado).all()


# ---------- Partición y métricas ----------

def test_particion_reproducida(art):
    X_tr, X_te, *_ = datos.particion()
    scaler = art.modelo.named_steps["preprocesamiento"].named_transformers_["numericas"]
    assert len(X_tr) == 4000 and len(X_te) == 1000
    np.testing.assert_allclose(scaler.mean_, X_tr[art.numericas].mean().values)
    ej = json.loads(C.RUTA_EJEMPLO.read_text(encoding="utf-8"))[0]
    assert X_tr.iloc[0].to_dict() == ej


def test_metricas_y_matriz_iguales_a_las_reportadas():
    m = datos.metricas_prueba()
    assert m["accuracy"] == pytest.approx(0.452, abs=1e-9)
    assert m["f1_macro"] == pytest.approx(0.4526, abs=1e-4)
    assert m["precision_macro"] == pytest.approx(0.454, abs=5e-4)
    assert m["recall_macro"] == pytest.approx(0.453, abs=5e-4)
    guardada = pd.read_csv(C.RUTA_MATRIZ, index_col=0).loc[C.ORDEN_CLASES, C.ORDEN_CLASES]
    assert (guardada.values == m["matriz"].values).all()


def test_verificaciones_en_vivo_pasan():
    assert all(ok for _, ok, _ in datos.verificaciones())


# ---------- Resultados leídos de archivos ----------

def test_archivos_de_resultados_consistentes(art):
    cv = datos.cv_inicial()
    rep = pd.read_csv(C.REPRODUCCION / "cv_inicial.csv")
    a = cv.set_index("Modelo")["F1_macro_CV"].sort_index()
    b = rep.set_index("Modelo")["F1_macro_promedio"].sort_index()
    np.testing.assert_allclose(a.values, b.values)
    assert set(datos.importancias("5rep")["feature"]) == set(art.columnas)
    assert set(datos.importancias("10rep")["feature"]) == set(art.columnas)
    an = datos.validacion_anidada()
    assert an.sort_values("F1_macro_nested").iloc[-1]["Modelo"] == "Logistic Regression"
    ev = datos.evaluacion_final()
    assert ev["f1_macro"] == pytest.approx(datos.metricas_prueba()["f1_macro"])


def test_dependencia_parcial_en_vivo_igual_a_la_guardada(art):
    _, X_te, *_ = datos.particion()
    muestra = X_te.sample(250, random_state=C.SEMILLA)
    guardada = datos.pdp_guardada()
    for var, val in guardada.items():
        x, curvas = prediccion.dependencia_parcial(art, muestra, var)
        np.testing.assert_allclose(x, val["x"])
        np.testing.assert_allclose(curvas["Poor"], val["y"])
        np.testing.assert_allclose(sum(curvas.values()), 1.0)


# ---------- Explicación individual ----------

def test_explicacion_individual_reproduce_el_logit(art, X):
    X_tr, *_ = datos.particion()
    ref = prediccion.referencia(art, X_tr)
    for i in [0, 3, 10, 999, 4321]:
        e = prediccion.explicar(art, X.iloc[[i]], ref)
        for c in art.clases_modelo:
            s = e["tabla"].query("clase == @c")["contribucion"].sum()
            assert e["z_ref"][c] + s == pytest.approx(e["z_x"][c], abs=1e-10)
        assert set(e["tabla"]["variable"]) == set(art.columnas)


def test_coeficientes_suman_cero_entre_clases(art):
    lr = art.modelo.named_steps["modelo"]
    np.testing.assert_allclose(lr.coef_.sum(axis=0), 0, atol=1e-12)
    assert len(prediccion.coeficientes(art)) == 3 * lr.coef_.shape[1]


# ---------- Validación ----------

def test_reglas_de_coherencia_se_cumplen_en_todo_el_dataset(art, df):
    for _, fila in df[art.columnas].iterrows():
        assert reglas_coherencia(fila.to_dict()) == [], fila.name


def test_formulas_derivadas_iguales_al_notebook(df):
    u = [utilizacion_derivada(s, l) for s, l in zip(df.Saldo_Tarjeta, df.Limite_Tarjeta)]
    r = [ratio_derivado(d, i) for d, i in zip(df.Deuda_Pendiente, df.Ingreso_Mensual)]
    np.testing.assert_allclose(u, df.Utilizacion_Credito)
    np.testing.assert_allclose(r, df.Ratio_Deuda_Ingreso)


def test_validacion_detecta_entradas_invalidas(art, df):
    base = df.loc[0, art.columnas].to_dict()
    args = (art.columnas, datos.rangos(), art.categorias, datos.tipos_columnas())
    assert validar_perfil(base, *args)[0] == []
    for cambio in [{"Tipo_Ocupacion": "Astronauta"}, {"Edad": 120}, {"Edad": 30.5},
                   {"Tiene_Tarjeta_Credito": 2}, {"Ingreso_Mensual": None}, {"Numero_Prestamos": "dos"}]:
        p = {**base, **cambio}
        assert validar_perfil(p, *args)[0], cambio


def test_lote_con_columnas_faltantes_y_filas_invalidas(art, df):
    args = (art.columnas, datos.rangos(), art.categorias, datos.tipos_columnas())
    errores, *_ = validar_lote(df[art.columnas[:-1]].head(3), *args)
    assert errores and "Consultas_Credito_6M" in errores[0]
    lote = df[art.columnas].head(5).copy()
    lote.loc[1, "Tipo_Ocupacion"] = "Astronauta"
    errores, informe, listo, validos = validar_lote(lote, *args)
    assert not errores and validos == [0, 2, 3, 4] and informe.loc[1, "estado"] == "error"
    np.testing.assert_array_equal(art.modelo.predict_proba(listo), art.modelo.predict_proba(df[art.columnas].loc[validos]))


# ---------- Aplicación ----------

PAGINAS = ["inicio", "simulador", "resultado", "comparar", "lotes", "interpretabilidad", "modelos", "metodologia"]


@pytest.mark.parametrize("pagina", PAGINAS)
def test_paginas_se_ejecutan_sin_errores(pagina):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=120)
    at.run()
    if pagina != "inicio":
        at.switch_page(f"vistas/{pagina}.py").run()
    assert not at.exception, [e.value for e in at.exception]
