import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
import base64
from io import BytesIO

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================
st.set_page_config(
    page_title="Calculadora Previsional",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =============================================
# FUNCIÓN PARA MOSTRAR LOGO
# =============================================
def mostrar_logo():
    try:
        if not os.path.exists("logo_para_app.png"):
            st.sidebar.warning("⚠️ Archivo de logo no encontrado")
            return None
        
        logo = Image.open("logo_para_app.png")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(logo, width=180)
        return logo
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar el logo: {str(e)}")
        return None

# =============================================
# DATOS DE COEFICIENTES
# =============================================
data_anses = {
    "Fecha": ["2020-03", "2020-06", "2020-09", "2020-12", "2021-03", "2021-06", 
             "2021-09", "2021-12", "2022-03", "2022-06", "2022-09", "2022-12",
             "2023-03", "2023-06", "2023-09", "2023-12", "2024-03", "2024-04",
             "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10",
             "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
             "2025-05", "2025-06", "2025-07", "2025-08"],
    "Coeficiente": [
        None, 1.0612, 1.075, 1.05, 1.0807, 1.1212, 1.1239, 1.1211,
        1.1228, 1.15, 1.1553, 1.1562, 1.1704, 1.2092, 1.2329,
        1.2087, 1.2718, 1.274, 1.1101, 1.0883, 1.0418, 1.0458,
        1.0403, 1.0417, 1.0347, 1.0269, 1.0243, 1.027, 1.0221,
        1.024, 1.0373, 1.0278, 1.015, 1.0162
    ]
}

data_justicia = {
    "Fecha": ["2020-03", "2020-06", "2020-09", "2020-12", "2021-03", "2021-06",
             "2021-09", "2021-12", "2022-03", "2022-06", "2022-09", "2022-12",
             "2023-03", "2023-06", "2023-09", "2023-12", "2024-03", "2024-04",
             "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10",
             "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
             "2025-05", "2025-06", "2025-07", "2025-08"],
    "Coeficiente": [
        1.1156, 1.1089, 1.0988, 1.0455, 1.0807, 1.1212, 1.1239,
        1.1211, 1.1706, 1.1692, 1.1955, 1.1731, 1.2247, 1.2491,
        1.2957, 1.4087, 1.4633, 1.132, 1.1101, 1.0883, 1.0418,
        1.0458, 1.0403, 1.0417, 1.0347, 1.0269, 1.0243, 1.027,
        1.0221, 1.024, 1.0373, 1.0278, 1.015, 1.0612
    ]
}

df_anses = pd.DataFrame(data_anses)
df_justicia = pd.DataFrame(data_justicia)
df_anses["Fecha"] = pd.to_datetime(df_anses["Fecha"])
df_justicia["Fecha"] = pd.to_datetime(df_justicia["Fecha"])

# =============================================
# FUNCIÓN DE CÁLCULO
# =============================================
def calcular_actualizacion(haber_base, fecha_base):
    try:
        fecha_base_dt = pd.to_datetime(fecha_base)
        
        if fecha_base_dt <= pd.to_datetime("2020-02"):
            haber_marzo2020 = (haber_base + 1500) * 1.023
            coefs_anses = [haber_marzo2020 / haber_base] + list(
                df_anses[
                    (df_anses["Fecha"] > pd.to_datetime("2020-03")) & 
                    (df_anses["Fecha"] >= fecha_base_dt)
                ]["Coeficiente"]
            )
        else:
            coefs_anses = df_anses[df_anses["Fecha"] >= fecha_base_dt]["Coeficiente"]
        
        coefs_justicia = df_justicia[df_justicia["Fecha"] >= fecha_base_dt]["Coeficiente"]
        
        haber_anses = haber_base
        for coef in coefs_anses:
            if pd.notna(coef):
                haber_anses *= coef
        
        haber_justicia = haber_base
        for coef in coefs_justicia:
            haber_justicia *= coef
        
        return haber_anses, haber_justicia
    
    except Exception as e:
        raise ValueError(f"Error en el cálculo: {str(e)}")

# =============================================
# INTERFAZ DE USUARIO
# =============================================
mostrar_logo()

st.markdown("""
    <h1 style='text-align: center; margin-bottom: 10px;'>
    📈 Calculadora de Movilidad Previsional
    </h1>
    <h2 style='text-align: center; color: #666666; margin-top: 0; margin-bottom: 30px;'>
    Comparación: ANSeS vs. Fallos Martínez/Italiano
    </h2>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("### 📝 Datos de Entrada")
    nombre = st.text_input("Nombre de la persona:", value="Ejemplo")
    
    col1, col2 = st.columns(2)
    with col1:
        haber_base = st.number_input(
            "Haber base ($):", 
            min_value=0.0, 
            step=1000.0,
            format="%.2f", 
            value=50000.0
        )
    with col2:
        fecha_base = st.text_input(
            "Fecha de jubilación o primer cobro (YYYY-MM):", 
            value="2022-10"
        )

if st.button("🔄 Calcular", type="primary", use_container_width=True):
    with st.spinner("Calculando..."):
        try:
            haber_anses, haber_justicia = calcular_actualizacion(haber_base, fecha_base)
            diferencia = haber_justicia - haber_anses
            porcentaje = (diferencia / haber_anses) * 100 if haber_anses != 0 else 0
            
            st.markdown("---")
            st.subheader(f"🔍 Resultados para {nombre}:")
            
            st.markdown("""
                <style>
                    div[data-testid="stMetric"] {
                        min-width: 120px !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "ANSeS", 
                    f"${haber_anses:,.0f}".replace(",", ".")
                )
            with col2:
                st.metric(
                    "Justicia (Fallos)", 
                    f"${haber_justicia:,.0f}".replace(",", ".")
                )
            with col3:
                st.metric(
                    "Diferencia", 
                    f"${diferencia:,.0f}".replace(",", "."), 
                    f"{porcentaje:.1f}%",
                    delta_color="inverse"
                )
            
            with st.expander("📊 Ver detalles del cálculo"):
                st.write(f"**Haber base:** ${haber_base:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.write(f"**Fecha base:** {fecha_base}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")
with st.expander("ℹ️ Instrucciones y ejemplos"):
    st.markdown("""
    **📌 Ejemplos válidos:**  
    - `2020-02` → Jubilación pre-marzo 2020  
    - `2022-10` → Jubilación reciente  
    """)

st.markdown("""
    <style>
        .stButton>button {
            font-weight: bold;
            border: 2px solid #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)
