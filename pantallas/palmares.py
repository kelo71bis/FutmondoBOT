import streamlit as st
import pandas as pd

def mostrar_palmares(df_ligas, df_copas):
    c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns(5)
    if c_nav1.button("🏠 Menú Principal", use_container_width=True): st.session_state.pantalla = "🏠 Menú Principal"; st.rerun()
    if c_nav2.button("📈 Análisis", use_container_width=True): st.session_state.pantalla = "📈 Análisis por temporadas"; st.rerun()
    if c_nav3.button("🏆 Salón Fama", use_container_width=True): st.session_state.pantalla = "🏆 Salón de la Fama"; st.rerun()
    if c_nav4.button("⚔️ Cara a Cara", use_container_width=True): st.session_state.pantalla = "⚔️ Cara a Cara"; st.rerun()
    if c_nav5.button("🤼 Royal Rumble", use_container_width=True): st.session_state.pantalla = "🤼 Royal Rumble"; st.rerun()
        
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