# Prisma — Clasificación crediticia sintética colombiana
**Machine Learning II · Nicolás Barrera y Angie Loango**

### Aplicación en línea: **[prisma-riesgo-crediticio.streamlit.app](https://prisma-riesgo-crediticio.streamlit.app/)**

Prisma es la aplicación Streamlit del proyecto: clasifica perfiles crediticios **sintéticos** en `Good`, `Standard` o `Poor` con una regresión logística regularizada (`C = 0.001`) dentro de un Pipeline de scikit-learn. Permite simular perfiles, ver probabilidades y explicaciones, predecir por lotes y revisar la metodología y los resultados del notebook.

> Prototipo académico. Datos y etiquetas sintéticos: no sirve para aprobar o negar créditos reales.

**Objetivo académico:** comparar enfoques de clasificación de distinta complejidad y evaluar si las señales financieras, laborales y de comportamiento de 5.000 perfiles sintéticos, descritos por 23 variables predictoras, permiten recuperar una etiqueta sintética bajo un procedimiento reproducible.

## Aplicación desplegada

La versión pública de Prisma está en **https://prisma-riesgo-crediticio.streamlit.app/** y se puede usar desde el navegador, sin instalar nada. La aplicación carga el Pipeline serializado `models/modelo_credito.joblib` y muestra las probabilidades tal como las devuelve `predict_proba`.

Desde la aplicación se puede:

- consultar las cifras del proyecto y explorar el dataset por clase (**Inicio**);
- describir un perfil con las 23 variables y obtener su clasificación (**Simulador** y **Resultado**);
- comparar dos perfiles o clasificar un CSV completo (**Comparar perfiles** y **Predicción por lotes**);
- revisar cómo funciona el modelo, cómo se eligió y cómo se construyeron los datos (**Interpretabilidad**, **Comparación de modelos** y **Metodología**).

El 11 de noviembre de 2026 el equipo confirmó manualmente que funcionan las ocho secciones (registro en [docs/ESTADO_VERIFICACION.md](docs/ESTADO_VERIFICACION.md)). Si la aplicación lleva tiempo sin visitas, Streamlit puede mostrar primero un botón para reactivarla; tarda unos segundos en cargar.

## Guía para evaluadores

