import streamlit as st
import pandas as pd
import altair as alt

def mostrar_analisis(df, score_historico_dict):
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
        df_mostrar['Score Histórico'] = df_mostrar['Mánager'].map(score_historico_dict)
        df_mostrar.columns = ["Mánager", "Pts", "Score Histórico"]
        
        df_mostrar.index = df_mostrar.index + 1 
        df_mostrar.index.name = "Pos."
        df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
        
        col_tabla, col_info = st.columns([1, 1.8])
        with col_tabla:
            st.dataframe(
                df_mostrar, 
                use_container_width=True,
                column_config={
                    "Score Histórico": st.column_config.NumberColumn("Score Histórico ℹ️", help="Media de puntos por jornada a lo largo de toda la historia de la liga (incluida la 24/25).")
                }
            )
        with col_info:
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
            
            df_filtro_dinamico = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
            
            max_punt_din = df_filtro_dinamico.groupby('Mánager')['Puntos'].max()
            
            df_dinamico_positivos = df_filtro_dinamico[df_filtro_dinamico['Puntos'] > 0]
            min_punt_din = df_dinamico_positivos.groupby('Mánager')['Puntos'].min()
            
            jors_lider_acu = df_filtro_dinamico[df_filtro_dinamico['Posición'] == 1].groupby('Mánager').size()
            jors_lider_jor = df_filtro_dinamico[df_filtro_dinamico['Posición_Jornada'] == 1].groupby('Mánager').size()
            
            df_clasif = df_temp[df_temp['Jornada'] == jornada_seleccionada].sort_values(by="Puntos_Acumulados", ascending=False).copy()
            
            df_clasif['Máx'] = df_clasif['Mánager'].map(max_punt_din).round(1)
            
            def get_min_formateado(manager):
                val = min_punt_din.get(manager)
                if pd.isna(val): return "-"
                return round(val, 1)
            df_clasif['Mín'] = df_clasif['Mánager'].apply(get_min_formateado)
            
            df_clasif['Líder(G)'] = df_clasif['Mánager'].map(jors_lider_acu).fillna(0).astype(int)
            df_clasif['Líder(J)'] = df_clasif['Mánager'].map(jors_lider_jor).fillna(0).astype(int)
            
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Máx", "Mín", "Líder(G)", "Líder(J)"]].copy()
            df_mostrar.rename(columns={"Puntos_Acumulados": "Pts"}, inplace=True)
            
            df_mostrar = df_mostrar.reset_index(drop=True)
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.index.name = "Pos."
            df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
            
            st.dataframe(df_mostrar, use_container_width=True)
            
            # Formateo de la frase de los empanaos según la nueva petición
            empanaos = df_filtro_dinamico[df_filtro_dinamico['Puntos'] == 0]['Mánager'].unique()
            if len(empanaos) > 0:
                st.markdown(f"<p style='font-size:14px; color:#888888;'>💤 <b>Lista de empanaos de la liga (equipos que han hecho 0 puntos en alguna jornada):</b> {', '.join(empanaos)}</p>", unsafe_allow_html=True)
            
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
            
            df_temp_grafica = df_temp[
                (df_temp['Jornada'] >= rango_jornadas[0]) & 
                (df_temp['Jornada'] <= rango_jornadas[1]) &
                (df_temp['Mánager'].isin(managers_seleccionados))
            ]
            
            if not df_temp_grafica.empty:
                num_managers_total = df_temp['Mánager'].nunique()
                lista_posiciones_total = list(range(1, num_managers_total + 1))
                leyenda_config = alt.Legend(title=None, orient="bottom", columns=2)
                
                st.markdown("---")
                st.subheader("📊 Análisis Acumulado (Clasificación General)")
                tab_pos_acu, tab_mat_pos_acu, tab_pts_acu, tab_mat_pts_acu = st.tabs([
                    "🎢 Gráfico Posición", "🔢 Matriz Posición", "📈 Gráfico Puntos", "🔢 Matriz Puntos"
                ])
                
                with tab_pos_acu:
                    grafica_posiciones = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                        x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('Posición:Q', scale=alt.Scale(domain=[num_managers_total, 1]), title='Posición Acumulada', axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
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
                        y=alt.Y('Puntos_Acumulados:Q', scale=alt.Scale(domain=[min_pts_acu - margen_acu, max_pts_acu + margen_acu]), title='Puntos Acumulados'),
                        color=alt.Color('Mánager:N', legend=leyenda_config),
                        tooltip=['Mánager', 'Jornada', 'Puntos_Acumulados', 'Posición']
                    ).properties(height=420)
                    st.altair_chart(grafica_puntos_acu.interactive(), use_container_width=True)

                with tab_mat_pts_acu:
                    df_matriz_pts_acum = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Puntos_Acumulados')
                    st.dataframe(df_matriz_pts_acum.style.format(precision=1, na_rep="-"), use_container_width=True)

                st.markdown("---")
                st.subheader("⚡ Análisis de la Jornada Aislada")
                tab_pos_jor, tab_mat_pos_jor, tab_pts_jor, tab_mat_pts_jor = st.tabs([
                    "🎯 Gráfico Posición", "🔢 Matriz Posición", "⚡ Gráfico Puntos", "🔢 Matriz Puntos"
                ])
                
                with tab_pos_jor:
                    grafica_pos_jornada = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                        x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('Posición_Jornada:Q', scale=alt.Scale(domain=[num_managers_total, 1]), title='Posición en la Jornada', axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
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
                        y=alt.Y('Puntos:Q', scale=alt.Scale(domain=[min_pts_jor - margen_jor, max_pts_jor + margen_jor]), title='Puntos en la Jornada'),
                        color=alt.Color('Mánager:N', legend=leyenda_config),
                        tooltip=['Mánager', 'Jornada', 'Puntos', 'Posición_Jornada']
                    ).properties(height=420)
                    st.altair_chart(grafica_puntos_jor, use_container_width=True)

                with tab_mat_pts_jor:
                    df_matriz_pts_jor = df_temp_grafica.pivot(index='Mánager', columns='Jornada', values='Puntos')
                    st.dataframe(df_matriz_pts_jor.style.format(precision=1, na_rep="-"), use_container_width=True)