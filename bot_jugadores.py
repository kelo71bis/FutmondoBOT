import requests
import pandas as pd
import os

# 1. Regla de oro para Producción
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")

URL_LINEUP = "https://api.futmondo.com/1/userteam/roundlineup"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 2. CONFIGURACIÓN DE LA JORNADA (Actualizar en cada ejecución)
NUM_JORNADA = 31
TEMPORADA = "2025/26"
HASH_JORNADA = "6868f3aaca97b13338e6ce78" # El código que sacaste con F12

EQUIPOS = {
    "5f452f5e66dd374930eb2b71": "FC Mikelona",
    "5f453062ec331549297ee6b8": "Real Dendryd",
    "5f47aeb6c387a50bca03dd55": "Cruyffisme FC",
    "5f45324dec331549297ee971": "Jatafe",
    "62d5bd9ad8106d3355b5bdc1": "Pallejandro",
    "5f47ab5b9e2edb0bb831c703": "Bichos Team",
    "5f4531e9764e7d491e029746": "Cracklos F.C",
    "5f4530beec331549297ee6d6": "URSS"
}

def extraer_rendimiento():
    print(f"⚽ Extrayendo Rendimiento Individual - Jornada {NUM_JORNADA}...")
    
    filas_puntos = []
    
    for id_equipo, nombre_equipo in EQUIPOS.items():
        print(f"   -> Leyendo pizarra táctica de: {nombre_equipo}")
        
        payload = {
            "header": {
                "token": TOKEN,
                "userid": "5dcac7a682052f531c77f140"
            },
            "query": {
                "championshipId": "5f452f5d3e7c0d5ae0fbe924",
                "round": HASH_JORNADA,
                "userteamId": id_equipo
            },
            "answer": {}
        }
        
        response = requests.post(URL_LINEUP, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            datos = response.json().get("answer", {})
            jugadores_alineados = datos.get("players", [])
            
            for jug in jugadores_alineados:
                # Extraemos las estadísticas avanzadas si existen
                stats = jug.get("detailedPoints", {}).get("data", {})
                
                filas_puntos.append({
                    "Temporada": TEMPORADA,
                    "Jornada": NUM_JORNADA,
                    "ID_Equipo_Futmondo": id_equipo,
                    "Equipo_Futmondo": nombre_equipo,
                    "ID_Jugador": jug.get("id"),
                    "Nombre_Jugador": jug.get("name"),
                    "Posicion": jug.get("role"),
                    "Puntos_Jornada": jug.get("points", 0),
                    # Stats avanzadas extraídas de tu JSON
                    "Minutos_Jugados": stats.get("mins_played", 0),
                    "Goles": stats.get("goals", 0),
                    "Asistencias": stats.get("goal_assist", 0),
                    "Tarjetas_Amarillas": stats.get("yellow_card", 0),
                    "Tarjetas_Rojas": stats.get("red_card", 0)
                })
        else:
            print(f"   ❌ Error al leer alineación de {nombre_equipo}: HTTP {response.status_code}")

    # 3. Guardado y Fusión
    if filas_puntos:
        df_nuevo = pd.DataFrame(filas_puntos)
        archivo_salida = "Fact_Puntos_Jugadores.xlsx"
        
        if os.path.exists(archivo_salida):
            df_historico = pd.read_excel(archivo_salida)
            # Limpiamos los datos de esta jornada por si ya existían (evitar duplicados)
            df_historico = df_historico[~((df_historico['Temporada'] == TEMPORADA) & (df_historico['Jornada'] == NUM_JORNADA))]
            df_final = pd.concat([df_historico, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(archivo_salida, index=False)
        print(f"✅ ¡Jornada cerrada! Se ha registrado el rendimiento de {len(df_nuevo)} jugadores alineados.")
    else:
        print("⚠️ No se encontraron jugadores alineados (¿Está bien el Hash de la jornada?).")

if __name__ == "__main__":
    extraer_rendimiento()