import pandas as pd
import os

def generar_palmares_liga():
    print("🏆 Generando Palmarés de Liga Histórico...")
    
    ruta_master = "datos/vistas_negocio/Fact_Global_Master.xlsx"
    ruta_salida = "datos/maestros/md_palmares_liga.xlsx"
    
    if not os.path.exists(ruta_master):
        print(f"❌ Error: No se encuentra {ruta_master}")
        return

    # 1. Cargar datos globales
    df = pd.read_excel(ruta_master)
    
    # 2. Encontrar la última jornada de cada temporada
    max_jornadas = df.groupby('Temporada')['Jornada'].max().reset_index()
    
    # Quedarnos solo con las filas de esas jornadas finales
    df_finales = pd.merge(df, max_jornadas, on=['Temporada', 'Jornada'])
    
    palmares_calculado = []
    
    # 3. Extraer Campeón y Subcampeón dinámicamente CON FRENO PARA LIGAS EN CURSO
    temporadas = df_finales['Temporada'].unique()
    for temp in temporadas:
        df_temp = df_finales[df_finales['Temporada'] == temp].sort_values(by='Puntos_Acumulados', ascending=False)
        jornada_max_temp = df_temp.iloc[0]['Jornada']
        
        # 🛑 REGLA DE ORO: Solo repartimos trofeos si se llegó a la J38 (o es la foto de la 24/25)
        if jornada_max_temp == 38 or temp == '2024/25':
            campeon_id = df_temp.iloc[0]['ID_Futmondo']
            subcampeon_id = df_temp.iloc[1]['ID_Futmondo'] if len(df_temp) > 1 else None
            
            palmares_calculado.append({"Temporada": temp, "Competicion": "Liga", "Posicion": "Campeón", "ID_Futmondo": campeon_id})
            if subcampeon_id:
                palmares_calculado.append({"Temporada": temp, "Competicion": "Liga", "Posicion": "Subcampeón", "ID_Futmondo": subcampeon_id})
        else:
            print(f"⏳ Temporada {temp} en curso (Jornada {int(jornada_max_temp)}/38). Aún no hay campeón oficial.")

    df_calculado = pd.DataFrame(palmares_calculado)

    # 4. HARDCODEO: Inyectar la Temporada Fantasma 2020/21
    datos_2020 = pd.DataFrame([
        {"Temporada": "2020/21", "Competicion": "Liga", "Posicion": "Campeón", "ID_Futmondo": "5f452f5e66dd374930eb2b71"}, # Mikelona
        {"Temporada": "2020/21", "Competicion": "Liga", "Posicion": "Subcampeón", "ID_Futmondo": "LEGACY_ARSENATI"} # Arsenati
    ])

    # Unir todo
    if not df_calculado.empty:
        df_palmares_final = pd.concat([datos_2020, df_calculado], ignore_index=True)
    else:
        df_palmares_final = datos_2020

    # 5. Guardar el archivo Maestro
    os.makedirs("datos/maestros", exist_ok=True)
    df_palmares_final.to_excel(ruta_salida, index=False)
    print(f"✅ ¡Palmarés de Liga generado con éxito en {ruta_salida}!")

if __name__ == "__main__":
    generar_palmares_liga()