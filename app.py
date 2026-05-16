import streamlit as st
import pandas as pd
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
        
        df_temp = df[df['Temporada'] == temporada_sel]
        jornada_maxima = int(df_temp['Jornada'].max())
        
        rango_jornadas = st.slider("🔍 Rango de Jornadas en Gráfica", 1, jornada_maxima, (1, jornada_maxima))
        
        col1, col2 = st.columns([1, 1.8])
        with col1:
            st.subheader(f"📊 Tabla (Jornada {jornada_maxima})")
            df_clasif = df_temp[df_temp['Jornada'] == jornada_maxima].sort_values(by="Puntos_Acumulados", ascending=False)
            df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
            df_mostrar.index = df_mostrar.index + 1 
            df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
            st.dataframe(df_mostrar, use_container_width=True)
            
        with col2:
            st.subheader("📈 Evolución de Puntos")
            df_temp_grafica = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
            df_grafica = df_temp_grafica.pivot(index='Jornada', columns='Mánager', values='Puntos_Acumulados')
            st.line_chart(df_grafica, height=420)

    # ==========================================
    # PANTALLA 2: SALÓN DE LA FAMA
    # ==========================================
    elif menu == "🏆 Salón de la Fama":
        st.title("🏆 El Salón de la Fama")
        st.write("El Top 10 histórico de las mejores y peores jornadas de la Liga Santanguissa.")
        st.markdown("---")
        
        df_records = df[~((df['Jornada'] == 1) & (df['Temporada'] == '2025/26')) & (df['Temporada'] != '2024/25')]
        df_desastres = df_records[df_records['Puntos'] > 0]
        
        top10_mejores = df_records.nlargest(10, 'Puntos').reset_index(drop=True)
        top10_peores = df_desastres.nsmallest(10, 'Puntos').reset_index(drop=True)
        
        col1, col2 = st.columns(2)
        
        # 🟢 TOP 10 MEJORES
        with col1:
            st.subheader("🚀 Las Mejores Exhibiciones")
            top1 = top10_mejores.iloc[0]
            st.success(f"🥇 **{top1['Mánager']}**")
            st.metric(label=f"Jornada {int(top1['Jornada'])} ({top1['Temporada']})", value=f"{top1['Puntos']} pts")
            
            c_top2, c_top3 = st.columns(2)
            with c_top2:
                top2 = top10_mejores.iloc[1]
                st.info(f"🥈 **{top2['Mánager']}**")
                st.markdown(f"**{top2['Puntos']} pts** (J{int(top2['Jornada'])} - {top2['Temporada']})")
            with c_top3:
                top3 = top10_mejores.iloc[2]
                st.info(f"🥉 **{top3['Mánager']}**")
                st.markdown(f"**{top3['Puntos']} pts** (J{int(top3['Jornada'])} - {top3['Temporada']})")
                
            st.caption("Puestos del 4 al 10:")
            df_resto_mejores = top10_mejores.iloc[3:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
            df_resto_mejores.index = range(4, 11)
            st.dataframe(df_resto_mejores, use_container_width=True)
            
        # 🔴 TOP 10 PEORES
        with col2:
            st.subheader("💩 Los Mayores Desastres")
            if not top10_peores.empty:
                bot1 = top10_peores.iloc[0]
                st.error(f"🥇 **{bot1['Mánager']}**")
                st.metric(label=f"Jornada {int(bot1['Jornada'])} ({bot1['Temporada']})", value=f"{bot1['Puntos']} pts")
                
                c_bot2, c_bot3 = st.columns(2)
                with c_bot2:
                    bot2 = top10_peores.iloc[1]
                    st.warning(f"🥈 **{bot2['Mánager']}**")
                    st.markdown(f"**{bot2['Puntos']} pts** (J{int(bot2['Jornada'])} - {bot2['Temporada']})")
                with c_bot3:
                    bot3 = top10_peores.iloc[2]
                    st.warning(f"🥉 **{bot3['Mánager']}**")
                    st.markdown(f"**{bot3['Puntos']} pts** (J{int(bot3['Jornada'])} - {bot3['Temporada']})")
                    
                st.caption("Puestos del 4 al 10:")
                df_resto_peores = top10_peores.iloc[3:][['Mánager', 'Puntos', 'Jornada', 'Temporada']]
                df_resto_peores.index = range(4, 11)
                st.dataframe(df_resto_peores, use_container_width=True)
            st.caption("ℹ️ *Nota: Se excluyen las jornadas con 0 puntos o puntuación negativa.*")

        # ---------------------------------------------------------
        # 🏅 NUEVO MEDALLERO (CIELO E INFIERNO)
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("🏅 El Medallero de Jornadas (Cielo e Infierno)")
        st.write("¿Quién domina las jornadas y quién se arrastra por el fango? *(Excluida temporada 2024/25)*")
        
        # Copia segura para operar
        df_medallero = df_records.copy()
        
        # Clasificar a los mánagers dentro de cada jornada
        # Rank=1 en Mejor significa que sacó la máxima puntuación
        # Rank=1 en Peor significa que sacó la mínima puntuación
        df_medallero['Rank_Mejor'] = df_medallero.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False)
        df_medallero['Rank_Peor'] = df_medallero.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=True)
        
        # Contar cuántas veces ha quedado cada uno en estas posiciones
        df_oros = df_medallero[df_medallero['Rank_Mejor'] == 1].groupby('Mánager').size()
        df_platas = df_medallero[df_medallero['Rank_Mejor'] == 2].groupby('Mánager').size()
        df_penultimos = df_medallero[df_medallero['Rank_Peor'] == 2].groupby('Mánager').size()
        df_ultimos = df_medallero[df_medallero['Rank_Peor'] == 1].groupby('Mánager').size()
        
        # Unir todo en un solo DataFrame
        tabla_medallas = pd.DataFrame({
            '🥇 1º (Oros)': df_oros,
            '🥈 2º (Platas)': df_platas,
            '⚠️ Penúltimos': df_penultimos,
            '💩 Últimos': df_ultimos
        }).fillna(0).astype(int)
        
        # Ordenar la tabla: Primero los que tienen más Oros, a igualdad, el que tenga más Platas
        tabla_medallas = tabla_medallas.sort_values(by=['🥇 1º (Oros)', '🥈 2º (Platas)'], ascending=[False, False]).reset_index()
        tabla_medallas.index = tabla_medallas.index + 1
        
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
            
            tabla_titulos['Total Títulos'] = tabla_titulos['Ligas'] + tabla_titulos['Copas']
            tabla_titulos = tabla_titulos.sort_values(by=['Total Títulos', 'Ligas'], ascending=[False, False]).reset_index(drop=True)
            tabla_titulos.index = tabla_titulos.index + 1
            
            st.dataframe