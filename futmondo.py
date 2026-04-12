import requests
import pandas as pd
import time
from datetime import datetime
import os

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("FUTMONDO_TOKEN")
USER_ID = "5dcac7a682052f531c77f140"
CHAMPIONSHIP_ID = "5f452f5d3e7c0d5ae0fbe924"
USER_TEAM_ID = "5f452f5e66dd374930eb2b71"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": "https://app.futmondo.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def obtener_temporada():
    hoy = datetime.now()
    # Genera formato estándar corto: "2025/26"
    if hoy.month >= 8:
        return f"{hoy.year}/{str(hoy.year + 1)[-2:]}"
    else:
        return f"{hoy.year - 1}/{str(hoy.year)[-2:]}"

TEMPORADA = obtener_temporada()

# Reemplazamos la barra por guión bajo SOLO para el nombre del archivo (Windows no admite barras)
ARCHIVO_HECHOS = f"Fact_Futmondo_{TEMPORADA.replace('/', '_')}.xlsx" 

def obtener_id_jornadas():
    url = "https://api.futmondo.com/1/userteam/rounds"
    payload = {"header": {"token": TOKEN, "userid": USER_ID}, "query": {"championshipId": CHAMPIONSHIP_ID, "userteamId": USER_TEAM_ID}, "answer": {}}
    try:
        res = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        return res.json().get("answer", []) if res.status_code == 200 else []
    except:
        return []

def procesar_datos():
    print(f"🚀 Extrayendo Tabla de Hechos - Temporada {TEMPORADA}...")
    
    jornadas = obtener_id_jornadas()
    if not isinstance(jornadas, list):
        print("🛑 Error al conectar con Futmondo.")
        return

    jornadas_validas = [j for j in jornadas if isinstance(j, dict) and j.get('status') in ["closed", "running"]]
    
    datos_raw = []
    for j in jornadas_validas:
        num_jornada = j['number']
        url_puntos = "https://api.futmondo.com/1/ranking/round"
        payload = {"header": {"token": TOKEN, "userid": USER_ID}, "query": {"championshipId": CHAMPIONSHIP_ID, "roundNumber": j['id'], "userteamId": USER_TEAM_ID}, "answer": {}}
        
        try:
            res_p = requests.post(url_puntos, json=payload, headers=HEADERS, timeout=10)
            if res_p.status_code == 200:
                ranking = res_p.json().get("answer", {}).get("ranking", [])
                for eq in ranking:
                    datos_raw.append({
                        "ID_Futmondo": str(eq.get("id", eq.get("userteamId", ""))).strip(),
                        "Jornada": int(num_jornada),
                        "Puntos": float(eq.get("points", 0)),
                        "Temporada": TEMPORADA # Aquí entra como "2025/26"
                    })
            time.sleep(0.4)
        except:
            pass

    df_hechos = pd.DataFrame(datos_raw)

    # --- INYECCIÓN DE AJUSTES MANUALES (Mapeo Blindado) ---
    if os.path.exists("Ajustes_Manuales.xlsx"):
        print("\n🔧 Leyendo Ajustes_Manuales.xlsx...")
        ajustes = pd.read_excel("Ajustes_Manuales.xlsx")
        
        ajustes_aplicados = 0
        for _, row in ajustes.iterrows():
            # Limpiamos los datos de ambas partes para asegurar que hagan "Match"
            id_ajuste = str(row['ID_Futmondo']).strip()
            jornada_ajuste = int(row['Jornada'])
            temporada_ajuste = str(row['Temporada']).strip()
            puntos_ajuste = float(row['Puntos_Ajuste'])

            # Creamos la máscara de cruce
            mask = (df_hechos['ID_Futmondo'] == id_ajuste) & \
                   (df_hechos['Jornada'] == jornada_ajuste) & \
                   (df_hechos['Temporada'] == temporada_ajuste)
            
            if mask.any():
                df_hechos.loc[mask, 'Puntos'] += puntos_ajuste
                ajustes_aplicados += 1
                print(f"   ✔️ Aplicado ajuste de {puntos_ajuste} pts al ID [{id_ajuste}] en Jornada {jornada_ajuste}.")
            else:
                print(f"   ⚠️ No se encontró coincidencia para el ID [{id_ajuste}] en Jornada {jornada_ajuste}. Revisa la temporada.")
                
        print(f"📊 Total de ajustes aplicados: {ajustes_aplicados}\n")

    # --- MÉTRICA CALCULADA: ACUMULADOS ---
    df_hechos = df_hechos.sort_values(by=["ID_Futmondo", "Jornada"])
    df_hechos['Puntos_Acumulados'] = df_hechos.groupby('ID_Futmondo')['Puntos'].cumsum()

    # Guardar la tabla final
    columnas_final = ["ID_Futmondo", "Jornada", "Temporada", "Puntos", "Puntos_Acumulados"]
    df_hechos = df_hechos[columnas_final].sort_values(by=["Temporada", "Jornada", "Puntos"], ascending=[True, True, False])
    df_hechos.to_excel(ARCHIVO_HECHOS, index=False)
    
    print(f"✅ ETL Finalizado. Archivo '{ARCHIVO_HECHOS}' actualizado con éxito.")

if __name__ == "__main__":
    procesar_datos()
