
"""Configuración central: rutas relativas, orden de clases y paleta.

Todas las rutas se resuelven a partir de la carpeta del proyecto,
sin rutas absolutas.
"""
from __future__ import annotations

from pathlib import Path

# ============================================================
# 1. RUTAS PRINCIPALES DEL PROYECTO
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent

# Carpetas del proyecto
DATOS = RAIZ / "data"
ARTEFACTOS = RAIZ / "models"
RESULTADOS = RAIZ / "resultados"
REPRODUCCION = RESULTADOS / "reproduccion"

# ============================================================
# 2. ARCHIVOS DEL MODELO
# ============================================================

RUTA_MODELO = ARTEFACTOS / "modelo_credito.joblib"
RUTA_ENCODER = ARTEFACTOS / "encoder_etiquetas.joblib"
RUTA_ESQUEMA = ARTEFACTOS / "esquema.json"
RUTA_EJEMPLO = ARTEFACTOS / "ejemplo_entrada.json"

# ============================================================
# 3. DATOS
# ============================================================

RUTA_CATEGORIAS = DATOS / "categorias_validas.json"
RUTA_DATASET = DATOS / "dataset_credit_score_colombia.csv"

# ============================================================
# 4. RESULTADOS Y EVALUACIÓN
# ============================================================

RUTA_IMPORTANCIAS = RESULTADOS / "interpretabilidad_importancias.csv"
RUTA_MATRIZ = RESULTADOS / "matriz_confusion_final.csv"
RUTA_CV = RESULTADOS / "comparacion_modelos_cv.csv"
RUTA_PDP = RESULTADOS / "dependencia_parcial_datos.json"

# ============================================================
# 5. PARÁMETROS DEL MODELO
# ============================================================

# Parámetros de partición idénticos a los del notebook
# (celda de train_test_split).
SEMILLA = 42
TEST_SIZE = 0.20
OBJETIVO = "Credit_Score"
COLUMNA_EXCLUIDA = "Antiguedad_Laboral_Años"

# ============================================================
# 6. CLASES DE RIESGO CREDITICIO
# ============================================================

# Orden de presentación (ordinal).
# NO es el orden interno del codificador, que es alfabético
# (Good, Poor, Standard).
# La correspondencia se resuelve siempre con:
# encoder.inverse_transform(modelo.classes_).

ORDEN_CLASES = ["Good", "Standard", "Poor"]

NOMBRE_CLASE = {
    "Good": "Good",
    "Standard": "Standard",
    "Poor": "Poor",
}

DESCRIPCION_CLASE = {
    "Good": "perfil sintético de menor riesgo relativo",
    "Standard": "perfil sintético de riesgo intermedio",
    "Poor": "perfil sintético de mayor riesgo relativo",
}

# ============================================================
# 7. PALETA DE COLORES POR CLASE
# ============================================================

# Paleta semáforo suave elegida por el equipo:
# verde, ámbar y rojo de baja saturación.
#
# Validada con el script de paleta:
# contraste de Standard < 3:1 y separación CVD verde/ámbar
# en el límite. Por eso cada barra y leyenda llevan
# siempre el nombre de la clase escrito.

COLOR_CLASE = {
    "Good": "#3FA67A",
    "Standard": "#E5A535",
    "Poor": "#E06A5A",
}

TEXTO_SOBRE_CLASE = {
    "Good": "#FFFFFF",
    "Standard": "#3B2A05",
    "Poor": "#FFFFFF",
}

SUAVE_CLASE = {
    "Good": "rgba(63,166,122,.15)",
    "Standard": "rgba(229,165,53,.18)",
    "Poor": "rgba(224,106,90,.14)",
}

# ============================================================
# 8. COLORES GENERALES DE LA INTERFAZ PRISMA
# ============================================================

# Tokens de interfaz (tema claro)

TINTA = "#111827"
TINTA_2 = "#4B5563"
TINTA_3 = "#6B7280"

LINEA = "#E5E7EB"

SUPERFICIE = "#FFFFFF"
SUAVE = "#F5F8F7"
TARJETA = "#FFFFFF"

ACENTO = "#0F766E"
ACENTO_CLARO = "#E7F3F1"
ACENTO_OSCURO = "#0B5A54"

# Alias utilizados por módulos anteriores
MARINO = ACENTO_OSCURO
TURQUESA = ACENTO
AZUL_ELECTRICO = ACENTO
