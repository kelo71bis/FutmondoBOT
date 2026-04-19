import requests
import pandas as pd
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

TOKEN = os.getenv("FUTMONDO_TOKEN")

URL_MATCH = "https://api.futmondo.com/2/match/fetchmatch"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TEMPORADA_ACTUAL = "2025/26"
MODO_PUNTUACION = "presstats" 
MODO_PRUEBA = False # 🚀 LISTO PARA CARGA COMPLETA

def atrapar_jugadores(nodo, lista_resultados):
    """Radar para encontrar bloques de jugadores en el JSON"""
    if isinstance(nodo, dict):
        if "p" in nodo and "s" in nodo and isinstance(nodo.get("p"), dict) and "_id" in nodo.get("p"):
            lista_resultados.append(nodo)
        else:
            for valor in nodo.values():
                atrapar_jugadores(valor, lista_resultados)
    elif isinstance(nodo, list):
        for item in nodo:
            atrapar_jugadores(item, lista_resultados)

def generar_td_rendimiento():
    temporada_limpia = TEMPORADA_ACTUAL.replace("/", "_")
    print(f"⚽ Actualizando Rendimiento - Temporada {TEMPORADA_ACTUAL}...")
    
    ruta_partidos = "datos/maestros/md_partidos.xlsx"
    ruta_rendimiento = f"datos/hechos/td_rendimiento_{temporada_limpia}.xlsx"
    
    if not os.path.exists(ruta_partidos):
        print("⚠️ No se encontró md_partidos.xlsx.")
        return

    # 1. Identificar partidos finalizados
    df_partidos = pd.read_excel(ruta_partidos)
    df_finalizados = df_partidos[df_partidos['estado_partido'] == 'F']
    partidos_completados = df_finalizados['id_partido'].tolist()
    
    # 2. Identificar qué partidos YA tenemos en el Excel (Lógica Delta)
    partidos_procesados = []
    if os.path.exists(ruta_rendimiento):
        df_existente = pd.read_excel(ruta_rendimiento)
        if not df_existente.empty and 'id_partido' in df_existente.columns:
            partidos_procesados = df_existente['id_partido'].unique().tolist()
    else:
        df_existente = pd.DataFrame()
        
    # 3. Filtrar solo los que faltan por descargar
    partidos_a_consultar = [p for p in partidos_completados if p not in partidos_procesados]
    
    if not partidos_a_consultar:
        print("✅ Todo al día. No hay partidos nuevos que procesar.")
        return
        
    total_partidos = len(partidos_a_consultar)
    print(f"🔍 Detectados {total_partidos} partidos pendientes de descarga.")
    
    filas_rendimiento = []
    
    for i, id_partido in enumerate(partidos_a_consultar, 1):
        print(f"   ⏳ Descargando acta {i}/{total_partidos}...", end="\r")
        
        payload = {
            "header": {"token": TOKEN, "userid": "5dcac7a682052f531c77f140"},
            "query": {"matchId": id_partido},
            "answer": {}
        }
        
        try:
            response = requests.post(URL_MATCH, headers=HEADERS, json=payload, timeout=10)
            
            if response.status_code == 200:
                json_completo = response.json()
                jugadores_partido = []
                atrapar_jugadores(json_completo, jugadores_partido)
                
                for jug in jugadores_partido:
                    p_info = jug.get("p", {})
                    s_info = jug.get("s", {})
                    data = s_info.get("data", {})
                    
                    rol_jugado = s_info.get("role")
                    puntos_jugador = 0
                    
                    # Extraer puntos del modo presstats respetando la posición jugada
                    for pts in s_info.get("po", []):
                        if pts.get("mode") == MODO_PUNTUACION:
                            if pts.get("r") == rol_jugado or "r" not in pts:
                                puntos_jugador = pts.get("p", 0)
                                break
                    
                    # Fallback si el mapeo de rol falla
                    if puntos_jugador == 0:
                        for pts in s_info.get("po", []):
                            if pts.get("mode") == MODO_PUNTUACION:
                                puntos_jugador = pts.get("p", 0)
                                break

                    filas_rendimiento.append({
                        "id_jugador": p_info.get("_id"),
                        "puntos": puntos_jugador,
                        "id_partido": id_partido,
                        "titular": "Sí" if s_info.get("st") == "st" else "No",
                        "goles": data.get("goals", 0),
                        "asistencias": data.get("goal_assist", 0),
                        "minutos_jugados": data.get("mins_played", 0),
                        "amarilla": data.get("yellow_card", 0),
                        "roja": data.get("red_card", 0)
                    })
            else:
                print(f"\n   ❌ Error HTTP {response.status_code} en partido {id_partido}")
        except Exception as e:
            print(f"\n   ⚠️ Error en partido {id_partido}: {e}")
            
        # Pausa de seguridad para evitar bloqueos en la carga masiva inicial
        time.sleep(0.4)
            
    print("\n✅ Procesamiento finalizado. Guardando datos...")
    
    if filas_rendimiento:
        df_nuevos = pd.DataFrame(filas_rendimiento)
        os.makedirs("datos/hechos", exist_ok=True)
        
        # Unimos lo nuevo con lo viejo y guardamos
        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        
        columnas_ordenadas = ["id_jugador", "puntos", "id_partido", "titular", "goles", "asistencias", "minutos_jugados", "amarilla", "roja"]
        df_final = df_final[columnas_ordenadas]
            
        df_final.to_excel(ruta_rendimiento, index=False)
        print(f"💾 ¡Hecho! Archivo actualizado con un total de {len(df_final)} registros.")

if __name__ == "__main__":
    generar_td_rendimiento()