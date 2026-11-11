# Prisma — Clasificación crediticia sintética colombiana
**Machine Learning II · Nicolás Barrera y Angie Loango**

Prisma es la aplicación Streamlit del proyecto: clasifica perfiles crediticios **sintéticos** en `Good`, `Standard` o `Poor` con una regresión logística regularizada (`C = 0.001`) dentro de un Pipeline de scikit-learn. Permite simular perfiles, ver probabilidades y explicaciones, predecir por lotes y revisar la metodología y los resultados del notebook.

> Prototipo académico. Datos y etiquetas sintéticos: no sirve para aprobar o negar créditos reales.

## Ejecución

Desde esta carpeta (Python 3.11 – 3.14):

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para reproducir el entrenamiento, abrir `ProyectoML2_EntregaFinal_FICO_Colombia.ipynb` y ejecutar todas las celdas en orden. El notebook regenera datos y artefactos; no mezclar salidas de ejecuciones distintas.

Pruebas automáticas (27):

```bash
python -m pytest -q
```

## Módulos de la aplicación

| Página | Qué hace |
|---|---|
| **Inicio** | Demostración en vivo con un perfil real, cifras verificadas, distribución de clases y exploración interactiva de variables por clase. |
| **Simulador** | Formulario de las 23 variables en 5 secciones con indicador de progreso, rangos validados, reglas de coherencia, vista previa en vivo, carga de perfiles del dataset, corrección automática y restablecer. |
| **Resultado** | Clase predicha, probabilidades exactas de `predict_proba`, interpretación, explicación individual exacta y descarga (HTML y CSV). |
| **Comparar perfiles** | Dos perfiles lado a lado: probabilidades, diferencias por variable y descarga CSV. |
| **Predicción por lotes** | Carga de CSV, validación fila a fila, predicción con el mismo Pipeline y descarga de resultados. Incluye plantilla. |
| **Interpretabilidad** | Importancia por permutación, coeficientes, dependencia parcial, matriz de confusión (globales) y método de la explicación individual. |
| **Comparación de modelos** | CV inicial de 10 modelos, ajuste de hiperparámetros, validación anidada, evaluación final y techo teórico. |
| **Metodología** | Objetivo, construcción del dataset, generación de etiquetas, justificación de pesos (FICO), variables, entrenamiento, limitaciones y verificaciones en vivo. |

## Arquitectura

```
app.py                     Punto de entrada: configuración, estilos y navegación
prisma_app/
  config.py                Rutas relativas, orden de clases y paleta
  datos.py                 Carga en caché de artefactos, dataset y resultados; métricas y verificaciones en vivo
  esquema.py               Metadatos de las 23 variables (etiquetas, unidades, grupos) y pesos de generación
  validacion.py            Tipos, rangos, categorías, reglas de coherencia y validación de lotes
  prediccion.py            predict_proba con correspondencia índice→clase, explicación exacta, coeficientes, PDP
  estado.py                Estado de sesión compartido entre páginas
  graficos.py              Gráficos Plotly con estilo uniforme
  componentes.py           Componentes visuales (espectro de probabilidades, cifras, avisos)
  estilos.py               Hoja de estilos
  reporte.py               Resumen descargable de una predicción
vistas/                    Una página por módulo
static/                    Logo y fuentes Sora e Instrument Sans (licencia SIL OFL), sin depender de internet
.streamlit/config.toml     Tema y servicio de archivos estáticos
tests/test_integridad.py   Pruebas de integridad y de ejecución de cada página
resultados/reproduccion/   Tablas que el notebook calcula pero no había exportado (ver abajo)
legacy/app_original.py     Versión anterior de la app, como referencia
```

## Integridad técnica

- **Modelo intacto**: se usan `artefactos/modelo_credito.joblib` y `encoder_etiquetas.joblib` sin reentrenar.
- **Esquema**: las 23 columnas, su orden y sus dtypes se toman del Pipeline y del dataset; las categorías, del `OneHotEncoder`.
- **Clases**: el codificador ordena `Good=0, Poor=1, Standard=2`; las columnas de `predict_proba` se nombran siempre con `encoder.inverse_transform(modelo.classes_)` y se comprueba que `argmax(predict_proba) == predict()`.
- **Probabilidades** sin transformar; no se convierten en probabilidades de incumplimiento ni se usan umbrales de aprobación.
- **Valores iniciales**: el registro real del entrenamiento más cercano a la mediana, para que el perfil sea coherente.
- **Validación**: rangos observados en los 5.000 registros; 15 reglas de coherencia extraídas del generador del notebook, que se cumplen en el 100 % del dataset. Las utilizaciones y la razón deuda/ingreso pueden calcularse con las fórmulas exactas del notebook.
- **Métricas** recalculadas en vivo sobre la partición 80/20 reproducida (semilla 42), idénticas a las reportadas.
- **Explicación individual**: descomposición exacta del logit de la regresión logística frente al perfil promedio del entrenamiento; la suma de contribuciones reproduce `decision_function`.
- **Dependencia parcial**: cálculo explícito que reproduce `resultados/dependencia_parcial_datos.json` con diferencia 0.
- Los pesos de generación de etiquetas solo se documentan; la app nunca los usa para predecir.

### Resultados reproducidos

El notebook entregado no conservaba salidas y el proyecto no incluía las tablas de ajuste de hiperparámetros ni de validación anidada. Se re-ejecutó una copia del notebook con las versiones de `requirements.txt`; el dataset y el modelo regenerados son **idénticos byte a byte** a los entregados. Las tablas están en `resultados/reproduccion/` y el procedimiento en `resultados/reproduccion/REPRODUCCION.md`.

## Segunda entrega

La carpeta `segunda_entrega/` conserva el notebook, el informe y el dataset de la entrega anterior. Ese dataset se generó con una ponderación distinta de la etiqueta, por eso sus métricas (F1 macro ≈ 0,481) no son comparables con las de la entrega final (F1 macro 0,4526). El modelo y la aplicación usan el dataset de la raíz.

## Fuentes
- FICO, What's in your credit score: https://www.myfico.com/credit-education/whats-in-your-credit-score
- Gutiérrez-Rueda, Estrada y Capera (2011): https://doi.org/10.32468/tef.61
- Koshti, Molia y Varia (2025): https://www.ijsat.org/research-paper.php?id=4759

Declaración de IA: se utilizó inteligencia artificial generativa como herramienta de apoyo en el desarrollo del proyecto.
