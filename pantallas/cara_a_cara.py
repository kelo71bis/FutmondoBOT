import streamlit as st
import pandas as pd
import altair as alt
import random

def mostrar_cara_a_cara(df, df_ligas, df_copas, clasificacion_2020_21):
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
    if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
    if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
    if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
    if c_nav4.button("🥇 Palmarés", use_container_width=True): st.session_state.pantalla = "🥇 Palmarés Histórico"; st.rerun()
        
    st.title("🏟️ Coliseo Cara a Cara")
    st.markdown("---")
    
    lista_todos_managers = sorted(df['Mánager'].unique().tolist())
    
    if st.button("🎲 Combate Aleatorio (Sorpréndeme)", use_container_width=True):
        pares_validos = []
        for m_a in lista_todos_managers:
            for m_b in lista_todos_managers:
                if m_a != m_b:
                    seasons_a = set(df[df['Mánager'] == m_a]['Temporada'].unique())
                    seasons_b = set(df[df['Mánager'] == m_b]['Temporada'].unique())
                    if m_a in clasificacion_2020_21: seasons_a.add("2020/21")
                    if m_b in clasificacion_2020_21: seasons_b.add("2020/21")
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
        seasons_m1 = set(df[df['Mánager'] == m1]['Temporada'].unique())
        seasons_m2 = set(df[df['Mánager'] == m2]['Temporada'].unique())
        if m1 in clasificacion_2020_21: seasons_m1.add("2020/21")
        if m2 in clasificacion_2020_21: seasons_m2.add("2020/21")
        
        temporadas_comunes = sorted(list(seasons_m1.intersection(seasons_m2)), reverse=True)
        
        with col_f3:
            temporadas_h2h_sel = st.multiselect("📅 Temporadas del combate (vacío = Todas):", temporadas_comunes, default=[], placeholder="Todas las temporadas compartidas")
        
        seasons_to_use = temporadas_h2h_sel if len(temporadas_h2h_sel) > 0 else temporadas_comunes
        
        if len(seasons_to_use) == 0:
            st.warning("⚠️ No hay temporadas disponibles para analizar.")
        else:
            df_h2h = df[(df['Mánager'].isin([m1, m2])) & (df['Temporada'].isin(seasons_to_use)) & (df['Temporada'] != '2024/25')]
            df_pivot = df_h2h.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos').dropna() if not df_h2h.empty else pd.DataFrame()
            
            df_pivot = df_pivot.sort_index(level=['Temporada', 'Jornada'], ascending=[True, True])
            
            total_jornadas = len(df_pivot)
            wins_m1 = (df_pivot[m1] > df_pivot[m2]).sum() if total_jornadas > 0 else 0
            wins_m2 = (df_pivot[m2] > df_pivot[m1]).sum() if total_jornadas > 0 else 0
            empates = (df_pivot[m1] == df_pivot[m2]).sum() if total_jornadas > 0 else 0
            
            if total_jornadas > 0:
                mask_m1_wins = df_pivot[m1] > df_pivot[m2]
                streak_m1_h2h = mask_m1_wins.groupby((~mask_m1_wins).cumsum()).sum().max()
                
                mask_m2_wins = df_pivot[m2] > df_pivot[m1]
                streak_m2_h2h = mask_m2_wins.groupby((~mask_m2_wins).cumsum()).sum().max()
            else:
                streak_m1_h2h = streak_m2_h2h = 0
            
            pct_m1 = (wins_m1 / total_jornadas) * 100 if total_jornadas > 0 else 0
            pct_m2 = (wins_m2 / total_jornadas) * 100 if total_jornadas > 0 else 0
            
            st.markdown("---")
            st.markdown(f"**{m1}** y **{m2}** han coincidido en un total de **{total_jornadas} jornadas** registradas a lo largo de **{len(seasons_to_use)} temporadas** compartidas.")
            st.markdown(f"**{m1}** ha quedado por encima de **{m2}** en **{wins_m1} jornadas** ({pct_m1:.1f}%), mientras que **{m2}** ha hecho lo contrario en **{wins_m2} jornadas** ({pct_m2:.1f}%). *(Empataron en {empates} ocasiones)*.")
            st.write("Este es el resultado del cara a cara global (Ligas completas terminadas uno por encima del otro):")
            st.markdown("<br>", unsafe_allow_html=True)
            
            ligas_m1_final = 0
            ligas_m2_final = 0
            
            df_finales_h2h = df[(df['Mánager'].isin([m1, m2])) & (df['Temporada'].isin(seasons_to_use))].copy()
            if not df_finales_h2h.empty:
                df_fin_loc = df_finales_h2h.loc[df_finales_h2h.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()]
                df_fin_pivot = df_fin_loc.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna()
                if m1 in df_fin_pivot.columns and m2 in df_fin_pivot.columns:
                    ligas_m1_final += (df_fin_pivot[m1] > df_fin_pivot[m2]).sum()
                    ligas_m2_final += (df_fin_pivot[m2] > df_fin_pivot[m1]).sum()
            
            if "2020/21" in seasons_to_use and m1 in clasificacion_2020_21 and m2 in clasificacion_2020_21:
                idx_m1 = clasificacion_2020_21.index(m1)
                idx_m2 = clasificacion_2020_21.index(m2)
                if idx_m1 < idx_m2: ligas_m1_final += 1
                else: ligas_m2_final += 1

            ligas_tot_m1 = len(df_ligas[(df_ligas['Mánager'] == m1) & (df_ligas['Posicion'] == 'Campeón')]) if df_ligas is not None else 0
            copas_tot_m1 = len(df_copas[(df_copas['Mánager'] == m1) & (df_copas['Posicion'] == 'Campeón')]) if df_copas is not None else 0
            stars_m1 = "⭐" * ligas_tot_m1 if ligas_tot_m1 > 0 else "-"
            cups_m1 = "🏆" * copas_tot_m1 if copas_tot_m1 > 0 else "-"

            ligas_tot_m2 = len(df_ligas[(df_ligas['Mánager'] == m2) & (df_ligas['Posicion'] == 'Campeón')]) if df_ligas is not None else 0
            copas_tot_m2 = len(df_copas[(df_copas['Mánager'] == m2) & (df_copas['Posicion'] == 'Campeón')]) if df_copas is not None else 0
            stars_m2 = "⭐" * ligas_tot_m2 if ligas_tot_m2 > 0 else "-"
            cups_m2 = "🏆" * copas_tot_m2 if copas_tot_m2 > 0 else "-"

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

            st.subheader("⚖️ Estadísticas del combate")
            
            def calcular_media_h2h(manager_name):
                df_m = df[(df['Mánager'] == manager_name) & (df['Temporada'].isin(seasons_to_use))]
                df_reg = df_m[df_m['Temporada'] != '2024/25']
                s_r = df_reg['Puntos'].sum()
                c_r = len(df_reg)
                
                df_2425 = df_m[df_m['Temporada'] == '2024/25']
                if not df_2425.empty:
                    s_24 = df_2425['Puntos_Acumulados'].max()
                    c_24 = 38
                else:
                    s_24, c_24 = 0, 0
                tot_s = s_r + s_24
                tot_c = c_r + c_24
                return tot_s / tot_c if tot_c > 0 else 0

            media_m1 = calcular_media_h2h(m1)
            media_m2 = calcular_media_h2h(m2)
            
            df_m1_reg = df_h2h[df_h2h['Mánager'] == m1]
            df_m2_reg = df_h2h[df_h2h['Mánager'] == m2]
            
            max_jor_m1 = df_m1_reg['Puntos'].max() if not df_m1_reg.empty else 0
            max_jor_m2 = df_m2_reg['Puntos'].max() if not df_m2_reg.empty else 0
            
            valid_min_m1 = df_m1_reg[df_m1_reg['Puntos'] > 0]['Puntos']
            valid_min_m2 = df_m2_reg[df_m2_reg['Puntos'] > 0]['Puntos']
            min_jor_m1_str = f"{valid_min_m1.min():.1f}" if not valid_min_m1.empty else "-"
            min_jor_m2_str = f"{valid_min_m2.min():.1f}" if not valid_min_m2.empty else "-"
            
            df_all_seasons = df[df['Temporada'].isin(seasons_to_use) & (df['Temporada'] != '2024/25')].copy()
            if not df_all_seasons.empty:
                df_all_seasons['Rank_Jor'] = df_all_seasons.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
                veces_lider_m1 = len(df_all_seasons[(df_all_seasons['Mánager'] == m1) & (df_all_seasons['Rank_Jor'] == 1)])
                veces_lider_m2 = len(df_all_seasons[(df_all_seasons['Mánager'] == m2) & (df_all_seasons['Rank_Jor'] == 1)])
                
                df_lideres_all = df_all_seasons[df_all_seasons['Rank_Jor'] == 1].sort_values(['Mánager', 'Temporada', 'Jornada'])
                df_lideres_all['Grupo_Racha'] = (df_lideres_all['Jornada'] != df_lideres_all['Jornada'].shift() + 1).cumsum()
                r_m1 = df_lideres_all[df_lideres_all['Mánager'] == m1].groupby(['Temporada', 'Grupo_Racha']).size()
                r_m2 = df_lideres_all[df_lideres_all['Mánager'] == m2].groupby(['Temporada', 'Grupo_Racha']).size()
                racha_max_m1 = int(r_m1.max()) if not r_m1.empty else 0
                racha_max_m2 = int(r_m2.max()) if not r_m2.empty else 0
            else:
                veces_lider_m1 = veces_lider_m2 = racha_max_m1 = racha_max_m2 = 0

            html_table = f"""<div style="display: flex; justify-content: center; width: 100%;">
<table style="width: 70%; border-collapse: collapse; font-size: 17px; font-family: sans-serif; text-align: center;">
<tr style="border-bottom: 1px solid #f0f2f6;">
<td style="width: 25%; font-size: 22px; font-weight: bold; color: #2ca02c; padding: 12px;">{media_m1:.1f}</td>
<td style="width: 50%; color: #7f7f7f; font-weight: 500;">Media Puntos por Jornada</td>
<td style="width: 25%; font-size: 22px; font-weight: bold; color: #d62728; padding: 12px;">{media_m2:.1f}</td>
</tr>"""
            
            show_seasonal_metrics = len(seasons_to_use) > 1
            
            if show_seasonal_metrics and not df_finales_h2h.empty:
                df_fin_loc = df_finales_h2h.loc[df_finales_h2h.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()]
                df_fin_pivot_full = df_fin_loc.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna(how='all')
                
                media_final_m1 = df_fin_pivot_full[m1].mean() if m1 in df_fin_pivot_full.columns else 0
                media_final_m2 = df_fin_pivot_full[m2].mean() if m2 in df_fin_pivot_full.columns else 0
                max_temp_p_m1 = df_fin_pivot_full[m1].max() if m1 in df_fin_pivot_full.columns else 0
                max_temp_p_m2 = df_fin_pivot_full[m2].max() if m2 in df_fin_pivot_full.columns else 0
                
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
</tr>"""

            html_table += f"""
