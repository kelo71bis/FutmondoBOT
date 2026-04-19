# scripts/validador_temporada.py
import pandas as pd
import os
import sys

ruta = "datos/maestros/md_partidos.xlsx"

if os.path.exists(ruta):
    df = pd.read_excel(ruta)
    # Filtramos la última jornada de LaLiga (Jornada 38)
    jornada_38 = df[df['jornada'] == 38]
    
    if not jornada_38.empty:
        # Comprobamos si TODOS los partidos de la J38 están cerrados
        if (jornada_38['estado_jornada'] == 'closed').all():
            print("🛑 LaLiga ha terminado. Abortando cargas.")
            # Salimos con código 1 para que GitHub Actions detenga el workflow
            sys.exit(1) 
        
print("🟢 LaLiga sigue en juego. Procediendo con la carga diaria.")
sys.exit(0)