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

URL_TEAMS = "https://api.futmondo.com/2/championship/teams"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def generar_td_admin():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"📋 Actualizando Tabla de Administración (Fondos y Títulos) - Día: {fecha_hoy}...")
    
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
    
    response = requests.post(URL_TEAMS, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        equipos = response.json().get("answer", {}).get("teams", [])
        filas_admin = []
        
        for eq in equipos:
            premios = eq.get("awards", {})
            
            filas_admin.append({
                "id_propietario": eq.get("teamid"),
                "fondos": eq.get("budget", 0),
                "titulos_liga": premios.get("l", 0),
                "titulos_copa": premios.get("c", 0),
                "titulos_otros": premios.get("o", 0),
                "fecha_carga": fecha_hoy
            })
            
        df_hoy = pd.DataFrame(filas_admin)
        
        # 📂 Arquitectura de carpetas: Directamente en datos/hechos/
        os.makedirs("datos/hechos", exist_ok=True)
        ruta_archivo = "datos/hechos/td_admin.xlsx"
        
        # 🔄 LÓGICA DE UPSERT DIARIO (Un solo archivo infinito)
        if os.path.exists(ruta_archivo):
            df_existente = pd.read_excel(ruta_archivo)
            df_combinado = pd.concat([df_existente, df_hoy], ignore_index=True)
            df_final = df_combinado.drop_duplicates(subset=['id_propietario', 'fecha_carga'], keep='last')
        else:
            df_final = df_hoy
            
        df_final.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Tabla td_admin actualizada en '{ruta_archivo}'!")
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_td_admin()