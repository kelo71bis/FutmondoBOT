import requests
import pandas as pd
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")

URL_STANDING = "https://api.futmondo.com/2/league/standing"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def generar_maestro_equipos():
    print("🏟️ Extrayendo Maestro de Equipos de LaLiga...")
    
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
    
    response = requests.post(URL_STANDING, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        equipos = response.json().get("answer", {}).get("standing", [])
        filas_nuevas = []
        
        for eq in equipos:
            filas_nuevas.append({
                "id_equipo_real": eq.get("_id"),
                "nombre_equipo": eq.get("name"),
                "alias_equipo": eq.get("shortname")
            })
            
        df_nuevos = pd.DataFrame(filas_nuevas)
        
        # 📂 Arquitectura de carpetas
        os.makedirs("datos/maestros", exist_ok=True)
        ruta_archivo = "datos/maestros/md_equipos.xlsx"
        
        # 🔄 LÓGICA DE UPSERT
        if os.path.exists(ruta_archivo):
            df_existente = pd.read_excel(ruta_archivo)
            
            # Combinamos y eliminamos duplicados quedándonos con el último (por si cambiaran de nombre/alias)
            df_combinado = pd.concat([df_existente, df_nuevos], ignore_index=True)
            df_final = df_combinado.drop_duplicates(subset=['id_equipo_real'], keep='last')
        else:
            df_final = df_nuevos
            
        df_final.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Maestro de Equipos UPSERT completado! Total en base de datos: {len(df_final)} equipos históricos.")
        print(df_final.head())
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_maestro_equipos()