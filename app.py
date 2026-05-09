#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Hipertehuelche AI: Intelligence Hub
Senior UX/UI Developer - Supply Chain Analytics
Versión: 1.0 - Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Hipertehuelche AI - Intelligence Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================
st.markdown("""
<style>
    /* Fondo y color principal */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Título principal */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00C853 0%, #00E676 50%, #69F0AE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Subtítulo */
    .sub-title {
        font-size: 1.2rem;
        color: #B0BEC5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Separador */
    .custom-divider {
        background: linear-gradient(90deg, transparent, #00C853, transparent);
        height: 2px;
        margin: 2rem 0;
    }
    
    /* Botón de refrescar */
    .stButton > button {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4);
    }
    
    /* Tablas */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Filtros */
    .stSelectbox > div > div {
        background-color: #1a237e;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE CARGA DE DATOS
# ============================================================
@st.cache_data
def cargar_datos():
    """
    Carga las tres pestañas del Excel
    Cachea los datos para mejorar rendimiento
    """
    archivo = "Analisis_Inventario_Construccion.xlsx"
    
    try:
        # Cargar cada pestaña
        df_criticos = pd.read_excel(archivo, sheet_name='SKUs Críticos (Comprar Ya)')
        df_inmovilizado = pd.read_excel(archivo, sheet_name='Capital Inmovilizado (Frenar)')
        df_depuracion = pd.read_excel(archivo, sheet_name='Sugerencia Depuración Surtido')
        
        # Calcular métricas adicionales
        total_inmovilizado = df_inmovilizado['Valor_Inmovilizado'].sum()
        ahorro_potencial = total_inmovilizado * 0.15
        skus_criticos_count = len(df_criticos)
        
        return {
            'criticos': df_criticos,
            'inmovilizado': df_inmovilizado,
            'depuracion': df_depuracion,
            'total_inmovilizado': total_inmovilizado,
            'ahorro_potencial': ahorro_potencial,
            'skus_criticos_count': skus_criticos_count
        }
    except FileNotFoundError:
        st.error(f"❌ No se encuentra el archivo {archivo}")
        st.info("Asegúrate de que el archivo Excel está en la misma carpeta que app.py")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None

# ============================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================
def crear_kpi_card(titulo, valor, formato, icono, color):
    """Crea una tarjeta de KPI con estilo"""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {color}; margin-bottom: 0.5rem;">{icono} {titulo}</h3>
            <p style="font-size: 2.5rem; font-weight: 700; margin: 0;">{formato.format(valor)}</p>
        </div>
        """, unsafe_allow_html=True)

def grafico_barras_top10(df):
    """Gráfico de barras horizontales Top 10 SKUs más inmovilizados"""
    if df is not None and not df.empty:
        top10 = df.nlargest(10, 'Valor_Inmovilizado')
        
        fig = px.bar(
            top10,
            x='Valor_Inmovilizado',
            y='SKU_ID',
            orientation='h',
            title='🏆 Top 10 SKUs con Mayor Capital Inmovilizado',
            color='Valor_Inmovilizado',
            color_continuous_scale=['#00C853', '#FFD600', '#FF1744'],
            text='Valor_Inmovilizado'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=20,
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Capital Inmovilizado ($)",
            yaxis_title="SKU ID"
        )
        
        fig.update_traces(
            texttemplate='$%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Capital: $%{x:,.2f}<br>Categoría: %{customdata}<extra></extra>',
            customdata=top10['Categoria']
        )
        
        return fig
    return None

