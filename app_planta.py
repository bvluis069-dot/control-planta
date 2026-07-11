import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

st.set_page_config(page_title="Grupo Sánchez - Control Avanzado", layout="wide")

st.title("🏭 Monitoreo y Control de Producción — Base Solvente T2")
st.markdown("---")

# 1. ESTABLECER CONEXIÓN CON GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Leer las filas activas desde Google Sheets (Pestaña llamada 'Activas')
    df_actual = conn.read(worksheet="Activas", ttl="0d")
except Exception as e:
    st.error("Conectando con la base de datos central...")
    # Datos de respaldo por si la hoja está vacía al inicio
    df_actual = pd.DataFrame([
        {"Orden": "ORD-001", "Lote": "L-1044431", "Kg": 1200, "Etapa_Actual": "Pesado", "Comentarios": "Turno A"},
        {"Orden": "ORD-002", "Lote": "L-1044432", "Kg": 800, "Etapa_Actual": "Mezclado (20 min)", "Comentarios": "Muestra tomada"},
        {"Orden": "ORD-003", "Lote": "L-1044433", "Kg": 2000, "Etapa_Actual": "En espera", "Comentarios": "Materia prima lista"}
    ])

# ==========================================
# VISTA 1: TABLERO VISUAL SIMULTÁNEO (3 LÍNEAS)
# ==========================================
st.subheader("📊 Pistas de Fabricación en Tiempo Real (Monitoreo)")

# Aseguramos que maneje las primeras 3 fabricaciones de la lista
df_tres = df_actual.head(3)
cols_fab = st.columns(3)
etapas_lista = ["En espera", "Pre-pesado", "Pesado", "Mezclado (20 min)", "Recirculación", "Envasado"]

for index, row in df_tres.iterrows():
    with cols_fab[index]:
        st.markdown(f"### ⚙️ Fabricación {index + 1}: {row.get('Orden', 'S/O')}")
        st.caption(f"**Lote:** {row.get('Lote', '-')} | **Cantidad:** {row.get('Kg', 0)} Kg")
        
        etapa_actual = row.get('Etapa_Actual', 'En espera')
        
        # Dibujar la línea de tiempo dinámica con iconos de estado
        for etapa in etapas_lista:
            if etapa == etapa_actual:
                st.markdown(f"🟠 **[{etapa}]** <-- En proceso")
            elif etapa in etapas_lista and etapa_actual in etapas_lista and etapas_lista.index(etapa) < etapas_lista.index(etapa_actual):
                st.markdown(f"🟢 {etapa} ✓")
            else:
                st.markdown(f"⚪ {etapa}")
        
        st.markdown(f"*Nota: {row.get('Comentarios', '')}*")

st.markdown("---")

# ==========================================
# VISTA 2: FORMATO MODIFICABLE (Editor General)
# ==========================================
st.subheader("📝 Panel de Edición y Cambios (Estilo Excel)")
st.info("💡 Haz doble clic sobre cualquier celda para modificar datos o avanzar de etapa. Al terminar, presiona el botón de guardar abajo.")

# Componente interactivo para modificar los datos directamente en la web
datos_editados = st.data_editor(
    df_actual,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_central"
)

# Botón para sincronizar los cambios de vuelta a Google Sheets
if st.button("💾 Guardar y Sincronizar con la Nube", type="primary"):
    try:
        # Sobreescribir la hoja de Google Sheets con los nuevos datos modificados
        conn.update(worksheet="Activas", data=datos_editados)
        st.success("¡Sincronización exitosa! Los datos se han actualizado en Google Sheets y en ambas pantallas.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error al guardar: {e}. Verifica la configuración de Secrets.")
