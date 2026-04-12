import pandas as pd
import os

# Datos finales de tu captura 24/25
totales_24_25 = {
    "5f453062ec331549297ee6b8": 2668, # Real Dendryd
    "5f47aeb6c387a50bca03dd55": 2559, # Cruyffisme FC
    "5f45324dec331549297ee971": 2520, # Jatafe club de gafe
    "5f452f5e66dd374930eb2b71": 2406, # FC Mikelona
    "62d5bd9ad8106d3355b5bdc1": 2365, # Pallejandro S.A.D
    "5f47ab5b9e2edb0bb831c703": 2322, # Bichos team
    "5f4531e9764e7d491e029746": 2101, # Cracklos F.C
    "5f4530beec331549297ee6d6": 1962  # URSS
}

JORNADAS = 38
TEMPORADA = "2024/25"
filas_nuevas = []

print(f"🪄 Generando 38 jornadas lineales para la temporada {TEMPORADA}...")

for equipo_id, total in totales_24_25.items():
    # Reparto simple: la mayoría de jornadas tendrán la misma puntuación
    puntos_base = total // JORNADAS
    resto = total % JORNADAS
    acumulado = 0
    
    for j in range(1, JORNADAS + 1):
        # Repartimos el 'resto' en las primeras jornadas para que no se note
        puntos_esta_jornada = puntos_base + (1 if j <= resto else 0)
        acumulado += puntos_esta_jornada
        
        filas_nuevas.append({
            "ID_Futmondo": equipo_id,
            "Jornada": j,
            "Temporada": TEMPORADA,
            "Puntos": puntos_esta_jornada,
            "Puntos_Acumulados": acumulado
        })

df_24_25 = pd.DataFrame(filas_nuevas)

# --- INTEGRACIÓN EN EL HISTÓRICO ---
archivo_hist = "Fact_Historica_Total.xlsx"

if os.path.exists(archivo_hist):
    df_old = pd.read_excel(archivo_hist)
    # Quitamos cualquier dato previo de la 24/25 para no duplicar
    df_old = df_old[df_old['Temporada'] != TEMPORADA]
    df_final = pd.concat([df_old, df_24_25], ignore_index=True)
else:
    df_final = df_24_25

# Ordenamos para que los acumulados y rankings se calculen bien luego
df_final = df_final.sort_values(by=["Temporada", "Jornada", "ID_Futmondo"])
df_final.to_excel(archivo_hist, index=False)

print(f"✅ Temporada 24/25 inyectada en '{archivo_hist}'.")