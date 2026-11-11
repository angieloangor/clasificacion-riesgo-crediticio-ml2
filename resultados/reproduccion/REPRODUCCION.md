# Reproducción de resultados no exportados

**Fecha:** 10 de noviembre de 2026
**Motivo:** el notebook entregado no conserva salidas, y el proyecto no incluía como archivo las tablas de ajuste de hiperparámetros ni de validación cruzada anidada.

## Procedimiento
1. Se copió `ProyectoML2_EntregaFinal_FICO_Colombia.ipynb` a una carpeta aislada (el original no se modificó).
2. Se añadió **al final de la copia** una única celda que exporta objetos ya calculados por el notebook (`resultados_cv`, `resultados_busqueda`, `resultados_nested`, `importancias_df`, métricas finales, IC bootstrap, oráculo y prueba log1p del SVM). Esa celda no altera datos, pesos, modelos ni semillas.
3. Se ejecutaron todas las celdas en orden con Python 3.13, numpy 2.3.5, pandas 2.2.3, scipy 1.17.0, scikit-learn 1.8.0, xgboost 3.1.3, lightgbm 4.6.0 (versiones de `requirements.txt` del notebook).

## Verificación de identidad
| Comprobación | Resultado |
|---|---|
| `dataset_credit_score_colombia.csv` regenerado vs. original | idéntico byte a byte (SHA-256 `0fb26f3c…2d45`) |
| `modelo_credito.joblib` regenerado vs. original | idéntico byte a byte (SHA-256 `05e73a82…30fa`) |
| `predict_proba` en los 5.000 registros | diferencia máxima 0.0 |
| `cv_inicial.csv` vs. `resultados/comparacion_modelos_cv.csv` | mismos valores |
| Accuracy / F1 macro de prueba | 0.452 / 0.4526 (iguales a `docs/RESULTADOS_VERIFICADOS.md`) |

Por lo tanto, las tablas de esta carpeta corresponden exactamente al modelo entregado.

## Archivos
- `cv_inicial.csv` — comparación inicial, 10 modelos, CV estratificada de 3 folds.
- `ajuste_hiperparametros.csv` — mejor F1 macro CV de GridSearchCV (6 modelos ajustados) y parámetros.
- `validacion_anidada.csv` — CV anidada 3×2 de los dos finalistas.
- `evaluacion_final.json` — métricas de prueba, reporte por clase, IC bootstrap 95 %, oráculo y SVM con log1p.
- `importancia_permutacion_10rep.csv` — importancia por permutación con 10 repeticiones (configuración del notebook). El archivo `resultados/interpretabilidad_importancias.csv` usa 5 repeticiones; por eso sus cifras difieren ligeramente.
- `notebook_reejecutado_con_salidas.ipynb` — copia ejecutada, con salidas visibles.

## Observación
La celda markdown "Techo teórico de la simulación" del notebook original menciona un F1 del modelo final de 0.481, cifra de una ejecución anterior. La ejecución actual da 0.4526 (modelo final) y 0.5790 (oráculo).

## Procedencia y regeneración de artefactos

Esta sección indica qué puede regenerarse con los archivos versionados. **Ejecutar el notebook principal no regenera todos los artefactos del proyecto.**

| Archivo | Origen | Generación automatizada en el repositorio | Lo lee Streamlit |
|---|---|---|---|
| `data/dataset_credit_score_colombia.csv` | Notebook principal, celda 44 | Sí | Sí |
| `data/dataset_credit_score_colombia.xlsx` | Notebook principal, celda 44 | Sí | No |
| `models/modelo_credito.joblib`, `models/encoder_etiquetas.joblib`, `models/esquema.json` | Notebook principal, celda 104 | Sí | Sí |
| `models/ejemplo_entrada.json` | Notebook principal, celda 104 | Sí | No; lo usan las pruebas |
| `resultados/reproduccion/ajuste_hiperparametros.csv`, `validacion_anidada.csv`, `evaluacion_final.json`, `importancia_permutacion_10rep.csv` | Celda de exportación de la copia re-ejecutada | Solo dentro de `notebook_reejecutado_con_salidas.ipynb` | Sí |
| `resultados/reproduccion/cv_inicial.csv` | Celda de exportación de la copia re-ejecutada | Solo dentro de `notebook_reejecutado_con_salidas.ipynb` | No; lo usan las pruebas |
| `data/categorias_validas.json` | Artefacto complementario | No | Sí |
| `resultados/interpretabilidad_importancias.csv` | Artefacto complementario | No | Sí |
| `resultados/matriz_confusion_final.csv` | Artefacto complementario | No | Sí |
| `resultados/comparacion_modelos_cv.csv` | Artefacto complementario | No | Sí |
| `resultados/dependencia_parcial_datos.json` | Artefacto complementario | No | Sí |
| `resultados/comparacion_10_modelos.png`, `dependencia_parcial.png`, `importancia_permutacion.png`, `matriz_confusion.png`, `pesos_fico_adaptado.png` | Artefacto complementario | No | No |

Algunas secciones de la aplicación muestran un aviso u omiten contenido cuando falta un archivo opcional, pero la aplicación completa requiere todos los marcados con "Sí".

Las pruebas automatizadas contrastan parte de los artefactos complementarios sin regenerarlos:

- `data/categorias_validas.json` se compara con las categorías del `OneHotEncoder` y del dataset.
- `resultados/matriz_confusion_final.csv` se compara con la matriz recalculada a partir del modelo.
- `resultados/dependencia_parcial_datos.json` se compara con la dependencia parcial recalculada.
- `resultados/comparacion_modelos_cv.csv` se compara con `cv_inicial.csv`.
- `resultados/interpretabilidad_importancias.csv` solo se comprueba en sus variables, no en sus valores.
- Las cinco imágenes PNG no tienen comprobación automatizada.

### Limitaciones

1. El notebook principal genera únicamente los seis archivos de `data/` y `models/` indicados arriba.
2. La celda que exporta las tablas de esta carpeta solo existe en la copia re-ejecutada y escribe en una carpeta `export/`; el notebook principal no las exporta.
3. Los cinco archivos de datos complementarios y las cinco imágenes no tienen en el repositorio un procedimiento de generación, por lo que deben conservarse. Si se perdieran, no se recuperarían ejecutando el notebook.
4. La identidad byte a byte documentada arriba se obtuvo con Python 3.13 y las versiones indicadas en el procedimiento. La versión actual del notebook, con las rutas adaptadas a `data/` y `models/`, no se ha ejecutado completa.
