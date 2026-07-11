import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Grupo Sánchez - Control Remoto", layout="wide")

# --- SIMULACIÓN DE BASE DE DATOS (Conexión local temporal antes de enlazar API) ---
# En el paso siguiente cambiaremos esto por la conexión directa a tu Google Sheets
if "df_fabricaciones" not in st.session_state:
    st.session_state.df_fabricaciones = pd.DataFrame([
        {"Orden": "ORD-001", "Lote": "L-1044431", "Kg": 1200, "Etapa_Actual": "Pesado", "Comentarios": "Operador en turno A"},
        {"Orden": "ORD-002", "Lote": "L-1044432", "Kg": 800, "Etapa_Actual": "Mezclado (20 min)", "Comentarios": "Esperando muestra de control"},
        {"Orden": "ORD-003", "Lote": "L-1044433", "Kg": 2000, "Etapa_Actual": "En espera", "Comentarios": "Materia prima completa"}
    ])

st.title("🏭 Monitoreo y Control de Producción — Base Solvente T2")
st.markdown("---")

# ==========================================
# VISTA 1: MONITOREO VISUAL SIMULTÁNEO (Las 3 Fabricaciones)
# ==========================================
st.subheader("📊 Pistas de Fabricación en Tiempo Real (Desde Casa)")

cols_fab = st.columns(3)
etapas_lista = ["En espera", "Pre-pesado", "Pesado", "Mezclado (20 min)", "Recirculación", "Envasado"]

for index, row in st.session_state.df_fabricaciones.iterrows():
    with cols_fab[index]:
        st.markdown(f"### ⚙️ Línea {index + 1}: {row['Orden']}")
        st.caption(f"**Lote:** {row['Lote']} | **Cantidad:** {row['Kg']} Kg")
        
        # Dibujar barra visual de progreso para cada una de las 3 órdenes
        etapa_actual = row['Etapa_Actual']
        
        for etapa in etapas_lista:
            if etapa == etapa_actual:
                # Etapa actual en naranja brillante
                st.markdown(f"🟠 **[{etapa}]** <-- En proceso")
            elif etapas_lista.index(etapa) < etapas_lista.index(etapa_actual if etapa_actual in etapas_lista else "En espera"):
                # Etapas del pasado en verde
                st.markdown(f"🟢 {etapa} ✓")
            else:
                # Etapas futuras en gris
                st.markdown(f"⚪ {etapa}")
        
        st.markdown(f"*Nota: {row['Comentarios']}*")

st.markdown("---")

# ==========================================
# VISTA 2: FORMATO MODIFICABLE (Estilo Excel)
# ==========================================
st.subheader("📝 Panel de Control Modificable (Editor de Datos)")
st.info("💡 Puedes dar doble clic sobre cualquier celda de abajo para modificar los datos (Kg, Lote o cambiar la Etapa). Los cambios se reflejarán arriba inmediatamente.")

# El data_editor permite modificar los datos directamente en la pantalla
datos_editados = st.data_editor(
    st.session_state.df_fabricaciones,
    num_rows="dynamic", # Te permite agregar o quitar filas si hay más fabricaciones
    use_container_width=True
)

# Guardar los cambios hechos en la tabla modificable al estado del sistema
if st.button("💾 Guardar y Sincronizar Cambios"):
    st.session_state.df_fabricaciones = datos_editados
    st.success("¡Datos actualizados correctamente en el sistema!")
    time.sleep(1)
    st.rerun()