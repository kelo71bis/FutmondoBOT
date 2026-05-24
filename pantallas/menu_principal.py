import streamlit as st
import pandas as pd

def mostrar_menu(df):
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
        
    st.markdown("---")
    
    st.subheader("⚔️ Matriz de Enfrentamientos")
    st.caption("Lee por filas: cuántas jornadas le ha ganado el mánager de la fila al de la columna de forma directa. (Los empates suman a ambos).")
    
    df_panel_base = df[df['Temporada'] != '2024/25'].copy()
    lista_seasons_panel = sorted(df_panel_base['Temporada'].unique().tolist(), reverse=True)
    
    seasons_panel_sel = st.multiselect(
        "📅 Filtrar temporadas de la matriz (vacío = Todas):", 
        lista_seasons_panel, 
        default=[],
        placeholder="Todas las temporadas"
    )
    
    seasons_to_use = seasons_panel_sel if len(seasons_panel_sel) > 0 else lista_seasons_panel
    
    df_panel_filtered = df_panel_base[df_panel_base['Temporada'].isin(seasons_to_use)]
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