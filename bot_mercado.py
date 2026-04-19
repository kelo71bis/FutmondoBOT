import requests
import pandas as pd
import os
from datetime import datetime

# 1. Regla de oro para Producción (GitHub) vs Local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Si estamos en GitHub, usamos los Secrets automáticamente

TOKEN = os.getenv("FUTMONDO_TOKEN")

# 2. Configuración de la API
URL_ROSTER = "https://api.futmondo.com/1/userteam/roster"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Los 8 equipos de LaLiga Santanguissa
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

def capturar_mercado():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"📈 Iniciando captura de mercado para el día: {fecha_hoy}")
    
    filas_mercado = []
    
    # 3. Bucle para extraer la plantilla de cada uno de los 8 equipos
    for id_equipo, nombre_equipo in EQUIPOS.items():
        print(f"   -> Escaneando caja fuerte de: {nombre_equipo}...")
        
        payload = {
            "header": {
                "token": TOKEN,
                "userid": "5dcac7a682052f531c77f140"
            },
            "query": {
                "championshipId": "5f452f5d3e7c0d5ae0fbe924",
                "userteamId": id_equipo
            },
            "answer": {}
        }
        
        response = requests.post(URL_ROSTER, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            jugadores = response.json().get("answer", [])
            
            for jug in jugadores:
                filas_mercado.append({
                    "Fecha": fecha_hoy,
                    "ID_Equipo_Futmondo": id_equipo,
                    "Equipo_Futmondo": nombre_equipo,
                    "ID_Jugador": jug.get("id"),
                    "Nombre_Jugador": jug.get("name"),
                    "Posicion": jug.get("role"),
                    "Equipo_Real": jug.get("team"), # Ej: Getafe, R. Oviedo
                    "Valor_Mercado": jug.get("value", 0),
                    "Precio_Compra": jug.get("buyPrice", 0)
                })
        else:
            print(f"   ❌ Error al leer {nombre_equipo}: HTTP {response.status_code}")

    # 4. Guardado y Fusión Histórica
    if filas_mercado:
        df_hoy = pd.DataFrame(filas_mercado)
        archivo_mercado = "Fact_Evolucion_Mercado.xlsx"
        
        if os.path.exists(archivo_mercado):
            df_historico = pd.read_excel(archivo_mercado)
            # Evitamos duplicar si ejecutamos el script 2 veces el mismo día
            df_historico = df_historico[df_historico['Fecha'] != fecha_hoy]
            df_final = pd.concat([df_historico, df_hoy], ignore_index=True)
        else:
            df_final = df_hoy
            
        df_final.to_excel(archivo_mercado, index=False)
        print(f"✅ ¡Mercado cerrado! Se han capturado {len(df_hoy)} activos financieros hoy.")
    else:
        print("⚠️ No se encontraron jugadores.")

if __name__ == "__main__":
    capturar_mercado()