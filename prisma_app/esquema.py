"""Metadatos de las 23 variables predictoras.

Los nombres de columna son EXACTAMENTE los de `artefactos/esquema.json`.
Aquí solo se añaden etiquetas legibles, unidades, ayudas y el grupo del formulario;
los rangos y valores iniciales se derivan de los datos (ver datos.py).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    nombre: str          # nombre exacto de la columna
    etiqueta: str        # texto para la interfaz
    tipo: str            # entero | decimal | dinero | proporcion | binaria | categorica
    unidad: str = ""
    ayuda: str = ""
    paso: float | None = None
    derivada: bool = False   # se puede calcular con la fórmula del notebook


VARIABLES: dict[str, Variable] = {v.nombre: v for v in [
    Variable("Edad", "Edad", "entero", "años",
             "Generada con una normal truncada entre 18 y 75 años."),
    Variable("Tipo_Ocupacion", "Tipo de ocupación", "categorica", "",
             "Situación laboral principal del perfil."),
    Variable("Formalidad_Laboral", "Formalidad laboral", "categorica", "",
             "Formal o informal; 'No aplica' para desempleados y pensionados."),
    Variable("Antiguedad_Laboral_Meses", "Antigüedad laboral", "entero", "meses",
             "Meses en la ocupación actual. Nunca supera (edad − 18) × 12."),
    Variable("Ingreso_Mensual", "Ingreso mensual", "dinero", "COP",
             "Ingreso mensual en pesos colombianos. Puede ser 0 en desempleados.", 50_000),
    Variable("Variabilidad_Ingreso", "Variabilidad del ingreso", "proporcion", "índice 0–1",
             "Escala sintética: 0 = ingreso estable, 1 = muy variable.", 0.01),
    Variable("Tipo_Cotizante", "Tipo de cotizante", "categorica", "",
             "Relación con el sistema de seguridad social (aportes a pensión y salud)."),
    Variable("Meses_Cotizados_12M", "Meses cotizados (12 meses)", "entero", "meses",
             "Meses con aportes en el último año (0 a 12)."),
    Variable("IBC_Aproximado", "IBC aproximado", "dinero", "COP",
             "Ingreso base de cotización: salario o ingreso sobre el que se calculan los aportes.", 50_000),
    Variable("Antiguedad_Crediticia_Meses", "Antigüedad crediticia", "entero", "meses",
             "Meses desde el primer producto de crédito. Nunca supera (edad − 18) × 12."),
    Variable("Numero_Productos_Financieros", "Productos financieros", "entero", "productos",
             "Total de productos (cuentas, tarjetas, préstamos)."),
    Variable("Numero_Prestamos", "Préstamos activos", "entero", "préstamos",
             "Número de préstamos. No puede superar el total de productos."),
    Variable("Tiene_Tarjeta_Credito", "Tiene tarjeta", "binaria", "",
             "1 = sí, 0 = no. El modelo la recibe como variable numérica 0/1."),
    Variable("Limite_Tarjeta", "Cupo de la tarjeta", "dinero", "COP",
             "Límite de crédito aprobado. Es 0 si no tiene tarjeta.", 50_000),
    Variable("Saldo_Tarjeta", "Saldo de la tarjeta", "dinero", "COP",
             "Saldo utilizado. No puede superar el cupo.", 50_000),
    Variable("Utilizacion_Credito", "Utilización del crédito", "proporcion", "proporción 0–1",
             "Saldo ÷ cupo, redondeado a 3 decimales (0,25 = 25 %).", 0.001, derivada=True),
    Variable("Deuda_Pendiente", "Deuda pendiente", "dinero", "COP",
             "Saldo de tarjeta más deuda asociada a préstamos.", 100_000),
    Variable("Ratio_Deuda_Ingreso", "Deuda / ingreso anual", "proporcion", "veces",
             "Deuda pendiente ÷ (ingreso mensual × 12), acotado a [0, 3]. Si el ingreso es 0 y hay deuda, el notebook asigna 2,0.",
             0.001, derivada=True),
    Variable("Comportamiento_Pago_Tarjeta", "Comportamiento de pago", "categorica", "",
             "Cómo paga la tarjeta. 'No aplica' si no tiene tarjeta."),
    Variable("Monto_Pagado_Tarjeta", "Monto pagado de la tarjeta", "dinero", "COP",
             "Pago del último periodo. No supera el saldo.", 10_000),
    Variable("Numero_Retrasos_12M", "Retrasos (12 meses)", "entero", "retrasos",
             "Número de pagos atrasados en el último año."),
    Variable("Dias_Mora_Promedio", "Días de mora promedio", "decimal", "días",
             "Promedio de días de atraso. Es 0 si no hay retrasos.", 0.1),
    Variable("Consultas_Credito_6M", "Consultas de crédito (6 meses)", "entero", "consultas",
             "Solicitudes de crédito registradas en los últimos 6 meses."),
]}

# Grupos del simulador. Cubren las 23 variables exactamente una vez.
GRUPOS: list[tuple[str, str, list[str]]] = [
    ("ingresos", "Información financiera",
     ["Ingreso_Mensual", "Variabilidad_Ingreso", "IBC_Aproximado"]),
    ("historial", "Historial crediticio",
     ["Antiguedad_Crediticia_Meses", "Comportamiento_Pago_Tarjeta", "Numero_Retrasos_12M",
      "Dias_Mora_Promedio", "Consultas_Credito_6M"]),
    ("deuda", "Endeudamiento y utilización",
     ["Numero_Productos_Financieros", "Numero_Prestamos", "Tiene_Tarjeta_Credito",
      "Limite_Tarjeta", "Saldo_Tarjeta", "Utilizacion_Credito",
      "Monto_Pagado_Tarjeta", "Deuda_Pendiente", "Ratio_Deuda_Ingreso"]),
    ("laboral", "Situación laboral y estabilidad",
     ["Tipo_Ocupacion", "Formalidad_Laboral", "Antiguedad_Laboral_Meses",
      "Tipo_Cotizante", "Meses_Cotizados_12M"]),
    ("otras", "Otras características",
     ["Edad"]),
]

# Nombres cortos para el paso a paso del simulador (mismo orden que GRUPOS).
GRUPOS_CORTOS = ["Ingresos", "Historial crediticio", "Deuda y uso del crédito", "Situación laboral", "Otras"]

# Pesos del mecanismo de generación de etiquetas (celda PESOS_FICO_CO del notebook).
# Se reproducen solo para documentarlos; la aplicación nunca los usa para predecir.
PESOS_GENERACION = [
    # (señal, variable, grupo FICO, peso, signo)
    ("Utilización del crédito", "Utilizacion_Credito", "Montos adeudados", 0.30 / 2, +1),
    ("Deuda / ingreso", "Ratio_Deuda_Ingreso", "Montos adeudados", 0.30 / 2, +1),
    ("Retrasos 12M", "Numero_Retrasos_12M", "Historial de pagos", 0.35 / 3, +1),
    ("Días de mora", "Dias_Mora_Promedio", "Historial de pagos", 0.35 / 3, +1),
    ("Comportamiento de pago", "Comportamiento_Pago_Tarjeta", "Historial de pagos", 0.35 / 3, +1),
    ("Consultas 6M", "Consultas_Credito_6M", "Crédito nuevo", 0.10, +1),
    ("Variabilidad del ingreso", "Variabilidad_Ingreso", "Ingresos y cotización", 0.06, +1),
    ("Meses sin cotizar", "Meses_Cotizados_12M", "Ingresos y cotización", 0.04, +1),
    ("Antigüedad crediticia", "Antiguedad_Crediticia_Meses", "Antigüedad crediticia", 0.15, -1),
]


def etiqueta(nombre: str) -> str:
    v = VARIABLES.get(nombre)
    return v.etiqueta if v else nombre.replace("_", " ")


def formato_valor(nombre: str, valor) -> str:
    """Formato legible para tablas y resúmenes (no altera el valor del modelo)."""
    v = VARIABLES.get(nombre)
    if v is None:
        return str(valor)
    if v.tipo == "categorica":
        return str(valor)
    if v.tipo == "binaria":
        return "Sí" if int(valor) == 1 else "No"
    if v.tipo == "dinero":
        return f"$ {float(valor):,.0f}".replace(",", ".")
    if v.tipo == "proporcion":
        return f"{float(valor):.3f}".replace(".", ",")
    if v.tipo == "decimal":
        return f"{float(valor):.1f}".replace(".", ",") + (f" {v.unidad}" if v.unidad else "")
    x = float(valor)
    txt = f"{int(x)}" if x.is_integer() else f"{x:.1f}".replace(".", ",")
    return txt + (f" {v.unidad}" if v.unidad else "")
