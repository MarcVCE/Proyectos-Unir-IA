import pandas as pd

# Paso 1: Crear un DataFrame a partir de la lista de ventas
ventas = [
    {"Producto": "Laptop", "Categoría": "Electrónica", "Unidades": 5, "Precio_unitario": 800},
    {"Producto": "Smartphone", "Categoría": "Electrónica", "Unidades": 10, "Precio_unitario": 600},
    {"Producto": "Impresora", "Categoría": "Oficina", "Unidades": 7, "Precio_unitario": 150},
    {"Producto": "Monitor", "Categoría": "Electrónica", "Unidades": 3, "Precio_unitario": 200},
    {"Producto": "Teclado", "Categoría": "Oficina", "Unidades": 15, "Precio_unitario": 25},
    {"Producto": "Smartphone", "Categoría": "Electrónica", "Unidades": 4, "Precio_unitario": 600},
    {"Producto": "Laptop", "Categoría": "Electrónica", "Unidades": 2, "Precio_unitario": 800},
    {"Producto": "Teclado", "Categoría": "Oficina", "Unidades": 10, "Precio_unitario": 25}
]

df = pd.DataFrame(ventas)

# Paso 2: Exploración básica
# Mostrar las primeras 5 filas y las últimas 5 filas
head = df.head()
tail = df.tail()

# Obtener un resumen estadístico de las ventas
resumen = df.describe()

# Mostrar la cantidad de productos vendidos por categoría
cantidad_por_categoria = df['Categoría'].value_counts()

# Usar el método info para mostrar la estructura del DataFrame
info = df.info()

# Paso 3: Modificación del DataFrame
# Crear una nueva columna "Total" que almacene el total por producto
df['Total'] = df['Unidades'] * df['Precio_unitario']

# Aplicar un descuento del 10% a los productos de la categoría "Oficina"
df.loc[df['Categoría'] == 'Oficina', 'Precio_unitario'] *= 0.9

# Paso 4: Selección de datos
# Seleccionar los productos de la categoría "Electrónica" con más de 5 unidades vendidas
productos_electronica = df.loc[(df['Categoría'] == 'Electrónica') & (df['Unidades'] > 5)]

# Mostrar resultados
print("Head del DataFrame:")
print(head)
print("\nTail del DataFrame:")
print(tail)
print("\nResumen estadístico del DataFrame:")
print(resumen)
print("\nCantidad de productos por categoría:")
print(cantidad_por_categoria)
print("\nInformación del DataFrame:")
print(info)
print("\nDataFrame modificado:")
print(df)
print("\nProductos de 'Electrónica' con más de 5 unidades vendidas:")
print(productos_electronica)