"""Predicción y explicación individual con el Pipeline original.

Las probabilidades se toman sin modificar de `predict_proba`. Las columnas de
`predict_proba` se nombran con `encoder.inverse_transform(modelo.classes_)`,
que es la única correspondencia índice → clase válida (el codificador ordena
alfabéticamente: Good=0, Poor=1, Standard=2).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def predecir(art, X: pd.DataFrame) -> pd.DataFrame:
    """Devuelve Prob_Good, Prob_Standard, Prob_Poor y Clase_predicha para cada fila."""
    proba = art.modelo.predict_proba(X)
    df = pd.DataFrame(proba, columns=[f"Prob_{c}" for c in art.clases_modelo], index=X.index)
    pred_idx = art.modelo.predict(X).astype(int)
    df["Clase_predicha"] = art.encoder.inverse_transform(pred_idx)
    # Comprobación defensiva: la clase de predict() debe ser el argmax de predict_proba().
    argmax = np.array(art.clases_modelo)[proba.argmax(axis=1)]
    if not (argmax == df["Clase_predicha"].values).all():
        raise RuntimeError("Inconsistencia entre predict() y predict_proba(): revisar artefactos.")
    return df[[f"Prob_{c}" for c in C.ORDEN_CLASES] + ["Clase_predicha"]]


def _matriz_transformada(art, X):
    pre = art.modelo.named_steps["preprocesamiento"]
    T = pre.transform(X)
    return np.asarray(T.toarray() if hasattr(T, "toarray") else T, dtype=float), pre.get_feature_names_out()


def _variable_original(nombre_transformado: str, categoricas: list) -> str:
    base = nombre_transformado.split("__", 1)[1]
    for c in categoricas:
        if base.startswith(c + "_"):
            return c
    return base


def referencia(art, X_train: pd.DataFrame) -> np.ndarray:
    """Media de la matriz transformada de entrenamiento (perfil de referencia)."""
    T, _ = _matriz_transformada(art, X_train)
    return T.mean(axis=0)


def explicar(art, x: pd.DataFrame, ref: np.ndarray) -> dict:
    """Descomposición aditiva exacta de las puntuaciones lineales (logits).

    Para la clase k:  z_k(x) = b_k + w_k·t(x)
                      z_k(x) − z_k(ref) = Σ_j w_kj · (t_j(x) − t̄_j)
    Las columnas one-hot se suman de vuelta a su variable original.
    """
    lr = art.modelo.named_steps["modelo"]
    T, nombres = _matriz_transformada(art, x)
    t = T[0]
    originales = [_variable_original(n, art.categoricas) for n in nombres]
    filas = []
    for k_idx, clase in enumerate(art.clases_modelo):
        contrib = lr.coef_[k_idx] * (t - ref)
        s = pd.Series(contrib, index=originales).groupby(level=0).sum()
        for var, val in s.items():
            filas.append({"clase": clase, "variable": var, "contribucion": float(val)})
    tabla = pd.DataFrame(filas)
    z_ref = lr.intercept_ + lr.coef_ @ ref
    z_x = lr.decision_function(T)[0]
    return {
        "tabla": tabla,
        "z_ref": dict(zip(art.clases_modelo, z_ref)),
        "z_x": dict(zip(art.clases_modelo, z_x)),
    }


def coeficientes(art) -> pd.DataFrame:
    """Coeficientes de la regresión logística por clase, con escala de cada variable."""
    lr = art.modelo.named_steps["modelo"]
    pre = art.modelo.named_steps["preprocesamiento"]
    nombres = pre.get_feature_names_out()
    scaler = pre.named_transformers_["numericas"]
    escala = dict(zip(art.numericas, scaler.scale_))
    filas = []
    for k_idx, clase in enumerate(art.clases_modelo):
        for n, w in zip(nombres, lr.coef_[k_idx]):
            var = _variable_original(n, art.categoricas)
            es_cat = var in art.categoricas
            nivel = n.split("__", 1)[1][len(var) + 1:] if es_cat else ""
            filas.append({"clase": clase, "termino": n.split("__", 1)[1], "variable": var,
                          "nivel": nivel, "tipo": "categórica" if es_cat else "numérica",
                          "coeficiente": float(w), "desv_estandar": escala.get(var, np.nan)})
    return pd.DataFrame(filas)


def dependencia_parcial(art, muestra: pd.DataFrame, variable: str, n: int = 20):
    """Dependencia parcial por fuerza bruta.

    Rejilla lineal de n puntos entre los percentiles 5 y 95 de la muestra; para cada
    valor se fija la variable en todas las filas y se promedia predict_proba.
    Reproduce exactamente `resultados/dependencia_parcial_datos.json`.
    """
    lo, hi = np.percentile(muestra[variable], [5, 95])
    rejilla = np.linspace(lo, hi, n)
    medias = []
    for v in rejilla:
        t = muestra.copy()
        t[variable] = v
        medias.append(art.modelo.predict_proba(t).mean(axis=0))
    medias = np.array(medias)
    return rejilla, {c: medias[:, i] for i, c in enumerate(art.clases_modelo)}