| Qué revisar | Dónde |
|---|---|
| Aplicación en línea | [prisma-riesgo-crediticio.streamlit.app](https://prisma-riesgo-crediticio.streamlit.app/) |
| Notebook de entrenamiento | [notebooks/](notebooks/) |
| Notebook ejecutado, con salidas | [notebook_reejecutado_con_salidas.ipynb](resultados/reproduccion/notebook_reejecutado_con_salidas.ipynb) |
| Informe final | [reports/INFORME_FINAL_ML2.pdf](reports/INFORME_FINAL_ML2.pdf) |
| Datasets y modelos | [data/](data/) y [models/](models/) |
| Las 23 variables predictoras | [docs/DOCUMENTACION_23_VARIABLES.md](docs/DOCUMENTACION_23_VARIABLES.md) |
| Métricas verificadas | [docs/RESULTADOS_VERIFICADOS.md](docs/RESULTADOS_VERIFICADOS.md) |
| Tablas y figuras de resultados | [resultados/](resultados/) |
| Registro de pruebas de la aplicación | [docs/PRUEBAS_APLICACION.txt](docs/PRUEBAS_APLICACION.txt) |
| Estado de cada tipo de verificación | [docs/ESTADO_VERIFICACION.md](docs/ESTADO_VERIFICACION.md) |
| Reproducibilidad y procedencia de los archivos | [resultados/reproduccion/REPRODUCCION.md](resultados/reproduccion/REPRODUCCION.md) |
| Capturas de la aplicación | [docs/capturas/](docs/capturas/) |

## Instalación y ejecución

Todos los comandos se ejecutan desde la raíz del repositorio, con Python 3.11 – 3.14.

### 1. Instalar las dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate    # En Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

`requirements.txt` fija las versiones con las que se entrenó el modelo. El Pipeline serializado depende de scikit-learn 1.8.0, por lo que esas versiones no deben cambiarse.

### 2. Iniciar la aplicación Streamlit

```bash
streamlit run app.py
```

### 3. Ejecutar las pruebas automatizadas

```bash
python -m pytest -q
```

Las 27 pruebas de `tests/test_integridad.py` comprueban la integridad de los artefactos y que cada página se ejecute sin errores. No ejecutan el notebook ni reentrenan el modelo.

### 4. Ubicación de datos y modelos

| Carpeta | Archivos |
|---|---|
| `data/` | `dataset_credit_score_colombia.csv`, `dataset_credit_score_colombia.xlsx`, `categorias_validas.json` |
| `models/` | `modelo_credito.joblib`, `encoder_etiquetas.joblib`, `esquema.json`, `ejemplo_entrada.json` |

La aplicación lee el dataset desde `data/dataset_credit_score_colombia.csv` y el Pipeline desde `models/modelo_credito.joblib`. Las rutas están centralizadas en `prisma_app/config.py`.

### 5. Abrir y reproducir el notebook

Jupyter no está incluido en `requirements.txt`, por lo que debe instalarse en el mismo entorno:

```bash
python -m pip install jupyterlab
jupyter lab notebooks/ProyectoML2_EntregaFinal_FICO_Colombia.ipynb
```

Para reproducir el entrenamiento, ejecutar todas las celdas en orden. El notebook localiza la raíz del proyecto buscando las carpetas `data/` y `models/`.

> **Precaución:** ejecutar el notebook completo sobrescribe `data/dataset_credit_score_colombia.csv`, `data/dataset_credit_score_colombia.xlsx` y los cuatro archivos de `models/`. Conviene hacerlo sobre una copia del proyecto y no mezclar salidas de ejecuciones distintas.

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

```text
app.py                     Punto de entrada: configuración, estilos y navegación
requirements.txt           Dependencias de la aplicación, el notebook y las pruebas
pytest.ini                 Configuración de pytest
data/                      Datasets y categorías válidas
models/                    Modelo entrenado, codificador y archivos JSON
notebooks/                 Notebook principal
reports/                   Informe final (INFORME_FINAL_ML2.pdf)
resultados/                Métricas, tablas y gráficas de evaluación
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
docs/                      Documentación de variables, registros de verificación y capturas
```

## Integridad técnica

- **Modelo intacto**: se usan `models/modelo_credito.joblib` y `models/encoder_etiquetas.joblib` sin reentrenar.
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

Esa re-ejecución es anterior a la reorganización de carpetas y el notebook no se ha vuelto a ejecutar desde entonces. Las pruebas automatizadas verifican el software y la coherencia de los artefactos existentes, pero no constituyen una nueva reproducción del entrenamiento.

### Limitaciones de reproducibilidad

El notebook principal regenera únicamente los dos archivos del dataset y los cuatro de `models/`. Otros artefactos que usa la aplicación o que sirven de evidencia no tienen un procedimiento de generación automatizado en el repositorio, por lo que deben conservarse. El detalle por archivo está en la sección "Procedencia y regeneración de artefactos" de [REPRODUCCION.md](resultados/reproduccion/REPRODUCCION.md).


## Fuentes

- FICO, What's in your credit score: https://www.myfico.com/credit-education/whats-in-your-credit-score
- Gutiérrez-Rueda, Estrada y Capera (2011): https://doi.org/10.32468/tef.61
- Koshti, Molia y Varia (2025): https://www.ijsat.org/research-paper.php?id=4759

## Declaración de uso de inteligencia artificial

Durante el desarrollo de Prisma se utilizaron herramientas de inteligencia artificial generativa como apoyo en el diseño visual de la aplicación, la organización de contenidos, la redacción de la documentación y la presentación de resultados. Su uso fue complementario al trabajo del equipo: la construcción del dataset, la selección del modelo, la interpretación de las métricas y las decisiones técnicas son responsabilidad de Nicolás Barrera y Angie Loango, quienes deben comprenderlas y sustentarlas.
