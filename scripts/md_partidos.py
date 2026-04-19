import requests
import pandas as pd
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")

URL_MATCHES = "https://api.futmondo.com/2/league/matches"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TEMPORADA_ACTUAL = "2025/26"

def generar_maestro_partidos():
    print("⚽ Extrayendo Maestro de Partidos y Calendario...")
    
    payload = {
        "header": {
            "token": TOKEN,
            "userid": "5dcac7a682052f531c77f140"
        },
        "query": {
            "leagueId": "504e4f584d8bec9a67000079"
        },
        "answer": {}
    }
    
    response = requests.post(URL_MATCHES, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        jornadas = response.json().get("answer", {}).get("rounds", [])
        filas_nuevas = []
        
        for jornada in jornadas:
            num_jornada = jornada.get("number")
            estado_jornada = jornada.get("status") # "closed", "open", etc.
            partidos = jornada.get("matches", [])
            
            for match in partidos:
                # Extracción de fechas y horas
                fecha_utc_str = match.get("info", {}).get("date")
                
                # Si hay fecha, la procesamos
                if fecha_utc_str:
                    # Convertimos a formato Fecha/Hora de Pandas
                    dt_utc = pd.to_datetime(fecha_utc_str)
                    
                    # Extraemos la fecha pura (YYYY-MM-DD)
                    fecha_partido = dt_utc.strftime("%Y-%m-%d")
                    # Extraemos la hora UTC
                    hora_utc = dt_utc.strftime("%H:%M")
                    
                    # Convertimos a la zona horaria de España (maneja automáticamente horario de verano/invierno)
                    dt_esp = dt_utc.tz_convert('Europe/Madrid')
                    hora_esp = dt_esp.strftime("%H:%M")
                else:
                    fecha_partido, hora_utc, hora_esp = None, None, None
                
                filas_nuevas.append({
                    "id_partido": match.get("_id"),
                    "jornada": num_jornada,
                    "temporada": TEMPORADA_ACTUAL,
                    "id_equipo_local": match.get("h", {}).get("id"),
                    "id_equipo_visitante": match.get("a", {}).get("id"),
                    "goles_local": match.get("h", {}).get("score"),
                    "goles_visitante": match.get("a", {}).get("score"),
                    "fecha_partido": fecha_partido,
                    "hora_utc": hora_utc,
                    "hora_esp": hora_esp,
                    "estado_jornada": estado_jornada,
                    "estado_partido": match.get("st") # "F" (Finalizado), etc.
                })
                
        df_nuevos = pd.DataFrame(filas_nuevas)
        
        # 📂 Arquitectura de carpetas
        os.makedirs("datos/maestros", exist_ok=True)
        ruta_archivo = "datos/maestros/md_partidos.xlsx"
        
        # 🔄 LÓGICA DE UPSERT
        if os.path.exists(ruta_archivo):
            df_existente = pd.read_excel(ruta_archivo)
            df_combinado = pd.concat([df_existente, df_nuevos], ignore_index=True)
            # El ID del partido es único. Nos quedamos con el último (que tendrá los goles actualizados)
            df_final = df_combinado.drop_duplicates(subset=['id_partido'], keep='last')
        else:
            df_final = df_nuevos
            
        df_final.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Maestro de Partidos UPSERT completado! Total: {len(df_final)} partidos registrados.")
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_maestro_partidos()