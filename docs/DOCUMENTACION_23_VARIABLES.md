# Documentación de las 23 variables predictoras

El CSV contiene 25 columnas: 23 predictores, una columna derivada `Antiguedad_Laboral_Años` que se excluye para evitar duplicidad y la etiqueta `Credit_Score`. El notebook excluye explícitamente las dos últimas al formar `X`.

**Peso cero no significa que la variable no sea usada por el modelo:** significa que no tiene coeficiente explícito en el mecanismo de generación de la etiqueta. Las 23 entran en el Pipeline y sus coeficientes se aprenden durante el entrenamiento.

| Predictor | Grupo | Criterio de inclusión/dirección | Peso en etiqueta |
|---|---|---|---|
| Edad | Sociodemográfica | No se usa para generar la etiqueta; posible sesgo | 0 % |
| Tipo_Ocupacion | Laboral | Contexto del perfil; no tiene peso directo | 0 % |
| Formalidad_Laboral | Laboral | Contexto del perfil; no tiene peso directo | 0 % |
| Antiguedad_Laboral_Meses | Laboral | Se conserva como predictor, no entra al índice | 0 % |
| Ingreso_Mensual | Capacidad de pago | Variable contextual, relacionada con deuda/ingreso | 0 % |
| Variabilidad_Ingreso | Estabilidad económica | Mayor variación: mayor riesgo supuesto | 6 % |
| Tipo_Cotizante | Laboral | Contexto de cotización; no entra al índice | 0 % |
| Meses_Cotizados_12M | Estabilidad laboral | Se transforma en meses sin cotización; mayor ausencia: mayor riesgo | 4 % |
| IBC_Aproximado | Capacidad de pago | Contexto del perfil; no entra al índice | 0 % |
| Antiguedad_Crediticia_Meses | Historial crediticio | Mayor duración: menor riesgo supuesto | 15 % (protector) |
| Numero_Productos_Financieros | Crédito | Contexto; sin ponderación directa | 0 % |
| Numero_Prestamos | Crédito | Contexto; sin ponderación directa | 0 % |
| Tiene_Tarjeta_Credito | Crédito | Contexto; sin ponderación directa | 0 % |
| Limite_Tarjeta | Crédito | Se relaciona con utilización; evitar doble conteo | 0 % |
| Saldo_Tarjeta | Crédito | Se relaciona con utilización; evitar doble conteo | 0 % |
| Utilizacion_Credito | Endeudamiento | Mayor utilización: mayor riesgo supuesto | 15 % |
| Deuda_Pendiente | Endeudamiento | Relacionada con ratio deuda/ingreso; evitar doble conteo | 0 % |
| Ratio_Deuda_Ingreso | Endeudamiento | Mayor proporción: mayor riesgo supuesto | 15 % |
| Comportamiento_Pago_Tarjeta | Historial de pagos | Comportamiento desfavorable: mayor riesgo supuesto | 11,67 % |
| Monto_Pagado_Tarjeta | Pagos | Relacionado con comportamiento de pago; sin peso adicional | 0 % |
| Numero_Retrasos_12M | Historial de pagos | Más atrasos: mayor riesgo supuesto | 11,67 % |
| Dias_Mora_Promedio | Historial de pagos | Mora más prolongada: mayor riesgo supuesto | 11,67 % |
| Consultas_Credito_6M | Crédito nuevo | Más consultas: mayor riesgo supuesto, con cautela | 10 % |

**Fundamento y cautelas:** FICO publica porcentajes por grupos para su sistema general, no pesos colombianos individuales. La división interna 35/3, 30/2 y el reparto 6/4 son decisiones del equipo. Las relaciones de mora, utilización y antigüedad son hipótesis de simulación respaldadas conceptualmente por los factores FICO; su tamaño exacto no está validado empíricamente. La pertinencia del contexto colombiano se discute a partir de Gutiérrez-Rueda, Estrada y Capera (2011), sin atribuirles pesos. No usar este prototipo para decisiones reales.

Referencias: https://www.myfico.com/credit-education/whats-in-your-credit-score ; https://doi.org/10.32468/tef.61
