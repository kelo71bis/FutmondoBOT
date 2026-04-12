import pandas as pd

# Mapeo de IDs (Añadiendo Arsenati que vi en tu imagen)
mapa_equipos = {
    "FC Mikelona": "5f452f5e66dd374930eb2b71",
    "Real Dendryd": "5f453062ec331549297ee6b8",
    "Cruyffisme FC": "5f47aeb6c387a50bca03dd55",
    "Pallejandro": "62d5bd9ad8106d3355b5bdc1",
    "URSS": "5f4530beec331549297ee6d6",
    "Bichos Team": "5f47ab5b9e2edb0bb831c703",
    "Jatafe": "5f45324dec331549297ee971",
    "Cracklos F.C": "5f4531e9764e7d491e029746",
    "Arsenati": "LEGACY_ARSENATI"
}

# Tus datos transcritos desde la imagen
datos_copas = [
    ("2020/21", "01", "FC Mikelona", "Cruyffisme FC"),
    ("2020/21", "02", "URSS", "FC Mikelona"),
    ("2020/21", "03", "Cruyffisme FC", "FC Mikelona"),
    ("2021/22", "01", "Bichos Team", "Real Dendryd"),
    ("2021/22", "02", "URSS", "FC Mikelona"),
    ("2021/22", "03", "Arsenati", "Bichos Team"),
    ("2022/23", "01", "URSS", "Jatafe"),
    ("2022/23", "02", "Jatafe", "Real Dendryd"),
    ("2022/23", "03", "FC Mikelona", "Pallejandro"),
    ("2023/24", "01", "Jatafe", "FC Mikelona"),
    ("2023/24", "02", "FC Mikelona", "Jatafe"),
    ("2023/24", "03", "Real Dendryd", "URSS"),
    ("2024/25", "01", "Real Dendryd", "Bichos Team"),
    ("2024/25", "02", "Real Dendryd", "Jatafe"),
    ("2024/25", "03", "Cruyffisme FC", "Pallejandro"),
    ("2025/26", "01", "FC Mikelona", "Jatafe"),
    ("2025/26", "02", "Pallejandro", "FC Mikelona")
]

filas = []
for temp, copa, campeon, finalista in datos_copas:
    # Fila del Campeón
    filas.append({
        "Temporada": temp,
        "Copa": copa,
        "Posicion": "Campeón",
        "ID_Futmondo": mapa_equipos.get(campeon, "ID_DESCONOCIDO")
    })
    # Fila del Finalista
    filas.append({
        "Temporada": temp,
        "Copa": copa,
        "Posicion": "Finalista",
        "ID_Futmondo": mapa_equipos.get(finalista, "ID_DESCONOCIDO")
    })

df_palmares = pd.DataFrame(filas)
df_palmares.to_excel("Fact_Palmares_Copa.xlsx", index=False)
print("✅ Historial de Copas generado: 'Fact_Palmares_Copa.xlsx'")