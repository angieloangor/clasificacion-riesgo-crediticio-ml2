# Resultados verificados — ejecución del 9 de noviembre de 2026

Se ejecutaron todas las celdas de código del notebook en orden en un entorno local, con semilla 42. Se corrigió la importación de NumPy, que estaba comentada. La ejecución terminó sin excepciones.

- Dataset: 5.000 filas y 25 columnas, sin valores faltantes ni duplicados.
- Ponderación única: FICO adaptado a Colombia; suma de pesos absolutos = 1.
- Modelo seleccionado por la regla implementada: **Logistic Regression**, C=0.001.
- Accuracy de prueba: **0.452**.
- Precision macro: **0.454**.
- Recall macro: **0.453**.
- F1 macro de prueba: **0.453** (valor sin redondear reportado: 0.4526).
- Intervalo bootstrap 95 % de F1 macro: **[0.422, 0.486]**.
- Se generaron los artefactos de inferencia en `artefactos/` (ubicación en esa fecha; actualmente están en `models/`).
- Se verificó la carga del Pipeline y una predicción sobre un registro sintético.
- En esa fecha se comprobó sintácticamente `app.py`, sin verificar la interfaz en navegador. La prueba en navegador se registró después, el 10 de noviembre, en `docs/PRUEBAS_APLICACION.txt`.

## Interpretación y precauciones

El desempeño es moderado y no permite uso en decisiones de crédito reales. El objetivo es sintético y probabilístico; las métricas reflejan capacidad de reproducir etiquetas simuladas, no morosidad observada. Los coeficientes de la función softmax y el reparto 6 % / 4 % son supuestos del equipo, no estimaciones oficiales. La validez externa sigue sin comprobarse.

El F1 macro de 0.481 pertenece a la segunda entrega, conservada en la rama `main` de GitHub (commit `c783e85`). Esa entrega usó otra ponderación de la etiqueta y su dataset difiere del actual en 502 de las 5.000 etiquetas, por lo que esa cifra no es comparable con el 0.4526 de esta versión.

## Pendiente para cierre académico

1. Revisar manualmente las gráficas, matriz de confusión y explicaciones para redactar hallazgos específicos.
2. Completar el informe técnico final con comparación cuantitativa frente al artículo y citas comprobadas.
3. Prueba de la interfaz Streamlit en macOS: realizada manualmente por el equipo el 10 de noviembre, con Google Chrome y Streamlit en `localhost:8501`. Se verificaron las páginas Inicio, Simulador y Resultado (`docs/ESTADO_VERIFICACION.md` y `docs/PRUEBAS_APLICACION.txt`, sección 4). Las otras cinco páginas no formaron parte de esa prueba manual en macOS; su evidencia en navegador es la prueba del 10 de noviembre en Linux con Chromium (`docs/PRUEBAS_APLICACION.txt`, sección 2, y `docs/capturas/`). La prueba manual en macOS ocurrió antes de la última reorganización, que movió `interpretabilidad_importancias.csv` y `matriz_confusion_final.csv` a `resultados/`.
4. Preparar la sustentación oral y una demostración funcional.
