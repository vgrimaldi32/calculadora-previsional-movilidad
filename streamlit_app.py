import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
import base64
from io import BytesIO

# =============================================
# CONFIGURACIÓN INICIAL MEJORADA
# =============================================

# Configuración de la página
st.set_page_config(
    page_title="Calculadora Previsional",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =============================================
# MANEJO DEL LOGO OPTIMIZADO
# =============================================

def mostrar_logo():
    """
    Función optimizada para mostrar el logo con manejo de errores robusto
    """
    try:
        # Verificar existencia del archivo
        if not os.path.exists("logo_para_app.png"):
            st.sidebar.warning("⚠️ Archivo 'logo_para_app.png' no encontrado en el directorio")
            return None
        
        # Cargar y redimensionar logo
        logo = Image.open("logo_para_app.png")
        
        # Mostrar logo centrado
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(logo, width=180)
        
        return logo
    
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar el logo: {str(e)}")
        return None

# =============================================
# INTERFAZ PRINCIPAL
# =============================================

# Mostrar logo
mostrar_logo()

# Título principal
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 10px;'>
    📈 Calculadora de Movilidad Previsional
    </h1>
""", unsafe_allow_html=True)

# Subtítulo
st.markdown("""
    <h2 style='text-align: center; color: #666666; margin-top: 0; margin-bottom: 30px;'>
    Comparación: ANSeS vs. Fallos Martínez/Italiano
    </h2>
""", unsafe_allow_html=True)

# =============================================
# DATOS DE ACTUALIZACIÓN
# =============================================

# --- Datos ANSeS ---
data_anses = {
    "Fecha": ["2020-03", "2020-06", "2020-09", "2020-12", "2021-03", "2021-06", 
             "2021-09", "2021-12", "2022-03", "2022-06", "2022-09", "2022-12",
             "2023-03", "2023-06", "2023-09", "2023-12", "2024-03", "2024-04",
             "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10",
             "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
             "2025-05", "2025-06"],
    "Coeficiente": [
        None,  # Marzo 2020 (se calcula aparte si es jubilación pre-2020)
        1.0612, 1.075, 1.05, 1.0807, 1.1212, 1.1239, 1.1211,
        1.1228, 1.15, 1.1553, 1.1562, 1.1704, 1.2092, 1.2329,
        1.2087, 1.2718, 1.274, 1.1101, 1.0883, 1.0418, 1.0458,
        1.0403, 1.0417, 1.0347, 1.0269, 1.0243, 1.027, 1.0221,
        1.024, 1.0373, 1.0278
    ]
}

# --- Datos Justicia ---
data_justicia = {
    "Fecha": ["2020-03", "2020-06", "2020-09", "2020-12", "2021-03", "2021-06",
             "2021-09", "2021-12", "2022-03", "2022-06", "2022-09", "2022-12",
             "2023-03", "2023-06", "2023-09", "2023-12", "2024-03", "2024-04",
             "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10",
             "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
             "2025-05", "2025-06"],
    "Coeficiente": [
        1.1156, 1.1089, 1.0988, 1.0455, 1.0807, 1.1212, 1.1239,
        1.1211, 1.1706, 1.1692, 1.1955, 1.1731, 1.2247, 1.2491,
        1.2957, 1.4087, 1.4633, 1.132, 1.1101, 1.0883, 1.0418,
        1.0458, 1.0403, 1.0417, 1.0347, 1.0269, 1.0243, 1.027,
        1.0221, 1.024, 1.0373, 1.0278
    ]
}

# Convertir a DataFrames
df_anses = pd.DataFrame(data_anses)
df_justicia = pd.DataFrame(data_justicia)
df_anses["Fecha"] = pd.to_datetime(df_anses["Fecha"])
df_justicia["Fecha"] = pd.to_datetime(df_justicia["Fecha"])

# =============================================
# INTERFAZ DE USUARIO
# =============================================

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
            value="2022-10",
            help="Formato: AAAA-MM (ej: 2020-03)"
        )

# =============================================
# FUNCIÓN DE CÁLCULO
# =============================================

def calcular_actualizacion(haber_base, fecha_base):
    """
    Calcula la actualización del haber según ANSeS y Justicia
    """
    try:
        fecha_base_dt = pd.to_datetime(fecha_base)
        
        # ANSeS: Fórmula especial para jubilados pre-marzo 2020
        if fecha_base_dt <= pd.to_datetime("2020-02"):
            haber_marzo2020 = (haber_base + 1500) * 1.023  # $1500 + 2.3%
            coefs_anses = [haber_marzo2020 / haber_base] + list(
                df_anses[
                    (df_anses["Fecha"] > pd.to_datetime("2020-03")) & 
                    (df_anses["Fecha"] >= fecha_base_dt)
                ]["Coeficiente"]
            )
        else:
            coefs_anses = df_anses[df_anses["Fecha"] >= fecha_base_dt]["Coeficiente"]
        
        # Justicia: Siempre desde fecha_base
        coefs_justicia = df_justicia[df_justicia["Fecha"] >= fecha_base_dt]["Coeficiente"]
        
        # Aplicar coeficientes (ignorar NaN)
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
# BOTÓN DE CÁLCULO Y RESULTADOS
# =============================================

if st.button("🔄 Calcular", type="primary", use_container_width=True):
    with st.spinner("Calculando..."):
        try:
            haber_anses, haber_justicia = calcular_actualizacion(haber_base, fecha_base)
            diferencia = haber_justicia - haber_anses
            porcentaje = (diferencia / haber_anses) * 100 if haber_anses != 0 else 0
            
            st.markdown("---")
            st.subheader(f"🔍 Resultados para {nombre}:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "ANSeS", 
                    f"${haber_anses:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."),
                    help="Cálculo según coeficientes oficiales de ANSeS"
                )
            with col2:
                st.metric(
                    "Justicia (Fallos)", 
                    f"${haber_justicia:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."),
                    help="Cálculo según fallos Martínez/Italiano"
                )
            with col3:
                st.metric(
                    "Diferencia", 
                    f"${diferencia:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."), 
                    f"{porcentaje:.2f}%",
                    delta_color="inverse",
                    help="Diferencia entre ambos cálculos"
                )
            
            # Mostrar detalles adicionales
            with st.expander("📊 Ver detalles del cálculo"):
                st.write(f"**Haber base:** ${haber_base:,.2f}")
                st.write(f"**Fecha base:** {fecha_base}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}. Por favor verifica los datos ingresados.")

# =============================================
# INFORMACIÓN ADICIONAL
# =============================================

st.markdown("---")
with st.expander("ℹ️ Instrucciones y ejemplos"):
    st.markdown("""
    **📌 Ejemplos válidos:**  
    - **Jubilación en 2020**: `2020-02` → Aplica $1500 + 2.3% en marzo 2020 + coeficientes posteriores.  
    - **Jubilación en 2022**: `2022-10` → Solo usa coeficientes desde octubre 2022.  
    - **Jubilación en 2024**: `2024-03` → Coeficientes desde marzo 2024.  
    
    **⚠️ Notas importantes:**  
    - Todos los cálculos son aproximados y deben ser verificados por un profesional.  
    - Los coeficientes pueden ser actualizados periódicamente.  
    """)

# =============================================
# ESTILOS ADICIONALES
# =============================================

st.markdown("""
    <style>
        .stButton>button {
            font-weight: bold;
            border: 2px solid #4CAF50;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
        }
        .stAlert {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)
