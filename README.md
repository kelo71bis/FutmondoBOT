# 🏆 Guía de Operaciones: Liga Santanguissa (FutmondoBOT)

Este documento detalla la estructura del proyecto, el flujo de los datos y los pasos exactos necesarios para mantener y actualizar el portal estadístico de la Liga Santanguissa.

---

## 🏗️ 1. Arquitectura y Mapa de Archivos

El proyecto está dividido estrictamente en tres capas: **Datos Maestros** (configuración), **Scripts** (motores de cálculo) y **Aplicación Web** (visualización).

\`\`\`text
FutmondoBOT/
│
├── app.py                             # Código principal de la web en Streamlit
├── requirements.txt                   # Librerías necesarias para el servidor de la nube
├── README.md                          # Esta guía de operaciones
│
├── datos/
│   ├── maestros/
│   │   ├── md_propietarios.xlsx       # Base de datos de mánagers (IDs y Nombres)
│   │   ├── md_palmares_liga.xlsx      # Historial de campeones de liga (Autogenerado)
│   │   └── md_palmares_copa.xlsx      # Historial de campeones de copa (Interactivo)
│   │
│   ├── hechos/
│   │   └── td_puntos_jugadores_XX.xlsx # Puntos detallados descargados por el bot
│   │
│   └── vistas_negocio/
│       └── Fact_Global_Master.xlsx    # El Excel Maestro unificado (Histórico + Actual)
│
└── scripts/
    ├── crear_vista_global.py          # Procesa, limpia y unifica el máster global
    ├── md_palmares_liga.py            # Calcula los campeones de liga (Regla Jornada 38)
    └── md_palmares_copa.py            # Asistente por consola para registrar copas
\`\`\`

---

## 🔄 2. Matriz de Actualización (¿Qué se automatiza y qué no?)

| Proceso / Tarea | Tipo | ¿Cómo se ejecuta? | ¿Cuándo hay que hacerlo? |
| :--- | :--- | :--- | :--- |
| **Descarga de puntos** | 🤖 **Auto** | Bot de scraping en Futmondo. | Cada mañana tras cerrar la jornada. |
| **Cálculo Global** | 🏃‍♂️ **Manual** | `python scripts/crear_vista_global.py` | Siempre después de descargar datos nuevos. |
| **Palmarés de Liga** | 🏃‍♂️ **Manual** | `python scripts/md_palmares_liga.py` | Una vez al año (al acabar la jornada 38). |
| **Palmarés de Copa** | ✍️ **Interactivo** | `python scripts/md_palmares_copa.py` | Al finalizar cada torneo interno de Copa. |
| **Actualizar la Web** | 🤖 **Auto** | `Commit` y `Push origin` (GitHub Desktop).| Cada vez que haya cambios en los Excels. |

---

## 🛠️ 3. Manual de Procedimientos Frecuentes

### A) El flujo semanal para actualizar la web (Día de Jornada)
Cuando termina una jornada y quieres que los puntos suban a internet:
1. Asegúrate de que el bot ha descargado los últimos puntos en `datos/hechos/`.
2. Abre la terminal de VS Code y consolida los datos ejecutando:
   \`\`\`bash
   python scripts/crear_vista_global.py
   \`\`\`
3. Abre **GitHub Desktop**, verifica que `Fact_Global_Master.xlsx` se ha modificado.
4. Escribe un resumen (ej: *"Jornada 12"*), dale a **Commit to main** y luego a **Push origin**.
5. *Fin.* En 60 segundos la web pública se actualiza sola.

### B) Cómo añadir o corregir un Campeón de Copa (Lógica UPSERT)
1. Ejecuta el asistente en la terminal:
   \`\`\`bash
   python scripts/md_palmares_copa.py
   \`\`\`
2. Responde a las 4 preguntas con números. El sistema usará la lista oficial de mánagers.
3. *Si te has equivocado de campeón:* Vuelve a ejecutar el script usando la **misma Temporada, misma Copa y misma Posición**. El sistema aplicará un UPSERT y pisará el error sin duplicar líneas.
4. Haz `Commit` y `Push` de `md_palmares_copa.xlsx` vía GitHub Desktop.

---

## 📅 4. Protocolo de Cambio de Temporada (Verano)

Al empezar una nueva temporada en Futmondo, sigue estos 3 pasos:

**Paso 1: Cerrar la temporada en el Palmarés**
Asegúrate de que la jornada 38 del año finalizado está calculada y reparte el trofeo ejecutando:
\`\`\`bash
python scripts/md_palmares_liga.py
\`\`\`

**Paso 2: Nuevo archivo de hechos**
El bot empezará a descargar datos en un nuevo Excel. Asegúrate de que su nombre sigue el patrón oficial (ej: `td_puntos_jugadores_2026_27.xlsx`).

**Paso 3: Actualizar el puente Global**
Abre `scripts/crear_vista_global.py` y busca el bloque de rutas en las primeras líneas. Modifica la ruta del archivo "actual" para que apunte al de la nueva temporada:
\`\`\`python
rutas = {
    "historico": "Fact_Global_Master_1.xlsx",
    "actual": "datos/hechos/td_puntos_jugadores_2026_27.xlsx", # <- Actualiza el año aquí
    "salida": "datos/vistas_negocio/Fact_Global_Master.xlsx"
}
\`\`\`
Guarda el archivo, ejecuta el script global y la nueva temporada quedará enlazada automáticamente con todo el histórico anterior.