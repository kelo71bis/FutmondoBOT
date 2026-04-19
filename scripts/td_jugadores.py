import requests
import pandas as pd
import os
from datetime import datetime

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

def generar_td_jugadores():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"📈 Capturando fluctuaciones de mercado para el día: {fecha_hoy}...")
    
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
        filas_hechos = []
        
        for jug in jugadores:
            # Lógica para detectar si es de un usuario o de la máquina
            es_maquina = jug.get("computer", True)
            # Si el jugador es de la máquina, le asignamos el ID del Mercado. Si no, el de su dueño.
            id_prop = "SYS_COMPUTER" if es_maquina else jug.get("userteamId")
            
            filas_hechos.append({
                "id_jugador": jug.get("id"),
                "id_propietario": id_prop,
                "valor_mercado": jug.get("value", 0),
                "diferencia_dia": jug.get("change", 0),
                "fecha_carga": fecha_hoy
            })
            
        df_nuevos = pd.DataFrame(filas_hechos)
        
        # 📂 Arquitectura de carpetas: Ahora va a la carpeta de HECHOS
        os.makedirs("datos/hechos", exist_ok=True)
        ruta_archivo = "datos/hechos/td_jugadores.xlsx"
        
        # 🔄 LÓGICA DE ACUMULACIÓN (Append)
        if os.path.exists(ruta_archivo):
            df_existente = pd.read_excel(ruta_archivo)
            
            # Combinamos histórico con lo de hoy
            df_combinado = pd.concat([df_existente, df_nuevos], ignore_index=True)
            
            # Si corremos el bot 2 veces el mismo día, borramos el duplicado 
            # basándonos en la clave compuesta: jugador + fecha
            df_final = df_combinado.drop_duplicates(subset=['id_jugador', 'fecha_carga'], keep='last')
        else:
            df_final = df_nuevos
            
        df_final.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Mercado cerrado! Se han capturado las valoraciones de {len(df_nuevos)} jugadores.")
        print(f"📊 Total de registros en la serie temporal: {len(df_final)}")
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_td_jugadores()