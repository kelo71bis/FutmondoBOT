import pandas as pd

def limpiar_excel():
    ruta = "datos/hechos/td_puntos_jugadores_2025_26.xlsx"
    print(f"📂 Abriendo {ruta}...")
    
    df = pd.read_excel(ruta)
    filas_antes = len(df)
    print(f"📊 Filas totales antes de limpiar: {filas_antes}")
    
    # Aquí está la magia: nos quedamos solo con la última actualización de cada jugador por jornada
    columnas_clave = ['temporada', 'jornada', 'id_propietario', 'id_jugador']
    df_limpio = df.drop_duplicates(subset=columnas_clave, keep='last')
    
    filas_despues = len(df_limpio)
    print(f"📊 Filas totales después de limpiar: {filas_despues}")
    print(f"🧹 ¡Se han eliminado {filas_antes - filas_despues} filas duplicadas de pura basura!")
    
    # Guardamos el archivo limpio sobreescribiendo el sucio
    df_limpio.to_excel(ruta, index=False)
    print("✅ Excel origen limpiado y guardado correctamente.")

if __name__ == "__main__":
    limpiar_excel()