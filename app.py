import streamlit as st
import pandas as pd
import altair as alt
import os
import random

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

# 🛡️ HISTORIAL FIJO DE LA TEMPORADA INAUGURAL 2020/21 (Para el marcador grande)
clasificacion_2020_21 = ["Mikelona", "Arsenati", "Curyffisme", "URSS", "Jatafe", "Dendryd", "Cracklos", "Bichos"]

if df is not None:
    # 🔄 INICIALIZAR SESSION STATE PARA EVITAR REINICIOS DE SELECCIÓN
    if 'pantalla' not in st.session_state:
        st.session_state.pantalla = "🏠 Menú Principal"
    if 'm1_sel' not in st.session_state:
        st.session_state.m1_sel = "-- Selecciona un Mánager --"
    if 'm2_sel' not in st.session_state:
        st.session_state.m2_sel = "-- Selecciona un Mánager --"

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
        
        # 🥊 NUEVA MATRIZ DE ENFRENTAMIENTOS GLOBAL EN PANEL DE CONTROL
        st.subheader("⚔️ Matriz de Abuso Colectivo (Historial cruzado)")
        st.caption("Lee por filas: cuántas jornadas le ha ganado el mánager de la fila al de la columna de forma directa. Ajusta las temporadas en el filtro.")
        
        df_panel_base = df[df['Temporada'] != '2024/25'].copy()
        lista_seasons_panel = sorted(df_panel_base['Temporada'].unique().tolist(), reverse=True)
        
        seasons_panel_sel = st.multiselect(
            "📅 Filtrar temporadas de la matriz:", 
            lista_seasons_panel, 
            default=lista_seasons_panel,
            key="panel_matriz_seasons"
        )
        
        if len(seasons_panel_sel) > 0:
            df_panel_filtered = df_panel_base[df_panel_base['Temporada'].isin(seasons_panel_sel)]
            df_pivot_panel = df_panel_filtered.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos').dropna(how='all')
            all_managers_panel = sorted(df_panel_filtered['Mánager'].unique().tolist())
            
            matriz_panel_dict = {m1: {m2: 0 for m2 in all_managers_panel} for m1 in all_managers_panel}
            for m1 in all_managers_panel:
                for m2 in all_managers_panel:
                    if m1 != m2 and m1 in df_pivot_panel.columns and m2 in df_pivot_panel.columns:
                        valid_jors = df_pivot_panel[[m1, m2]].dropna()
                        wins = (valid_jors[m1] > valid_jors[m2]).sum()
                        ties = (valid_jors[m1] == valid_jors[m2]).sum()
                        matriz_panel_dict[m1][m2] = int(wins + ties)
                    else:
                        matriz_panel_dict[m1][m2] = "-"
                        
            df_matriz_panel = pd.DataFrame(matriz_panel_dict).T
            st.dataframe(df_matriz_panel, use_container_width=True)
        else:
            st.warning("Selecciona al menos una temporada para pintar la matriz global.")
            
        st.markdown("---")
        st.write("Acceso rápido al resto de secciones:")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📈 Análisis por temporadas", use_container_width=True):
                st.session_state.pantalla = "📈 Análisis por temporadas"
                st.rerun()
            st.markdown("##")
            if st.button("🥇 Vitrina de Trofeos e Historial", use_container_width=True):
                st.session_state.pantalla = "🥇 Palmarés Histórico"
                st.rerun()

        with c2:
            if st.button("🏆 El Salón de la Fama (Récords)", use_container_width=True):
                st.session_state.pantalla = "🏆 Salón de la Fama"
                st.rerun()
            st.markdown("##")
            if st.button("⚔️ Cara a Cara", use_container_width=True):
                st.session_state.pantalla = "⚔️ Cara a Cara"
                st.rerun()

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
            
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados"]].copy()
            df_mostrar.columns = ["Mánager", "Puntos Temporada"]
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.index.name = "Pos."
            st.dataframe(df_mostrar.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
            st.info("ℹ️ Para la temporada 2024/25 solo disponemos del cierre de puntos acumulados. Por este motivo, las gráficas no están habilitadas.")
                
        else:
            df_temp['Posición'] = df_temp.groupby('Jornada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
            df_temp['Posición_Jornada'] = df_temp.groupby('Jornada')['Puntos'].rank(method='min', ascending=False).astype(int)
            jornada_maxima = int(df_temp['Jornada'].max())
            
            col1, col2 = st.columns([1.2, 1.8])
            
            with col1:
                rango_jornadas = st.slider("🔍 Rango de Jornadas", 1, jornada_maxima, (1, jornada_maxima))
                jornada_seleccionada = rango_jornadas[1] 
                
                st.subheader(f"📊 Tabla (Jornada {jornada_seleccionada})")
                
                # --- CÁLCULO DE MÉTRICAS DINÁMICAS HASTA LA JORNADA SELECCIONADA ---
                df_filtro_dinamico = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
                
                max_punt_din = df_filtro_dinamico.groupby('Mánager')['Puntos'].max()
                min_punt_din = df_filtro_dinamico.groupby('Mánager')['Puntos'].min()
                
                jors_lider_acu = df_filtro_dinamico[df_filtro_dinamico['Posición'] == 1].groupby('Mánager').size()
                jors_lider_jor = df_filtro_dinamico[df_filtro_dinamico['Posición_Jornada'] == 1].groupby('Mánager').size()
                
                df_clasif = df_temp[df_temp['Jornada'] == jornada_seleccionada].sort_values(by="Puntos_Acumulados", ascending=False).copy()
                
                df_clasif['Max. Punt.'] = df_clasif['Mánager'].map(max_punt_din)
                df_clasif['Mín. Punt.'] = df_clasif['Mánager'].map(min_punt_din)
                df_clasif['Líder Gral.'] = df_clasif['Mánager'].map(jors_lider_acu).fillna(0).astype(int)
                df_clasif['Líder Jornada'] = df_clasif['Mánager'].map(jors_lider_jor).fillna(0).astype(int)
                
                df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Max. Punt.", "Mín. Punt.", "Líder Gral.", "Líder Jornada"]].copy()
                df_mostrar.columns = ["Mánager", "Pts Acum.", "Máx Jor.", "Mín Jor.", "Líder(Acu)", "Líder(Jor)"]
                
                df_mostrar = df_mostrar.reset_index(drop=True)
                df_mostrar.index = df_mostrar.index + 1 
                df_mostrar.index.name = "Pos."
                
                st.dataframe(df_mostrar.set_index(['Pos.', 'Mánager']), use_container_width=True)
                
            with col2:
                lista_managers_disponibles = sorted(df_temp['Mánager'].unique().tolist())
                managers_seleccionados = st.multiselect(
                    "👥 Filtrar Equipos en Gráficas:", 
                    lista_managers_disponibles, 
                    default=[],
                    placeholder="Todos los equipos seleccionados por defecto"
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
                    
                    # --- REORDENADO: BLOQUE ACUMULADO ARRIBA ---
                    st.markdown("---")
                    st.subheader("📊 Análisis Acumulado (Clasificación General)")
                    tab_pos_acu, tab_mat_pos_acu, tab_pts_acu, tab_mat_pts_acu = st.tabs([
                        "🎢 Gráfico Posición", "🔢 Matriz Posición", "📈 Gráfico Puntos", "🔢 Matriz Puntos"
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
                        st.dataframe(df_matriz_pts_acum.style.format(precision=1, na_rep="-"), use_container_width=True)

                    # --- BLOQUE JORNADA AISLADA ABAJO ---
                    st.markdown("---")
                    st.subheader("⚡ Análisis de la Jornada Aislada")
                    tab_pos_jor, tab_mat_pos_jor, tab_pts_jor, tab_mat_pts_jor = st.tabs([
                        "🎯 Gráfico Posición", "🔢 Matriz Posición", "⚡ Gráfico Puntos", "🔢 Matriz Puntos"
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
                        st.dataframe(df_matriz_pts_jor.style.format(precision=1, na_rep="-"), use_container_width=True)
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
        
        # --- BLOQUE 1: HITOS JORNADA ---
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
                    st.metric(label=f"Jornada {int(top1['Jornada'])} ({top1['Temporada']})", value=f"{top1['Puntos']:.1f} pts")
                    
                    df_resto_mejores = top10_mejores.iloc[1:][['Mánager', 'Puntos', 'Jornada', 'Temporada']].copy()
                    df_resto_mejores['Puntos'] = df_resto_mejores['Puntos'].round(1)
                    df_resto_mejores.index = range(2, 2 + len(df_resto_mejores))
                    df_resto_mejores.index.name = "Pos."
                    st.dataframe(df_resto_mejores.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
                
            with col2:
                st.subheader("☠️ Los Mayores Desastres")
                if not top10_peores.empty:
                    bot1 = top10_peores.iloc[0]
                    st.error(f"🥇 **{bot1['Mánager']}**")
                    st.metric(label=f"Jornada {int(bot1['Jornada'])} ({bot1['Temporada']})", value=f"{bot1['Puntos']:.1f} pts")
                    
                    df_resto_peores = top10_peores.iloc[1:][['Mánager', 'Puntos', 'Jornada', 'Temporada']].copy()
                    df_resto_peores['Puntos'] = df_resto_peores['Puntos'].round(1)
                    df_resto_peores.index = range(2, 2 + len(df_resto_peores))
                    df_resto_peores.index.name = "Pos."
                    st.dataframe(df_resto_peores.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

        st.markdown("---")
        
        # --- BLOQUE 2: RÉCORDS TEMPORADA COMPLETA (CON POSICIÓN FINAL) ---
        st.header("👑 Récords de Temporada Completa")
        df_records['Rank_Temp_Final'] = df_records.groupby('Temporada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
        df_finales = df_records.loc[df_records.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()].copy()
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("🏆 Mayor Puntuación Final")
            top10_temp_max = df_finales.nlargest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada', 'Rank_Temp_Final']]
            top10_temp_max.columns = ['Mánager', 'Puntos Totales', 'Temporada', 'Pos. Final']
            top10_temp_max.index = range(1, 1 + len(top10_temp_max))
            top10_temp_max.index.name = "Pos."
            st.dataframe(top10_temp_max.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
            
        with col_t2:
            st.subheader("📉 Peor Puntuación Final")
            top10_temp_min = df_finales.nsmallest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada', 'Rank_Temp_Final']]
            top10_temp_min.columns = ['Mánager', 'Puntos Totales', 'Temporada', 'Pos. Final']
            top10_temp_min.index = range(1, 1 + len(top10_temp_min))
            top10_temp_min.index.name = "Pos."
            st.dataframe(top10_temp_min.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

        st.markdown("---")

        # --- BLOQUE 3: MAYORES RACHAS HISTÓRICAS (CON POSICIÓN FINAL) ---
        st.header("🔥 Mayores Rachas Históricas")
        
        df_rachas = df_records.copy()
        df_rachas['Pos_Acum'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=False)
        df_rachas['Pos_Acum_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=True)
        
        # Mapeo de posición final para meterlo en las rachas
        pos_final_map = df_finales.set_index(['Mánager', 'Temporada'])['Rank_Temp_Final'].to_dict()
        
        # Rachas Líder Acumulado
        df_lideres = df_rachas[df_rachas['Pos_Acum'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_lideres['Grupo_Racha'] = (df_lideres['Jornada'] != df_lideres['Jornada'].shift() + 1).cumsum()
        rachas_lider = df_lideres.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
        rachas_lider['Rango'] = "J" + rachas_lider['J_Inicio'].astype(int).astype(str) + " - J" + rachas_lider['J_Fin'].astype(int).astype(str)
        top10_rachas_lider = rachas_lider.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
        top10_rachas_lider['Pos. Final Año'] = top10_rachas_lider.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
        top10_rachas_lider.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
        
        # Rachas Último Acumulado
        df_ultimos_streak = df_rachas[df_rachas['Pos_Acum_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_ultimos_streak['Grupo_Racha'] = (df_ultimos_streak['Jornada'] != df_ultimos_streak['Jornada'].shift() + 1).cumsum()
        rachas_ultimo = df_ultimos_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
        rachas_ultimo['Rango'] = "J" + rachas_ultimo['J_Inicio'].astype(int).astype(str) + " - J" + rachas_ultimo['J_Fin'].astype(int).astype(str)
        top10_rachas_ultimo = rachas_ultimo.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
        top10_rachas_ultimo['Pos. Final Año'] = top10_rachas_ultimo.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
        top10_rachas_ultimo.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']

        # Rachas Jornada Aislada
        df_rachas['Pos_Jor_Mejor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
        df_rachas['Pos_Jor_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=True)
        
        df_mvp_streak = df_rachas[df_rachas['Pos_Jor_Mejor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_mvp_streak['Grupo_Racha'] = (df_mvp_streak['Jornada'] != df_mvp_streak['Jornada'].shift() + 1).cumsum()
        rachas_mvp = df_mvp_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
        rachas_mvp['Rango'] = "J" + rachas_mvp['J_Inicio'].astype(int).astype(str) + " - J" + rachas_mvp['J_Fin'].astype(int).astype(str)
        top10_rachas_mvp = rachas_mvp.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
        top10_rachas_mvp['Pos. Final Año'] = top10_rachas_mvp.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
        top10_rachas_mvp.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
        
        df_peor_streak = df_rachas[df_rachas['Pos_Jor_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
        df_peor_streak['Grupo_Racha'] = (df_peor_streak['Jornada'] != df_peor_streak['Jornada'].shift() + 1).cumsum()
        rachas_peor_jor = df_peor_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
        rachas_peor_jor['Rango'] = "J" + rachas_peor_jor['J_Inicio'].astype(int).astype(str) + " - J" + rachas_peor_jor['J_Fin'].astype(int).astype(str)
        top10_rachas_peor_jor = rachas_peor_jor.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
        top10_rachas_peor_jor['Pos. Final Año'] = top10_rachas_peor_jor.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
        top10_rachas_peor_jor.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']

        st.subheader("Jornadas seguidas en la cumbre o en el pozo")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.caption("👑 **Líderes de Hierro** (Semanas consecutivas siendo 1º de la general)")
            top10_rachas_lider.index = range(1, 1 + len(top10_rachas_lider))
            st.dataframe(top10_rachas_lider.reset_index().set_index(['Rank', 'Mánager'] if 'Rank' in top10_rachas_lider else ['Mánager']), use_container_width=True)
        with col_r2:
            st.caption("⚓ **Fango Eterno** (Semanas consecutivas siendo último de la general)")
            top10_rachas_ultimo.index = range(1, 1 + len(top10_rachas_ultimo))
            st.dataframe(top10_rachas_ultimo.reset_index().set_index(['Rank', 'Mánager'] if 'Rank' in top10_rachas_ultimo else ['Mánager']), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Jornadas consecutivas dando la nota (para bien y para mal)")
        col_r3, col_r4 = st.columns(2)
        with col_r3:
            st.caption("⬆️ **Jornadas consecutivas On Fire** (Semanas seguidas ganando la jornada)")
            top10_rachas_mvp.index = range(1, 1 + len(top10_rachas_mvp))
            st.dataframe(top10_rachas_mvp.reset_index().set_index(['Rank', 'Mánager'] if 'Rank' in top10_rachas_mvp else ['Mánager']), use_container_width=True)
        with col_r4:
            st.caption("💩 **Jornadas consecutivas dando pena** (Semanas seguidas siendo el peor de la jornada)")
            top10_rachas_peor_jor.index = range(1, 1 + len(top10_rachas_peor_jor))
            st.dataframe(top10_rachas_peor_jor.reset_index().set_index(['Rank', 'Mánager'] if 'Rank' in top10_rachas_peor_jor else ['Mánager']), use_container_width=True)

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
                
                tabla_medallas = pd.DataFrame({'🥇 1º (Oros)': df_oros, '🥈 2º (Platas)': df_platas, '⚠️ Penúltimos': df_penultimos, '💩 Últimos': df_ultimos}).fillna(0).astype(int)
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
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("Resumen Histórico de Copas")
                resumen_copa = df_copas.groupby(['Mánager', 'Posicion']).size().unstack(fill_value=0)
                if 'Campeón' not in resumen_copa: resumen_copa['Campeón'] = 0
                if 'Finalista' not in resumen_copa: resumen_copa['Finalista'] = 0
                resumen_copa = resumen_copa[['Campeón', 'Finalista']]
                resumen_copa = resumen_copa[(resumen_copa['Campeón'] > 0) | (resumen_copa['Finalista'] > 0)]
                resumen_copa = resumen_copa.sort_values(by=['Campeón', 'Finalista'], ascending=[False, False])
                st.dataframe(resumen_copa, use_container_width=True)

    # ==========================================
    # PANTALLA 4: CARA A CARA (⚔️ COLISEO)
    # ==========================================
    elif st.session_state.pantalla == "⚔️ Cara a Cara":
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
        if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
        if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
        if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
        if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
            
        st.title("⚔️ Coliseo Cara a Cara")
        st.markdown("---")
        
        lista_todos_managers = sorted(df['Mánager'].unique().tolist())
        
        # 🎰 BOTÓN DE SELECCIÓN ALEATORIA GLOBAL
        if st.button("🎲 Combate Aleatorio (Sorpréndeme)", use_container_width=True):
            # Buscamos combinaciones válidas que sí hayan coincidido históricamente
            pares_validos = []
            for m_a in lista_todos_managers:
                for m_b in lista_todos_managers:
                    if m_a != m_b:
                        seasons_a = set(df[df['Mánager'] == m_a]['Temporada'].unique())
                        seasons_b = set(df[df['Mánager'] == m_b]['Temporada'].unique())
                        if len(seasons_a.intersection(seasons_b)) > 0:
                            pares_validos.append((m_a, m_b))
            if pares_validos:
                chosen = random.choice(pares_validos)
                st.session_state.m1_sel = chosen[0]
                st.session_state.m2_sel = chosen[1]
                st.rerun()

        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            m1 = st.selectbox("🔴 Contendiente 1:", ["-- Selecciona un Mánager --"] + lista_todos_managers, index=(lista_todos_managers.index(st.session_state.m1_sel)+1 if st.session_state.m1_sel in lista_todos_managers else 0))
            st.session_state.m1_sel = m1
            
        valid_m2 = []
        if m1 != "-- Selecciona un Mánager --":
            seasons_m1 = set(df[df['Mánager'] == m1]['Temporada'].unique())
            # Añadir manualmente la 2020/21 si m1 está en la lista inaugural
            if m1 in clasificacion_2020_21: seasons_m1.add("2020/21")
            
            for m in lista_todos_managers:
                if m != m1:
                    seasons_m = set(df[df['Mánager'] == m]['Temporada'].unique())
                    if m in clasificacion_2020_21: seasons_m.add("2020/21")
                    if len(seasons_m1.intersection(seasons_m)) > 0:
                        valid_m2.append(m)
        
        with col_f2:
            opciones_m2 = ["-- Esperando rival --"] if m1 == "-- Selecciona un Mánager --" else ["-- Selecciona un Mánager --"] + valid_m2
            idx_m2 = opciones_m2.index(st.session_state.m2_sel) if st.session_state.m2_sel in opciones_m2 else 0
            m2 = st.selectbox("🔵 Contendiente 2:", opciones_m2, index=idx_m2)
            st.session_state.m2_sel = m2
            
        if m1 == "-- Selecciona un Mánager --" or m2 == "-- Selecciona un Mánager --" or m2 == "-- Esperando rival --":
            st.info("👆 Selecciona a dos mánagers o dale al dado para abrir las puertas del Coliseo.")
        else:
            # FILTRO TEMPORADAS COMPLETO INDEPENDIENTE DE MATRIZ
            seasons_m1 = set(df[df['Mánager'] == m1]['Temporada'].unique())
            seasons_m2 = set(df[df['Mánager'] == m2]['Temporada'].unique())
            if m1 in clasificacion_2020_21: seasons_m1.add("2020/21")
            if m2 in clasificacion_2020_21: seasons_m2.add("2020/21")
            
            temporadas_comunes = sorted(list(seasons_m1.intersection(seasons_m2)), reverse=True)
            
            with col_f3:
                # Conservar selección en state para evitar reinicios al marcar checks
                if 'seasons_h2h' not in st.session_state:
                    st.session_state.seasons_h2h = temporadas_comunes
                temporadas_h2h_sel = st.multiselect("📅 Temporadas del combate:", temporadas_comunes, default=temporadas_comunes)
            
            if len(temporadas_h2h_sel) == 0:
                st.warning("Selecciona al menos una temporada.")
            else:
                # PROCESAMIENTO DE HISTORIAL JORNADA A JORNADA (Excluyendo las vacías 24/25 y 20/21)
                df_h2h = df[(df['Mánager'].isin([m1, m2])) & (df['Temporada'].isin(temporadas_h2h_sel)) & (df['Temporada'] != '2024/25')]
                df_pivot = df_h2h.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos').dropna() if not df_h2h.empty else pd.DataFrame()
                
                total_jornadas = len(df_pivot)
                wins_m1 = (df_pivot[m1] > df_pivot[m2]).sum() if total_jornadas > 0 else 0
                wins_m2 = (df_pivot[m2] > df_pivot[m1]).sum() if total_jornadas > 0 else 0
                empates = (df_pivot[m1] == df_pivot[m2]).sum() if total_jornadas > 0 else 0
                
                pct_m1 = (wins_m1 / total_jornadas) * 100 if total_jornadas > 0 else 0
                pct_m2 = (wins_m2 / total_jornadas) * 100 if total_jornadas > 0 else 0
                
                st.markdown(f"**{m1}** y **{m2}** han coincidido en un total de **{total_jornadas} jornadas** registradas a lo largo de **{len(temporadas_h2h_sel)} temporadas** compartidas.")
                st.markdown(f"**{m1}** ha quedado por encima de **{m2}** en **{wins_m1} jornadas** ({pct_m1:.1f}%), mientras que **{m2}** ha hecho lo contrario en **{wins_m2} jornadas** ({pct_m2:.1f}%). *(Empataron en {empates} ocasiones)*.")
                st.write("Este es el resultado del cara a cara global (Ligas completas terminadas uno por encima del otro):")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- CALCULO DEL MARCADOR GIGANTE (INCLUYE 2024/25 Y 2020/21) ---
                ligas_m1_final = 0
                ligas_m2_final = 0
                
                # 1. Procesar temporadas regulares de Excel
                df_finales_h2h = df[(df['Mánager'].isin([m1, m2])) & (df['Temporada'].isin(temporadas_h2h_sel))].copy()
                if not df_finales_h2h.empty:
                    df_fin_loc = df_finales_h2h.loc[df_finales_h2h.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()]
                    df_fin_pivot = df_fin_loc.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna()
                    ligas_m1_final += (df_fin_pivot[m1] > df_fin_pivot[m2]).sum()
                    ligas_m2_final += (df_fin_pivot[m2] > df_fin_pivot[m1]).sum()
                
                # 2. Sumar temporada inaugural 2020/21 si está seleccionada en el filtro
                if "2020/21" in temporadas_h2h_sel and m1 in clasificacion_2020_21 and m2 in clasificacion_2020_21:
                    idx_m1 = clasificacion_2020_21.index(m1)
                    idx_m2 = clasificacion_2020_21.index(m2)
                    if idx_m1 < idx_m2: # Menor índice = mejor posición
                        ligas_m1_final += 1
                    else:
                        ligas_m2_final += 1

                # Títulos en filas separadas
                ligas_tot_m1 = len(df_ligas[(df_ligas['Mánager'] == m1) & (df_ligas['Posicion'] == 'Campeón')]) if df_ligas is not None else 0
                copas_tot_m1 = len(df_copas[(df_copas['Mánager'] == m1) & (df_copas['Posicion'] == 'Campeón')]) if df_copas is not None else 0
                stars_m1 = "⭐" * ligas_tot_m1 if ligas_tot_m1 > 0 else "-"
                cups_m1 = "🏆" * copas_tot_m1 if copas_tot_m1 > 0 else "-"

                ligas_tot_m2 = len(df_ligas[(df_ligas['Mánager'] == m2) & (df_ligas['Posicion'] == 'Campeón')]) if df_ligas is not None else 0
                copas_tot_m2 = len(df_copas[(df_copas['Mánager'] == m2) & (df_copas['Posicion'] == 'Campeón')]) if df_copas is not None else 0
                stars_m2 = "⭐" * ligas_tot_m2 if ligas_tot_m2 > 0 else "-"
                cups_m2 = "🏆" * copas_tot_m2 if copas_tot_m2 > 0 else "-"

                # Renderizado del Marcador Gigante
                col_mar1, col_mar2, col_mar3 = st.columns([1.2, 1, 1.2])
                with col_mar1:
                    st.markdown(f"<h2 style='text-align: center; color: #2ca02c; margin-bottom:2px;'>{m1}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size:14px; margin:0; color:gray;'>Ligas: {stars_m1}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size:14px; margin:0; color:gray;'>Copas: {cups_m1}</p>", unsafe_allow_html=True)
                with col_mar2:
                    st.markdown(f"<h1 style='text-align: center; font-size: 75px; margin-top: -15px;'>{ligas_m1_final} - {ligas_m2_final}</h1>", unsafe_allow_html=True)
                with col_mar3:
                    st.markdown(f"<h2 style='text-align: center; color: #d62728; margin-bottom:2px;'>{m2}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size:14px; margin:0; color:gray;'>Ligas: {stars_m2}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size:14px; margin:0; color:gray;'>Copas: {cups_m2}</p>", unsafe_allow_html=True)

                st.markdown("<br><hr>", unsafe_allow_html=True)

                # --- 🗲 ESTADÍSTICAS DEL COMBATE ALINEADAS AL 100% ---
                st.subheader("⚖️ Estadísticas del combate")
                
                # Cálculos métricas
                df_m1 = df_h2h[df_h2h['Mánager'] == m1]
                df_m2 = df_h2h[df_h2h['Mánager'] == m2]
                
                media_m1 = df_m1['Puntos'].mean() if not df_m1.empty else 0
                media_m2 = df_m2['Puntos'].mean() if not df_m2.empty else 0
                
                max_jor_m1 = df_m1['Puntos'].max() if not df_m1.empty else 0
                max_jor_m2 = df_m2['Puntos'].max() if not df_m2.empty else 0
                min_jor_m1 = df_m1['Puntos'].min() if not df_m1.empty else 0
                min_jor_m2 = df_m2['Puntos'].min() if not df_m2.empty else 0
                
                # Filtro global para calcular líderes de jornada reales en esos años compartidos
                df_all_seasons = df[df['Temporada'].isin(temporadas_h2h_sel)].copy()
                df_all_seasons['Rank_Jor'] = df_all_seasons.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
                
                veces_lider_m1 = len(df_all_seasons[(df_all_seasons['Mánager'] == m1) & (df_all_seasons['Rank_Jor'] == 1)])
                veces_lider_m2 = len(df_all_seasons[(df_all_seasons['Mánager'] == m2) & (df_all_seasons['Rank_Jor'] == 1)])
                
                # Rachas On Fire
                df_lideres_all = df_all_seasons[df_all_seasons['Rank_Jor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
                df_lideres_all['Grupo_Racha'] = (df_lideres_all['Jornada'] != df_lideres_all['Jornada'].shift() + 1).cumsum()
                racha_max_m1 = df_lideres_all[df_lideres_all['Mánager'] == m1].groupby(['Temporada', 'Grupo_Racha']).size().max()
                racha_max_m2 = df_lideres_all[df_lideres_all['Mánager'] == m2].groupby(['Temporada', 'Grupo_Racha']).size().max()
                racha_max_m1 = int(racha_max_m1) if pd.notna(racha_max_m1) else 0
                racha_max_m2 = int(racha_max_m2) if pd.notna(racha_max_m2) else 0

                # Lógica condicional de Filtro de Única Temporada
                show_seasonal_metrics = len(temporadas_h2h_sel) > 1

                # 💡 TRUCO ELEGANTE: Cuadrícula HTML oculta en una tabla limpia para alinear las métricas de combate como en un PPT
                html_table = f"""
                <div style="display: flex; justify-content: center; width: 100%;">
                    <table style="width: 70%; border-collapse: collapse; font-size: 17px; font-family: sans-serif; text-align: center;">
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="width: 25%; font-size: 22px; font-weight: bold; color: #2ca02c; padding: 12px;">{media_m1:.1f}</td>
                            <td style="width: 50%; color: #7f7f7f; font-weight: 500;">Media Puntos por Jornada</td>
                            <td style="width: 25%; font-size: 22px; font-weight: bold; color: #d62728; padding: 12px;">{media_m2:.1f}</td>
                        </tr>
                """
                
                if show_seasonal_metrics:
                    media_final_m1 = df_fin_pivot[m1].mean() if m1 in df_fin_pivot.columns else 0
                    media_final_m2 = df_fin_pivot[m2].mean() if m2 in df_fin_pivot.columns else 0
                    max_temp_p_m1 = df_fin_pivot[m1].max() if m1 in df_fin_pivot.columns else 0
                    max_temp_p_m2 = df_fin_pivot[m2].max() if m2 in df_fin_pivot.columns else 0
                    
                    html_table += f"""
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{media_final_m1:.0f}</td>
                            <td style="color: #7f7f7f; font-weight: 500;" title="Puntuación acumulada media al cierre de los años analizados">Media Puntos por Temporada ℹ️</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{media_final_m2:.0f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_temp_p_m1:.0f}</td>
                            <td style="color: #7f7f7f; font-weight: 500;">Máxima Puntuación de Temporada</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_temp_p_m2:.0f}</td>
                        </tr>
                    """

                html_table += f"""
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_jor_m1:.1f}</td>
                            <td style="color: #7f7f7f; font-weight: 500;">Máxima Puntuación en Jornada</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_jor_m2:.1f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{min_jor_m1:.1f}</td>
                            <td style="color: #7f7f7f; font-weight: 500;">Mínima Puntuación en Jornada</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{min_jor_m2:.1f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{veces_lider_m1}</td>
                            <td style="color: #7f7f7f; font-weight: 500;">Veces Líder de la Jornada</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{veces_lider_m2}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f0f2f6;">
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{racha_max_m1}</td>
                            <td style="color: #7f7f7f; font-weight: 500;">Mejor Racha On Fire (Jornadas líder consecutivas)</td>
                            <td style="font-size: 22px; font-weight: bold; padding: 12px;">{racha_max_m2}</td>
                        </tr>
                    </table>
                </div>
                """
                st.markdown(html_table, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # --- 4. SANGRE CON EJE X VISIBLE ---
                if total_jornadas > 0:
                    st.subheader("🩸 La Sangría: Diferencia de Puntos Directa")
                    st.caption("Eje X activo cronológicamente. Barras hacia arriba (verde) = gana el Contendiente 1. Barras hacia abajo (rojo) = gana el Contendiente 2.")
                    
                    df_diff = df_pivot[m1] - df_pivot[m2]
                    df_diff = df_diff.reset_index()
                    df_diff.columns = ['Temporada', 'Jornada', 'Diferencia']
                    df_diff['Orden'] = range(len(df_diff))
                    df_diff['Jor_Eje'] = df_diff['Temporada'].str.replace("20", "") + "-J" + df_diff['Jornada'].astype(str)
                    df_diff['Ganador'] = df_diff['Diferencia'].apply(lambda x: m1 if x > 0 else (m2 if x < 0 else 'Empate'))

                    chart_diff = alt.Chart(df_diff).mark_bar().encode(
                        x=alt.X('Jor_Eje:O', title='Jornadas jugadas (Evolución histórica)', sort=alt.EncodingSortField(field="Orden", order="ascending"), axis=alt.Axis(labelAngle=-90, labelFontSize=9)),
                        y=alt.Y('Diferencia:Q', title='Diferencia de puntos (Pts)'),
                        color=alt.Color('Ganador:N', scale=alt.Scale(domain=[m1, m2, 'Empate'], range=['#2ca02c', '#d62728', '#7f7f7f']), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=['Temporada', 'Jornada', 'Diferencia', 'Ganador']
                    ).properties(height=380)
                    st.altair_chart(chart_diff, use_container_width=True)

                # --- 5. TABLA HISTÓRICA INMUTABLE (INCLUYE LA 24-25 FIJA) ---
                st.markdown("---")
                st.subheader("📈 Historial Inmutable de Puntuaciones Finales")
                st.caption("Esta tabla refleja el cierre total de puntos acumulados al final de cada liga jugada. No le afectan los filtros de arriba.")
                
                df_inmutable_base = df.loc[df.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()].copy()
                df_inmutable_fil = df_inmutable_base[df_inmutable_base['Mánager'].isin([m1, m2])]
                df_matriz_finales = df_inmutable_fil.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna(how='all')
                
                st.dataframe(df_matriz_finales.style.format(precision=0, na_rep="-"), use_container_width=True)

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