def grafico_donut_abc(df):
    """Gráfico donut de distribución ABC"""
    if df is not None and 'Clase_ABC' in df.columns:
        abc_counts = df['Clase_ABC'].value_counts().reset_index()
        abc_counts.columns = ['Clase', 'Cantidad']
        
        colores = {'A': '#00C853', 'B': '#FFD600', 'C': '#FF1744'}
        
        fig = go.Figure(data=[go.Pie(
            labels=abc_counts['Clase'],
            values=abc_counts['Cantidad'],
            hole=0.6,
            marker=dict(colors=[colores[c] for c in abc_counts['Clase']]),
            textinfo='label+percent',
            textfont=dict(color='white', size=14),
            hovertemplate='<b>Clase %{label}</b><br>Cantidad: %{value} SKUs<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='📊 Distribución de Clasificación ABC',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=20,
            height=500,
            annotations=[dict(
                text='ABC<br>Analysis',
                x=0.5, y=0.5,
                font_size=20,
                font_color='white',
                showarrow=False
            )]
        )
        
        return fig
    return None

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """Dashboard principal de Hipertehuelche AI"""
    
    # Título principal
    st.markdown('<h1 class="main-title">🚀 Hipertehuelche AI: Intelligence Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Supply Chain Analytics & Inventory Optimization Platform</p>', unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner('🔄 Cargando datos del inventario...'):
        datos = cargar_datos()
    
    if datos is None:
        st.stop()
    
    # ============================================================
    # KPIS SUPERIORES
    # ============================================================
    st.markdown("## 📊 Indicadores Clave de Desempeño")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    kpi_cols = st.columns(3)
    
    with kpi_cols[0]:
        crear_kpi_card(
            "Capital Inmovilizado",
            datos['total_inmovilizado'],
            "${:,.2f}",
            "💰",
            "#FF1744"
        )
    
    with kpi_cols[1]:
        crear_kpi_card(
            "SKUs en Quiebre/Críticos",
            datos['skus_criticos_count'],
            "{:,.0f}",
            "🔴",
            "#FFD600"
        )
    
    with kpi_cols[2]:
        crear_kpi_card(
            "Ahorro Potencial (15%)",
            datos['ahorro_potencial'],
            "${:,.2f}",
            "💎",
            "#00C853"
        )
    
    # ============================================================
    # GRÁFICOS DINÁMICOS
    # ============================================================
    st.markdown("## 📈 Análisis Visual")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    grafico_cols = st.columns(2)
    
    with grafico_cols[0]:
        fig_barras = grafico_barras_top10(datos['inmovilizado'])
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
    
    with grafico_cols[1]:
        fig_donut = grafico_donut_abc(datos['criticos'])
        if fig_donut:
            st.plotly_chart(fig_donut, use_container_width=True)
    
    # ============================================================
    # INTERACTIVIDAD - FILTRO POR CATEGORÍA
    # ============================================================
    st.markdown("## 🔍 Exploración de Inventario")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Obtener categorías únicas
    categorias = ['Todas'] + sorted(datos['criticos']['Categoria'].unique().tolist())
    categoria_seleccionada = st.selectbox(
        "Filtrar por Categoría:",
        categorias,
        key="filtro_categoria"
    )
    
    # Filtrar datos según selección
    if categoria_seleccionada != 'Todas':
        df_filtrado = datos['criticos'][datos['criticos']['Categoria'] == categoria_seleccionada]
    else:
        df_filtrado = datos['criticos']
    
    # ============================================================
    # TABA DETALLADA
    # ============================================================
    st.markdown(f"### 📋 SKUs Críticos - {categoria_seleccionada}")
    st.markdown(f"**Total registros:** {len(df_filtrado)}")
    
    # Mostrar DataFrame con formato
    st.dataframe(
        df_filtrado.style
            .background_gradient(subset=['Stock_Actual', 'Reorder_Point'], cmap='RdYlGn')
            .format({'Costo_Unitario': '${:,.2f}', 'Venta_Promedio_Semanal': '{:,.1f}'}),
        use_container_width=True,
        height=400
    )
    
    # ============================================================
    # PIE DE PÁGINA
    # ============================================================
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with col2:
        st.markdown("**Fuente:** Analisis_Inventario_Construccion.xlsx")
    
    with col3:
        if st.button("🔄 Refrescar Datos"):
            st.cache_data.clear()
            st.rerun()

# ============================================================
# EJECUTAR APP
# ============================================================
if __name__ == "__main__":
    main()