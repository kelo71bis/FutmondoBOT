import requests
import pandas as pd
import os
import sys

# Configuración básica
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")
URL_MATCHES = "https://api.futmondo.com/2/league/matches"
HEADERS = {"Content-Type": "application/json; charset=utf-8"}
# Usamos el ID de LaLiga que encontramos antes
LEAGUE_ID = "504e4f584d8bec9a67000079"

def comprobar_estado_temporada():
    print("🔍 Comprobando si la temporada está activa...")
    
    payload = {
        "header": {"token": TOKEN, "userid": "5dcac7a682052f531c77f140"},
        "query": {"leagueId": LEAGUE_ID},
        "answer": {}
    }
    
    try:
        response = requests.post(URL_MATCHES, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("⚠️ No se pudo conectar con la API. Por seguridad, asumimos activa.")
            return True

        jornadas = response.json().get("answer", {}).get("rounds", [])
        
        if not jornadas:
            print("🌑 No hay calendario cargado. Probablemente pre-temporada profunda.")
            return False

        # Buscamos la última jornada disponible en la API
        ultima_jornada = jornadas[-1]
        num_ultima = ultima_jornada.get("number")
        estado_ultima = ultima_jornada.get("status")

        # LÓGICA DE CORTE
        # Si la última jornada es la 38 y está cerrada, la liga ha terminado.
        if num_ultima == 38 and estado_ultima == "closed":
            print(f"🏁 Jornada {num_ultima} FINALIZADA. Temporada concluida.")
            return False
        
        # En cualquier otro caso (jornadas abiertas, liga empezando, etc.)
        print(f"🟢 Temporada activa. Estamos en/hacia la jornada {num_ultima}.")
        return True

    except Exception as e:
        print(f"❌ Error en el validador: {e}")
        return True # En caso de duda, mejor que intente cargar datos

if __name__ == "__main__":
    activa = comprobar_estado_temporada()
    
    # Escribimos el resultado para que GitHub Actions lo lea
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"activa={str(activa).lower()}", file=fh)