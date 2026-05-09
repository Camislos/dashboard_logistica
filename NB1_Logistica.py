
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Logística", layout="wide")

# --- ESTILO PERSONALIZADO (BASADO EN IMAGEN 1/3) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: white; }
    [data-testid="stMetricValue"] { color: #00D4FF; font-size: 36px; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #808495; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO (LECTURA EN Z) ---
st.title("📊 Dashboard de Operaciones Logísticas")
st.markdown("### Visualización de KPIs y Flujos de Distribución")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    return pd.read_csv('datos_logistica.csv')

df = load_data()

# --- FILAS SUPERIORES: KPIs (LECTURA EN Z) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Envíos", len(df))
col2.metric("Costo Promedio", f"${df['Costo_Envio'].mean():,.0f}")
col3.metric("Días Entrega Avg", f"{df['Tiempo_Entrega_Dias'].mean():.1f} d")
col4.metric("Entregados", len(df[df['Estado'] == 'Entregado']))

st.divider()

# --- CUERPO PRINCIPAL (LECTURA EN F) ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Tendencia de Costos por Fecha")
    fig_line = px.line(df.sort_values('Fecha'), x='Fecha', y='Costo_Envio', 
                       color_discrete_sequence=['#00D4FF'], template='plotly_dark')
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Distribución por Estado")
    fig_pie = px.pie(df, names='Estado', hole=0.4, 
                     color_discrete_sequence=['#00D4FF', '#FF8C00', '#2E8B57', '#DC143C'], 
                     template='plotly_dark')
    st.plotly_chart(fig_pie, use_container_width=True)

# TABLA DETALLADA ABAJO
st.subheader("Detalle de Envíos Recientes")
st.dataframe(df.head(10), use_container_width=True)
