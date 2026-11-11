"""Carga en caché de artefactos, dataset y resultados del proyecto.

Nada se inventa aquí: cada función lee un archivo del proyecto o recalcula
con el Pipeline original. Si un archivo no existe, se devuelve None y la
interfaz lo informa.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split

from . import config as C


@dataclass(frozen=True)
class Artefactos:
    modelo: object
    encoder: object
    columnas: list
    categoricas: list
    numericas: list
    categorias: dict          # categoría -> lista de valores válidos (del OneHotEncoder)
    clases_modelo: list       # nombre de clase para cada columna de predict_proba
    nombre_modelo: str


@st.cache_resource(show_spinner="Cargando el modelo entrenado…")
def cargar_artefactos() -> Artefactos:
    modelo = joblib.load(C.RUTA_MODELO)
    encoder = joblib.load(C.RUTA_ENCODER)
    esquema = json.loads(C.RUTA_ESQUEMA.read_text(encoding="utf-8"))
    ohe = modelo.named_steps["preprocesamiento"].named_transformers_["categoricas"]
    cols_cat = esquema["categoricas"]
    categorias = {c: [str(x) for x in cats] for c, cats in zip(cols_cat, ohe.categories_)}
    clases = [str(c) for c in encoder.inverse_transform(modelo.classes_.astype(int))]
    return Artefactos(modelo, encoder, list(esquema["columnas"]), list(cols_cat),
                      list(esquema["numericas"]), categorias, clases, esquema.get("modelo", ""))


@st.cache_data(show_spinner=False)
def cargar_dataset() -> pd.DataFrame:
    return pd.read_csv(C.RUTA_DATASET, encoding="utf-8-sig")


@st.cache_data(show_spinner=False)
def tipos_columnas() -> dict:
    """dtype de cada predictor tal como aparece en el dataset de entrenamiento."""
    df = cargar_dataset()
    return {c: str(df[c].dtype) for c in cargar_artefactos().columnas}


@st.cache_data(show_spinner=False)
def particion():
    """Reproduce exactamente el train_test_split del notebook (80/20, estratificado, semilla 42)."""
    df = cargar_dataset()
    X = df.drop(columns=[C.OBJETIVO, C.COLUMNA_EXCLUIDA])
    y = df[C.OBJETIVO]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=C.TEST_SIZE, random_state=C.SEMILLA, stratify=y)
    return X_tr, X_te, y_tr, y_te


@st.cache_data(show_spinner=False)
def rangos() -> dict:
    """Mínimo y máximo observados en los 5.000 registros para cada predictor numérico."""
    df = cargar_dataset()
    return {c: (float(df[c].min()), float(df[c].max())) for c in cargar_artefactos().numericas}


@st.cache_data(show_spinner=False)
def perfil_base() -> tuple[dict, int]:
    """Registro real del entrenamiento más cercano a la mediana (en escala estandarizada).

    Se usa un registro existente, y no medianas sueltas, para que el perfil inicial
    sea coherente (p. ej., sin cupo de tarjeta cuando no hay tarjeta).
    """
    art = cargar_artefactos()
    X_tr, *_ = particion()
    num = art.numericas
    z = (X_tr[num] - X_tr[num].mean()) / X_tr[num].std(ddof=0)
    med = z.median()
    idx = (z - med).pow(2).sum(axis=1).idxmin()
    return X_tr.loc[idx, art.columnas].to_dict(), int(idx)


@st.cache_data(show_spinner=False)
def indices_entrenamiento() -> set:
    X_tr, *_ = particion()
    return set(int(i) for i in X_tr.index)


@st.cache_data(show_spinner="Calculando métricas sobre el conjunto de prueba…")
def metricas_prueba() -> dict:
    """Métricas recalculadas en vivo con el Pipeline original sobre las 1.000 filas de prueba."""
    art = cargar_artefactos()
    _, X_te, _, y_te = particion()
    pred = art.encoder.inverse_transform(art.modelo.predict(X_te).astype(int))
    cm = confusion_matrix(y_te, pred, labels=C.ORDEN_CLASES)
    return {
        "accuracy": accuracy_score(y_te, pred),
        "precision_macro": precision_score(y_te, pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_te, pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_te, pred, average="macro", zero_division=0),
        "f1_por_clase": dict(zip(C.ORDEN_CLASES, f1_score(y_te, pred, labels=C.ORDEN_CLASES, average=None))),
        "precision_por_clase": dict(zip(C.ORDEN_CLASES, precision_score(y_te, pred, labels=C.ORDEN_CLASES, average=None, zero_division=0))),
        "recall_por_clase": dict(zip(C.ORDEN_CLASES, recall_score(y_te, pred, labels=C.ORDEN_CLASES, average=None))),
        "matriz": pd.DataFrame(cm, index=C.ORDEN_CLASES, columns=C.ORDEN_CLASES),
        "n": len(y_te),
    }


# ---------- Archivos de resultados (None si no existen) ----------

def _csv(ruta):
    return pd.read_csv(ruta) if ruta.exists() else None


@st.cache_data(show_spinner=False)
def cv_inicial():
    return _csv(C.RUTA_CV)


@st.cache_data(show_spinner=False)
def ajuste_hiperparametros():
    return _csv(C.REPRODUCCION / "ajuste_hiperparametros.csv")


@st.cache_data(show_spinner=False)
def validacion_anidada():
    return _csv(C.REPRODUCCION / "validacion_anidada.csv")


@st.cache_data(show_spinner=False)
def evaluacion_final():
    ruta = C.REPRODUCCION / "evaluacion_final.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


@st.cache_data(show_spinner=False)
def importancias(version: str = "5rep"):
    if version == "10rep":
        df = _csv(C.REPRODUCCION / "importancia_permutacion_10rep.csv")
        if df is not None:
            df = df.rename(columns={"Variable": "feature", "Importancia": "importance", "Desviacion": "sd"})
        return df
    return _csv(C.RUTA_IMPORTANCIAS)


@st.cache_data(show_spinner=False)
def matriz_guardada():
    return pd.read_csv(C.RUTA_MATRIZ, index_col=0) if C.RUTA_MATRIZ.exists() else None


@st.cache_data(show_spinner=False)
def pdp_guardada():
    return json.loads(C.RUTA_PDP.read_text(encoding="utf-8")) if C.RUTA_PDP.exists() else None


@st.cache_data(show_spinner="Verificando integridad del modelo…")
def verificaciones() -> list[tuple[str, bool, str]]:
    """Comprobaciones automáticas que se muestran en la sección de metodología."""
    art = cargar_artefactos()
    X_tr, X_te, *_ = particion()
    pre = art.modelo.named_steps["preprocesamiento"]
    scaler = pre.named_transformers_["numericas"]
    cat_json = json.loads(C.RUTA_CATEGORIAS.read_text(encoding="utf-8")) if C.RUTA_CATEGORIAS.exists() else {}
    proba = art.modelo.predict_proba(X_te)
    pred_idx = art.modelo.predict(X_te)
    res = []
    res.append(("El esquema tiene 23 predictores y coincide con el Pipeline",
                len(art.columnas) == 23 and list(art.modelo.feature_names_in_) == art.columnas,
                f"{C.RUTA_ESQUEMA.relative_to(C.RAIZ).as_posix()} vs. modelo.feature_names_in_"))
    res.append(("Categorías válidas iguales a las del OneHotEncoder",
                all(sorted(cat_json.get(k, [])) == sorted(v) for k, v in art.categorias.items()),
                "categorias_validas.json vs. OneHotEncoder.categories_"))
    res.append(("Partición 80/20 reproducida (media del StandardScaler = media de entrenamiento)",
                bool(np.allclose(scaler.mean_, X_tr[art.numericas].mean().values)) and scaler.n_samples_seen_ == len(X_tr),
                f"{len(X_tr)} entrenamiento / {len(X_te)} prueba"))
    res.append(("Clases del codificador en el orden de predict_proba",
                set(art.clases_modelo) == set(C.ORDEN_CLASES),
                " · ".join(f"columna {i} = {c}" for i, c in enumerate(art.clases_modelo))))
    res.append(("Probabilidades suman 1 en todas las filas de prueba",
                bool(np.allclose(proba.sum(axis=1), 1.0)), f"máx. desviación {np.abs(proba.sum(1) - 1).max():.1e}"))
    res.append(("argmax(predict_proba) coincide con predict()",
                bool((art.modelo.classes_[proba.argmax(1)] == pred_idx).all()), "1.000 filas de prueba"))
    m = metricas_prueba()
    guardada = matriz_guardada()
    res.append(("Matriz de confusión recalculada = matriz guardada",
                guardada is not None and (guardada.loc[C.ORDEN_CLASES, C.ORDEN_CLASES].values == m["matriz"].values).all(),
                "matriz_confusion_final.csv"))
    return res
