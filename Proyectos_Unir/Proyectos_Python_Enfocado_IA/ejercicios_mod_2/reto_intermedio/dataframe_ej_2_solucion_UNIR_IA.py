import pandas as pd

# Paso 1: Crear el DataFrame a partir de la lista de diccionarios
data = [
    {"nombre": "Juan", "edad": 25, "ciudad": "Madrid", "ingresos": 3000},
    {"nombre": "Ana", "edad": None, "ciudad": None, "ingresos": 2500},
    {"nombre": "Pedro", "edad": 30, "ciudad": "Barcelona", "ingresos": None},
    {"nombre": None, "edad": None, "ciudad": "Valencia", "ingresos": None},
    {"nombre": "Luisa", "edad": 35, "ciudad": "Madrid", "ingresos": None}
]

df = pd.DataFrame(data)

# Paso 2: Identificar cuántos valores faltantes (NaN) hay por columna usando .sum()
valores_faltantes = df.isna().sum()
print("Valores faltantes por columna:")
print(valores_faltantes)

# Paso 3: Rellenar los valores faltantes en columnas numéricas con la media
df['edad'] = df['edad'].fillna(df['edad'].mean())
df['ingresos'] = df['ingresos'].fillna(df['ingresos'].mean())

# Paso 4: Rellenar los valores faltantes en columnas categóricas con la moda
df['ciudad'] = df['ciudad'].fillna(df['ciudad'].mode()[0])
df['nombre'] = df['nombre'].fillna(df['nombre'].mode()[0])

print("\nDataFrame después de rellenar los valores faltantes:")
print(df)

# Paso 5: Convertir la columna 'ciudad' a variable categórica
df['ciudad'] = df['ciudad'].astype('category')

# Paso 6: Agregar una nueva fila con la ciudad 'Sevilla'
new_row = pd.DataFrame([{"nombre": "Nuevo", "edad": 40, "ciudad": "Sevilla", "ingresos": 4000}])
df = pd.concat([df, new_row], ignore_index=True)

# Paso 7: Volver a convertir la columna 'ciudad' a categoría
df['ciudad'] = df['ciudad'].astype('category')

# Paso 8: Verificar las categorías actuales
print("\nCategorías actuales en 'ciudad':")
print(df['ciudad'].cat.categories)

# Paso 9: Establecer las categorías exactas y reordenarlas
df['ciudad'] = df['ciudad'].cat.set_categories(['Madrid', 'Barcelona', 'Valencia', 'Sevilla'])
df['ciudad'] = df['ciudad'].cat.reorder_categories(['Madrid', 'Barcelona', 'Valencia', 'Sevilla'])

print("\nCategorías después de reordenar:")
print(df['ciudad'].cat.categories)

# Paso 10: Crear un segundo DataFrame
data_extra = [
    {"nombre": "Juan", "profesion": "Ingeniero"},
    {"nombre": "Ana", "profesion": "Médico"},
    {"nombre": "Pedro", "profesion": "Abogado"},
    {"nombre": "Luisa", "profesion": "Diseñadora"},
    {"nombre": "Nuevo", "profesion": "Artista"}
]

df_extra = pd.DataFrame(data_extra)

# Paso 11: Realizar merge especificando los parámetros (usar many_to_one)
df_final = df.merge(df_extra, on="nombre", how="inner", validate="many_to_one")

print("\nDataFrame final después del merge:")
print(df_final)