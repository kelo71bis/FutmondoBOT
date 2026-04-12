import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("FUTMONDO_TOKEN")
URL_COPA = "https://api.futmondo.com/5/cup/get"

PAYLOAD = {
    "header": {
        "token": TOKEN,
        "userid": "5dcac7a682052f531c77f140"
    },
    "query": {
        "championshipId": "5f452f5d3e7c0d5ae0fbe924",
        "userteamId": "5f452f5e66dd374930eb2b71"
    },
    "answer": {}
}

# --- 2. CONFIGURACIÓN DE JORNADAS (Tú actualizas esto cada vez que hacéis Copa) ---
# Aquí le decimos al bot en qué jornadas reales de liga cae cada eliminatoria
MAPEO_JORNADAS = {
    1: {"nombre": "Cuartos", "ida": 28, "vuelta": 29},
    2: {"nombre": "Semifinal", "ida": 30, "vuelta": 31},
    3: {"nombre": "Final", "ida": 32, "vuelta": None} # La final suele ser a partido único
}
TEMPORADA_ACTUAL = "2025/26"
NOMBRE_COPA = "Copa 03"
# ---------------------------------------------------------------------------------

def extraer_copa():
    print(f"🏆 Descargando datos de la {NOMBRE_COPA}...")
    response = requests.post(URL_COPA, headers={"Content-Type": "application/json; charset=utf-8"}, json=PAYLOAD)
    
    if response.status_code != 200:
        print(f"❌ Error al conectar: {response.status_code}")
        return

    rondas = response.json().get("answer", {}).get("rounds", [])
    filas_copa = []
    
    for ronda in rondas:
        num_ronda = ronda.get("number")
        conf = MAPEO_JORNADAS.get(num_ronda, {})
        nombre_ronda = conf.get("nombre", f"Ronda {num_ronda}")
        jornada_ida = conf.get("ida")
        jornada_vuelta = conf.get("vuelta")
        
        for partido in ronda.get("matches", []):
            home = partido.get("home", {})
            away = partido.get("away", {})
            
            if not home.get("team") or not away.get("team"):
                continue # Aún no hay rivales decididos
                
            id_local = home["team"]["_id"]
            id_visitante = away["team"]["_id"]
            scores_local = home.get("scores", [])
            scores_visitante = away.get("scores", [])
            
            # FILA 1: PARTIDO DE IDA
            if jornada_ida is not None:
                filas_copa.append({
                    "Temporada": TEMPORADA_ACTUAL,
                    "Copa": NOMBRE_COPA,
                    "Ronda": nombre_ronda,
                    "Partido": "Ida",
                    "Jornada": jornada_ida,
                    "ID_Local": id_local,
                    "ID_Visitante": id_visitante,
                    "Pts_Local": scores_local[0] if len(scores_local) > 0 else 0,
                    "Pts_Visitante": scores_visitante[0] if len(scores_visitante) > 0 else 0
                })
                
            # FILA 2: PARTIDO DE VUELTA
            if jornada_vuelta is not None:
                # En la vuelta, el que era local en la ida juega de visitante
                filas_copa.append({
                    "Temporada": TEMPORADA_ACTUAL,
                    "Copa": NOMBRE_COPA,
                    "Ronda": nombre_ronda,
                    "Partido": "Vuelta",
                    "Jornada": jornada_vuelta,
                    "ID_Local": id_visitante, # Invertimos local/visitante
                    "ID_Visitante": id_local,
                    "Pts_Local": scores_visitante[1] if len(scores_visitante) > 1 else 0,
                    "Pts_Visitante": scores_local[1] if len(scores_local) > 1 else 0
                })

    if filas_copa:
        df_copa = pd.DataFrame(filas_copa)
        df_copa.to_excel("Fact_Tracking_Copa.xlsx", index=False)
        print("✅ Datos procesados con la Jornada asignada. Archivo generado: 'Fact_Tracking_Copa.xlsx'")
    else:
        print("⚠️ No hay datos para procesar.")

if __name__ == "__main__":
    extraer_copa()