<tr style="border-bottom: 1px solid #f0f2f6;">
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_jor_m1:.1f}</td>
<td style="color: #7f7f7f; font-weight: 500;">Máxima Puntuación en Jornada</td>
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{max_jor_m2:.1f}</td>
</tr>
<tr style="border-bottom: 1px solid #f0f2f6;">
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{min_jor_m1_str}</td>
<td style="color: #7f7f7f; font-weight: 500;">Mínima Puntuación en Jornada</td>
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{min_jor_m2_str}</td>
</tr>
<tr style="border-bottom: 1px solid #f0f2f6;">
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{wins_m1}</td>
<td style="color: #7f7f7f; font-weight: 500;">Jornadas siendo mejor</td>
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{wins_m2}</td>
</tr>
<tr style="border-bottom: 1px solid #f0f2f6;">
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{int(streak_m1_h2h)}</td>
<td style="color: #7f7f7f; font-weight: 500;">Jornadas consecutivas siendo mejor</td>
<td style="font-size: 22px; font-weight: bold; padding: 12px;">{int(streak_m2_h2h)}</td>
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
</div>"""
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

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

            st.markdown("---")
            st.subheader("📈 Histórico Temporadas")
            st.caption("Esta tabla refleja el cierre total de puntos acumulados al final de cada liga compartida.")
            
            df_inmutable_base = df.loc[df.groupby(['Temporada', 'Mánager'])['Jornada'].idxmax()].copy()
            df_inmutable_fil = df_inmutable_base[(df_inmutable_base['Mánager'].isin([m1, m2])) & (df_inmutable_base['Temporada'].isin(seasons_to_use))]
            
            if not df_inmutable_fil.empty:
                df_matriz_finales = df_inmutable_fil.pivot(index='Temporada', columns='Mánager', values='Puntos_Acumulados').dropna(how='all')
            else:
                df_matriz_finales = pd.DataFrame(columns=[m1, m2])
                
            if "2020/21" in seasons_to_use and m1 in clasificacion_2020_21 and m2 in clasificacion_2020_21:
                idx_m1 = clasificacion_2020_21.index(m1)
                idx_m2 = clasificacion_2020_21.index(m2)
                df_matriz_finales.loc['2020/21'] = {m1: f"Pos. {idx_m1+1} (Sin Pts)", m2: f"Pos. {idx_m2+1} (Sin Pts)"}
            
            df_matriz_finales = df_matriz_finales.sort_index(ascending=False)
            
            def format_mixed(val):
                if isinstance(val, (int, float)):
                    return f"{val:.0f}"
                return val if pd.notna(val) else "-"
                
            st.dataframe(df_matriz_finales.map(format_mixed), use_container_width=True)