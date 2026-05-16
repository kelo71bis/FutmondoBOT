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
    # 🗂️ MENÚ DE NAVEGACIÓN LATERAL
    st.sidebar.title("⚽ Menú de Liga")
    menu = st.sidebar.radio("Navegación", [
        "🏠 Visión General", 
        "🏆 Salón de la Fama", 
        "🥇 Palmarés Histórico",
        "👤 Perfiles (Próximamente)", 
        "⚔️ Cara a Cara (Próximamente)"
    ])
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ Info Histórica Importante"):
        st.caption("• **2020/21**: Faltan los datos de la temporada inaugural.")
        st.caption("• **2022/23**: **Pallejandro** se une sustituyendo a **Arsenati**.")
        st.caption("• **2024/25**: Solo hay foto final de puntos acumulados. Sus jornadas no cuentan para récords ni MVPs.")

    # ==========================================
    # PANTALLA 1: VISIÓN GENERAL
    # ==========================================
    if menu == "🏠 Visión General":
        st.title("🏠 Clasificación Actual")
        st.markdown("---")
        
        col_filtros, col_vacio = st.columns([1, 3])
        with col_filtros:
            temporadas = df['Temporada'].unique().tolist()
            temporada_sel = st.selectbox("📅 Selecciona la Temporada", temporadas, index=len(temporadas)-1)
        
        # Filtramos la temporada elegida
        df_temp = df[df['Temporada'] == temporada_sel].copy()
        
        # 🛡️ CONDICIÓN ESPECIAL: TEMPORADA 2024/25
        if temporada_sel == "2024/25":
            st.subheader("📊 Tabla Final (Temporada 2024/25)")
            # Nos aseguramos de coger solo la última jornada disponible para que no se dupliquen datos
            jornada_max_2425 = df_temp['Jornada'].max()
            df_clasif = df_temp[df_temp['Jornada'] == jornada_max_2425].sort_values(by="Puntos_Acumulados", ascending=False)
            
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
            
            # 🧊 Congelamos Posición y Mánager
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.index.name = "Pos."
            df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
            
            col_tabla, col_info = st.columns([1, 1.8])
            with col_tabla:
                st.dataframe(df_mostrar, use_container_width=True)
            with col_info:
                st.info("ℹ️ Para la temporada 2024/25 solo disponemos del cierre de puntos acumulados. Por este motivo, las gráficas de evolución temporal por jornada no están habilitadas.")
                
        # 🚀 COMPORTAMIENTO NORMAL (Otras temporadas)
        else:
            df_temp['Posición'] = df_temp.groupby('Jornada')['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
            df_temp['Posición_Jornada'] = df_temp.groupby('Jornada')['Puntos'].rank(method='min', ascending=False).astype(int)
            
            jornada_maxima = int(df_temp['Jornada'].max())
            
            col1, col2 = st.columns([1, 1.8])
            
            # COLUMNA IZQUIERDA: Slider + Tabla (Ideal para el orden en móvil)
            with col1:
                rango_jornadas = st.slider("🔍 Rango de Jornadas", 1, jornada_maxima, (1, jornada_maxima))
                jornada_seleccionada = rango_jornadas[1] # Coge el valor máximo del rango seleccionado
                
                st.subheader(f"📊 Tabla (Jornada {jornada_seleccionada})")
                df_clasif = df_temp[df_temp['Jornada'] == jornada_seleccionada].sort_values(by="Puntos_Acumulados", ascending=False)
                df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
                df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
                
                # 🧊 Congelamos Posición y Mánager
                df_mostrar.index = df_mostrar.index + 1 
                df_mostrar.index.name = "Pos."
                df_mostrar = df_mostrar.reset_index().set_index(['Pos.', 'Mánager'])
                
                st.dataframe(df_mostrar, use_container_width=True)
                
            # COLUMNA DERECHA: Filtro Equipos + Gráficas (Aparecerá debajo en móvil)
            with col2:
                lista_managers_disponibles = sorted(df_temp['Mánager'].unique().tolist())
                managers_seleccionados = st.multiselect(
                    "👥 Filtrar Equipos en Gráficas:", 
                    lista_managers_disponibles, 
                    default=lista_managers_disponibles
                )
                
                st.subheader("📈 Análisis de Evolución")
                
                df_temp_grafica = df_temp[
                    (df_temp['Jornada'] >= rango_jornadas[0]) & 
                    (df_temp['Jornada'] <= rango_jornadas[1]) &
                    (df_temp['Mánager'].isin(managers_seleccionados))
                ]
                
                if not df_temp_grafica.empty:
                    tab_pos, tab_pos_jor, tab_pts_acu, tab_pts_jor = st.tabs([
                        "🎢 Posición Acumulada", 
                        "🎯 Posición en Jornada", 
                        "📈 Puntos Acumulados",
                        "⚡ Puntos en Jornada"
                    ])
                    
                    num_managers_total = df_temp['Mánager'].nunique()
                    lista_posiciones_total = list(range(1, num_managers_total + 1))
                    
                    with tab_pos:
                        grafica_posiciones = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Posición:Q', 
                                    scale=alt.Scale(domain=[num_managers_total, 1]), 
                                    title='Posición Acumulada', 
                                    axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
                            color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="bottom")),
                            tooltip=['Mánager', 'Jornada', 'Posición', 'Puntos_Acumulados']
                        ).properties(height=420)
                        st.altair_chart(grafica_posiciones, use_container_width=True)
                        
                    with tab_pos_jor:
                        grafica_pos_jornada = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Posición_Jornada:Q', 
                                    scale=alt.Scale(domain=[num_managers_total, 1]), 
                                    title='Posición en la Jornada', 
                                    axis=alt.Axis(values=lista_posiciones_total, format='d', tickMinStep=1)),
                            color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="bottom")),
                            tooltip=['Mánager', 'Jornada', 'Puntos', 'Posición_Jornada']
                        ).properties(height=420)
                        st.altair_chart(grafica_pos_jornada, use_container_width=True)
                        
                    with tab_pts_acu:
                        min_pts_acu = int(df_temp_grafica['Puntos_Acumulados'].min())
                        max_pts_acu = int(df_temp_grafica['Puntos_Acumulados'].max())
                        margen_acu = max(20, int((max_pts_acu - min_pts_acu) * 0.05))
                        
                        grafica_puntos_acu = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Puntos_Acumulados:Q', 
                                    scale=alt.Scale(domain=[min_pts_acu - margen_acu, max_pts_acu + margen_acu]), 
                                    title='Puntos Acumulados'),
                            color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="bottom")),
                            tooltip=['Mánager', 'Jornada', 'Puntos_Acumulados', 'Posición']
                        ).properties(height=420)
                        st.altair_chart(grafica_puntos_acu, use_container_width=True)
                        
                    with tab_pts_jor:
                        min_pts_jor = int(df_temp_grafica['Puntos'].min())
                        max_pts_jor = int(df_temp_grafica['Puntos'].max())
                        margen_jor = max(10, int((max_pts_jor - min_pts_jor) * 0.1))
                        
                        grafica_puntos_jor = alt.Chart(df_temp_grafica).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X('Jornada:O', title='Jornada', axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('Puntos:Q', 
                                    scale=alt.Scale(domain=[min_pts_jor - margen_jor, max_pts_jor + margen_jor]), 
                                    title='Puntos en la Jornada'),
                            color=alt.Color('Mánager:N', legend=alt.Legend(title="Equipos", orient="bottom")),
                            tooltip=['Mánager', 'Jornada', 'Puntos', 'Posición_Jornada']
                        ).properties(height=420)
                        st.altair_chart(grafica_puntos_jor, use_container_width=True)
                else:
                    st.warning("⚠️ Selecciona al menos un mánager en el filtro para pintar las gráficas.")

    # ==========================================
    # PANTALLA 2: SALÓN DE LA FAMA
    # ==========================================
    elif menu == "🏆 Salón de la Fama":
        st.title("🏆 El Salón de la Fama")
        st.write("Consulta los mejores y peores registros históricos o fíltralos por una temporada concreta.")
        st.markdown("---")
        
        df_base_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26')) & (df['Temporada'] != '2024/25')]
        
        col_filtro_sf, _ = st.columns([1, 3])
        with col_filtro_sf:
            lista_temporadas = ["Todas las temporadas"] + sorted(df_base_records['Temporada'].unique().tolist(), reverse=True)
            temporada_sf_sel = st.selectbox("📅 Filtrar por Temporada:", lista_temporadas, index=0)
            
        if temporada_sf_sel != "Todas las temporadas":
            df_records = df_base_records[df_base_records['Temporada'] == temporada_sf_sel]
        else:
            df_records = df_base_records
            
        df_desastres = df_records[df_records['Puntos'] > 0]
        
        if not df_records.empty:
            limite_mejores = min(10, len(df_records))
            limite_peores = min(10, len(df_desastres))
            
            top10_mejores = df_records.nlargest(limite_mejores, 'Puntos').reset_index(drop=True)
            top10_peores = df_desastres.nsmallest(limite_peores, 'Puntos').reset_index(drop=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Las Mejores Exhibiciones")
                if not top10_mejores.empty:
                    top1 = top10_mejores.iloc[0]
                    st.success(f"🥇 **{top1['Mánager']}**")
                    st.metric(label=f"Jornada {int(top1['Jornada'])} ({top1['Temporada']})", value=f"{top1['Puntos']} pts")
                    
                    c_top2, c_top3 = st.columns(2)
                    with c_top2:
                        if len(top10_mejores) > 1:
                            top2 = top10_mejores.iloc[1]
                            st.info(f"🥈 **{top2['Mánager']}**")
                            st.markdown(f"**{top2['Puntos']} pts** (J{int(top2['Jornada'])} - {top2['Temporada']})")
                    with c_top3:
                        if len(top10_mejores) > 2:
                            top3 = top10_mejores.iloc[2]
                            st.info(f"🥉 **{top3['Mánager']}**")
                            st.markdown(f"**{top3['Puntos']} pts** (J{int(top3['Jornada'])} - {top3['Temporada']})")
                        
                    if len(top10_mejores) > 3:
                        st.caption("Puestos del 4 al 10:")
                        df_resto_mejores = top10_mejores.iloc[3:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
                        
                        # 🧊 Congelamos Posición y Mánager
                        df_resto_mejores.index = range(4, 4 + len(df_resto_mejores))
                        df_resto_mejores.index.name = "Pos."
                        df_resto_mejores = df_resto_mejores.reset_index().set_index(['Pos.', 'Mánager'])
                        st.dataframe(df_resto_mejores, use_container_width=True)
                
            with col2:
                st.subheader("💩 Los Mayores Desastres")
                if not top10_peores.empty:
                    bot1 = top10_peores.iloc[0]
                    st.error(f"🥇 **{bot1['Mánager']}**")
                    st.metric(label=f"Jornada {int(bot1['Jornada'])} ({bot1['Temporada']})", value=f"{bot1['Puntos']} pts")
                    
                    c_bot2, c_bot3 = st.columns(2)
                    with c_bot2:
                        if len(top10_peores) > 1:
                            bot2 = top10_peores.iloc[1]
                            st.warning(f"🥈 **{bot2['Mánager']}**")
                            st.markdown(f"**{bot2['Puntos']} pts** (J{int(bot2['Jornada'])} - {bot2['Temporada']})")
                    with c_bot3:
                        if len(top10_peores) > 2:
                            bot3 = top10_peores.iloc[2]
                            st.warning(f"🥉 **{bot3['Mánager']}**")
                            st.markdown(f"**{bot3['Puntos']} pts** (J{int(bot3['Jornada'])} - {bot3['Temporada']})")
                        
                    if len(top10_peores) > 3:
                        st.caption("Puestos del 4 al 10:")
                        df_resto_peores = top10_peores.iloc[3:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
                        
                        # 🧊 Congelamos Posición y Mánager
                        df_resto_peores.index = range(4, 4 + len(df_resto_peores))
                        df_resto_peores.index.name = "Pos."
                        df_resto_peores = df_resto_peores.reset_index().set_index(['Pos.', 'Mánager'])
                        st.dataframe(df_resto_peores, use_container_width=True)
                st.caption("ℹ️ *Nota: Se excluyen las jornadas con 0 puntos o puntuación negativa.*")

        st.markdown("---")
        st.subheader("🏅 El Medallero de Jornadas (Cielo e Infierno)")
        st.write(f"Conteo de posiciones por jornada aplicando el filtro actual: **{temporada_sf_sel}**")
        
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
            
            # 🧊 Congelamos Posición y Mánager
            tabla_medallas = tabla_medallas.sort_values(by=['🥇 1º (Oros)', '🥈 2º (Platas)'], ascending=[False, False]).reset_index()
            tabla_medallas.index = tabla_medallas.index + 1
            tabla_medallas.index.name = "Pos."
            tabla_medallas = tabla_medallas.reset_index().set_index(['Pos.', 'Mánager'])
            
            st.dataframe(tabla_medallas, use_container_width=True)

    # ==========================================
    # PANTALLA 3: PALMARÉS HISTÓRICO
    # ==========================================
    elif menu == "🥇 Palmarés Histórico":
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
            
            # 🧊 Congelamos Posición y Mánager
            tabla_titulos['Total Títulos'] = tabla_titulos['Ligas'] + tabla_titulos['Copas']
            tabla_titulos = tabla_titulos.sort_values(by=['Total Títulos', 'Ligas'], ascending=[False, False]).reset_index(drop=True)
            tabla_titulos.index = tabla_titulos.index + 1
            tabla_titulos.index.name = "Pos."
            tabla_titulos = tabla_titulos.reset_index().set_index(['Pos.', 'Mánager'])
            
            st.dataframe(tabla_titulos[['Ligas', 'Copas', 'Total Títulos']], use_container_width=True)

    elif menu in ["👤 Perfiles (Próximamente)", "⚔️ Cara a Cara (Próximamente)"]:
        st.title(menu)
        st.info("🚧 Estamos trabajando en esta sección. ¡Pronto habrá más salseo!")

else:
    st.error("❌ Faltan los archivos de datos globales.")