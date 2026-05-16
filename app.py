import streamlit as st
import pandas as pd
import altair as alt
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
        
        df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
        
        if os.path.exists(ruta_ligas):
            df_ligas = pd.read_excel(ruta_ligas)
            df_ligas['Mánager'] = df_ligas['ID_Futmondo'].map(mapeo_nombres).fillna(df_ligas['ID_Futmondo'])
            
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
        
        # Filtramos la temporada y usamos .copy() para poder añadir columnas nuevas sin avisos de Pandas
        df_temp = df[df['Temporada'] == temporada_sel].copy()
        
        # 🧮 CALCULAMOS LA POSICIÓN JORNADA A JORNADA
        df_temp['Posición'] = df_temp.groupby('Jornada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
        
        jornada_maxima = int(df_temp['Jornada'].max())
        
        rango_jornadas = st.slider("🔍 Rango de Jornadas en Gráficas", 1, jornada_maxima, (1, jornada_maxima))
        
        col1, col2 = st.columns([1, 1.8])
        with col1:
            st.subheader(f"📊 Tabla (Jornada {jornada_maxima})")
            df_clasif = df_temp[df_temp['Jornada'] == jornada_maxima].sort_values(by="Puntos_Acumulados", ascending=False)
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
            st.dataframe(df_mostrar, use_container_width=True)
            
        with col2:
            st.subheader("📈 Análisis de Evolución")
            
            # Filtramos los datos para el slider
            df_temp_grafica = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
            
            # 🗂️ PESTAÑAS PARA LAS GRÁFICAS
            tab_pos, tab_pts = st.tabs(["🎢 Evolución de Posición", "📈 Puntos Acumulados"])
            
            # GRÁFICA DE POSICIONES (EJE INVERTIDO Y BLOQUEADO CON ALTAIR)
            with tab_pos:
                # Contamos cuántos mánagers hay para fijar el límite del eje Y
                num_managers = df_temp['Mánager'].nunique()
                # Creamos una lista con todos los números [1, 2, 3... hasta num_managers] para las etiquetas
                lista_posiciones = list(range(1, num_managers + 1))
                
                grafica_posiciones = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                    x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('Posición:Q', 
                            scale=alt.Scale(domain=[num_managers, 1]), 
                            title='Posición', 
                            axis=alt.Axis(values=lista_posiciones, format='d', tickMinStep=1)), # <- Forzamos a pintar cada número
                    color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="right")),
                    tooltip=['Mánager', 'Jornada', 'Posición', 'Puntos_Acumulados']
                ).properties(height=420)
                
                st.altair_chart(grafica_posiciones, use_container_width=True)
                
            # GRÁFICA DE PUNTOS (CON ALTAIR Y LÍMITES DINÁMICOS)
            with tab_pts:
                # Calculamos el mínimo y máximo de puntos en el tramo seleccionado
                min_pts = int(df_temp_grafica['Puntos_Acumulados'].min())
                max_pts = int(df_temp_grafica['Puntos_Acumulados'].max())
                
                # Le damos un 5% de margen por arriba y por abajo (o un mínimo de 20 puntos si están muy empatados)
                margen = max(20, int((max_pts - min_pts) * 0.05)) 
                
                grafica_puntos = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                    x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('Puntos_Acumulados:Q', 
                            scale=alt.Scale(domain=[min_pts - margen, max_pts + margen]), 
                            title='Puntos Acumulados'),
                    color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="right")),
                    tooltip=['Mánager', 'Jornada', 'Puntos_Acumulados', 'Posición'] # He añadido la posición al tooltip como extra
                ).properties(height=420)
                
                st.altair_chart(grafica_puntos, use_container_width=True)

    # ==========================================
    # PANTALLA 2: SALÓN DE LA FAMA
    # ==========================================
    elif menu == "🏆 Salón de la Fama":
        st.title("🏆 El Salón de la Fama")
        st.write("Consulta los mejores y peores registros históricos o fíltralos por una temporada concreta.")
        st.markdown("---")
        
        df_base_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26')) & (df['Temporada'] != '2024/25')]
        
        col_filtro_sf, _ = st.columns([1, 3])
        with col_filtro_sf:
            lista_temporadas = ["Todas las temporadas"] + sorted(df_base_records['Temporada'].unique().tolist(), reverse=True)
            temporada_sf_sel = st.selectbox("📅 Filtrar por Temporada:", lista_temporadas, index=0)
            
        if temporada_sf_sel != "Todas las temporadas":
            df_records = df_base_records[df_base_records['Temporada'] == temporada_sf_sel]
        else:
            df_records = df_base_records
            
        df_desastres = df_records[df_records['Puntos'] > 0]
        
        if not df_records.empty:
            limite_mejores = min(10, len(df_records))
            limite_peores = min(10, len(df_desastres))
            
            top10_mejores = df_records.nlargest(limite_mejores, 'Puntos').reset_index(drop=True)
            top10_peores = df_desastres.nsmallest(limite_peores, 'Puntos').reset_index(drop=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Las Mejores Exhibiciones")
                if not top10_mejores.empty:
                    top1 = top10_mejores.iloc[0]
                    st.success(f"🥇 **{top1['Mánager']}**")
                    st.metric(label=f"Jornada {int(top1['Jornada'])} ({top1['Temporada']})", value=f"{top1['Puntos']} pts")
                    
                    c_top2, c_top3 = st.columns(2)
                    with c_top2:
                        if len(top10_mejores) > 1:
                            top2 = top10_mejores.iloc[1]
                            st.info(f"🥈 **{top2['Mánager']}**")
                            st.markdown(f"**{top2['Puntos']} pts** (J{int(top2['Jornada'])} - {top2['Temporada']})")
                    with c_top3:
                        if len(top10_mejores) > 2:
                            top3 = top10_mejores.iloc