import requests
import pandas as pd
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TEMPORADA_ACTUAL = "2025/26"
LEAGUE_ID = "504e4f584d8bec9a67000079"
CHAMPIONSHIP_ID = "5f452f5d3e7c0d5ae0fbe924"
USER_ID = "5dcac7a682052f531c77f140"

# 🛑 BOTÓN ROJO: Ponlo en True para que descargue TODO de cero (ideal para arreglar errores)
# Una vez lo hayas ejecutado y arreglado, puedes volver a ponerlo en False para el día a día.
FORZAR_RECARGA_COMPLETA = False 

def generar_td_puntos():
    print("🧠 Construyendo td_puntos_jugadores desde la API de Alineaciones...")
    
    # 1. Obtener los IDs de las jornadas cerradas
    print("   📅 Obteniendo calendario de jornadas...")
    payload_rounds = {
        "header": {"token": TOKEN, "userid": USER_ID},
        "query": {"leagueId": LEAGUE_ID},
        "answer": {}
    }
    
    res_rounds = requests.post("https://api.futmondo.com/2/league/matches", headers=HEADERS, json=payload_rounds)
    jornadas_cerradas = []
    if res_rounds.status_code == 200:
        rounds = res_rounds.json().get("answer", {}).get("rounds", [])
        for r in rounds:
            if r.get("status") == "closed":
                jornadas_cerradas.append({
                    "id": r.get("_id"),
                    "numero": r.get("number")
                })
    
    if not jornadas_cerradas:
        print("⚠️ No hay jornadas cerradas todavía.")
        return

    # 2. Obtener la lista de usuarios/propietarios
    print("   👥 Obteniendo propietarios...")
    payload_teams = {
        "header": {"token": TOKEN, "userid": USER_ID},
        "query": {"championshipId": CHAMPIONSHIP_ID},
        "answer": {}
    }
    
    res_teams = requests.post("https://api.futmondo.com/2/championship/teams", headers=HEADERS, json=payload_teams)
    propietarios = []
    if res_teams.status_code == 200:
        teams = res_teams.json().get("answer", {}).get("teams", [])
        propietarios = [t.get("teamid") for t in teams]

    # 3. Lógica Delta o Recarga Completa
    temporada_limpia = TEMPORADA_ACTUAL.replace("/", "_")
    ruta_td = f"datos/hechos/td_puntos_jugadores_{temporada_limpia}.xlsx"
    os.makedirs("datos/hechos", exist_ok=True)
    
    if os.path.exists(ruta_td) and not FORZAR_RECARGA_COMPLETA:
        df_existente = pd.read_excel(ruta_td)
        df_existente['clave_delta'] = df_existente['jornada'].astype(str) + "_" + df_existente['id_propietario']
        combinaciones_procesadas = df_existente['clave_delta'].unique().tolist()
        df_existente = df_existente.drop(columns=['clave_delta'])
    else:
        if FORZAR_RECARGA_COMPLETA:
            print("   ⚠️ RECARGA COMPLETA ACTIVADA: Ignorando datos guardados. Se descargará todo de cero.")
        df_existente = pd.DataFrame()
        combinaciones_procesadas = []

    filas_td = []
    total_combinaciones = len(jornadas_cerradas) * len(propietarios)
    contador = 0

    print(f"🔍 Escaneando alineaciones históricas ({total_combinaciones} posibles combinaciones)...")

    for jor in jornadas_cerradas:
        for prop in propietarios:
            contador += 1
            clave_actual = f"{jor['numero']}_{prop}"
            
            if clave_actual in combinaciones_procesadas:
                continue 
                
            print(f"   ⏳ Extrayendo J{jor['numero']} - Equipo {prop} ({contador}/{total_combinaciones})...", end="\r")
            
            payload_lineup = {
                "header": {"token": TOKEN, "userid": USER_ID},
                "query": {"championshipId": CHAMPIONSHIP_ID, "round": jor["id"], "userteamId": prop},
                "answer": {}
            }
            
            try:
                res_lineup = requests.post("https://api.futmondo.com/1/userteam/roundlineup", headers=HEADERS, json=payload_lineup)
                if res_lineup.status_code == 200:
                    respuesta = res_lineup.json().get("answer", {})
                    jugadores = respuesta.get("players", [])
                    
                    jugadores_alineados = 0
                    
                    for jug in jugadores:
                        pos_alineacion = jug.get("position", 99)
                        es_titular = "Sí" if pos_alineacion <= 11 else "No"
                        
                        if es_titular == "Sí":
                            jugadores_alineados += 1
                            
                        detalles = jug.get("detailedPoints", {}).get("data", {})
                        
                        filas_td.append({
                            "temporada": TEMPORADA_ACTUAL,
                            "jornada": jor["numero"],
                            "id_propietario": prop,
                            "id_jugador": jug.get("id"),
                            "posicion": jug.get("role", "Desconocido"),
                            "titular": es_titular,
                            "puntos": jug.get("points", 0),
                            "minutos": detalles.get("mins_played", 0),
                            "goles": detalles.get("goals", 0),
                            "asistencias": detalles.get("goal_assist", 0),
                            "amarillas": detalles.get("yellow_card", 0),
                            "rojas": detalles.get("red_card", 0)
                        })
                        
                    # LÓGICA DEL -5 (HUECO VACÍO)
                    huecos_libres = 11 - jugadores_alineados
                    for _ in range(huecos_libres):
                        filas_td.append({
                            "temporada": TEMPORADA_ACTUAL,
                            "jornada": jor["numero"],
                            "id_propietario": prop,
                            "id_jugador": "HUECO_VACIO",
                            "posicion": "Ninguna",
                            "titular": "Sí",
                            "puntos": -5,
                            "minutos": 0,
                            "goles": 0,
                            "asistencias": 0,
                            "amarillas": 0,
                            "rojas": 0
                        })
                        
            except Exception as e:
                print(f"\n   ⚠️ Error en J{jor['numero']} / Prop {prop}: {e}")
                
            time.sleep(0.5)

    print("\n✅ Extracción completada. Guardando tabla de hechos...")
    
    if filas_td:
        df_nuevos = pd.DataFrame(filas_td)
        
        if not df_existente.empty:
            df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        else:
            df_final = df_nuevos
            
        columnas_ordenadas = ["temporada", "jornada", "id_propietario", "id_jugador", "posicion", "titular", "puntos", "minutos", "goles", "asistencias", "amarillas", "rojas"]
        df_final = df_final[columnas_ordenadas]
            
        df_final.to_excel(ruta_td, index=False)
        print(f"💾 ¡Datos guardados en datos/hechos/ con {len(df_final)} registros totales!")
    else:
        print("✅ No había datos nuevos que guardar.")

if __name__ == "__main__":
    generar_td_puntos()