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
    # 🔄 CONTROL DE NAVEGACIÓN MEDIANTE SESSION STATE
    if 'pantalla' not in st.session_state:
        st.session_state.pantalla = "🏠 Menú Principal"

    # 🗂️ BARRA LATERAL
    st.sidebar.title("⚽ Menú de Liga")
    opciones_sidebar = [
        "🏠 Menú Principal",
        "📈 Análisis por temporadas", 
        "🏆 Salón de la Fama", 
        "🥇 Palmarés Histórico",
        "👤 Perfiles (Próximamente)", 
        "⚔️ Cara a Cara"
    ]
    
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
    # PANTALLA 0: MENÚ PRINCIPAL
    # ==========================================
    if st.session_state.pantalla == "🏠 Menú Principal":
        st.title("🏆 Liga Santanguissa - Panel de Control")
        st.subheader("Bienvenido a la web oficial de estadísticas y datos históricos de LaLiga Santanguissa.")
        st.markdown("---")
        
        st.write("Selecciona una sección para empezar a analizar los datos:")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📈 Análisis por temporadas", use_container_width=True):
                st.session_state.pantalla = "📈 Análisis por temporadas"
                st.rerun()
            st.caption("Consulta las tablas dinámicas por jornada y el scalextric de gráficas temporales.")
            
            st.markdown("##")
            if st.button("🥇 Vitrina de Trofeos e Historial", use_container_width=True):
                st.session_state.pantalla = "🥇 Palmarés Histórico"
                st.rerun()
            st.caption("El palmarés completo de ligas y copas, y el ranking de reyes de títulos.")

        with c2:
            if st.button("🏆 El Salón de la Fama (Récords)", use_container_width=True):
                st.session_state.pantalla = "🏆 Salón de la Fama"
                st.rerun()
            st.caption("El Top 10 histórico de mayores exhibiciones, rachas, desastres y el Club de los 100.")
            
            st.markdown("##")
            if st.button("⚔️ Cara a Cara", use_container_width=True):
                st.session_state.pantalla = "⚔️ Cara a Cara"
                st.rerun()
            st.caption("Cruza las trayectorias de dos o más mánagers y descubre quién manda en vuestros duelos.")

    # ==========================================
    # PANTALLA 1: ANÁLISIS POR TEMPORADAS
    # ==========================================
    elif st.session_state.pantalla == "📈 Análisis por temporadas":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("🏆 Salón de la Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav3.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
        if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
            
        st.title("📈 Análisis por temporadas")
        st.markdown("---")
        
        col_filtros, col_vacio = st.columns([1, 3])
        with col_filtros:
            temporadas = df['Temporada'].unique().tolist()
            temporada_sel = st.selectbox("📅 Selecciona la Temporada", temporadas, index=len(temporadas)-1)
        
        df_temp = df[df['Temporada'] == temporada_sel].copy()
        
        if temporada_sel == "2024/25":
            st.subheader("📊 Tabla Final (Temporada 2024/25)")
            jornada_max_2425 = df_temp['Jornada'].max()
            df_clasif = df_temp[df_temp['Jornada'] == jornada_max_2425].sort_values(by="Puntos_Acumulados", ascending=False)
            
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
            
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.index.name = "Pos."
            df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
            
            col_tabla, col_info = st.columns([1, 1.8])
            with col_tabla:
                st.dataframe(df_mostrar, use_container_width=True)
            with col_info:
                st.info("ℹ️ Para la temporada 2024/25 solo disponemos del cierre de puntos acumulados. Por este motivo, las gráficas de evolución temporal por jornada no están habilitadas.")
                
        else:
            df_temp['Posición'] = df_temp.groupby('Jornada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
            df_temp['Posición_Jornada'] = df_temp.groupby('Jornada')['Puntos'].rank(method='min', ascending=False).astype(int)
            
            jornada_maxima = int(df_temp['Jornada'].max())
            
            col1, col2 = st.columns([1, 1.8])
            
            with col1:
                rango_jornadas = st.slider("🔍 Rango de Jornadas", 1, jornada_maxima, (1, jornada_maxima))
                jornada_seleccionada = rango_jornadas[1] 
                
                st.subheader(f"📊 Tabla (Jornada {jornada_seleccionada})")
                df_clasif = df_temp[df_temp['Jornada'] == jornada_seleccionada].sort_values(by="Puntos_Acumulados", ascending=False)
                df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
                df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
                
                df_mostrar.index = df_mostrar.index + 1 
                df_mostrar.index.name = "Pos."
                df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
                
                st.dataframe(df_mostrar, use_container_width=True)
                
            with col2:
                lista_managers_disponibles = sorted(df_temp['Mánager'].unique().tolist())
                managers_seleccionados = st.multiselect(
                    "👥 Filtrar Equipos en Gráficas:", 
                    lista_managers_disponibles, 
                    default=[],
                    placeholder="Todos los equipos (selecciona para aislar)"
                )
                
                if len(managers_seleccionados) == 0:
                    managers_seleccionados = lista_managers_disponibles
                
                st.caption("💡 *Tip: Usa el buscador de equipos de arriba y el deslizador de jornadas para aislar trayectorias y ver el gráfico mucho más limpio.*")
                
                df_temp_grafica = df_temp[
                    (df_temp['Jornada'] >= rango_jornadas[0]) & 
                    (df_temp['Jornada'] <= rango_jornadas[1]) &
                    (df_temp['Mánager'].isin(managers_seleccionados))
                ]
                
                if not df_temp_grafica.empty:
                    num_managers_total = df_temp['Mánager'].nunique()
                    lista_posiciones_total = list(range(1, num_managers_total + 1))
                    leyenda_config = alt.Legend(title=None, orient="bottom", columns=2)
                    
                    # --- BLOQUE 1: ANÁLISIS ACUMULADO (AQUÍ ARRIBA AHORA) ---
                    st.markdown("---")
                    st.subheader("📊 Análisis Acumulado (Clasificación General)")
                    tab_pos_acu, tab_pts_acu, tab_mat_acu = st.tabs(["🎢 Posición", "📈 Puntos", "🔢 Matriz"])
                    
                    with tab_pos_acu:
                        grafica_posiciones = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Posición:Q', 
                                    scale=alt.Scale(domain=[num_managers_total, 1]), 
                                    title='Posición Acumulada', 
                                    axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
                            color=alt.Color('Mánager:N', legend=leyenda_config),
                            tooltip=['Mánager', 'Jornada', 'Posición', 'Puntos_Acumulados']
                        ).properties(height=420)
                        st.altair_chart(grafica_posiciones, use_container_width=True)

                    with tab_pts_acu:
                        min_pts_acu = int(df_temp_grafica['Puntos_Acumulados'].min())
                        max_pts_acu = int(df_temp_grafica['Puntos_Acumulados'].max())
                        margen_acu = max(20, int((max_pts_acu - min_pts_acu) * 0.05))
                        
                        grafica_puntos_acu = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Puntos_Acumulados:Q', 
                                    scale=alt.Scale(domain=[min_pts_acu - margen_acu, max_pts_acu + margen_acu]), 
                                    title='Puntos Acumulados'),
                            color=alt.Color('Mánager:N', legend=leyenda_config),
                            tooltip=['Mánager', 'Jornada', 'Puntos_Acumulados', 'Posición']
                        ).properties(height=420)
                        st.altair_chart(grafica_puntos_acu.interactive(), use_container_width=True)

                    with tab_mat_acu:
                        df_matriz_acum = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Posición')
                        st.dataframe(df_matriz_acum.style.format(precision=0, na_rep="-"), use_container_width=True)

                    # --- BLOQUE 2: ANÁLISIS DE LA JORNADA (AQUÍ ABAJO AHORA) ---
                    st.markdown("---")
                    st.subheader("⚡ Análisis de la Jornada Aislada")
                    tab_pos_jor, tab_pts_jor, tab_mat_jor = st.tabs(["🎯 Posición", "⚡ Puntos", "🔢 Matriz"])
                    
                    with tab_pos_jor:
                        grafica_pos_jornada = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Posición_Jornada:Q', 
                                    scale=alt.Scale(domain=[num_managers_total, 1]), 
                                    title='Posición en la Jornada', 
                                    axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
                            color=alt.Color('Mánager:N', legend=leyenda_config),
                            tooltip=['Mánager', 'Jornada', 'Puntos', 'Posición_Jornada']
                        ).properties(height=420)
                        st.altair_chart(grafica_pos_jornada, use_container_width=True)

                    with tab_pts_jor:
                        min_pts_jor = int(df_temp_grafica['Puntos'].min())
                        max_pts_jor = int(df_temp_grafica['Puntos'].max())
                        margen_jor = max(10, int((max_pts_jor - min_pts_jor) * 0.1))
                        
                        grafica_puntos_jor = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Puntos:Q', 
                                    scale=alt.Scale(domain=[min_pts_jor - margen_jor, max_pts_jor + margen_jor]), 
                                    title='Puntos en la Jornada'),
                            color=alt.Color('Mánager:N', legend=leyenda_config),
                            tooltip=['Mánager', 'Jornada', 'Puntos', 'Posición_Jornada']
                        ).properties(height=420)
                        st.altair_chart(grafica_puntos_jor, use_container_width=True)

                    with tab_mat_jor:
                        df_matriz_jor = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Posición_Jornada')
                        st.dataframe(df_matriz_jor.style.format(precision=0, na_rep="-"), use_container_width=True)
                else:
                    st.warning("⚠️ Selecciona al menos un mánager en el filtro para pintar los análisis.")

    # ==========================================
    # PANTALLA 2: SALÓN DE LA FAMA
    # ==========================================
    elif st.session_state.pantalla == "🏆 Salón de la Fama":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
        if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
            
        st.title("🏆 El Salón de la Fama")
        st.write("Consulta los mayores hitos, desastres y rachas de la historia de LaLiga Santanguissa.")
        st.markdown("---")
        
        df_base_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26')) & (df['Temporada'] != '2024/25')].copy()
        
        col_filtro_sf, _ = st.columns([1, 3])
        with col_filtro_sf:
            lista_temporadas_reales = sorted(df_base_records['Temporada'].unique().tolist(), reverse=True)
            temporadas_sf_sel = st.multiselect(
                "📅 Filtrar por Temporada(s):", 
                lista_temporadas_reales, 
                default=[],
                placeholder="Todas las temporadas"
            )
            
        if len(temporadas_sf_sel) > 0:
            df_records = df_base_records[df_base_records['Temporada'].isin(temporadas_sf_sel)].copy()
            texto_filtro = ", ".join(temporadas_sf_sel)
        else:
            df_records = df_base_records.copy()
            texto_filtro = "Todas las temporadas"
            
        df_desastres = df_records[df_records['Puntos'] > 0]
        
        # --- BLOQUE 1: PUNTUACIONES EN UNA JORNADA ---
        if not df_records.empty:
            limite_mejores = min(10, len(df_records))
            limite_peores = min(10, len(df_desastres))
            
            top10_mejores = df_records.nlargest(limite_mejores, 'Puntos').reset_index(drop=True)
            top10_peores = df_desastres.nsmallest(limite_peores, 'Puntos').reset_index(drop=True)
            
            st.header("⚡ Hitos en una sola Jornada")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Las Mejores Exhibiciones")
                if not top10_mejores.empty:
                    top1 = top10_mejores.iloc[0]
                    st.success(f"🥇 **{top1['Mánager']}**")
                    st.metric(label=f"Jornada {int(top1['Jornada'])} ({top1['Temporada']})", value=f"{top1['Puntos']} pts")
                    
                    df_resto_mejores = top10_mejores.iloc[1:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
                    df_resto_mejores.index = range(2, 2 + len(df_resto_mejores))
                    df_resto_mejores.index.name = "Pos."
                    df_resto_mejores = df_resto_mejores.reset_index().set_index(['Pos.', 'Mánager'])
                    st.dataframe(df_resto_mejores, use_container_width=True)
                
            with col2:
                st.subheader("☠️ Los Mayores Desastres")
                if not top10_peores.empty:
                    bot1 = top10_peores.iloc[0]
                    st.error(f"🥇 **{bot1['Mánager']}**")
                    st.metric(label=f"Jornada {int(bot1['Jornada'])} ({bot1['Temporada']})", value=f"{bot1['Puntos']} pts")
                    
                    df_resto_peores = top10_peores.iloc[1:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
                    df_resto_peores.index = range(2, 2 + len(df_resto_peores))
                    df_resto_peores.index.name = "Pos."
                    df_resto_peores = df_resto_peores.reset_index().set_index(['Pos.', 'Mánager'])
                    st.dataframe(df_resto_peores, use_container_width=True)

        st.markdown("---")
        
        # --- BLOQUE 2: RÉCORDS DE TEMPORADA COMPLETA ---
        st.header("👑 Récords de Temporada Completa")
        df_finales = df_records.loc[df_records.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()].copy()
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("🏆 Mayor Puntuación Final")
            top10_temp_max = df_finales.nlargest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada']]
            top10_temp_max.columns = ['Mánager', 'Puntos Totales', 'Temporada']
            top10_temp_max.index = range(1, 1 + len(top10_temp_max))
            top10_temp_max.index.name = "Pos."
            st.dataframe(top10_temp_max.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
            
        with col_t2:
            st.subheader("📉 Peor Puntuación Final")
            top10_temp_min = df_finales.nsmallest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada']]
            top10_temp_min.columns = ['Mánager', 'Puntos Totales', 'Temporada']
            top10_temp_min.index = range(1, 1 + len(top10_temp_min))
            top10_temp_min.index.name = "Pos."
            st.dataframe(top10_temp_min.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

        st.markdown("---")

        # --- BLOQUE 3: RACHAS HISTÓRICAS ---
        st.header("🔥 Rachas Históricas")
        df_rachas = df_records.copy()
        
        df_rachas['Pos_Acum'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=False)
        df_rachas['Pos_Acum_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=True)
        
        df_lideres = df_rachas[df_rachas['Pos_Acum'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_lideres['Grupo_Racha'] = (df_lideres['Jornada'] != df_lideres['Jornada'].shift() + 1).cumsum()
        rachas_lider = df_lideres.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(
            Jornadas_Seguidas=('Jornada', 'size'),
            J_Inicio=('Jornada', 'min'),
            J_Fin=('Jornada', 'max')
        ).reset_index()
        rachas_lider['Rango'] = "J" + rachas_lider['J_Inicio'].astype(int).astype(str) + " - J" + rachas_lider['J_Fin'].astype(int).astype(str)
        top10_rachas_lider = rachas_lider.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']]
        top10_rachas_lider.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada']
        
        df_ultimos_streak = df_rachas[df_rachas['Pos_Acum_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_ultimos_streak['Grupo_Racha'] = (df_ultimos_streak['Jornada'] != df_ultimos_streak['Jornada'].shift() + 1).cumsum()
        rachas_ultimo = df_ultimos_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(
            Jornadas_Seguidas=('Jornada', 'size'),
            J_Inicio=('Jornada', 'min'),
            J_Fin=('Jornada', 'max')
        ).reset_index()
        rachas_ultimo['Rango'] = "J" + rachas_ultimo['J_Inicio'].astype(int).astype(str) + " - J" + rachas_ultimo['J_Fin'].astype(int).astype(str)
        top10_rachas_ultimo = rachas_ultimo.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']]
        top10_rachas_ultimo.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada']

        df_rachas['Pos_Jor_Mejor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
        df_rachas['Pos_Jor_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=True)
        
        df_mvp_streak = df_rachas[df_rachas['Pos_Jor_Mejor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_mvp_streak['Grupo_Racha'] = (df_mvp_streak['Jornada'] != df_mvp_streak['Jornada'].shift() + 1).cumsum()
        rachas_mvp = df_mvp_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(
            Jornadas_Seguidas=('Jornada', 'size'),
            J_Inicio=('Jornada', 'min'),
            J_Fin=('Jornada', 'max')
        ).reset_index()
        rachas_mvp['Rango'] = "J" + rachas_mvp['J_Inicio'].astype(int).astype(str) + " - J" + rachas_mvp['J_Fin'].astype(int).astype(str)
        top10_rachas_mvp = rachas_mvp.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']]
        top10_rachas_mvp.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada']
        
        df_peor_streak = df_rachas[df_rachas['Pos_Jor_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_peor_streak['Grupo_Racha'] = (df_peor_streak['Jornada'] != df_peor_streak['Jornada'].shift() + 1).cumsum()
        rachas_peor_jor = df_peor_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(
            Jornadas_Seguidas=('Jornada', 'size'),
            J_Inicio=('Jornada', 'min'),
            J_Fin=('Jornada', 'max')
        ).reset_index()
        rachas_peor_jor['Rango'] = "J" + rachas_peor_jor['J_Inicio'].astype(int).astype(str) + " - J" + rachas_peor_jor['J_Fin'].astype(int).astype(str)
        top10_rachas_peor_jor = rachas_peor_jor.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']]
        top10_rachas_peor_jor.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada']

        st.subheader("El Trono y El Pozo de la Clasificación General")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.caption("👑 **Líderes de Hierro** (Semanas consecutivas siendo 1º)")
            top10_rachas_lider.index = range(1, 1 + len(top10_rachas_lider))
            top10_rachas_lider.index.name = "Rank"
            st.dataframe(top10_rachas_lider.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)
        with col_r2:
            st.caption("⚓ **Fango Eterno** (Semanas consecutivas siendo último)")
            top10_rachas_ultimo.index = range(1, 1 + len(top10_rachas_ultimo))
            top10_rachas_ultimo.index.name = "Rank"
            st.dataframe(top10_rachas_ultimo.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Héroes y Villanos del Fin de Semana")
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.caption("🌟 **MVP en Serie** (Jornadas seguidas haciendo la mejor puntuación)")
            top10_rachas_mvp.index = range(1, 1 + len(top10_rachas_mvp))
            top10_rachas_mvp.index.name = "Rank"
            st.dataframe(top10_rachas_mvp.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)
        with col_r4:
            st.caption("🤦‍♂️ **Ruina Consecutiva** (Jornadas seguidas haciendo la peor puntuación)")
            top10_rachas_peor_jor.index = range(1, 1 + len(top10_rachas_peor_jor))
            top10_rachas_peor_jor.index.name = "Rank"
            st.dataframe(top10_rachas_peor_jor.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)

        st.markdown("---")

        # --- BLOQUE 4: MEDALLERO Y CLUB DE LOS 100 ---
        col_m1, col_m2 = st.columns([1.5, 1])
        
        with col_m1:
            st.subheader("🏅 Medallero de Jornadas (y retratadas)")
            st.caption(f"Filtro aplicado: **{texto_filtro}**")
            
            if not df_records.empty:
                df_medallero = df_records.copy()
                df_medallero['Rank_Mejor'] = df_medallero.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
                df_medallero['Rank_Peor'] = df_medallero.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=True)
                
                df_oros = df_medallero[df_medallero['Rank_Mejor'] == 1].groupby('Mánager').size()
                df_platas = df_medallero[df_medallero['Rank_Mejor'] == 2].groupby('Mánager').size()
                df_penultimos = df_medallero[df_medallero['Rank_Peor'] == 2].groupby('Mánager').size()
                df_ultimos = df_medallero[df_medallero['Rank_Peor'] == 1].groupby('Mánager').size()
                
                tabla_medallas = pd.DataFrame({
                    '🥇 1º (Oros)': df_oros,
                    '🥈 2º (Platas)': df_platas,
                    '⚠️ Penúltimos': df_penultimos,
                    '💩 Últimos': df_ultimos
                }).fillna(0).astype(int)
                
                tabla_medallas = tabla_medallas.sort_values(by=['🥇 1º (Oros)', '🥈 2º (Platas)'], ascending=[False, False]).reset_index()
                tabla_medallas.index = tabla_medallas.index + 1
                tabla_medallas.index.name = "Pos."
                st.dataframe(tabla_medallas.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
                
        with col_m2:
            st.subheader("💯 El Club de los 100")
            st.caption("Veces que se han sumado ≥ 100 puntos en una jornada.")
            df_100 = df_records[df_records['Puntos'] >= 100]
            if not df_100.empty:
                ranking_100 = df_100.groupby('Mánager').size().reset_index(name='Veces ≥ 100 pts')
                ranking_100 = ranking_100.sort_values(by='Veces ≥ 100 pts', ascending=False).reset_index(drop=True)
                ranking_100.index = ranking_100.index + 1
                ranking_100.index.name = "Pos."
                st.dataframe(ranking_100.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
            else:
                st.info("Nadie ha llegado a los 100 puntos con este filtro.")

    # ==========================================
    # PANTALLA 3: PALMARÉS HISTÓRICO
    # ==========================================
    elif st.session_state.pantalla == "🥇 Palmarés Histórico":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
            
        st.title("🥇 Vitrina de Trofeos")
        st.markdown("---")
        
        col_liga, col_copa = st.columns(2)
        
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
            tabla_titulos.index.name = "Pos."
            tabla_titulos = tabla_titulos.reset_index().set_index(['Pos.', 'Mánager'])
            
            st.dataframe(tabla_titulos[['Ligas', 'Copas', 'Total Títulos']], use_container_width=True)

    # ==========================================
    # PANTALLA 4: CARA A CARA (¡NUEVO!)
    # ==========================================
    elif st.session_state.pantalla == "⚔️ Cara a Cara":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
            
        st.title("⚔️ Cara a Cara (Head-to-Head)")
        st.markdown("---")
        
        # Filtro de mánagers vacío por defecto
        lista_todos_managers = sorted(df['Mánager'].unique().tolist())
        st.write("Elige a los contendientes para ver quién es el padre de quién históricamente:")
        
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            managers_h2h = st.multiselect(
                "👥 Selecciona Mánagers (mínimo 2):", 
                lista_todos_managers, 
                default=[]
            )
            
        if len(managers_h2h) < 2:
            st.warning("⚠️ **¡Cobardes!** Selecciona al menos a dos mánagers para meterlos en la jaula de barro y ver el historial.")
        else:
            # 🛡️ TRUCO MAGIA: Calcular temporadas donde coincidieron TODOS los elegidos
            df_h2h_base = df[df['Mánager'].isin(managers_h2h) & (df['Temporada'] != '2024/25')]
            temporadas_por_manager = df_h2h_base.groupby('Temporada')['Mánager'].nunique()
            temporadas_comunes = temporadas_por_manager[temporadas_por_manager == len(managers_h2h)].index.tolist()
            temporadas_comunes = sorted(temporadas_comunes, reverse=True)
            
            if not temporadas_comunes:
                st.error("❌ Los mánagers seleccionados nunca han coincidido en la misma temporada.")
            else:
                with col_f2:
                    temporadas_h2h_sel = st.multiselect(
                        "📅 Temporadas en las que han coincidido (filtra si quieres):", 
                        temporadas_comunes, 
                        default=temporadas_comunes
                    )
                
                if len(temporadas_h2h_sel) == 0:
                    st.warning("Selecciona al menos una temporada.")
                else:
                    st.markdown("---")
                    # Filtramos los datos finales para la pelea
                    df_h2h = df_h2h_base[df_h2h_base['Temporada'].isin(temporadas_h2h_sel)]
                    
                    # 1. MATRIZ DE ENFRENTAMIENTOS (Con empates incluidos)
                    st.subheader("🥊 Matriz de Enfrentamientos Directos")
                    st.caption("Lee por filas: veces que el mánager de la fila le sacó más puntos en una jornada al mánager de la columna. *(Los empates suman +1 para ambos)*.")
                    
                    df_pivot_h2h = df_h2h.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos')
                    
                    matriz_dict = {m1: {m2: 0 for m2 in managers_h2h} for m1 in managers_h2h}
                    
                    for m1 in managers_h2h:
                        for m2 in managers_h2h:
                            if m1 != m2:
                                # Victorias de m1 sobre m2 (estrictamente mayor)
                                wins = (df_pivot_h2h[m1] > df_pivot_h2h[m2]).sum()
                                # Empates
                                ties = (df_pivot_h2h[m1] == df_pivot_h2h[m2]).sum()
                                matriz_dict[m1][m2] = wins + ties
                            else:
                                matriz_dict[m1][m2] = "-" # Diagonal
                                
                    df_matriz_pelea = pd.DataFrame(matriz_dict).T
                    st.dataframe(df_matriz_pelea, use_container_width=True)
                    
                    # 2. QUESO DE VICTORIAS EXCLUSIVAS (Sin empates)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("🧀 Dominio del Grupo (El Queso de la Gloria)")
                    st.caption(f"Jornadas en las que un mánager ha sacado **la mejor puntuación de todo el grupo seleccionado** sin empatar con nadie.")
                    
                    # Buscamos al campeón absoluto de cada jornada dentro del subset
                    ganadores_absolutos = []
                    for idx, row in df_pivot_h2h.iterrows():
                        max_puntos_grupo = row.max()
                        managers_con_max = row[row == max_puntos_grupo].index.tolist()
                        
                        # Solo hay victoria si hay UN único mánager con la puntuación máxima
                        if len(managers_con_max) == 1:
                            ganadores_absolutos.append(managers_con_max[0])
                            
                    if ganadores_absolutos:
                        df_queso = pd.Series(ganadores_absolutos).value_counts().reset_index()
                        df_queso.columns = ['Mánager', 'Victorias Absolutas']
                        
                        # Asegurarnos de que salgan a 0 los que no tienen victorias
                        para_añadir = [m for m in managers_h2h if m not in df_queso['Mánager'].tolist()]
                        if para_añadir:
                            df_ceros = pd.DataFrame({'Mánager': para_añadir, 'Victorias Absolutas': [0]*len(para_añadir)})
                            df_queso = pd.concat([df_queso, df_ceros], ignore_index=True)
                            
                        # Gráfico circular (Quesito / Donut) con Altair
                        grafica_queso = alt.Chart(df_queso).mark_arc(innerRadius=60, stroke="#fff", strokeWidth=2).encode(
                            theta=alt.Theta(field="Victorias Absolutas", type="quantitative"),
                            color=alt.Color(field="Mánager", type="nominal", legend=alt.Legend(title=None, orient="right")),
                            tooltip=['Mánager', 'Victorias Absolutas']
                        ).properties(height=350)
                        
                        col_q1, col_q2 = st.columns([1, 2])
                        with col_q1:
                            df_queso.index = df_queso.index + 1
                            df_queso.index.name = "Rank"
                            st.dataframe(df_queso, use_container_width=True)
                        with col_q2:
                            st.altair_chart(grafica_queso, use_container_width=True)
                    else:
                        st.info("🤷‍♂️ Parece increíble, pero no ha habido ninguna victoria exclusiva sin empate en este grupo.")

    elif st.session_state.pantalla in ["👤 Perfiles (Próximamente)"]:
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
            
        st.title(st.session_state.pantalla)
        st.info("🚧 Estamos trabajando en esta sección.")

else:
    st.error("❌ Faltan los archivos de datos globales.")