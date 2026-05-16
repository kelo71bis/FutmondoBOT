import streamlit as st
import pandas as pd
import os

# ⚙️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Liga Santanguissa - Futmondo", page_icon="🏆", layout="wide")

# 🏆 CABECERA
st.title("⚽ Liga Santanguissa")
st.write("Portal estadístico oficial. Los datos se sincronizan automáticamente con Futmondo.")
st.markdown("---")

# 📂 RUTAS DE LOS ARCHIVOS
ruta_master = "datos/vistas_negocio/Fact_Global_Master.xlsx"
ruta_propietarios = "datos/maestros/md_propietarios.xlsx" # <- Revisa si tu script md_propietarios lo guarda aquí

# Control de errores: Verificar que ambos archivos existan antes de cargar la web
if not os.path.exists(ruta_master):
    st.error(f"❌ No se encuentra el archivo global en: {ruta_master}")
elif not os.path.exists(ruta_propietarios):
    st.error(f"❌ No se encuentra el maestro de propietarios en: {ruta_propietarios}. Ejecuta tu script de propietarios primero.")
else:
    # 1. Cargar las bases de datos en memoria
    df = pd.read_excel(ruta_master)
    df_prop = pd.read_excel(ruta_propietarios)
    
    # 🔄 CRUCE DE DATOS AUTOMÁTICO (Sin meter nada a mano)
    # Convertimos el maestro de propietarios en un diccionario de mapeo {ID: Nombre}
    mapeo_nombres = df_prop.set_index('id_propietario')['nombre'].to_dict()
    # Sustituimos el ID de Futmondo por el nombre real del mánager. Si no lo encuentra, deja el ID por seguridad.
    df['Mánager'] = df['ID_Futmondo'].map(mapeo_nombres).fillna(df['ID_Futmondo'])
    
    # 📅 MENÚ LATERAL (Filtros)
    st.sidebar.header("🎯 Filtros de Consulta")
    temporadas = df['Temporada'].unique().tolist()
    temporada_sel = st.sidebar.selectbox("📅 Selecciona la Temporada", temporadas, index=len(temporadas)-1)
    
    # Filtrar datos por la temporada seleccionada
    df_temp = df[df['Temporada'] == temporada_sel]
    jornada_maxima = int(df_temp['Jornada'].max())
    
    # ⏱️ Selector de rango de jornadas para desapelotonar las líneas de la gráfica
    rango_jornadas = st.sidebar.slider(
        "🔍 Rango de Jornadas en Gráfica", 
        min_value=1, 
        max_value=jornada_maxima, 
        value=(1, jornada_maxima)
    )
    
    # 📐 MAQUETACIÓN: Dividimos la pantalla en dos columnas
    col1, col2 = st.columns([1, 1.8])
    
    with col1:
        st.subheader(f"📊 Clasificación (Jornada {jornada_maxima})")
        
        # Filtrar solo la última jornada disponible para la tabla
        df_clasif = df_temp[df_temp['Jornada'] == jornada_maxima].copy()
        df_clasif = df_clasif.sort_values(by="Puntos_Acumulados", ascending=False)
        
        # Limpiar la tabla para la vista web usando los nombres automáticos
        df_mostrar = df_clasif[["Mánager", "Puntos_Acumulados", "Acumulado_Total"]].reset_index(drop=True)
        df_mostrar.index = df_mostrar.index + 1 
        df_mostrar.columns = ["Mánager", "Puntos Temporada", "Puntos Históricos"]
        
        st.dataframe(df_mostrar, use_container_width=True)
        
    with col2:
        st.subheader("📈 Evolución del Campeonato")
        
        # Filtrar los datos de la gráfica según el rango del slider de jornadas
        df_temp_grafica = df_temp[(df_temp['Jornada'] >= rango_jornadas[0]) & (df_temp['Jornada'] <= rango_jornadas[1])]
        
        # Pivotar la tabla usando la columna 'Mánager' dinámica
        df_grafica = df_temp_grafica.pivot(index='Jornada', columns='Mánager', values='Puntos_Acumulados')
        
        # Dibujar la gráfica estirada para que respire bien
        st.line_chart(df_grafica, height=420)
        
    # 🌟 SECCIÓN EXTRA: El MVP de la jornada
    st.markdown("---")
    df_mvp = df_clasif.sort_values(by="Puntos", ascending=False).iloc[0]
    st.success(f"🔥 **MVP de la Jornada {jornada_maxima}:** **{df_mvp['Mánager']}** ha ganado la jornada con **{df_mvp['Puntos']} puntos**.")