import streamlit as st
import pandas as pd

def mostrar_salon_fama(df):
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
    if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
    if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
    if c_nav3.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
    if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
        
    st.title("🏆 El Salón de la Fama")
    st.write("Consulta los mayores hitos, desastres y rachas de la historia de LaLiga Santanguissa.")
    st.markdown("---")
    
    df_all_seasons = df.copy()
    
    col_filtro_sf, _ = st.columns([1, 3])
    with col_filtro_sf:
        lista_temporadas_reales = sorted(df_all_seasons['Temporada'].unique().tolist(), reverse=True)
        temporadas_sf_sel = st.multiselect("📅 Filtrar por Temporada(s):", lista_temporadas_reales, default=[], placeholder="Todas las temporadas")
        
    if len(temporadas_sf_sel) > 0:
        df_filtered = df_all_seasons[df_all_seasons['Temporada'].isin(temporadas_sf_sel)].copy()
        texto_filtro = ", ".join(temporadas_sf_sel)
    else:
        df_filtered = df_all_seasons.copy()
        texto_filtro = "Todas las temporadas"
        
    df_records = df_filtered[df_filtered['Temporada'] != '2024/25'].copy()
    df_desastres = df_records[df_records['Puntos'] > 0]
    
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
    
    st.header("👑 Récords de Temporada Completa")
    df_finales = df_filtered.loc[df_filtered.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()].copy()
    df_finales['Pos. Final'] = df_finales.groupby('Temporada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("🏆 Mayor Puntuación Final")
        top10_temp_max = df_finales.nlargest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada', 'Pos. Final']]
        top10_temp_max.columns = ['Mánager', 'Puntos Totales', 'Temporada', 'Pos. Final']
        top10_temp_max.index = range(1, 1 + len(top10_temp_max))
        top10_temp_max.index.name = "Pos."
        st.dataframe(top10_temp_max.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
        
    with col_t2:
        st.subheader("📉 Peor Puntuación Final")
        top10_temp_min = df_finales.nsmallest(10, 'Puntos_Acumulados')[['Mánager', 'Puntos_Acumulados', 'Temporada', 'Pos. Final']]
        top10_temp_min.columns = ['Mánager', 'Puntos Totales', 'Temporada', 'Pos. Final']
        top10_temp_min.index = range(1, 1 + len(top10_temp_min))
        top10_temp_min.index.name = "Pos."
        st.dataframe(top10_temp_min.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

    st.markdown("---")

    st.header("🔥 Mayores Rachas Históricas")
    df_rachas = df_records.copy()
    df_rachas['Pos_Acum'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=False)
    df_rachas['Pos_Acum_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=True)
    
    pos_final_map = df_finales.set_index(['Mánager', 'Temporada'])['Pos. Final'].to_dict()
    
    df_lideres = df_rachas[df_rachas['Pos_Acum'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
    df_lideres['Grupo_Racha'] = (df_lideres['Jornada'] != df_lideres['Jornada'].shift() + 1).cumsum()
    rachas_lider = df_lideres.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
    rachas_lider['Rango'] = "J" + rachas_lider['J_Inicio'].astype(int).astype(str) + " - J" + rachas_lider['J_Fin'].astype(int).astype(str)
    top10_rachas_lider = rachas_lider.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
    top10_rachas_lider['Pos. Final Año'] = top10_rachas_lider.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
    top10_rachas_lider.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
    top10_rachas_lider.index = range(1, 1 + len(top10_rachas_lider))
    top10_rachas_lider.index.name = "Pos."
    
    df_ultimos_streak = df_rachas[df_rachas['Pos_Acum_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
    df_ultimos_streak['Grupo_Racha'] = (df_ultimos_streak['Jornada'] != df_ultimos_streak['Jornada'].shift() + 1).cumsum()
    rachas_ultimo = df_ultimos_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
    rachas_ultimo['Rango'] = "J" + rachas_ultimo['J_Inicio'].astype(int).astype(str) + " - J" + rachas_ultimo['J_Fin'].astype(int).astype(str)
    top10_rachas_ultimo = rachas_ultimo.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
    top10_rachas_ultimo['Pos. Final Año'] = top10_rachas_ultimo.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
    top10_rachas_ultimo.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
    top10_rachas_ultimo.index = range(1, 1 + len(top10_rachas_ultimo))
    top10_rachas_ultimo.index.name = "Pos."

    df_rachas['Pos_Jor_Mejor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
    df_rachas['Pos_Jor_Peor'] = df_rachas.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=True)
    
    df_mvp_streak = df_rachas[df_rachas['Pos_Jor_Mejor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
    df_mvp_streak['Grupo_Racha'] = (df_mvp_streak['Jornada'] != df_mvp_streak['Jornada'].shift() + 1).cumsum()
    rachas_mvp = df_mvp_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
    rachas_mvp['Rango'] = "J" + rachas_mvp['J_Inicio'].astype(int).astype(str) + " - J" + rachas_mvp['J_Fin'].astype(int).astype(str)
    top10_rachas_mvp = rachas_mvp.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
    top10_rachas_mvp['Pos. Final Año'] = top10_rachas_mvp.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
    top10_rachas_mvp.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
    top10_rachas_mvp.index = range(1, 1 + len(top10_rachas_mvp))
    top10_rachas_mvp.index.name = "Pos."
    
    df_peor_streak = df_rachas[df_rachas['Pos_Jor_Peor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
    df_peor_streak['Grupo_Racha'] = (df_peor_streak['Jornada'] != df_peor_streak['Jornada'].shift() + 1).cumsum()
    rachas_peor_jor = df_peor_streak.groupby(['Mánager', 'Temporada', 'Grupo_Racha']).agg(Jornadas_Seguidas=('Jornada', 'size'), J_Inicio=('Jornada', 'min'), J_Fin=('Jornada', 'max')).reset_index()
    rachas_peor_jor['Rango'] = "J" + rachas_peor_jor['J_Inicio'].astype(int).astype(str) + " - J" + rachas_peor_jor['J_Fin'].astype(int).astype(str)
    top10_rachas_peor_jor = rachas_peor_jor.nlargest(10, 'Jornadas_Seguidas')[['Mánager', 'Jornadas_Seguidas', 'Rango', 'Temporada']].copy()
    top10_rachas_peor_jor['Pos. Final Año'] = top10_rachas_peor_jor.set_index(['Mánager', 'Temporada']).index.map(pos_final_map)
    top10_rachas_peor_jor.columns = ['Mánager', 'Jornadas Seguidas', 'Rango', 'Temporada', 'Pos. Final Año']
    top10_rachas_peor_jor.index = range(1, 1 + len(top10_rachas_peor_jor))
    top10_rachas_peor_jor.index.name = "Pos."

    st.subheader("Jornadas seguidas en la cumbre o en el pozo")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.caption("👑 **Líderes de Hierro** (Semanas consecutivas siendo 1º de la general)")
        st.dataframe(top10_rachas_lider.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
    with col_r2:
        st.caption("⚓ **Fango Eterno** (Semanas consecutivas siendo último de la general)")
        st.dataframe(top10_rachas_ultimo.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Jornadas consecutivas dando la nota (para bien y para mal)")
    col_r3, col_r4 = st.columns(2)
    with col_r3:
        st.caption("⬆️ **Jornadas consecutivas On Fire** (Semanas seguidas ganando la jornada)")
        st.dataframe(top10_rachas_mvp.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)
    with col_r4:
        st.caption("💩 **Jornadas consecutivas dando pena** (Semanas seguidas siendo el peor de la jornada)")
        st.dataframe(top10_rachas_peor_jor.reset_index().set_index(['Pos.', 'Mánager']), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("👨‍👦 Mayores Padreadas (Cara a Cara)")
    st.caption("Top 10 histórico de jornadas consecutivas donde un mánager superó en puntos a otro de forma directa.")
    
    # Lógica de cálculo masivo para padreadas
    df_pivot_sf = df_records.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos')
    df_pivot_sf = df_pivot_sf.sort_index(level=['Temporada', 'Jornada'], ascending=[True, True])
    
    managers_sf = df_records['Mánager'].unique().tolist()
    padreadas_list = []
    
    for m1 in managers_sf:
        for m2 in managers_sf:
            if m1 != m2 and m1 in df_pivot_sf.columns and m2 in df_pivot_sf.columns:
                valid_df = df_pivot_sf[[m1, m2]].dropna()
                if not valid_df.empty:
                    mask = valid_df[m1] > valid_df[m2]
                    if mask.any():
                        group = (~mask).cumsum()
                        streaks = mask.groupby(group).sum()
                        max_streak = int(streaks.max())
                        if max_streak > 0:
                            padreadas_list.append({
                                'Padre (Ganador)': m1,
                                'Hijo (Perdedor)': m2,
                                'Jornadas Seguidas': max_streak
                            })
                            
    if padreadas_list:
        df_padreadas = pd.DataFrame(padreadas_list)
        df_padreadas = df_padreadas.sort_values(by=['Jornadas Seguidas', 'Padre (Ganador)'], ascending=[False, True]).head(10).reset_index(drop=True)
        df_padreadas.index = df_padreadas.index + 1
        df_padreadas.index.name = "Pos."
        st.dataframe(df_padreadas.reset_index().set_index(['Pos.', 'Padre (Ganador)']), use_container_width=True)

    st.markdown("---")

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