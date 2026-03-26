# Comparación de Métodos de Codificación

## get_dummies de pandas
- **Ventajas:**
  - Fácil de implementar.
  - Directamente integrable con pandas DataFrame.
- **Desventajas:**
  - Puede generar muchas columnas si hay muchas categorías.

## OneHotEncoder de scikit-learn
- **Ventajas:**
  - Más flexible con parámetros como `sparse`.
  - Integrable con pipelines de scikit-learn.
- **Desventajas:**
  - Requiere manejo adicional para convertir a DataFrame.

## LabelEncoder de scikit-learn
- **Ventajas:**
  - Simple y rápido.
- **Desventajas:**
  - Asigna un valor ordinal que puede no tener sentido en el contexto, introduciendo sesgos.
