import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('data/data.csv')
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filtros")

date_min = df["Date"].min().date()
date_max = df["Date"].max().date()
date_range = st.sidebar.slider("Rango de Fechas", min_value=date_min, max_value=date_max, value=(date_min, date_max))

city = st.sidebar.multiselect("Ciudad", options=df["City"].unique(), default=df["City"].unique())
branch = st.sidebar.multiselect("Sucursal", options=df["Branch"].unique(), default=df["Branch"].unique())
customer_type = st.sidebar.multiselect("Tipo de Cliente", options=df["Customer type"].unique(), default=df["Customer type"].unique())
gender = st.sidebar.multiselect("Género", options=df["Gender"].unique(), default=df["Gender"].unique())

# Filtro
df_filtered = df[
    (df["City"].isin(city)) &
    (df["Branch"].isin(branch)) &
    (df["Customer type"].isin(customer_type)) &
    (df["Gender"].isin(gender)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

st.title("📊 Dashboard de Ventas - Visión Ejecutiva")

# Métricas clave
st.subheader("Métricas Generales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Ventas", f"${df_filtered['Total'].sum():,.2f}")
col2.metric("Clientes Únicos", df_filtered["Invoice ID"].nunique())
col3.metric("Ingreso Bruto", f"${df_filtered['gross income'].sum():,.2f}")
col4.metric("Rating Promedio", f"{df_filtered['Rating'].mean():.2f} ⭐")

# 1. Evolución de las Ventas Totales
st.subheader("1. Evolución de las Ventas Totales")
ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(data=ventas_diarias, x="Date", y="Total", ax=ax)
ax.set_ylabel("Total ($)")
ax.set_xlabel("Fecha")
ax.set_title("Ventas Totales por Fecha")
st.pyplot(fig)

# 2. Ingresos por Línea de Producto
st.subheader("2. Ingresos por Línea de Producto")
ventas_productos = df_filtered.groupby("Product line")["Total"].sum().sort_values()
fig, ax = plt.subplots(figsize=(10, 4))
ventas_productos.plot(kind="barh", ax=ax, color="skyblue")
ax.set_xlabel("Total ($)")
ax.set_title("Total de Ventas por Línea de Producto")
st.pyplot(fig)

# 3. Comparación del Gasto por Tipo de Cliente
st.subheader("3. Comparación del Gasto por Tipo de Cliente")
fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df_filtered, x="Customer type", y="Total", ax=ax)
ax.set_title("Gasto Total por Tipo de Cliente")
st.pyplot(fig)

# 4. Métodos de Pago Preferidos
st.subheader("4. Métodos de Pago Preferidos")
pagos = df_filtered["Payment"].value_counts()
fig, ax = plt.subplots()
ax.pie(pagos, labels=pagos.index, autopct='%1.1f%%', startangle=90)
ax.set_title("Distribución de Métodos de Pago")
st.pyplot(fig)

# Footer
st.markdown("---")
st.caption("Streamlit Dashboard - Grupo 22 - Andrés Hernández Morales, Javier Vera Maldonado")
