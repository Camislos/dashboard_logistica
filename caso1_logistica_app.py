
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ① Configuración
st.set_page_config(page_title='TransCargo Dashboard', page_icon='🚚',
                   layout='wide', initial_sidebar_state='expanded')

# ② Carga de datos con caché
@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), 'caso1_logistica_dataset.csv')
    df = pd.read_csv(ruta)
    df['fecha_despacho'] = pd.to_datetime(df['fecha_despacho'])
    return df

df = cargar_datos()

# ③ Sidebar con filtros
with st.sidebar:
    st.header("🔧 Filtros")
    transportistas_sel = st.multiselect("Transportista",
        sorted(df['transportista'].unique()), list(df['transportista'].unique()))
    tipos_carga_sel = st.multiselect("Tipo de Carga",
        sorted(df['tipo_carga'].unique()), list(df['tipo_carga'].unique()))
    estado_sel = st.selectbox("Estado", ['Todos'] + sorted(df['estado'].unique()))
    origen_sel = st.multiselect("Ciudad Origen",
        sorted(df['ciudad_origen'].unique()), list(df['ciudad_origen'].unique()))

# ④ Aplicar filtros
df_f = df.copy()
if transportistas_sel: df_f = df_f[df_f['transportista'].isin(transportistas_sel)]
if tipos_carga_sel:    df_f = df_f[df_f['tipo_carga'].isin(tipos_carga_sel)]
if estado_sel != 'Todos': df_f = df_f[df_f['estado'] == estado_sel]
if origen_sel:         df_f = df_f[df_f['ciudad_origen'].isin(origen_sel)]

# ⑤ Título
st.title("🚚 TransCargo — Dashboard de Operaciones Logísticas")
st.markdown("**Panel de control de envíos · 2024**")
st.markdown("---")

# ⑥ KPIs (patrón F)
k1, k2, k3, k4, k5 = st.columns(5)
total      = len(df_f)
entregados = len(df_f[df_f['estado'] == 'Entregado'])
tasa       = round(entregados / total * 100, 1) if total > 0 else 0
k1.metric("📦 Total Envíos",    f"{total:,}")
k2.metric("✅ Tasa Entrega",    f"{tasa}%")
k3.metric("💰 Costo Promedio",  f"${df_f['costo_envio_cop'].mean():,.0f}" if total > 0 else "$0")
k4.metric("⏰ Retraso Prom.",   f"{df_f['retraso_dias'].mean():.1f} días" if total > 0 else "0")
k5.metric("⭐ Calificación",    f"{df_f['calificacion_cliente'].mean():.1f}/5" if total > 0 else "0")
st.markdown("---")

# ⑦ Fila 1: línea + pie (patrón Z)
col1, col2 = st.columns([1.5, 1])
with col1:
    em = df_f.groupby(df_f['fecha_despacho'].dt.to_period('M')).agg(total=("id_envio","count")).reset_index()
    em['fecha_despacho'] = em['fecha_despacho'].astype(str)
    fig = px.line(em, x='fecha_despacho', y='total', markers=True,
                  title='📅 Envíos por Mes', color_discrete_sequence=['#2d6a9f'])
    fig.update_traces(line_width=3, marker_size=8)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    ec = df_f['estado'].value_counts().reset_index()
    fig2 = px.pie(ec, names='estado', values='count', title='📦 Estado de Envíos',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig2, use_container_width=True)

# ⑧ Fila 2: barras + scatter (patrón Z invertido)
col3, col4 = st.columns([1, 1.5])
with col3:
    ct = df_f.groupby('transportista')['costo_envio_cop'].mean().reset_index()
    ct.columns = ['transportista','costo_promedio']
    fig3 = px.bar(ct.sort_values('costo_promedio'), y='transportista', x='costo_promedio',
                  orientation='h', title='💰 Costo por Transportista',
                  color='costo_promedio', color_continuous_scale='Blues', text_auto='.2s')
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
with col4:
    fig4 = px.scatter(df_f, x='peso_kg', y='costo_envio_cop', color='tipo_carga',
                      size='distancia_km', hover_data=['transportista','ciudad_origen','ciudad_destino'],
                      title='⚖️ Peso vs Costo por Tipo de Carga', trendline='ols')
    st.plotly_chart(fig4, use_container_width=True)

# ⑨ Heatmap ancho completo
st.markdown("### 🌡️ Mapa de Calor — Retraso por Origen y Tipo de Carga")
pivot = df_f.pivot_table(values='retraso_dias', index='ciudad_origen',
                          columns='tipo_carga', aggfunc='mean').round(1)
fig5 = px.imshow(pivot, color_continuous_scale='RdYlGn_r', text_auto=True)
st.plotly_chart(fig5, use_container_width=True)

# ⑩ Tabla colapsable
with st.expander("📋 Ver datos filtrados"):
    st.dataframe(df_f.sort_values('fecha_despacho', ascending=False), use_container_width=True)
    st.download_button("⬇️ Descargar CSV", df_f.to_csv(index=False), "logistica_filtrado.csv")

st.caption("🔧 Streamlit + Plotly | Clase de Visualización de Datos")
