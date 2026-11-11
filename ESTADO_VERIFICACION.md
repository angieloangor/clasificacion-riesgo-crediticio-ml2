# Verificación de cierre

Estado al 10 de noviembre de 2026, después de reorganizar el proyecto en `data/`, `models/`, `notebooks/` y `reports/`. Cada tipo de verificación es independiente: completar uno no implica haber completado los demás.

## Pruebas automatizadas (pytest)
- Última ejecución en macOS, después de la reorganización: 27 pruebas aprobadas (ver `PRUEBAS_APLICACION.txt`).
- Comprueban el software y la coherencia de los artefactos existentes. No ejecutan el notebook ni reentrenan el modelo.

## Pruebas de la aplicación en navegador
- 10 de noviembre, Linux con Chromium: las 8 páginas cargaron sin excepciones y se probaron los flujos principales (`PRUEBAS_APLICACION.txt`, `docs/capturas/`).
- No se han repetido después de la reorganización ni consta una prueba en el computador de entrega (macOS).
- Una revisión anterior solo había llegado a revisión de código y compilación sintáctica, porque no se pudo instalar Streamlit en ese entorno.

## Ejecución del notebook
- 9 de noviembre: se ejecutaron todas las celdas de código sin excepciones (`RESULTADOS_VERIFICADOS.md`).
- 10 de noviembre: se ejecutó una copia aislada; sus salidas están en `resultados/reproduccion/notebook_reejecutado_con_salidas.ipynb`.
- La versión actual de `notebooks/` ajusta las rutas a `data/` y `models/` y aclara el texto de la sección "Techo teórico de la simulación". Esa versión no se ha ejecutado completa.

## Reproducción científica del entrenamiento
- 10 de noviembre: la copia aislada regeneró un dataset y un modelo idénticos byte a byte a los entregados (`resultados/reproduccion/REPRODUCCION.md`).
- No se repitió después de la reorganización. Los hashes SHA-256 actuales de `data/dataset_credit_score_colombia.csv` y `models/modelo_credito.joblib` coinciden con los registrados, lo que confirma que los archivos no cambiaron, no que el entrenamiento se haya reproducido de nuevo.

## Otras verificaciones
- Matriz de confusión: recalculada sobre test estratificado, semilla 42.
- Importancia por permutación: recalculada sobre test, 5 repeticiones (el notebook original configura 10; las cifras pueden variar). La versión con 10 repeticiones está en `resultados/reproduccion/importancia_permutacion_10rep.csv`.
- Inferencia del modelo serializado: verificada en ejecución previa.
- Informe: redactado, 4 páginas en `reports/INFORME_FINAL_ML2.pdf`; confirmar bibliografía.
- Dependencia parcial: interpretada en la sección 6 del informe.
- Sustentación oral: pendiente.
