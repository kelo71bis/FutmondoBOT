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
    
    # 🎯 PUNTOS EXACTOS JORNADA 1 (Copiados y pegados directamente de tu mensaje)
    PUNTOS_EXACTOS_J1 = {
        "5f45324dec331549297ee971": 79.0,
        "5f4530beec331549297ee6d6": 71.0,
        "62d5bd9ad8106d3355b5bdc1": 69.0,
        "5f47aeb6c387a50bca03dd55": 51.0,
        "5f4531e9764e7d491e029746": 43.0,
        "5f47ab5b9e2edb0bb831c703": 55.0,
        "5f452f5e66dd374930eb2b71": 41.0,
        "5f453062ec331549297ee6b8": 32.0
    }

    for nombre, ruta in rutas.items():
        if nombre != "salida" and not os.path.exists(ruta):
            print(f"⚠️ Falta {ruta}. Revisa los archivos.")
            return

    # 1. Cargar Histórico
    df_hist = pd.read_excel(rutas["historico"])
    df_hist = df_hist[df_hist['Temporada'] != '2025/26'].copy()
    
    # 2. Cargar Temporada Actual (desde el td_ original)
    df_actual = pd.read_excel(rutas["actual"])
    df_actual_agrupado = df_actual.groupby(['id_propietario', 'jornada', 'temporada'], as_index=False)['puntos'].sum()
    df_actual_agrupado = df_actual_agrupado.rename(columns={
        'id_propietario': 'ID_Futmondo', 'jornada': 'Jornada', 'temporada': 'Temporada', 'puntos': 'Puntos'
    })

    # 3. 🎯 INYECCIÓN DIRECTA DE LA JORNADA 1
    print("   💉 Inyectando los puntos EXACTOS de la Jornada 1...")
    def inyectar_j1_exacta(row):
        if row['Jornada'] == 1 and row['Temporada'] == '2025/26':
            return PUNTOS_EXACTOS_J1.get(row['ID_Futmondo'], row['Puntos'])
        return row['Puntos']
    
    df_actual_agrupado['Puntos'] = df_actual_agrupado.apply(inyectar_j1_exacta, axis=1)

    # 4. Unir todo
    print("   🔗 Consolidando y recalculando ránkings...")
    df_master = pd.concat([df_hist[['ID_Futmondo', 'Jornada', 'Temporada', 'Puntos']], df_actual_agrupado], ignore_index=True)
    df_master = df_master.sort_values(by=['Temporada', 'Jornada'])

    # 5. Recalcular Acumulados y Ránkings
    df_master['Puntos_Acumulados'] = df_master.groupby(['ID_Futmondo', 'Temporada'])['Puntos'].cumsum()
    df_master['Acumulado_Total'] = df_master.groupby(['ID_Futmondo'])['Puntos'].cumsum()
    
    df_master['Ranking_Jornada'] = df_master.groupby(['Temporada', 'Jornada'])['Puntos'].rank(method='min', ascending=False).astype(int)
    df_master['Ranking_Temporada'] = df_master.groupby(['Temporada', 'Jornada'])['Puntos_Acumulados'].rank(method='min', ascending=False).astype(int)
    df_master['Ranking_General'] = df_master.groupby(['Temporada', 'Jornada'])['Acumulado_Total'].rank(method='min', ascending=False).astype(int)

    # 6. Exportar
    os.makedirs("datos/vistas_negocio", exist_ok=True)
    df_master.to_excel(rutas["salida"], index=False)
    print(f"✅ ¡ÉXITO! Vista generada.")

if __name__ == "__main__":
    generar_vista_global()