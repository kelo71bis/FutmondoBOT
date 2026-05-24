import streamlit as st
import pandas as pd
import altair as alt
import os

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
        st.title("🏆 LaLiga Santanguissa - Panel de Control")
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
            st.caption("Cruza las trayectorias de dos mánagers y descubre quién manda en vuestros duelos directos.")

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
        
        # Calcular Score Histórico global para todos los mánagers
        score_historico_dict = df.groupby('Mánager')['Puntos'].mean().round(1).to_dict()
        
        if temporada_sel == "2024/25":
            st.subheader("📊 Tabla Final (Temporada 2024/25)")
            jornada_max_2425 = df_temp['Jornada'].max()
            df_clasif = df_temp[df_temp['Jornada'] == jornada_max_2425].sort_values(by="Puntos_Acumulados", ascending=False)
            
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados"]].copy()
            df_mostrar['Score Histórico'] = df_mostrar['Mánager'].map(score_historico_dict)
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Score Histórico"]
            
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.index.name = "Pos."
            df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
            
            col_tabla, col_info = st.columns([1, 1.8])
            with col_tabla:
                st.dataframe(
                    df_mostrar, 
                    use_container_width=True,
                    column_config={
                        "Score Histórico": st.column_config.NumberColumn(
                            "Score Histórico ℹ️",
                            help="Media de puntos por jornada a lo largo de toda la historia de la liga."
                        )
                    }
                )
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
                
                df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados"]].copy()
                df_mostrar['Score Histórico'] = df_mostrar['Mánager'].map(score_historico_dict)
                df_mostrar.columns = ["Mánager", "Puntos Temporada", "Score Histórico"]
                
                df_mostrar.index = df_mostrar.index + 1 
                df_mostrar.index.name = "Pos."
                df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
                
                st.dataframe(
                    df_mostrar, 
                    use_container_width=True,
                    column_config={
                        "Score Histórico": st.column_config.NumberColumn(
                            "Score Histórico ℹ️",
                            help="Media de puntos por jornada a lo largo de toda la historia de la liga."
                        )
                    }
                )
                
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
                    
                    # --- BLOQUE 1: ANÁLISIS ACUMULADO ---
                    st.markdown("---")
                    st.subheader("📊 Análisis Acumulado (Clasificación General)")
                    tab_pos_acu, tab_mat_pos_acu, tab_pts_acu, tab_mat_pts_acu = st.tabs([
                        "🎢 Posición", "🔢 Matriz Pos.", "📈 Puntos", "🔢 Matriz Pts."
                    ])
                    
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

                    with tab_mat_pos_acu:
                        df_matriz_acum = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Posición')
                        st.dataframe(df_matriz_acum.style.format(precision=0, na_rep="-"), use_container_width=True)

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

                    with tab_mat_pts_acu:
                        df_matriz_pts_acum = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Puntos_Acumulados')
                        st.dataframe(df_matriz_pts_acum.style.format(precision=0, na_rep="-"), use_container_width=True)

                    # --- BLOQUE 2: ANÁLISIS DE LA JORNADA ---
                    st.markdown("---")
                    st.subheader("⚡ Análisis de la Jornada Aislada")
                    tab_pos_jor, tab_mat_pos_jor, tab_pts_jor, tab_mat_pts_jor = st.tabs([
                        "🎯 Posición", "🔢 Matriz Pos.", "⚡ Puntos", "🔢 Matriz Pts."
                    ])
                    
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

                    with tab_mat_pos_jor:
                        df_matriz_jor = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Posición_Jornada')
                        st.dataframe(df_matriz_jor.style.format(precision=0, na_rep="-"), use_container_width=True)

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

                    with tab_mat_pts_jor:
                        df_matriz_pts_jor = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Puntos')
                        st.dataframe(df_matriz_pts_jor.style.format(precision=0, na_rep="-"), use_container_width=True)

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
        st.header("🔥 Mayores Rachas Históricas")
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

        st.subheader("Jornadas seguidas en la cumbre o en el pozo")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.caption("👑 **Líderes de Hierro** (Semanas consecutivas siendo 1º general)")
            top10_rachas_lider.index = range(1, 1 + len(top10_rachas_lider))
            top10_rachas_lider.index.name = "Rank"
            st.dataframe(top10_rachas_lider.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)
        with col_r2:
            st.caption("⚓ **Fango Eterno** (Semanas consecutivas siendo último general)")
            top10_rachas_ultimo.index = range(1, 1 + len(top10_rachas_ultimo))
            top10_rachas_ultimo.index.name = "Rank"
            st.dataframe(top10_rachas_ultimo.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Jornadas consecutivas dando la nota (para bien y para mal)")
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.caption("⬆️ **Jornadas consecutivas On Fire** (Jornadas seguidas con la mejor puntuación)")
            top10_rachas_mvp.index = range(1, 1 + len(top10_rachas_mvp))
            top10_rachas_mvp.index.name = "Rank"
            st.dataframe(top10_rachas_mvp.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)
        with col_r4:
            st.caption("💩 **Jornadas consecutivas dando pena** (Jornadas seguidas con la peor puntuación)")
            top10_rachas_peor_jor.index = range(1, 1 + len(top10_rachas_peor_jor))
            top10_rachas_peor_jor.index.name = "Rank"
            st.dataframe(top10_rachas_peor_jor.reset_index().set_index(['Rank', 'Mánager']), use_container_width=True)

        st.markdown("---")

        # --- BLOQUE 4: MEDALLERO Y CLUB DE LOS 100 ---
        col_m1, col_m2 = st.columns([1.5, 1])
        
        with col_m1:
            st.subheader("🏅 El Medallero Olímpico")
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
                
                # Tabla Resumen Ligas
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("Resumen Histórico de Liga")
                resumen_liga = df_ligas.groupby(['Mánager', 'Posicion']).size().unstack(fill_value=0)
                if 'Campeón' not in resumen_liga: resumen_liga['Campeón'] = 0
                if 'Subcampeón' not in resumen_liga: resumen_liga['Subcampeón'] = 0
                resumen_liga = resumen_liga[['Campeón', 'Subcampeón']]
                resumen_liga = resumen_liga[(resumen_liga['Campeón'] > 0) | (resumen_liga['Subcampeón'] > 0)]
                resumen_liga = resumen_liga.sort_values(by=['Campeón', 'Subcampeón'], ascending=[False, False])
                st.dataframe(resumen_liga, use_container_width=True)
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
                
                # Tabla Resumen Copas
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("Resumen Histórico de Copas")
                resumen_copa = df_copas.groupby(['Mánager', 'Posicion']).size().unstack(fill_value=0)
                if 'Campeón' not in resumen_copa: resumen_copa['Campeón'] = 0
                if 'Finalista' not in resumen_copa: resumen_copa['Finalista'] = 0
                resumen_copa = resumen_copa[['Campeón', 'Finalista']]
                resumen_copa = resumen_copa[(resumen_copa['Campeón'] > 0) | (resumen_copa['Finalista'] > 0)]
                resumen_copa = resumen_copa.sort_values(by=['Campeón', 'Finalista'], ascending=[False, False])
                st.dataframe(resumen_copa, use_container_width=True)
            else:
                st.warning("⚠️ No se ha encontrado el palmarés de copas.")
                
        st.markdown("---")
        st.subheader("👑 Reyes de la Liga (Recuento de Títulos Absoluto)")
        
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
    # PANTALLA 4: CARA A CARA (¡EL COLISEO 1vs1!)
    # ==========================================
    elif st.session_state.pantalla == "⚔️ Cara a Cara":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
            
        st.title("⚔️ Cara a Cara (El Coliseo 1vs1)")
        st.markdown("---")
        
        lista_todos_managers = sorted(df['Mánager'].unique().tolist())
        
        # FILTROS DE CONTENDIENTES (Bloqueos inteligentes)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            m1 = st.selectbox("🔴 Contendiente 1:", ["-- Selecciona un Mánager --"] + lista_todos_managers)
            
        valid_m2 = []
        if m1 != "-- Selecciona un Mánager --":
            seasons_m1 = set(df[(df['Mánager'] == m1) & (df['Temporada'] != '2024/25')]['Temporada'].unique())
            for m in lista_todos_managers:
                if m != m1:
                    seasons_m = set(df[(df['Mánager'] == m) & (df['Temporada'] != '2024/25')]['Temporada'].unique())
                    if len(seasons_m1.intersection(seasons_m)) > 0:
                        valid_m2.append(m)
        
        with col_f2:
            opciones_m2 = ["-- Esperando rival --"] if m1 == "-- Selecciona un Mánager --" else ["-- Selecciona un Mánager --"] + valid_m2
            m2 = st.selectbox("🔵 Contendiente 2:", opciones_m2)
            
        if m1 == "-- Selecciona un Mánager --" or m2 == "-- Selecciona un Mánager --" or m2 == "-- Esperando rival --":
            st.info("👆 Selecciona a dos mánagers para enfrentarlos en el Cara a Cara. El segundo selector solo mostrará a mánagers con los que el primero haya coincidido.")
        else:
            # FILTRO TEMPORADAS
            seasons_m1 = set(df[(df['Mánager'] == m1) & (df['Temporada'] != '2024/25')]['Temporada'].unique())
            seasons_m2 = set(df[(df['Mánager'] == m2) & (df['Temporada'] != '2024/25')]['Temporada'].unique())
            temporadas_comunes = sorted(list(seasons_m1.intersection(seasons_m2)), reverse=True)
            
            with col_f3:
                temporadas_h2h_sel = st.multiselect(
                    "📅 Temporadas del duelo:", 
                    temporadas_comunes, 
                    default=temporadas_comunes
                )
            
            if len(temporadas_h2h_sel) == 0:
                st.warning("⚠️ Selecciona al menos una temporada para iniciar el combate.")
            else:
                st.markdown("---")
                
                # DATOS FILTRADOS
                df_h2h = df[(df['Mánager'].isin([m1, m2])) & (df['Temporada'].isin(temporadas_h2h_sel))]
                df_pivot = df_h2h.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos').dropna()
                
                total_jornadas = len(df_pivot)
                total_temporadas = len(temporadas_h2h_sel)
                
                wins_m1 = (df_pivot[m1] > df_pivot[m2]).sum()
                wins_m2 = (df_pivot[m2] > df_pivot[m1]).sum()
                empates = (df_pivot[m1] == df_pivot[m2]).sum()
                
                pct_m1 = (wins_m1 / total_jornadas) * 100 if total_jornadas > 0 else 0
                pct_m2 = (wins_m2 / total_jornadas) * 100 if total_jornadas > 0 else 0
                
                # TEXTO INTRODUCTORIO
                st.markdown(f"**{m1}** y **{m2}** han coincidido en un total de **{total_jornadas} jornadas** a lo largo de **{total_temporadas} temporadas** en los registros analizados.")
                st.markdown(f"**{m1}** ha quedado por encima de **{m2}** en **{wins_m1} jornadas** ({pct_m1:.1f}%), mientras que **{m2}** ha hecho lo contrario en **{wins_m2} jornadas** ({pct_m2:.1f}%). (Empataron en {empates} ocasiones).")
                st.write("Este es el resultado del cara a cara global (Ligas terminadas uno por encima del otro):")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- EL MARCADOR GIGANTE ---
                df_finales = df_h2h.loc[df_h2h.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()]
                df_fin_pivot = df_finales.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna()
                ligas_m1 = (df_fin_pivot[m1] > df_fin_pivot[m2]).sum()
                ligas_m2 = (df_fin_pivot[m2] > df_fin_pivot[m1]).sum()
                
                # Trofeos Históricos Absolutos de cada uno
                ligas_tot_m1 = len(df_ligas[(df_ligas['Mánager']==m1) & (df_ligas['Posicion']=='Campeón')]) if df_ligas is not None else 0
                copas_tot_m1 = len(df_copas[(df_copas['Mánager']==m1) & (df_copas['Posicion']=='Campeón')]) if df_copas is not None else 0
                trofeos_m1 = ("⭐" * ligas_tot_m1) + ("🏆" * copas_tot_m1) if (ligas_tot_m1 + copas_tot_m1) > 0 else "Sin títulos"

                ligas_tot_m2 = len(df_ligas[(df_ligas['Mánager']==m2) & (df_ligas['Posicion']=='Campeón')]) if df_ligas is not None else 0
                copas_tot_m2 = len(df_copas[(df_copas['Mánager']==m2) & (df_copas['Posicion']=='Campeón')]) if df_copas is not None else 0
                trofeos_m2 = ("⭐" * ligas_tot_m2) + ("🏆" * copas_tot_m2) if (ligas_tot_m2 + copas_tot_m2) > 0 else "Sin títulos"

                col_mar1, col_mar2, col_mar3 = st.columns([1, 1, 1])
                with col_mar1:
                    st.markdown(f"<h2 style='text-align: center; color: #2ca02c;'>{m1}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align: center; letter-spacing: 2px;'>{trofeos_m1}</h5>", unsafe_allow_html=True)
                with col_mar2:
                    st.markdown(f"<h1 style='text-align: center; font-size: 70px; margin-top: -20px;'>{ligas_m1} - {ligas_m2}</h1>", unsafe_allow_html=True)
                with col_mar3:
                    st.markdown(f"<h2 style='text-align: center; color: #d62728;'>{m2}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align: center; letter-spacing: 2px;'>{trofeos_m2}</h5>", unsafe_allow_html=True)

                st.markdown("<br><hr>", unsafe_allow_html=True)

                # --- MÉTRICAS DE COMPARACIÓN ---
                st.subheader("⚖️ Comparativa de Métricas")
                
                # M1 Métricas
                df_m1 = df_h2h[df_h2h['Mánager']==m1]
                media_jor_m1 = df_m1['Puntos'].mean()
                max_jor_m1 = df_m1['Puntos'].max()
                min_jor_m1 = df_m1['Puntos'].min()
                
                df_all_h2h_seasons = df[df['Temporada'].isin(temporadas_h2h_sel)]
                df_all_h2h_seasons['Rank_Jor'] = df_all_h2h_seasons.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
                veces_lider_m1 = len(df_all_h2h_seasons[(df_all_h2h_seasons['Mánager']==m1) & (df_all_h2h_seasons['Rank_Jor']==1)])
                
                df_lideres = df_all_h2h_seasons[df_all_h2h_seasons['Rank_Jor']==1].sort_values(['Mánager', 'Temporada', 'Jornada'])
                df_lideres['Grupo_Racha'] = (df_lideres['Jornada'] != df_lideres['Jornada'].shift() + 1).cumsum()
                rachas_m1 = df_lideres[df_lideres['Mánager']==m1].groupby(['Temporada', 'Grupo_Racha']).size()
                max_racha_m1 = rachas_m1.max() if not rachas_m1.empty else 0

                # M2 Métricas
                df_m2 = df_h2h[df_h2h['Mánager']==m2]
                media_jor_m2 = df_m2['Puntos'].mean()
                max_jor_m2 = df_m2['Puntos'].max()
                min_jor_m2 = df_m2['Puntos'].min()
                
                veces_lider_m2 = len(df_all_h2h_seasons[(df_all_h2h_seasons['Mánager']==m2) & (df_all_h2h_seasons['Rank_Jor']==1)])
                
                rachas_m2 = df_lideres[df_lideres['Mánager']==m2].groupby(['Temporada', 'Grupo_Racha']).size()
                max_racha_m2 = rachas_m2.max() if not rachas_m2.empty else 0

                # Renderizar tabla manual de métricas para que quede visual
                col_met1, col_met2, col_met3 = st.columns([1, 1.5, 1])
                
                with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Media Puntos por Jornada</b></p>", unsafe_allow_html=True)
                with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_jor_m1:.1f}</b></p>", unsafe_allow_html=True)
                with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_jor_m2:.1f}</b></p>", unsafe_allow_html=True)

                if total_temporadas > 1:
                    media_jor_temp_m1 = df_m1.groupby('Temporada')['Puntos'].mean().mean()
                    media_jor_temp_m2 = df_m2.groupby('Temporada')['Puntos'].mean().mean()
                    
                    media_temp_m1 = df_finales[df_finales['Mánager']==m1]['Puntos_Acumulados'].mean()
                    media_temp_m2 = df_finales[df_finales['Mánager']==m2]['Puntos_Acumulados'].mean()
                    
                    with col_met2: st.markdown("<p style='text-align: center; color: gray;' title='Media de las medias por jornada de cada temporada analizada'><b>Media Puntos por Jornada y Temporada ℹ️</b></p>", unsafe_allow_html=True)
                    with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_jor_temp_m1:.1f}</b></p>", unsafe_allow_html=True)
                    with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_jor_temp_m2:.1f}</b></p>", unsafe_allow_html=True)
                    
                    with col_met2: st.markdown("<p style='text-align: center; color: gray;' title='Media de la puntuación final acumulada de cada temporada'><b>Media Puntos por Temporada ℹ️</b></p>", unsafe_allow_html=True)
                    with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_temp_m1:.0f}</b></p>", unsafe_allow_html=True)
                    with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{media_temp_m2:.0f}</b></p>", unsafe_allow_html=True)
                    
                    max_temp_m1 = df_finales[df_finales['Mánager']==m1]['Puntos_Acumulados'].max()
                    max_temp_m2 = df_finales[df_finales['Mánager']==m2]['Puntos_Acumulados'].max()
                    
                    with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Máxima Puntuación de Temporada</b></p>", unsafe_allow_html=True)
                    with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_temp_m1:.0f}</b></p>", unsafe_allow_html=True)
                    with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_temp_m2:.0f}</b></p>", unsafe_allow_html=True)

                with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Máxima Puntuación en Jornada</b></p>", unsafe_allow_html=True)
                with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_jor_m1}</b></p>", unsafe_allow_html=True)
                with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_jor_m2}</b></p>", unsafe_allow_html=True)
                
                with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Mínima Puntuación en Jornada</b></p>", unsafe_allow_html=True)
                with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{min_jor_m1}</b></p>", unsafe_allow_html=True)
                with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{min_jor_m2}</b></p>", unsafe_allow_html=True)

                with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Veces Líder de la Jornada</b></p>", unsafe_allow_html=True)
                with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{veces_lider_m1}</b></p>", unsafe_allow_html=True)
                with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{veces_lider_m2}</b></p>", unsafe_allow_html=True)

                with col_met2: st.markdown("<p style='text-align: center; color: gray;'><b>Mejor Racha On Fire (Jornadas líder consecutivas)</b></p>", unsafe_allow_html=True)
                with col_met1: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_racha_m1}</b></p>", unsafe_allow_html=True)
                with col_met3: st.markdown(f"<p style='text-align: center; font-size: 20px;'><b>{max_racha_m2}</b></p>", unsafe_allow_html=True)

                st.markdown("---")

                # --- 4. DIFERENCIA DE SANGRE ---
                st.subheader("🩸 La Sangría: Diferencia de Puntos Directa")
                st.caption(f"Diferencia exacta en cada jornada jugada. Barras verdes = gana **{m1}**. Barras rojas = gana **{m2}**.")
                
                df_diff = df_pivot[m1] - df_pivot[m2]
                df_diff = df_diff.reset_index()
                df_diff.columns = ['Temporada', 'Jornada', 'Diferencia']
                df_diff['Orden'] = range(len(df_diff))
                df_diff['Jornada_Global'] = df_diff['Temporada'] + " - J" + df_diff['Jornada'].astype(str)
                df_diff['Ganador'] = df_diff['Diferencia'].apply(lambda x: m1 if x > 0 else (m2 if x < 0 else 'Empate'))

                chart_diff = alt.Chart(df_diff).mark_bar().encode(
                    x=alt.X('Jornada_Global:O', title='Jornada (Cronológica)', sort=alt.EncodingSortField(field="Orden", order="ascending"), axis=alt.Axis(labels=False, ticks=False)),
                    y=alt.Y('Diferencia:Q', title='Diferencia (Pts)'),
                    color=alt.Color('Ganador:N', scale=alt.Scale(
                        domain=[m1, m2, 'Empate'], 
                        range=['#2ca02c', '#d62728', '#7f7f7f']
                    ), legend=alt.Legend(title="Ganador de Jornada", orient="bottom")),
                    tooltip=['Temporada', 'Jornada', 'Diferencia', 'Ganador']
                ).properties(height=350)
                
                st.altair_chart(chart_diff, use_container_width=True)

    elif st.session_state.pantalla in ["👤 Perfiles (Próximamente)"]:
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
            
        st.title(st.session_state.pantalla)
        st.info("🚧 Estamos trabajando en esta sección. Te jodes.")

else:
    st.error("❌ Faltan los archivos de datos globales.")