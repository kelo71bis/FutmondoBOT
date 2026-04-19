import requests
import pandas as pd
import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")
URL_MATCH = "https://api.futmondo.com/2/match/fetchmatch"
HEADERS = {"Content-Type": "application/json; charset=utf-8"}

def test_diagnostico():
    print("🎯 MODO FRANCOTIRADOR: Buscando el Real Madrid - Girona (J31)...")
    
    # 1. Localizar el partido exacto cruzando maestros
    try:
        df_partidos = pd.read_excel("datos/maestros/md_partidos.xlsx")
        df_equipos = pd.read_excel("datos/maestros/md_equipos.xlsx")
        
        # Cruzamos para tener los nombres/alias
        df = df_partidos.merge(df_equipos[['id_equipo_real', 'alias_equipo']], left_on='id_equipo_local', right_on='id_equipo_real', how='left')
        df = df.rename(columns={'alias_equipo': 'local'})
        df = df.merge(df_equipos[['id_equipo_real', 'alias_equipo']], left_on='id_equipo_visitante', right_on='id_equipo_real', how='left')
        df = df.rename(columns={'alias_equipo': 'visitante'})
        
        # Filtramos J31 y que juegue el RMA
        partido = df[(df['jornada'] == 31) & ((df['local'] == 'RMA') | (df['visitante'] == 'RMA'))]
        
        if partido.empty:
            print("❌ No encuentro el partido en md_partidos.xlsx")
            return
            
        id_partido = partido.iloc[0]['id_partido']
        print(f"✅ ¡Partido localizado! ID: {id_partido}")
        
    except Exception as e:
        print(f"❌ Error leyendo maestros: {e}")
        return

    # 2. Descargar el acta de ese partido
    payload = {"header": {"token": TOKEN, "userid": "5dcac7a682052f531c77f140"}, "query": {"matchId": id_partido}, "answer": {}}
    response = requests.post(URL_MATCH, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error de API: {response.status_code}")
        return
        
    json_data = response.json()
    
    # Guardamos el JSON crudo por si tenemos que investigarlo a mano
    with open("datos/acta_debug.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print("📁 JSON crudo guardado en datos/acta_debug.json por si acaso.\n")

    # 3. Radar enfocado en Valverde y Vinícius
    jugadores_encontrados = 0
    
    def buscar_jugadores(nodo):
        nonlocal jugadores_encontrados
        if isinstance(nodo, dict):
            # Condición más flexible: Si tiene "p" y "p" tiene "name"
            if "p" in nodo and "s" in nodo and isinstance(nodo.get("p"), dict) and "name" in nodo["p"]:
                nombre = nodo["p"]["name"]
                
                # Filtramos a las estrellas
                if "Valverde" in nombre or "Vin" in nombre or "Brahim" in nombre or "Díaz" in nombre:
                    jugadores_encontrados += 1
                    print(f"⭐ JUGADOR ENCONTRADO: {nombre}")
                    
                    po = nodo["s"].get("po", [])
                    if not po:
                        print("   ⚠️ No hay array de puntos 'po' para este jugador.")
                        
                    for p in po:
                        modo = p.get('mode')
                        puntos = p.get('p')
                        # Si encontramos los puntos de la captura, les ponemos un check verde
                        if puntos in [14.1, 11.7, 12.4]:
                            print(f"   ✅ MODO: '{modo}' -> PUNTOS: {puntos}  <-- ¡AQUÍ ESTÁ!")
                        else:
                            print(f"   - Modo: '{modo}' -> Puntos: {puntos}")
                    print("-" * 30)
            else:
                for v in nodo.values(): buscar_jugadores(v)
        elif isinstance(nodo, list):
            for i in nodo: buscar_jugadores(i)

    buscar_jugadores(json_data)
    
    if jugadores_encontrados == 0:
        print("❌ El radar no encontró a los jugadores. La estructura del JSON es diferente a lo esperado.")

if __name__ == "__main__":
    test_diagnostico()