import requests
import json
import os

# Nuestra regla a prueba de balas para entornos locales/nube
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Si estamos en GitHub, ignoramos este paso porque usa Secrets

TOKEN = os.getenv("FUTMONDO_TOKEN")

url = "https://api.futmondo.com/1/userteam/roster"

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

payload = {
    "header": {
        "token": TOKEN,
        "userid": "5dcac7a682052f531c77f140"
    },
    "query": {
        "championshipId": "5f452f5d3e7c0d5ae0fbe924",
        "userteamId": "5f45324dec331549297ee971" # Jatafe club de gafe
    },
    "answer": {}
}

print("🕵️‍♂️ Conectando con Futmondo para extraer la plantilla...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    datos = response.json()
    
    with open("plantilla_raw.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
        
    print("✅ ¡Éxito! Datos guardados en 'plantilla_raw.json'.")
else:
    print(f"❌ Error al conectar: {response.status_code}")