# Verificación de cierre

Estado al 11 de noviembre de 2026, después de reorganizar el proyecto en `data/`, `models/`, `notebooks/` y `reports/`. Cada tipo de verificación es independiente: completar uno no implica haber completado los demás.

## Pruebas automatizadas (pytest)
- Última ejecución en macOS, después de la reorganización: 27 pruebas aprobadas (ver `docs/PRUEBAS_APLICACION.txt`).
- 11 de noviembre: 27 pruebas aprobadas en Linux (Python 3.13.18, con las versiones fijadas en `requirements.txt`) sobre el commit `b8ce44f` de la rama `organizacion-final`, al preparar la entrega final (`docs/PRUEBAS_APLICACION.txt`, sección 6). Ese día no se repitieron en macOS.
- Comprueban el software y la coherencia de los artefactos existentes. No ejecutan el notebook ni reentrenan el modelo.

## Pruebas de la aplicación en navegador
- 10 de noviembre, Linux con Chromium: las 8 páginas cargaron sin excepciones y se probaron los flujos principales (`docs/PRUEBAS_APLICACION.txt`, `docs/capturas/`).
- Esas pruebas en Linux con Chromium no se han repetido después de la reorganización.
- 10 de noviembre, macOS con Google Chrome y Streamlit en `localhost:8501`: prueba manual del equipo, observada mediante capturas de pantalla. Se verificaron Inicio, Simulador y Resultado (`docs/PRUEBAS_APLICACION.txt`, sección 4). Las otras cinco páginas no formaron parte de esta prueba manual.
- Esta prueba manual es independiente de las 27 pruebas automatizadas de pytest. En ella no se ejecutó el notebook ni se reentrenó el modelo.
- Una revisión anterior solo había llegado a revisión de código y compilación sintáctica, porque no se pudo instalar Streamlit en ese entorno.

## Revisión manual de las ocho secciones (11 de noviembre de 2026)
- El equipo verificó manualmente las ocho secciones de Prisma en la aplicación pública de Streamlit Community Cloud (https://prisma-riesgo-crediticio.streamlit.app/): Inicio, Simulador, Resultado, Comparar perfiles, Predicción por lotes, Interpretabilidad, Comparación de modelos y Metodología. Según esa revisión, las ocho funcionan (`docs/PRUEBAS_APLICACION.txt`, sección 5).
- Es una revisión manual reportada por el equipo, **no una prueba automatizada**. No se adjuntaron capturas ni registros de esta revisión, y el reporte no detalla los pasos ejecutados en cada sección.
- El funcionamiento de la aplicación pública se apoya en esta revisión manual. No existe una prueba automatizada contra el despliegue: pytest prueba el código del repositorio en local.
- En esta revisión no se ejecutó el notebook ni se reentrenó el modelo.

## Ejecución del notebook
- 9 de noviembre: se ejecutaron todas las celdas de código sin excepciones (`docs/RESULTADOS_VERIFICADOS.md`).
- 10 de noviembre: se ejecutó una copia aislada; sus salidas están en `resultados/reproduccion/notebook_reejecutado_con_salidas.ipynb`.
- La versión actual de `notebooks/` ajusta las rutas a `data/` y `models/` y aclara el texto de la sección "Techo teórico de la simulación". Esa versión no se ha ejecutado completa.

## Reproducción científica del entrenamiento
- 10 de noviembre: la copia aislada regeneró un dataset y un modelo idénticos byte a byte a los entregados (`resultados/reproduccion/REPRODUCCION.md`).
- No se repitió después de la reorganización. Los hashes SHA-256 actuales de `data/dataset_credit_score_colombia.csv` y `models/modelo_credito.joblib` coinciden con los registrados, lo que confirma que los archivos no cambiaron, no que el entrenamiento se haya reproducido de nuevo.

## Otras verificaciones
- Matriz de confusión: recalculada sobre test estratificado, semilla 42.
- Importancia por permutación: recalculada sobre test, 5 repeticiones (el notebook original configura 10; las cifras pueden variar). La versión con 10 repeticiones está en `resultados/reproduccion/importancia_permutacion_10rep.csv`.
- Inferencia del modelo serializado: verificada en ejecución previa.
- Informe: versión definitiva del 11 de noviembre en `reports/INFORME_FINAL_ML2.pdf`, de 5 páginas. Su sección 8 distingue las 27 pruebas automatizadas de la verificación manual en Streamlit Community Cloud e incluye el enlace público. Contiene los nombres de Nicolás Barrera y Angie Loango, resumen integrado, gráficas, referencias externas y declaración de uso de IA. Sus cifras coinciden con `resultados/reproduccion/evaluacion_final.json`, `resultados/reproduccion/validacion_anidada.csv`, `resultados/reproduccion/ajuste_hiperparametros.csv` y `resultados/interpretabilidad_importancias.csv`.
- Dependencia parcial: interpretada en la página 4 del informe (apartado "Interpretabilidad y producto").
- Sustentación oral: pendiente.
