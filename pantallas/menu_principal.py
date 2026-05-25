import streamlit as st

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

        st.markdown("##")
        if st.button("🤼 Royal Rumble", use_container_width=True):
            st.session_state.pantalla = "🤼 Royal Rumble"
            st.rerun()
        st.caption("La matriz global de la liga. Todos contra todos en un Heatmap de abuso y humillación.")

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