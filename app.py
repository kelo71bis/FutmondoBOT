import streamlit as st
import pandas as pd
import os

# ⚙️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Liga Santanguissa", page_icon="🏆", layout="wide")

# 🧠 CACHÉ DE DATOS (Para que la web vaya a la velocidad de la luz al cambiar de menú)
@st.cache_data
def cargar_datos():
    ruta_master = "datos/vistas_negocio/Fact_Global_Master.xlsx"
    ruta_propietarios = "datos/maestros/md_propietarios.xlsx"
    
    if os.path.exists(ruta_master) and os.path.exists(ruta_propietarios):
        df = pd.read_excel(ruta_master)
        df_prop = pd.read_excel(ruta_propietarios)
        mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
        return df
    return None

df = cargar_datos()

if df is not None:
    # 🗂️ MENÚ DE NAVEGACIÓN LATERAL
    st.sidebar.title("⚽ Menú de Liga")
    menu = st.sidebar.radio("Navegación", [
        "🏠 Visión General", 
        "🏆 Salón de la Fama", 
        "👤 Perfiles (Próximamente)", 
        "⚔️ Cara a Cara (Próximamente)"
    ])
    
    # ⚠️ AVISO HISTÓRICO (Disclaimer)
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ Info Histórica Importante"):
        st.caption("• Faltan los datos de la temporada inaugural (2020/21).")
        st.caption("• **Pallejandro** se unió a la liga en la temporada 2022/23 sustituyendo a **Arsenati**. Tenlo en cuenta al mirar los puntos históricos totales.")

    # ==========================================
    # PANTALLA 1: VISIÓN GENERAL
    # ==========================================
    if menu == "🏠 Visión General":
        st.title("🏠 Clasificación Actual")
        st.markdown("---")
        
        col_filtros, col_vacio = st.columns([1, 3])
        with col_filtros:
            temporadas = df['Temporada'].unique().tolist()
            temporada_sel = st.selectbox("📅 Selecciona la Temporada", temporadas, index=len(temporadas)-1)
        
        df_temp = df[df['Temporada'] == temporada_sel]
        jornada_maxima = int(df_temp['Jornada'].max())
        
        rango_jornadas = st.slider("🔍 Rango de Jornadas en Gráfica", 1, jornada_maxima, (1, jornada_maxima))
        
        col1, col2 = st.columns([1, 1.8])
        
        with col1:
            st.subheader(f"📊 Tabla (Jornada {jornada_maxima})")
            df_clasif = df_temp[df_temp['Jornada'] == jornada_maxima].sort_values(by="Puntos_Acumulados", ascending=False)
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
            st.dataframe(df_mostrar, use_container_width=True)
            
        with col2:
            st.subheader("📈 Evolución de Puntos")
            df_temp_grafica = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
            df_grafica = df_temp_grafica.pivot(index='Jornada', columns='Mánager', values='Puntos_Acumulados')
            st.line_chart(df_grafica, height=420)

    # ==========================================
    # PANTALLA 2: SALÓN DE LA FAMA
    # ==========================================
    elif menu == "🏆 Salón de la Fama":
        st.title("🏆 El Salón de la Fama (y de la Infamia)")
        st.write("Los récords absolutos de la Liga Santanguissa desde que hay registros.")
        st.markdown("---")
        
        # Omitimos la Jornada 1 de la 2025/26 porque la hemos hardcodeado y puede desvirtuar récords "naturales"
        df_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26'))]
        
        col1, col2 = st.columns(2)
        
        # 🟢 MAYOR PUNTUACIÓN EN UNA JORNADA
        with col1:
            st.subheader("🚀 La Mayor Exhibición")
            mejor_jornada = df_records.loc[df_records['Puntos'].idxmax()]
            st.success(f"**{mejor_jornada['Mánager']}**")
            st.metric(label=f"Jornada {int(mejor_jornada['Jornada'])} ({mejor_jornada['Temporada']})", value=f"{mejor_jornada['Puntos']} pts")
            
        # 🔴 PEOR PUNTUACIÓN EN UNA JORNADA
        with col2:
            st.subheader("💩 El Mayor Desastre")
            peor_jornada = df_records.loc[df_records['Puntos'].idxmin()]
            st.error(f"**{peor_jornada['Mánager']}**")
            st.metric(label=f"Jornada {int(peor_jornada['Jornada'])} ({peor_jornada['Temporada']})", value=f"{peor_jornada['Puntos']} pts")

        st.markdown("---")
        st.subheader("🏅 El Medallero (Más veces MVP de la Jornada)")
        st.write("¿Quién ha ganado más jornadas a lo largo de la historia?")
        
        # Calcular MVP de cada jornada en toda la historia
        idx_mvps = df_records.groupby(['Temporada', 'Jornada'])['Puntos'].idxmax()
        df_mvps = df_records.loc[idx_mvps]
        conteo_mvps = df_mvps['Mánager'].value_counts().reset_index()
        conteo_mvps.columns = ['Mánager', 'Victorias de Jornada']
        conteo_mvps.index = conteo_mvps.index + 1
        
        st.dataframe(conteo_mvps, use_container_width=True)

    # ==========================================
    # PANTALLAS EN CONSTRUCCIÓN
    # ==========================================
    elif menu in ["👤 Perfiles (Próximamente)", "⚔️ Cara a Cara (Próximamente)"]:
        st.title(menu.split(" ")[0] + " " + menu.split(" ")[1])
        st.info("🚧 Estamos trabajando en esta sección. ¡Pronto habrá más salseo!")

else:
    st.error("❌ Faltan los archivos de datos. Comprueba que los Excels estén generados en sus carpetas.")