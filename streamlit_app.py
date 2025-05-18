import matplotlib.pyplot as plt
import seaborn as sns ### se cambio por px
import pandas as pd
import numpy as np ## no se utiliza
import plotly.express as px ### nueva libreria
import streamlit as st

# Configuración de página
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data/data.csv") ### Cambie dirección
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

# Evolución de las Ventas Totales
st.subheader("1. Evolución de las Ventas Totales")
st.markdown( "Se muestra la evolución diaria del total de ventas dentro del período"
            " y filtros seleccionados. Permite identificar tendencias, patrones estacionales o"
            " comportamientos atípicos en las ventas a lo largo del tiempo.")


ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()

fig = px.line(ventas_diarias,
    x="Date", y="Total",
    title="Ventas Totales por Fecha",
    labels={"Date": "Fecha", "Total": "Total de Ventas ($)"})

fig.update_layout(xaxis_title="Fecha",
    yaxis_title="Total de Ventas ($)",
    template="plotly_white",
    title_x=0.5)  # Centrar título)

st.plotly_chart(fig, use_container_width=True)

# Ingresos por Línea de Producto

st.subheader("2. Ingresos por Línea de Producto")
st.markdown("Los siguientes gráficos presentan el total de ingresos generados por cada línea de producto,"
            " así como la distribución de preferencias según género, considerando el período y filtros aplicados. Esta información permite"
            " identificar las categorías más rentables y comprender el perfil de los consumidores, facilitando la toma de decisiones"
            " estratégicas en comercialización e inventario")

ventas_productos = df_filtered.groupby("Product line")["Total"].sum().sort_values()
ventas_productos_df = ventas_productos.reset_index()

data_genero = df_filtered.groupby(["Product line", "Gender"]).size().reset_index(name="Cantidad")
col1, col2 = st.columns([1, 1])

# columna izquierda
with col1:
    fig_ingresos = px.bar(ventas_productos_df, x="Total", y="Product line",
        orientation="h",
        title="Ingresos por Línea de Producto",
        labels={"Total": "Total de Ventas ($)", "Product line": "Línea de Producto"},
        color_discrete_sequence=["darkblue"],
        opacity=0.5 )

    fig_ingresos.update_layout( width=600, height=400,
        template="plotly_white",
        xaxis_title="Total de Ventas ($)",
        yaxis_title="Línea de Producto",
        title_x=0.0 )


    st.plotly_chart(fig_ingresos, use_container_width=True)

# columna derecha
with col2:
    fig_genero = px.bar(
        data_genero,
        x='Cantidad',
        y='Product line',
        color='Gender',
        orientation='h',
        title='Preferencia de Productos por Género',
        color_discrete_map={'Male': '#66c2a5', 'Female': 'pink'},
        labels={'Cantidad': 'Cantidad de Usuarios', 'Product line': 'Línea de Producto'}    )

    fig_genero.update_layout(
        xaxis_title='Cantidad de Usuarios',
        yaxis_title='Línea de Producto',
        title_x=0.0,
        height=400 )

    fig.update_layout(template="plotly_white", title_x=0.1)

    st.plotly_chart(fig_genero, use_container_width=True)

# Comparación del Gasto por Tipo de Cliente
st.subheader("3. Comparación del Gasto por Tipo de Cliente")
st.markdown("En el gráfico de cajas se compara la distribución del gasto total entre clientes tipo Member y Normal."
            " Permite observar la mediana, el rango intercuartílico y la presencia de valores atípicos, lo que"
            " ayuda a identificar diferencias en los patrones de compra según el tipo de cliente.")

fig = px.box( df_filtered, x="Customer type",  y="Total",
    title="Gasto Total por Tipo de Cliente",
    labels={ "Customer type": "Tipo de Cliente",
        "Total": "Total ($)" },
    color="Customer type",
    color_discrete_sequence=["#1f77b4", "#ff7f0e"])

fig.update_layout(template="plotly_white", title_x=0.5)

st.plotly_chart(fig, use_container_width=True)

# Métodos de Pago Preferidos
st.subheader("4. Métodos de Pago Preferidos")
st.markdown("La visualización presenta la proporción relativa de los distintos métodos de pago utilizados por los clientes,"
    " lo que permite identificar tendencias de uso y preferencias según el período analizado y los criterios seleccionados.")

col1, col2, col3 = st.columns([1, 2, 1]) ## no encontre otra forma de centrar

with col2:
    pagos = df_filtered["Payment"].value_counts().reset_index()
    pagos.columns = ["Método de Pago", "Cantidad"]

    fig = px.pie(pagos,
        names="Método de Pago",values="Cantidad",title="Métodos de Pago Preferidos",
        hole=0,opacity=0.9)

    fig.update_traces(textinfo="percent+label")

    fig.update_layout(template="plotly_white", width=500,height=500,title_x=0.0 ) # Centrado del título dentro del gráfico

    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Streamlit Dashboard - Grupo 22 - Andrés Hernández Morales, Javier Vera Maldonado")
