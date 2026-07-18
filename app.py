import streamlit as st
import pandas as pd
import os

# 🚀 IMPORTAMOS NUESTRAS PANTALLAS MODULARES
from pantallas.menu_principal import mostrar_menu
from pantallas.analisis_temporadas import mostrar_analisis
from pantallas.salon_fama import mostrar_salon_fama
from pantallas.palmares import mostrar_palmares
from pantallas.cara_a_cara import mostrar_cara_a_cara
from pantallas.royal_rumble import mostrar_royal_rumble

# ⚙️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="LaLiga Santanguissa", page_icon="🏆", layout="wide")

# 🧠 CACHÉ DE DATOS
@st.cache_data
def cargar_datos():
    ruta_master = "datos/vistas_negocio/Fact_Global_Master.xlsx"
    ruta_propietarios = "datos/maestros/md_propietarios.xlsx"
    ruta_ligas = "datos/maestros/md_palmares_liga.xlsx"
    ruta_copas = "datos/maestros/md_palmares_copa.xlsx"
    
    df, df_ligas, df_copas = None, None, None
    
    if os.path.exists(ruta_master) and os.path.exists(ruta_propietarios):
        df = pd.read_excel(ruta_master)
        df_prop = pd.read_excel(ruta_propietarios)
        
        # 🛡️ ESCUDO ANTI-FALLOS: Forzar texto y limpiar espacios fantasma en los Excel
        df_prop['id_propietario'] = df_prop['id_propietario'].astype(str).str.strip()
        mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
        
        df['ID_Futmondo'] = df['ID_Futmondo'].astype(str).str.strip()
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
            
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['ID_Futmondo'] = df_ligas['ID_Futmondo'].astype(str).str.strip()
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
        if os.path.exists(ruta_copas):
            df_copas = pd.read_excel(ruta_copas)
            df_copas['ID_Futmondo'] = df_copas['ID_Futmondo'].astype(str).str.strip()
            df_copas['Mánager'] = df_copas['ID_Futmondo'].map(mapeo_nombres).fillna(df_copas['ID_Futmondo'])
            
    return df, df_ligas, df_copas

    
    df, df_ligas, df_copas = None, None, None
    
    if os.path.exists(ruta_master) and os.path.exists(ruta_propietarios):
        df = pd.read_excel(ruta_master)
        df_prop = pd.read_excel(ruta_propietarios)
        mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
        
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
            
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
        if os.path.exists(ruta_copas):
            df_copas = pd.read_excel(ruta_copas)
            df_copas['Mánager'] = df_copas['ID_Futmondo'].map(mapeo_nombres).fillna(df_copas['ID_Futmondo'])
            
    return df, df_ligas, df_copas

df, df_ligas, df_copas = cargar_datos()

# 🛡️ HISTORIAL FIJO DE LA TEMPORADA INAUGURAL 2020/21
clasificacion_2020_21 = ["FC Mikelona", "Arsenati", "Cruyffisme FC", "URSS", "Jatafe", "Real Dendryd", "Cracklos F.C", "Bichos Team"]

# 🧮 FUNCIÓN GLOBAL PARA LA MEDIA DE PUNTOS
def calcular_medias_globales(df_input):
    df_reg = df_input[df_input['Temporada'] != '2024/25']
    sum_reg = df_reg.groupby('Mánager')['Puntos'].sum()
    count_reg = df_reg.groupby('Mánager')['Puntos'].count()
    
    df_2425 = df_input[df_input['Temporada'] == '2024/25']
    sum_2425 = df_2425.groupby('Mánager')['Puntos_Acumulados'].max() if not df_2425.empty else pd.Series(dtype=float)
    
    managers = df_input['Mánager'].unique()
    res = {}
    for m in managers:
        s_r = sum_reg.get(m, 0)
        c_r = count_reg.get(m, 0)
        s_24 = sum_2425.get(m, 0) if pd.notna(sum_2425.get(m, 0)) else 0
        c_24 = 38 if s_24 > 0 else 0
        
        tot_sum = s_r + s_24
        tot_c = c_r + c_24
        res[m] = (tot_sum / tot_c) if tot_c > 0 else 0
    return res

if df is not None:
    score_historico_dict = calcular_medias_globales(df)
    
    # Inicializar Session State
    if 'pantalla' not in st.session_state: st.session_state.pantalla = "🏠 Menú Principal"

    # Barra Lateral
    st.sidebar.title("⚽ Menú de Liga")
    opciones_sidebar = ["🏠 Menú Principal", "📈 Análisis por temporadas", "🏆 Salón de la Fama", "🥇 Palmarés Histórico", "⚔️ Cara a Cara", "🤼 Royal Rumble", "👤 Perfiles (Próximamente)"]
    
    idx_actual = opciones_sidebar.index(st.session_state.pantalla) if st.session_state.pantalla in opciones_sidebar else 0
    menu_sidebar = st.sidebar.radio("Navegación Rápida", opciones_sidebar, index=idx_actual)
    
    if menu_sidebar != st.session_state.pantalla:
        st.session_state.pantalla = menu_sidebar
        st.rerun()

    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ Info Histórica Importante"):
        st.caption("• **2020/21**: Faltan los datos de la temporada inaugural.")
        st.caption("• **2022/23**: **Pallejandro** se une sustituyendo a **Arsenati**.")
        st.caption("• **2024/25**: Solo hay foto final de puntos acumulados. Sus jornadas no cuentan para récords ni MVPs.")

    # ==========================================
    # ENRUTADOR DE PANTALLAS
    # ==========================================
    if st.session_state.pantalla == "🏠 Menú Principal":
        mostrar_menu(df)
        
    elif st.session_state.pantalla == "📈 Análisis por temporadas":
        mostrar_analisis(df, score_historico_dict)
        
    elif st.session_state.pantalla == "🏆 Salón de la Fama":
        mostrar_salon_fama(df)
        
    elif st.session_state.pantalla == "🥇 Palmarés Histórico":
        mostrar_palmares(df_ligas, df_copas)
        
    elif st.session_state.pantalla == "⚔️ Cara a Cara":
        mostrar_cara_a_cara(df, df_ligas, df_copas, clasificacion_2020_21)
        
    elif st.session_state.pantalla == "🤼 Royal Rumble":
        mostrar_royal_rumble(df)
        
    elif st.session_state.pantalla == "👤 Perfiles (Próximamente)":
        st.title(st.session_state.pantalla)
        st.info("🚧 Estamos trabajando en esta sección.")

else:
    st.error("❌ Faltan los archivos de datos globales.")