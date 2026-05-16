import pandas as pd
import numpy as np
import os

def generar_vista_global():
    print("🌍 Construyendo Vista Global (Histórico + Temporada Actual)...")
    
    rutas = {
        "historico": "Fact_Global_Master_1.xlsx",
        "actual": "datos/hechos/td_puntos_jugadores_2025_26.xlsx",
        "salida": "datos/vistas_negocio/Fact_Global_Master.xlsx"
    }
    
# 🎯 PUNTOS EXACTOS JORNADA 1 (Nuevos valores hardcodeados)
    PUNTOS_EXACTOS_J1 = {
        "5f4530beec331549297ee6d6": 65.0, # URSS
        "5f4531e9764e7d491e029746": 49.0, # Cracklos
        "5f45324dec331549297ee971": 66.0, # Jatafe
        "5f47aeb6c387a50bca03dd55": 51.0, # Cruyffisme
        "5f453062ec331549297ee6b8": 41.0, # Dendryd
        "62d5bd9ad8106d3355b5bdc1": 56.0, # Pallejandro
        "5f452f5e66dd374930eb2b71": 41.0, # Mikelona
        "5f47ab5b9e2edb0bb831c703": 47.0  # Bichos
    }

    for nombre, ruta in rutas.items():
        if nombre != "salida" and not os.path.exists(ruta):
            print(f"⚠️ Falta {ruta}. Revisa los archivos.")
            return

    # 1. Cargar Histórico
    df_hist = pd.read_excel(rutas["historico"])
    df_hist = df_hist[df_hist['Temporada'] != '2025/26'].copy()
    
    # 2. Cargar Temporada Actual
    print("    📂 Cargando datos de temporada actual...")
    df_actual = pd.read_excel(rutas["actual"])
    
    # --- 🛡️ MEJORA CRÍTICA: LIMPIEZA DE DUPLICADOS EN EL ORIGEN ---
    # Usamos id_jugador para identificar filas únicas por jugador y jornada.
    subset_duplicados = ['id_propietario', 'id_jugador', 'jornada', 'temporada']
    
    antes = len(df_actual)
    df_actual_limpio = df_actual.drop_duplicates(subset=subset_duplicados, keep='last').copy()
    despues = len(df_actual_limpio)
    
    if antes != despues:
        print(f"    🧹 ¡LIMPIEZA! Se han eliminado {antes - despues} filas duplicadas de jugadores.")

    # Agrupamos por propietario y jornada
    df_actual_agrupado = df_actual_limpio.groupby(['id_propietario', 'jornada', 'temporada'], as_index=False)['puntos'].sum()
    df_actual_agrupado = df_actual_agrupado.rename(columns={
        'id_propietario': 'ID_Futmondo', 'jornada': 'Jornada', 'temporada': 'Temporada', 'puntos': 'Puntos'
    })

    # 3. 🎯 INYECCIÓN DIRECTA DE LA JORNADA 1
    print("    💉 Inyectando los puntos EXACTOS de la Jornada 1...")
    def inyectar_j1_exacta(row):
        if row['Jornada'] == 1 and row['Temporada'] == '2025/26':
            return PUNTOS_EXACTOS_J1.get(row['ID_Futmondo'], row['Puntos'])
        return row['Puntos']
    
    df_actual_agrupado['Puntos'] = df_actual_agrupado.apply(inyectar_j1_exacta, axis=1)

    # 4. Unir todo
    print("    🔗 Consolidando y recalculando ránkings...")
    df_master = pd.concat([df_hist[['ID_Futmondo', 'Jornada', 'Temporada', 'Puntos']], df_actual_agrupado], ignore_index=True)
    
    # Eliminar duplicados finales en el master
    df_master = df_master.drop_duplicates(subset=['ID_Futmondo', 'Jornada', 'Temporada'], keep='last')
    
    df_master = df_master.sort_values(by=['Temporada', 'Jornada'])

    # 5. Recalcular Acumulados y Ránkings
    print("    📈 Recalculando acumulados...")
    df_master['Puntos_Acumulados'] = df_master.groupby(['ID_Futmondo', 'Temporada'])['Puntos'].cumsum()
    df_master['Acumulado_Total'] = df_master.groupby(['ID_Futmondo'])['Puntos'].cumsum()
    
    df_master['Ranking_Jornada'] = df_master.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False).astype(int)
    df_master['Ranking_Temporada'] = df_master.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
    df_master['Ranking_General'] = df_master.groupby(['Temporada', 'Jornada'])['Acumulado_Total'].rank(method='min', ascending=False).astype(int)

    # 6. Exportar
    os.makedirs("datos/vistas_negocio", exist_ok=True)
    df_master.to_excel(rutas["salida"], index=False)
    print(f"✅ ¡ÉXITO! Vista Global regenerada correctamente.")

if __name__ == "__main__":
    generar_vista_global()