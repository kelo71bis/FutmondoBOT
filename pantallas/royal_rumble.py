import streamlit as st
import pandas as pd
import numpy as np

def mostrar_royal_rumble(df):
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
    if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
    if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
    if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
    if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
        
    st.title("🤼 Royal Rumble")
    st.write("La jaula de acero. Todos contra todos cruzando históricos directos.")
    st.markdown("---")

    # Filtro de Temporadas
    df_clean = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26'))].copy()
    lista_temporadas = sorted(df_clean['Temporada'].unique().tolist(), reverse=True)
    
    seasons_sel = st.multiselect(
        "📅 Filtrar temporadas de las matrices (vacío = Todas las compartidas):", 
        lista_temporadas, 
        default=[],
        placeholder="Todas las temporadas"
    )
    
    seasons_to_use = seasons_sel if len(seasons_sel) > 0 else lista_temporadas
    
    st.markdown("---")
    
    managers = sorted(df_clean['Mánager'].unique().tolist())
    
    # 1. Preparar estructuras vacías
    df_enf_disp = pd.DataFrame(index=managers, columns=managers, data="-")
    df_enf_num = pd.DataFrame(index=managers, columns=managers, data=np.nan)
    
    df_padr_disp = pd.DataFrame(index=managers, columns=managers, data="-")
    df_padr_num = pd.DataFrame(index=managers, columns=managers, data=np.nan)
    
    df_diff_tot_disp = pd.DataFrame(index=managers, columns=managers, data="-")
    df_diff_tot_num = pd.DataFrame(index=managers, columns=managers, data=np.nan)
    
    df_diff_med_disp = pd.DataFrame(index=managers, columns=managers, data="-")
    df_diff_med_num = pd.DataFrame(index=managers, columns=managers, data=np.nan)

    # 2. Cálculos masivos optimizados
    df_filtered = df_clean[df_clean['Temporada'].isin(seasons_to_use)]
    
    df_reg = df_filtered[df_filtered['Temporada'] != '2024/25']
    df_pivot_reg = df_reg.pivot(index=['Temporada', 'Jornada'], columns='Mánager', values='Puntos').sort_index()
    
    pts_tot_reg = df_reg.groupby(['Mánager', 'Temporada'])['Puntos'].sum()
    jors_reg = df_reg.groupby(['Mánager', 'Temporada'])['Puntos'].count()
    
    df_2425 = df_filtered[df_filtered['Temporada'] == '2024/25']
    if not df_2425.empty:
        pts_tot_2425 = df_2425.groupby(['Mánager', 'Temporada'])['Puntos_Acumulados'].max()
        jors_2425 = pd.Series(38, index=pts_tot_2425.index)
        pts_tot_all = pd.concat([pts_tot_reg, pts_tot_2425])
        jors_all = pd.concat([jors_reg, jors_2425])
    else:
        pts_tot_all = pts_tot_reg
        jors_all = jors_reg

    # Iterar pares
    for m1 in managers:
        for m2 in managers:
            if m1 == m2:
                continue
            
            s1 = set(df_filtered[df_filtered['Mánager'] == m1]['Temporada'].unique())
            s2 = set(df_filtered[df_filtered['Mánager'] == m2]['Temporada'].unique())
            shared = list(s1.intersection(s2))
            
            if not shared:
                continue
                
            # Matrices Enfrentamientos y Padreadas (Solo jornadas regulares)
            shared_reg = [s for s in shared if s != '2024/25']
            if shared_reg:
                df_pair = df_pivot_reg.loc[shared_reg, [m1, m2]].dropna()
                tot_jors = len(df_pair)
                if tot_jors > 0:
                    wins = (df_pair[m1] > df_pair[m2]).sum()
                    ties = (df_pair[m1] == df_pair[m2]).sum()
                    score = wins + ties
                    pct = (score / tot_jors) * 100
                    
                    df_enf_disp.at[m1, m2] = f"{score} ({pct:.1f}%)"
                    df_enf_num.at[m1, m2] = pct
                    
                    mask_wins = df_pair[m1] > df_pair[m2]
                    streak = mask_wins.groupby((~mask_wins).cumsum()).sum().max()
                    df_padr_disp.at[m1, m2] = str(int(streak))
                    df_padr_num.at[m1, m2] = int(streak)
            
            # Diferencia de Puntos y Medias
            pts_m1 = pts_tot_all.loc[m1] if m1 in pts_tot_all else pd.Series()
            pts_m2 = pts_tot_all.loc[m2] if m2 in pts_tot_all else pd.Series()
            jrs_m1 = jors_all.loc[m1] if m1 in jors_all else pd.Series()
            jrs_m2 = jors_all.loc[m2] if m2 in jors_all else pd.Series()
            
            sum_p_1 = pts_m1[pts_m1.index.isin(shared)].sum() if not pts_m1.empty else 0
            sum_p_2 = pts_m2[pts_m2.index.isin(shared)].sum() if not pts_m2.empty else 0
            sum_j_1 = jrs_m1[jrs_m1.index.isin(shared)].sum() if not jrs_m1.empty else 0
            sum_j_2 = jrs_m2[jrs_m2.index.isin(shared)].sum() if not jrs_m2.empty else 0
            
            if sum_j_1 > 0 and sum_j_2 > 0:
                diff_tot = sum_p_1 - sum_p_2
                df_diff_tot_disp.at[m1, m2] = f"{diff_tot:.1f}".replace('.0', '')
                df_diff_tot_num.at[m1, m2] = diff_tot
                
                mean_1 = sum_p_1 / sum_j_1
                mean_2 = sum_p_2 / sum_j_2
                diff_med = mean_1 - mean_2
                df_diff_med_disp.at[m1, m2] = f"{diff_med:.1f}"
                df_diff_med_num.at[m1, m2] = diff_med

    # 3. Función segura para aplicar el Heatmap sin errores de variables vacías
    def aplicar_heatmap(df_display, df_numeric, vmin, vmax):
        if df_numeric.isna().all().all():
            return df_display
        return df_display.style.background_gradient(axis=None, gmap=df_numeric, cmap='RdYlGn', vmin=vmin, vmax=vmax)

    # 4. Mostrar pestañas
    tab1, tab2, tab3, tab4 = st.tabs(["⚔️ Matriz de Enfrentamientos", "👨‍👦 Matriz de Padreadas", "🎯 Diferencia Pts Totales", "⚖️ Diferencia Pts Medios"])
    
    with tab1:
        st.subheader("⚔️ Matriz de Enfrentamientos")
        st.caption("Lee por filas: Jornadas ganadas + Empates (Porcentaje de éxito vs rival). Color verde = Dominador.")
        styled_enf = aplicar_heatmap(df_enf_disp, df_enf_num, vmin=0, vmax=100)
        st.dataframe(styled_enf, use_container_width=True)
        
    with tab2:
        st.subheader("👨‍👦 Matriz de Padreadas")
        st.caption("Lee por filas: Récord máximo de jornadas seguidas superando en puntos a la columna (sin empates).")
        max_padr = df_padr_num.max().max() if not df_padr_num.isna().all().all() else 1
        styled_padr = aplicar_heatmap(df_padr_disp, df_padr_num, vmin=0, vmax=max_padr)
        st.dataframe(styled_padr, use_container_width=True)
        
    with tab3:
        st.subheader("🎯 Diferencia de Puntos (Totales)")
        st.caption("Lee por filas: Suma de Puntos de la Fila - Suma de Puntos de la Columna en las temporadas que ambos jugaron juntos.")
        max_tot = df_diff_tot_num.abs().max().max() if not df_diff_tot_num.isna().all().all() else 1
        styled_tot = aplicar_heatmap(df_diff_tot_disp, df_diff_tot_num, vmin=-max_tot, vmax=max_tot)
        st.dataframe(styled_tot, use_container_width=True)
        
    with tab4:
        st.subheader("⚖️ Diferencia de Puntos (Medias)")
        st.caption("Lee por filas: Media de puntos (Fila) - Media de puntos (Columna) en sus temporadas compartidas.")
        max_med = df_diff_med_num.abs().max().max() if not df_diff_med_num.isna().all().all() else 1
        styled_med = aplicar_heatmap(df_diff_med_disp, df_diff_med_num, vmin=-max_med, vmax=max_med)
        st.dataframe(styled_med, use_container_width=True)