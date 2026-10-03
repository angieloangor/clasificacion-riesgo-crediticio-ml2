# Clasificación de riesgo crediticio con Machine Learning

Proyecto de Machine Learning II enfocado en la clasificación del riesgo crediticio en tres categorías: Good, Standard y Poor.

## Contenido del repositorio

- `ProyectoML2_SegundaEntrega.ipynb`: notebook principal con simulación, EDA, modelamiento y validación.
- `ProyectoML2_SegundaEntrega_Informe.pdf`: informe de la segunda entrega.
- `dataset_credit_score_colombia.csv`: dataset sintético utilizado.
- `dataset_credit_score_colombia.xlsx`: versión en Excel del dataset.
- `requirements.txt`: versiones de las librerías utilizadas.

## Modelos evaluados

- Decision Tree
- Regresión logística
- SVM
- Random Forest
- LightGBM
- Gradient Boosting
- AdaBoost
- XGBoost
- Naive Bayes

También se utiliza un `DummyClassifier` como línea base.

## Resultado principal

La Regresión logística fue seleccionada como modelo final después de validación cruzada y validación anidada.

El modelo final obtuvo un F1 macro aproximado de 0,481 sobre el conjunto de prueba.

## Autores

- Nicolás Barrera
- Angie Loango
