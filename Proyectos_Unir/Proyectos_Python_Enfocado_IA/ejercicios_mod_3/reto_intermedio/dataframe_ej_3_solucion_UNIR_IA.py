import pandas as pd
import matplotlib.pyplot as plt

# 1. Crear el DataFrame
data = [
    {"semana": "2023-01-01", "unidades_vendidas": 100, "precio": 8, "publicidad_1": 5, "oferta_1": None},
    {"semana": "2023-01-08", "unidades_vendidas": 200, "precio": 15, "publicidad_1": 8, "oferta_1": 2},
    {"semana": "2023-01-15", "unidades_vendidas": 950, "precio": 11, "publicidad_1": 6, "oferta_1": 3},
    {"semana": "2023-01-22", "unidades_vendidas": 150, "precio": 10, "publicidad_1": 7, "oferta_1": 1},
    {"semana": "2023-01-29", "unidades_vendidas": 1100, "precio": 20, "publicidad_1": 9, "oferta_1": None},
    {"semana": "2023-02-05", "unidades_vendidas": 120, "precio": 12, "publicidad_1": 5, "oferta_1": 2},
    {"semana": "2023-02-12", "unidades_vendidas": 250, "precio": 9, "publicidad_1": 8, "oferta_1": 1},
    {"semana": "2023-02-19", "unidades_vendidas": 300, "precio": 14, "publicidad_1": 7, "oferta_1": None},
    {"semana": "2023-02-26", "unidades_vendidas": 400, "precio": 17, "publicidad_1": 9, "oferta_1": 3},
    {"semana": "2023-03-05", "unidades_vendidas": 150, "precio": 13, "publicidad_1": 5, "oferta_1": 2},
    {"semana": "2023-03-12", "unidades_vendidas": 100, "precio": 10, "publicidad_1": 6, "oferta_1": None},
    {"semana": "2023-03-19", "unidades_vendidas": 500, "precio": 18, "publicidad_1": 10, "oferta_1": 4},
    {"semana": "2023-03-26", "unidades_vendidas": 180, "precio": 16, "publicidad_1": 8, "oferta_1": 2},
    {"semana": "2023-04-02", "unidades_vendidas": 170, "precio": 12, "publicidad_1": 7, "oferta_1": 1},
    {"semana": "2023-04-09", "unidades_vendidas": 1000, "precio": 22, "publicidad_1": 9, "oferta_1": None},
    {"semana": "2023-04-16", "unidades_vendidas": 210, "precio": 11, "publicidad_1": 5, "oferta_1": 3},
    {"semana": "2023-04-23", "unidades_vendidas": 230, "precio": 14, "publicidad_1": 8, "oferta_1": 2},
    {"semana": "2023-04-30", "unidades_vendidas": 190, "precio": 15, "publicidad_1": 6, "oferta_1": 1},
    {"semana": "2023-05-07", "unidades_vendidas": 300, "precio": 16, "publicidad_1": 9, "oferta_1": 4},
    {"semana": "2023-05-14", "unidades_vendidas": 250, "precio": 10, "publicidad_1": 7, "oferta_1": None},
    {"semana": "2023-05-21", "unidades_vendidas": 400, "precio": 17, "publicidad_1": 10, "oferta_1": 3},
    {"semana": "2023-05-28", "unidades_vendidas": 980, "precio": 23, "publicidad_1": 9, "oferta_1": None},
    {"semana": "2023-06-04", "unidades_vendidas": 150, "precio": 12, "publicidad_1": 5, "oferta_1": 2},
    {"semana": "2023-06-11", "unidades_vendidas": 170, "precio": 9, "publicidad_1": 6, "oferta_1": None}
]

df = pd.DataFrame(data)

# Asegurar que la columna de fechas esté en formato datetime
df['semana'] = pd.to_datetime(df['semana'])

# 2. Análisis de valores nulos
print("Valores nulos por columna:")
print(df.isna().sum())

#  Rellenar valores nulos con 'ffill' (forward fill) y luego 'bfill' (backward fill)
df.ffill(inplace=True)  # Rellenar hacia adelante
df.bfill(inplace=True)  # Rellenar hacia atrás los valores que quedaron nulos

print("\nDataFrame después de rellenar valores nulos:")
print(df)

# 3. Detección visual de outliers
# Box plot para detectar visualmente los outliers
df['unidades_vendidas'].plot.box()
plt.title('Box Plot de Unidades Vendidas')
plt.grid(True)
plt.show()

# 4. Cálculo de la correlación de Pearson entre las variables
correlation_matrix = df[['unidades_vendidas', 'precio', 'publicidad_1']].corr()

print("\nMatriz de correlación de Pearson:")
print(correlation_matrix)

# 5. Gráfico de dispersión (scatterplot) entre 'precio' y 'unidades_vendidas' usando el método plot de pandas
df.plot(x="precio", y="unidades_vendidas", kind="scatter", c="steelblue", title="Relación entre Precio y Unidades Vendidas")
plt.grid(True)  # Añadir cuadrícula al gráfico
plt.show()