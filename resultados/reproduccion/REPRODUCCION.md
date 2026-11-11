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
| Accuracy / F1 macro de prueba | 0.452 / 0.4526 (iguales a `RESULTADOS_VERIFICADOS.md`) |

Por lo tanto, las tablas de esta carpeta corresponden exactamente al modelo entregado.

## Archivos
- `cv_inicial.csv` — comparación inicial, 10 modelos, CV estratificada de 3 folds.
- `ajuste_hiperparametros.csv` — mejor F1 macro CV de GridSearchCV (6 modelos ajustados) y parámetros.
- `validacion_anidada.csv` — CV anidada 3×2 de los dos finalistas.
- `evaluacion_final.json` — métricas de prueba, reporte por clase, IC bootstrap 95 %, oráculo y SVM con log1p.
- `importancia_permutacion_10rep.csv` — importancia por permutación con 10 repeticiones (configuración del notebook). El archivo `interpretabilidad_importancias.csv` de la raíz usa 5 repeticiones; por eso sus cifras difieren ligeramente.
- `notebook_reejecutado_con_salidas.ipynb` — copia ejecutada, con salidas visibles.

## Observación
La celda markdown "Techo teórico de la simulación" del notebook original menciona un F1 del modelo final de 0.481, cifra de una ejecución anterior. La ejecución actual da 0.4526 (modelo final) y 0.5790 (oráculo).
