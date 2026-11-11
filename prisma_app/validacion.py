"""Validación de entradas y reglas de coherencia.

- Errores (bloquean la predicción): columnas faltantes, valores vacíos, tipos
  inválidos, categorías no vistas en entrenamiento y valores fuera del rango
  observado en el dataset.
- Advertencias (no bloquean): combinaciones que el generador del notebook nunca
  produce. Las 15 reglas se cumplen en el 100 % de los 5.000 registros
  (comprobado en tests/test_integridad.py), así que una advertencia indica un
  perfil fuera del soporte de los datos sintéticos.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .esquema import VARIABLES, etiqueta

TOL = 0.0015  # tolerancia para fórmulas redondeadas a 3 decimales


def utilizacion_derivada(saldo: float, limite: float) -> float:
    """Fórmula del notebook (celda 'UTILIZACIÓN DEL CRÉDITO')."""
    u = saldo / limite if limite > 0 else 0.0
    return float(np.round(min(max(u, 0.0), 1.0), 3))  # mismo redondeo que pandas .round(3)


def ratio_derivado(deuda: float, ingreso_mensual: float) -> float:
    """Fórmula del notebook (celda 'RATIO DEUDA / INGRESO ANUAL')."""
    anual = ingreso_mensual * 12
    if anual > 0:
        r = deuda / anual
    else:
        r = 2.0 if deuda > 0 else 0.0
    return float(np.round(min(max(r, 0.0), 3.0), 3))


def preparar_entrada(registros, columnas: list, tipos: dict) -> pd.DataFrame:
    """DataFrame con el orden exacto de columnas y los dtypes del entrenamiento."""
    df = pd.DataFrame(registros if isinstance(registros, list) else [registros]) \
        if not isinstance(registros, pd.DataFrame) else registros.copy()
    df = df[columnas]
    for c in columnas:
        t = tipos[c]
        if t.startswith("int"):
            df[c] = pd.to_numeric(df[c]).round().astype("int64")
        elif t.startswith("float"):
            df[c] = pd.to_numeric(df[c]).astype("float64")
        else:
            df[c] = df[c].astype(str)
    return df


def reglas_coherencia(p: dict) -> list[str]:
    """Devuelve mensajes de advertencia para un perfil (dict con las 23 columnas)."""
    a = []
    edad_meses = max((int(p["Edad"]) - 18) * 12, 0)
    tarjeta = int(p["Tiene_Tarjeta_Credito"])
    if tarjeta == 0:
        if p["Limite_Tarjeta"] > 0 or p["Saldo_Tarjeta"] > 0:
            a.append("Sin tarjeta, el cupo y el saldo deberían ser 0.")
        if p["Comportamiento_Pago_Tarjeta"] != "No aplica":
            a.append("Sin tarjeta, el comportamiento de pago debería ser 'No aplica'.")
        if p["Monto_Pagado_Tarjeta"] > 0:
            a.append("Sin tarjeta, el monto pagado debería ser 0.")
    else:
        if p["Limite_Tarjeta"] <= 0:
            a.append("Con tarjeta, el cupo debería ser mayor que 0.")
        if p["Comportamiento_Pago_Tarjeta"] == "No aplica":
            a.append("Con tarjeta, el comportamiento de pago no debería ser 'No aplica'.")
    if p["Saldo_Tarjeta"] > p["Limite_Tarjeta"]:
        a.append("El saldo de la tarjeta supera el cupo.")
    if p["Monto_Pagado_Tarjeta"] > p["Saldo_Tarjeta"]:
        a.append("El monto pagado supera el saldo de la tarjeta.")
    if abs(utilizacion_derivada(p["Saldo_Tarjeta"], p["Limite_Tarjeta"]) - p["Utilizacion_Credito"]) > TOL:
        a.append("La utilización no coincide con saldo ÷ cupo.")
    if abs(ratio_derivado(p["Deuda_Pendiente"], p["Ingreso_Mensual"]) - p["Ratio_Deuda_Ingreso"]) > TOL:
        a.append("La razón deuda/ingreso no coincide con deuda ÷ (ingreso × 12).")
    if int(p["Numero_Retrasos_12M"]) == 0 and p["Dias_Mora_Promedio"] > 0:
        a.append("Sin retrasos, los días de mora deberían ser 0.")
    if int(p["Numero_Retrasos_12M"]) > 0 and p["Dias_Mora_Promedio"] == 0:
        a.append("Con retrasos, los días de mora deberían ser mayores que 0.")
    if int(p["Numero_Prestamos"]) > int(p["Numero_Productos_Financieros"]):
        a.append("Hay más préstamos que productos financieros.")
    if int(p["Meses_Cotizados_12M"]) == 0 and p["IBC_Aproximado"] > 0:
        a.append("Sin meses cotizados, el IBC debería ser 0.")
    if p["Tipo_Cotizante"] == "Sin cotizacion" and int(p["Meses_Cotizados_12M"]) > 0:
        a.append("'Sin cotizacion' implica 0 meses cotizados.")
    if int(p["Antiguedad_Crediticia_Meses"]) > edad_meses:
        a.append("La antigüedad crediticia supera los meses posibles desde los 18 años.")
    if int(p["Antiguedad_Laboral_Meses"]) > edad_meses:
        a.append("La antigüedad laboral supera los meses posibles desde los 18 años.")
    combo = (p["Tipo_Ocupacion"], p["Formalidad_Laboral"], p["Tipo_Cotizante"])
    if combo not in COMBINACIONES_LABORALES:
        a.append("La combinación ocupación / formalidad / cotizante no aparece en el dataset.")
    return a


# Las 8 combinaciones observadas en el dataset (ver tests).
COMBINACIONES_LABORALES = {
    ("Cuenta propia", "Formal", "Independiente"),
    ("Cuenta propia", "Informal", "Sin cotizacion"),
    ("Dependiente", "Formal", "Dependiente"),
    ("Dependiente", "Informal", "Sin cotizacion"),
    ("Desempleado", "No aplica", "Sin cotizacion"),
    ("Independiente", "Formal", "Independiente"),
    ("Independiente", "Informal", "Sin cotizacion"),
    ("Pensionado", "No aplica", "Pensionado"),
}


def errores_valor(nombre: str, valor, rango: tuple | None, categorias: dict, tipo_dtype: str) -> str | None:
    """Error de un valor individual, o None si es válido."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)) or (isinstance(valor, str) and valor.strip() == ""):
        return f"{etiqueta(nombre)}: valor vacío."
    if nombre in categorias:
        if str(valor) not in categorias[nombre]:
            return f"{etiqueta(nombre)}: '{valor}' no es una categoría del entrenamiento."
        return None
    try:
        x = float(valor)
    except (TypeError, ValueError):
        return f"{etiqueta(nombre)}: '{valor}' no es numérico."
    if not np.isfinite(x):
        return f"{etiqueta(nombre)}: valor no finito."
    if tipo_dtype.startswith("int") and abs(x - round(x)) > 1e-9:
        return f"{etiqueta(nombre)}: debe ser un número entero."
    if VARIABLES[nombre].tipo == "binaria" and x not in (0.0, 1.0):
        return f"{etiqueta(nombre)}: debe ser 0 o 1."
    if rango is not None:
        lo, hi = rango
        if x < lo - 1e-9 or x > hi + 1e-9:
            return f"{etiqueta(nombre)}: {x:g} está fuera del rango observado [{lo:g}, {hi:g}]."
    return None


