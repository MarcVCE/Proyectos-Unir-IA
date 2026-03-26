# Comparación de Métodos de Codificación de Variables Categóricas

Dataset: **Adult Census Income (UCI)** — 32561 registros · 9 variables categóricas

---

## 1. `pd.get_dummies` (pandas)

### Descripción
Convierte cada categoría de una variable en una columna binaria (0/1) directamente desde un DataFrame de pandas. No requiere instanciar ningún objeto.

### Ventajas
- Sintaxis muy concisa — una sola línea transforma todas las variables.
- No requiere `fit` / `transform` — ideal para exploración rápida.
- Integrado en pandas, sin dependencias adicionales.
- `drop_first=True` elimina la primera categoría de cada variable para evitar multicolinealidad.

### Desventajas
- **No reutilizable en producción**: no guarda el estado del encoding. Si llegan nuevos datos con categorías distintas, el resultado puede diferir.
- No maneja categorías desconocidas en nuevos datos.
- No se integra directamente en un `Pipeline` de scikit-learn.

### Aplicación en este dataset
```python
df_dummies = pd.get_dummies(df, columns=cols_cat, drop_first=True, dtype=int)
```
Variables como `workclass` (9 categorías) generan 8 columnas binarias (`workclass_Local-gov`, `workclass_Private`, etc.), eliminando la primera como referencia.

---

## 2. `OneHotEncoder` (scikit-learn)

### Descripción
Equivalente a `get_dummies` pero implementado como objeto scikit-learn, lo que lo hace serializable y compatible con `Pipeline` y `ColumnTransformer`.

### Ventajas
- **Serializable**: se puede guardar con `joblib` y reutilizar exactamente en producción.
- Maneja categorías desconocidas en nuevos datos con `handle_unknown='ignore'`.
- Integrable en `Pipeline` de scikit-learn — el fit solo se realiza sobre datos de entrenamiento, evitando data leakage.
- `get_feature_names_out()` devuelve los nombres de las columnas generadas.

### Desventajas
- Más verboso que `get_dummies`.
- Requiere instanciar y llamar a `fit_transform`.
- El parámetro `sparse_output=False` (o `sparse=False` en versiones antiguas) es necesario para obtener un array denso.

### Aplicación en este dataset
```python
ohe = OneHotEncoder(drop="first", sparse_output=False, dtype=int)
X_cat_ohe = ohe.fit_transform(df[cols_cat])
```
Produce el mismo número de columnas que `get_dummies` con `drop_first=True`, pero el objeto `ohe` puede serializarse y aplicarse a nuevos datos con `ohe.transform(nuevos_datos)`.

---

## 3. `LabelEncoder` (scikit-learn)

### Descripción
Asigna un entero a cada categoría de forma ordinal (0, 1, 2, ...). No expande la dimensionalidad del dataset.

### Ventajas
- Mantiene el mismo número de columnas — no añade dimensionalidad.
- Útil para la **variable objetivo** (`income`: `<=50K` → 0, `>50K` → 1).
- Sencillo de aplicar y de interpretar.

### Desventajas
- **Introduce un orden artificial** entre categorías nominales: al asignar `Private=4`, `State-gov=6`, `Self-emp=5`, el modelo infiere que `State-gov > Self-emp > Private`, lo cual es incorrecto para variables sin orden natural.
- Este sesgo afecta especialmente a modelos lineales (regresión logística, SVM) y puede deteriorar su rendimiento.
- No adecuado para features nominales — solo para variables ordinales o para la variable objetivo.

### Aplicación en este dataset
```python
le = LabelEncoder()
df["income"] = le.fit_transform(df["income"])  # <=50K → 0, >50K → 1
```
Para las features categóricas nominales (`workclass`, `education`, etc.) se debe usar `get_dummies` u `OneHotEncoder` en su lugar.

---

## 4. Comparación resumida

| Criterio | `get_dummies` | `OneHotEncoder` | `LabelEncoder` |
|----------|--------------|-----------------|----------------|
| Dimensionalidad | Aumenta | Aumenta | Igual |
| Multicolinealidad | Evitable (`drop_first`) | Evitable (`drop='first'`) | No aplica |
| Reutilizable en producción | ❌ No | ✅ Sí | ✅ Sí |
| Integrable en Pipeline | ❌ No | ✅ Sí | ✅ Sí |
| Categorías desconocidas | ❌ No maneja | ✅ `handle_unknown` | ❌ Error |
| Orden artificial | No | No | ⚠️ Sí |
| Uso recomendado | Exploración / notebooks | Producción / train-test | Variable objetivo / ordinales |

---

## 5. Recomendación para este dataset

Para el dataset Adult Census Income, la estrategia óptima combina los tres:

1. **`OneHotEncoder`** dentro de un `ColumnTransformer` para las 8 features categóricas nominales (`workclass`, `education`, `marital_status`, `occupation`, `relationship`, `race`, `sex`, `native_country`).
2. **`LabelEncoder`** para codificar la variable objetivo `income` como 0/1.
3. **`get_dummies`** para exploración rápida y visualización en el notebook.

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler

# Variable objetivo
y = LabelEncoder().fit_transform(df["income"])

# Features
preprocessor = ColumnTransformer([
    ("ohe", OneHotEncoder(drop="first", handle_unknown="ignore"), cols_cat_features),
    ("num", StandardScaler(), cols_num)
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    # ("model", LogisticRegression())  # añadir modelo aquí
])
```
