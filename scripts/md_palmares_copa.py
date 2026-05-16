import pandas as pd
import os

def actualizar_copa():
    print("\n🏆 --- ASISTENTE: AÑADIR/ACTUALIZAR CAMPEÓN DE COPA --- 🏆\n")
    
    ruta_propietarios = "datos/maestros/md_propietarios.xlsx"
    ruta_copas = "datos/maestros/md_palmares_copa.xlsx"
    
    if not os.path.exists(ruta_propietarios):
        print(f"❌ Error: No existe el maestro de propietarios en {ruta_propietarios}")
        return

    # 1. Cargar lista de Mánagers
    df_prop = pd.read_excel(ruta_propietarios)
    
    # 🧹 FILTROS LIMPIEZA: Quitamos al MERCADO
    df_prop = df_prop[~df_prop['nombre'].str.contains('MERCADO', case=False, na=False)]
    
    nombres = df_prop['nombre'].tolist()
    ids = df_prop['id_propietario'].tolist()

    # 2. Preguntas interactivas (Prompts)
    temporada = input("1️⃣  Introduce la Temporada (ej. 2025/26): ")
    copa_num = input("2️⃣  Introduce el número de Copa (ej. 01, 02...): ").zfill(2) # zfill asegura que "1" pase a "01"
    
    # Mostrar opciones de Mánagers
    print("\n📋 Lista de Mánagers disponibles:")
    for i, nombre in enumerate(nombres):
        print(f"   [{i + 1}] {nombre}")
        
    try:
        idx_campeon = int(input("\n3️⃣  Escribe el NÚMERO del Campeón: ")) - 1
        idx_finalista = int(input("4️⃣  Escribe el NÚMERO del Finalista: ")) - 1
        
        id_campeon = ids[idx_campeon]
        id_finalista = ids[idx_finalista]
    except (ValueError, IndexError):
        print("❌ Error: Debes introducir un número válido de la lista.")
        return

    # 3. Crear las nuevas filas
    nuevas_filas = pd.DataFrame([
        {"Temporada": temporada, "Copa": copa_num, "Posicion": "Campeón", "ID_Futmondo": id_campeon},
        {"Temporada": temporada, "Copa": copa_num, "Posicion": "Finalista", "ID_Futmondo": id_finalista}
    ])

    # 4. Lógica UPSERT en el Excel
    if os.path.exists(ruta_copas):
        df_copas = pd.read_excel(ruta_copas)
        df_copas['Copa'] = df_copas['Copa'].astype(str).str.zfill(2)
        
        # Juntamos todo (lo viejo + lo nuevo)
        df_copas_final = pd.concat([df_copas, nuevas_filas], ignore_index=True)
        
        # 🔥 EL UPSERT: Borramos duplicados por las claves, quedándonos con el último (el nuevo)
        df_copas_final = df_copas_final.drop_duplicates(
            subset=['Temporada', 'Copa', 'Posicion'], 
            keep='last'
        )
    else:
        df_copas_final = nuevas_filas
        
    # 5. Ordenar el archivo para que quede bonito por dentro y guardar
    df_copas_final = df_copas_final.sort_values(by=['Temporada', 'Copa', 'Posicion']).reset_index(drop=True)
    df_copas_final.to_excel(ruta_copas, index=False)
    
    print("\n✨ ¡Registro guardado con éxito (UPSERT aplicado)!")
    print(f"🏅 {temporada} | Copa {copa_num}: 🥇 {nombres[idx_campeon]} | 🥈 {nombres[idx_finalista]}")
    print(f"📁 Guardado en {ruta_copas}\n")

if __name__ == "__main__":
    actualizar_copa()