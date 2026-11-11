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
- Se generaron los artefactos de inferencia en `artefactos/`.
- Se verificó la carga del Pipeline y una predicción sobre un registro sintético.
- Se comprobó sintácticamente `app.py`, pero **no se ha verificado la interfaz en navegador**.

## Interpretación y precauciones

El desempeño es moderado y no permite uso en decisiones de crédito reales. El objetivo es sintético y probabilístico; las métricas reflejan capacidad de reproducir etiquetas simuladas, no morosidad observada. Los coeficientes de la función softmax y el reparto 6 % / 4 % son supuestos del equipo, no estimaciones oficiales. La validez externa sigue sin comprobarse.

## Pendiente para cierre académico

1. Revisar manualmente las gráficas, matriz de confusión y explicaciones para redactar hallazgos específicos.
2. Completar el informe técnico final con comparación cuantitativa frente al artículo y citas comprobadas.
3. Abrir y probar la interfaz Streamlit en navegador y registrar evidencia.
4. Preparar la sustentación oral y una demostración funcional.
