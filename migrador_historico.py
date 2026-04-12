import pandas as pd
import re
import os

mapa_equipos = {
    "FC Mikelona": "5f452f5e66dd374930eb2b71",
    "Real Dendryd": "5f453062ec331549297ee6b8",
    "Cruyffisme FC": "5f47aeb6c387a50bca03dd55",
    "Pallejandro": "62d5bd9ad8106d3355b5bdc1",
    "Pallejandro SAD": "62d5bd9ad8106d3355b5bdc1", # Variante encontrada en tu CSV
    "URSS": "5f4530beec331549297ee6d6",
    "Bichos Team": "5f47ab5b9e2edb0bb831c703",
    "Jatafe": "5f45324dec331549297ee971",
    "Cracklos FC": "5f4531e9764e7d491e029746",
    "Arsenati": "LEGACY_ARSENATI"
}

def limpiar_temporada(temp):
    temp = str(temp).strip().replace("-", "/")
    if len(temp) == 9 and temp[4] == "/":
        return temp[:5] + temp[7:]
    return temp

def limpiar_jornada(jornada):
    numeros = re.findall(r'\d+', str(jornada))
    return int(numeros[0]) if numeros else 0

def migrar():
    # Buscamos el archivo que subiste (GitHub a veces le añade la extensión del tipo de archivo)
    archivo_input = "TestFMVE.xlsx" 
    if not os.path.exists(archivo_input):
        # Intentar con el nombre exacto que tiene en GitHub si es distinto
        archivo_input = [f for f in os.listdir('.') if 'TestFMVE' in f][0]

    print(f"Leyendo: {archivo_input}")
    df = pd.read_csv(archivo_input) if archivo_input.endswith('.csv') else pd.read_excel(archivo_input)

    df['ID_Futmondo'] = df['Equipo'].map(mapa_equipos)
    df['Temporada'] = df['Temporada'].apply(limpiar_temporada)
    df['Jornada'] = df['Jornada'].apply(limpiar_jornada)
    df['Puntos'] = pd.to_numeric(df['Puntos'], errors='coerce').fillna(0)

    df = df.sort_values(by=["Temporada", "ID_Futmondo", "Jornada"])
    df['Puntos_Acumulados'] = df.groupby(['Temporada', 'ID_Futmondo'])['Puntos'].cumsum()

    columnas_final = ["ID_Futmondo", "Jornada", "Temporada", "Puntos", "Puntos_Acumulados"]
    df_hechos = df[columnas_final]
    
    df_hechos.to_excel("Fact_Historica_Total.xlsx", index=False)
    print("✅ Fact_Historica_Total.xlsx generada con éxito.")

if __name__ == "__main__":
    migrar()
