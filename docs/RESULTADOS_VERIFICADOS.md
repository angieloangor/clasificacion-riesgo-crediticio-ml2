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

## Estado del cierre académico (11 de noviembre de 2026)

1. Hallazgos específicos sobre matriz de confusión, importancias y dependencia parcial: redactados en el informe final (`reports/INFORME_FINAL_ML2.pdf`, secciones 5 a 7).
2. Informe final: 5 páginas, centrado en explicar y justificar la metodología propia. No incluye una comparación cuantitativa con el artículo de referencia, porque no es un requisito y sus métricas no son comparables (otra población y etiquetas observadas).
3. Interfaz Streamlit: el 10 de noviembre el equipo probó manualmente Inicio, Simulador y Resultado en macOS con `localhost:8501` (`docs/PRUEBAS_APLICACION.txt`, sección 4). El 11 de noviembre verificó manualmente las ocho secciones en la aplicación pública de Streamlit Community Cloud (sección 5). Las pruebas automatizadas se registran por separado (secciones 1, 3 y 6).
4. Pendiente: sustentación oral y demostración funcional.
