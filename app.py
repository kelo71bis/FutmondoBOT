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
def cargar_datos_v3():
    ruta_master = "datos/vistas_negocio/Fact_Global_Master.xlsx"
    ruta_ligas = "datos/maestros/md_palmares_liga.xlsx"
    ruta_copas = "datos/maestros/md_palmares_copa.xlsx"
    
    df, df_ligas, df_copas = None, None, None
    
    if os.path.exists(ruta_master):
        df = pd.read_excel(ruta_master)
        
        # 🚑 PARCHE DE EMERGENCIA: Diccionario manual extraído de la clasificación
        mapeo_nombres = {
            "62d5bd9ad8106d3355b5bdc1": "Pallejandro",
            "5f452f5e66dd374930eb2b71": "FC Mikelona",
            "5f45324dec331549297ee971": "Jatafe",
            "5f453062ec331549297ee6b8": "Real Dendryd",
            "5f4530beec331549297ee6d6": "URSS",
            "5f47aeb6c387a50bca03dd55": "Cruyffisme FC",
            "5f4531e9764e7d491e029746": "Cracklos F.C",
            "5f47ab5b9e2edb0bb831c703": "Bichos Team"
        }
        
        # Aplicamos el parche limpiando los IDs por si acaso
        df['ID_Futmondo'] = df['ID_Futmondo'].astype(str).str.strip().str.lower()
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
        
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['ID_Futmondo'] = df_ligas['ID_Futmondo'].astype(str).str.strip().str.lower()
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
        if os.path.exists(ruta_copas):
            df_copas = pd.read_excel(ruta_copas)
            df_copas['ID_Futmondo'] = df_copas['ID_Futmondo'].astype(str).str.strip().str.lower()
            df_copas['Mánager'] = df_copas['ID_Futmondo'].map(mapeo_nombres).fillna(df_copas['ID_Futmondo'])
            
    return df, df_ligas, df_copas

df, df_ligas, df_copas = cargar_datos_v3()


        
        # 🛡️ ESCUDO ANTI-FALLOS Y ANTI-CACHÉ: Forzar texto, minúsculas y limpiar espacios
        df_prop['id_propietario'] = df_prop['id_propietario'].astype(str).str.strip().str.lower()
        mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
        
        df['ID_Futmondo'] = df['ID_Futmondo'].astype(str).str.strip().str.lower()
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
        
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['ID_Futmondo'] = df_ligas['ID_Futmondo'].astype(str).str.strip().str.lower()
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
        if os.path.exists(ruta_copas):
            df_copas = pd.read_excel(ruta_copas)
            df_copas['ID_Futmondo'] = df_copas['ID_Futmondo'].astype(str).str.strip().str.lower()
            df_copas['Mánager'] = df_copas['ID_Futmondo'].map(mapeo_nombres).fillna(df_copas['ID_Futmondo'])
            
    return df, df_ligas, df_copas

df, df_ligas, df_copas = cargar_datos_v2()


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