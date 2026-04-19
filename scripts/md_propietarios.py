import requests
import pandas as pd
import os

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

# Diccionario maestro: "ID_Equipo": ("ALIAS_CORTO", "NOMBRE_AMISTOSO")
INFO_EQUIPOS = {
    "5f452f5e66dd374930eb2b71": ("MIK", "FC Mikelona"),
    "5f453062ec331549297ee6b8": ("DEN", "Real Dendryd"),
    "5f47aeb6c387a50bca03dd55": ("CRU", "Cruyffisme FC"),
    "5f45324dec331549297ee971": ("JAT", "Jatafe"),
    "62d5bd9ad8106d3355b5bdc1": ("PAL", "Pallejandro"),
    "5f47ab5b9e2edb0bb831c703": ("BIC", "Bichos Team"),
    "5f4531e9764e7d491e029746": ("CRA", "Cracklos F.C"),
    "5f4530beec331549297ee6d6": ("URS", "URSS")
}

# 🛡️ GESTIÓN DE HISTÓRICOS Y SISTEMA
REGISTROS_EXTRA = [
    {
        "id_propietario": "LEGACY_ARSENATI",
        "nombre_propietario": "Arsenati",
        "alias": "ARS",
        "nombre": "Arsenati",
        "nombre_entrenador": "Desconocido",
        "estado": "Histórico"
    },
    {
        "id_propietario": "SYS_COMPUTER", # ID artificial para la máquina
        "nombre_propietario": "Mercado Libre",
        "alias": "MER",
        "nombre": "Mercado",
        "nombre_entrenador": "Futmondo",
        "estado": "Sistema"
    }
]

def generar_maestro_propietarios():
    print("👤 Extrayendo Maestro de Propietarios de Futmondo...")
    
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
        filas_maestro = []
        
        # 1. Cargamos a los que están jugando actualmente (Activos)
        for equipo in equipos:
            team_id = equipo.get("teamid")
            alias_corto, nombre_amistoso = INFO_EQUIPOS.get(team_id, ("N/A", "Desconocido"))
            
            filas_maestro.append({
                "id_propietario": team_id,
                "nombre_propietario": equipo.get("teamname"),
                "alias": alias_corto,
                "nombre": nombre_amistoso,
                "nombre_entrenador": equipo.get("name"),
                "estado": "Activo"
            })
            
        # 2. Inyectamos a las leyendas caídas (Históricos)
        filas_maestro.extend(REGISTROS_EXTRA)
            
        df_maestro = pd.DataFrame(filas_maestro)
        
        os.makedirs("datos/maestros", exist_ok=True)
        ruta_archivo = "datos/maestros/md_propietarios.xlsx"
        
        df_maestro.to_excel(ruta_archivo, index=False)
        
        print(f"✅ ¡Maestro actualizado! Guardado en '{ruta_archivo}' con {len(df_maestro)} propietarios (Activos + Históricos).")
        
    else:
        print(f"❌ Error al conectar con Futmondo: HTTP {response.status_code}")

if __name__ == "__main__":
    generar_maestro_propietarios()