def validar_perfil(p: dict, columnas, rangos, categorias, tipos) -> tuple[list, list]:
    errores = [e for c in columnas
               if (e := errores_valor(c, p.get(c), rangos.get(c), categorias, tipos[c]))]
    advertencias = [] if errores else reglas_coherencia(p)
    return errores, advertencias


def validar_lote(df: pd.DataFrame, columnas, rangos, categorias, tipos):
    """Valida un CSV completo.

    Devuelve (errores_globales, reporte por fila, DataFrame listo para el modelo
    con solo las filas válidas, índices válidos).
    """
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        return ([f"Faltan {len(faltantes)} columnas requeridas: " + ", ".join(faltantes)],
                None, None, [])
    filas = []
    validos = []
    for i, fila in df[columnas].iterrows():
        p = fila.to_dict()
        errs = [e for c in columnas if (e := errores_valor(c, p[c], rangos.get(c), categorias, tipos[c]))]
        adv = []
        if not errs:
            p_num = {c: (float(p[c]) if c not in categorias else str(p[c])) for c in columnas}
            adv = reglas_coherencia(p_num)
            validos.append(i)
        filas.append({"fila": i + 1,
                      "estado": "error" if errs else ("advertencia" if adv else "válida"),
                      "mensajes": " | ".join(errs or adv)})
    reporte = pd.DataFrame(filas)
    listo = preparar_entrada(df.loc[validos, columnas], columnas, tipos) if validos else None
    return [], reporte, listo, validos
