import streamlit as st
import pandas as pd
import os

# ⚙️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Liga Santanguissa", page_icon="🏆", layout="wide")

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
        mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
        
        # Mapeo manual para Arsenati (Histórico)
        mapeo_nombres['LEGACY_ARSENATI'] = 'Arsenati (Histórico)'
        
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
        
        # Cargar archivo de Ligas si existe
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
        # Cargar archivo de Copas si existe
        if os.path.exists(ruta_copas):
            df_copas = pd.read_excel(ruta_copas)
            df_copas['Mánager'] = df_copas['ID_Futmondo'].map(mapeo_nombres).fillna(df_copas['ID_Futmondo'])
            
    return df, df_ligas, df_copas

df, df_ligas, df_copas = cargar_datos()

if df is not None:
    # 🗂️ MENÚ DE NAVEGACIÓN LATERAL
    st.sidebar.title("⚽ Menú de Liga")
    menu = st.sidebar.radio("Navegación", [
        "🏠 Visión General", 
        "🏆 Salón de la Fama", 
        "🥇 Palmarés Histórico",
        "👤 Perfiles (Próximamente)", 
        "⚔️ Cara a Cara (Próximamente)"
    ])
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ Info Histórica Importante"):
        st.caption("• **2020/21**: Faltan los datos de la temporada inaugural.")
        st.caption("• **2022/23**: **Pallejandro** se une sustituyendo a **Arsenati**.")
        st.caption("• **2024/25**: Solo hay foto final de puntos acumulados. Sus jornadas no cuentan para récords ni MVPs.")

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
        st.title("🏆 El Salón de la Fama")
        st.markdown("---")
        
        df_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26')) & (df['Temporada'] != '2024/25')]
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚀 La Mayor Exhibición")
            mejor_jornada = df_records.loc[df_records['Puntos'].idxmax()]
            st.success(f"**{mejor_jornada['Mánager']}**")
            st.metric(label=f"Jornada {int(mejor_jornada['Jornada'])} ({mejor_jornada['Temporada']})", value=f"{mejor_jornada['Puntos']} pts")
            
        with col2:
            st.subheader("💩 El Mayor Desastre")
            df_desastres = df_records[df_records['Puntos'] > 0]
            if not df_desastres.empty:
                peor_jornada = df_desastres.loc[df_desastres['Puntos'].idxmin()]
                st.error(f"**{peor_jornada['Mánager']}**")
                st.metric(label=f"Jornada {int(peor_jornada['Jornada'])} ({peor_jornada['Temporada']})", value=f"{peor_jornada['Puntos']} pts")
            st.caption("ℹ️ *No se tienen en cuenta las jornadas con 0 puntos o puntuación negativa.*")

        st.markdown("---")
        st.subheader("🏅 El Medallero de Jornadas (MVPs)")
        idx_mvps = df_records.groupby(['Temporada', 'Jornada'])['Puntos'].idxmax()
        df_mvps = df_records.loc[idx_mvps]
        conteo_mvps = df_mvps['Mánager'].value_counts().reset_index()
        conteo_mvps.columns = ['Mánager', 'Victorias de Jornada']
        conteo_mvps.index = conteo_mvps.index + 1
        st.dataframe(conteo_mvps, use_container_width=True)

    # ==========================================
    # PANTALLA 3: PALMARÉS HISTÓRICO
    # ==========================================
    elif menu == "🥇 Palmarés Histórico":
        st.title("🥇 Vitrina de Trofeos")
        st.markdown("---")
        
        col_liga, col_copa = st.columns(2)
        
        # 1. Mostrar las Ligas
        with col_liga:
            st.subheader("🏆 Campeones de Liga")
            if df_ligas is not None:
                df_ligas_vista = df_ligas.pivot(index='Temporada', columns='Posicion', values='Mánager').reset_index()
                cols = ['Temporada']
                if 'Campeón' in df_ligas_vista.columns: cols.append('Campeón')
                if 'Subcampeón' in df_ligas_vista.columns: cols.append('Subcampeón')
                df_ligas_vista = df_ligas_vista[cols]
                st.dataframe(df_ligas_vista, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No se ha generado el palmarés de liga.")

        # 2. Mostrar las Copas
        with col_copa:
            st.subheader("🏆 Campeones de Copa")
            if df_copas is not None:
                df_copas_vista = df_copas.pivot(index=['Temporada', 'Copa'], columns='Posicion', values='Mánager').reset_index()
                df_copas_vista['Competición'] = "Copa " + df_copas_vista['Copa'].astype(str)
                
                cols = ['Temporada', 'Competición']
                if 'Campeón' in df_copas_vista.columns: cols.append('Campeón')
                if 'Finalista' in df_copas_vista.columns: cols.append('Finalista')
                
                df_copas_vista = df_copas_vista[cols]
                st.dataframe(df_copas_vista, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No se ha encontrado el palmarés de copas.")
                
        # 3. Recuento Total de Títulos
        st.markdown("---")
        st.subheader("👑 Reyes de la Liga (Recuento de Títulos)")
        
        campeones = []
        if df_ligas is not None:
            campeones_liga = df_ligas[df_ligas['Posicion'] == 'Campeón'][['Mánager']].copy()
            campeones_liga['Trofeo'] = 'Ligas'
            campeones.append(campeones_liga)
            
        if df_copas is not None:
            campeones_copa = df_copas[df_copas['Posicion'] == 'Campeón'][['Mánager']].copy()
            campeones_copa['Trofeo'] = 'Copas'
            campeones.append(campeones_copa)
            
        if campeones:
            df_todos_titulos = pd.concat(campeones, ignore_index=True)
            tabla_titulos = df_todos_titulos.groupby(['Mánager', 'Trofeo']).size().unstack(fill_value=0).reset_index()
            
            if 'Ligas' not in tabla_titulos.columns: tabla_titulos['Ligas'] = 0
            if 'Copas' not in tabla_titulos.columns: tabla_titulos['Copas'] = 0
            
            tabla_titulos['Total Títulos'] = tabla_titulos['Ligas'] + tabla_titulos['Copas']
            tabla_titulos = tabla_titulos.sort_values(by=['Total Títulos', 'Ligas'], ascending=[False, False]).reset_index(drop=True)
            tabla_titulos.index = tabla_titulos.index + 1
            
            st.dataframe(tabla_titulos[['Mánager', 'Ligas', 'Copas', 'Total Títulos']], use_container_width=True)

    elif menu in ["👤 Perfiles (Próximamente)", "⚔️ Cara a Cara (Próximamente)"]:
        st.title(menu)
        st.info("🚧 Estamos trabajando en esta sección. ¡Pronto habrá más salseo!")

else:
    st.error("❌ Faltan los archivos de datos globales.")