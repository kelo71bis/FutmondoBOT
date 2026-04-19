import requests
import pandas as pd
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")

URL_PLAYERS = "https://api.futmondo.com/5/league/championshipplayers"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TEMPORADA_ACTUAL = "2025/26"

def generar_maestro_jugadores():
    print("🏃‍♂️ Extrayendo Maestro de Jugadores de Futmondo...")
    
    payload = {
        "header": {
            "token": TOKEN,
            "userid": "5dcac7a682052f531c77f140"
        },
        "query": {
            "championshipId": "5f452f5d3e7c0d5ae0fbe924"
        },
        "answer": {}
    }
    
    response = requests.post(URL_PLAYERS, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        jugadores = response.json().get("answer", {}).get("players", [])
        filas_nuevas = []
        
        for jug in jugadores:
            filas_nuevas.append({
                "id_jugador": jug.get("id"),
                "nombre": jug.get("name"),
                "id_equipo_real": jug.get("teamId"), # Guardamos el ID del equipo de LaLiga
                "posicion": jug.get("role"),
                "temporada": TEMPORADA_ACTUAL
            })
            
        df_nuevos = pd.DataFrame(filas_nuevas)
        
        # 📂 Arquitectura de carpetas
        os.makedirs("datos/maestros", exist_ok=True)
        ruta_archivo = "datos/maestros/md_jugadores.xlsx"
        
        # 🔄 LÓGICA DE UPSERT
        if os.path.exists(ruta_archivo):
            df_existente = pd.read_excel(ruta_archivo)
            
            # Unimos los dos DataFrames (el viejo y el nuevo)
            df_combinado = pd.concat([df_existente, df_nuevos], ignore_index=True)
            
            # Eliminamos duplicados basándonos en Jugador + Temporada.
            # keep='last' asegura que si Josan cambió de equipo hoy (está en df_nuevos),
            # borre la fila vieja y se quede con la recién descargada.
            df_final = df_combinado.drop_duplicates(subset=['id_jugador', 'temporada'], keep='last')
        else:
            df_final = df_nuevos
            
        df_final.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Maestro de Jugadores UPSERT completado! Total en base de datos: {len(df_final)} registros.")
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_maestro_jugadores()