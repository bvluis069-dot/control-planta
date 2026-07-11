import streamlit as st
import time
from datetime import datetime
import pandas as pd

# Configuración de la página (Moderna y oscura)
st.set_page_config(page_title="Grupo Sánchez - Control de Procesos", layout="wide", initial_sidebar_state="collapsed")

# Estilo personalizado para los bloques de las etapas
st.markdown("""
    <style>
    .etapa-espera { background-color: #1e1e24; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #444; }
    .etapa-proceso { background-color: #ff9f1c; color: black; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; animation: pulse 2s infinite; }
    .etapa-listo { background-color: #172a28; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #2ec4b6; }
    h3 { margin-top: 5px !important; }
    </style>
""", unsafe_allow_html=True)

# Mantener el estado de la aplicación en la sesión web
if "etapa" not in st.session_state:
    st.session_state.etapa = 0
    st.session_state.orden = ""
    st.session_state.lote = ""
    st.session_state.kg = 0
    st.session_state.tiempos = {}

st.title("🏭 Sistema de Control de Procesos en Tiempo Real")
st.subheader("Grupo Sánchez — Base Solvente T2")

# --- VISTA DE ACCESO / REGISTRO ---
if st.session_state.etapa == 0:
    st.markdown("### 📝 Registro de Nueva Orden de Producción")
    with st.form("registro_orden"):
        col1, col2, col3 = st.columns(3)
        with col1:
            orden = st.text_input("Número de Orden", placeholder="Ej. ORD-2026")
        with col2:
            lote = st.text_input("Número de Lote", placeholder="Ej. L-1044431")
        with col3:
            kg = st.number_input("Kilogramos (Kg)", min_value=0, value=1000)
        
        btn_iniciar = st.form_submit_button("INICIAR PROCESO ➔")
        if btn_iniciar and orden and lote:
            st.session_state.orden = orden
            st.session_state.lote = lote
            st.session_state.kg = kg
            st.session_state.etapa = 1
            st.session_state.tiempos["inicio_total"] = time.time()
            st.session_state.tiempos["inicio_etapa"] = time.time()
            st.rerun()

# --- VISTA DEL PANEL VISUAL (LO QUE VES DESDE CASA) ---
else:
    # Encabezado con datos de producción
    st.info(f"**Orden Activa:** {st.session_state.orden}   |   **Lote:** {st.session_state.lote}   |   **Cantidad:** {st.session_state.kg} Kg")
    
    # Dibujar las etapas de forma dinámica
    cols = st.columns(6)
    nombres_etapas = ["Pre-pesado", "Pesado", "Mezclado (20 min)", "Recirc. Manual", "Recirc. Auto (10 min)", "Envasado"]
    iconos = ["📦", "⚖️", "🔄", "🛠️", "🔁", "🛍️"]
    
    for i in range(6):
        num_etapa = i + 1
        with cols[i]:
            if st.session_state.etapa > num_etapa:
                # Etapa completada
                st.markdown(f"<div class='etapa-listo'><h2>{iconos[i]}</h2><p>{nombres_etapas[i]}</p><b>✓ Listo</b></div>", unsafe_allow_html=True)
            elif st.session_state.etapa == num_etapa:
                # Etapa actual en proceso
                st.markdown(f"<div class='etapa-proceso'><h2>{iconos[i]}</h2><p>{nombres_etapas[i]}</p>⏳ En Proceso</div>", unsafe_allow_html=True)
            else:
                # Etapa en espera
                st.markdown(f"<div class='etapa-espera'><h2>{iconos[i]}</h2><p>{nombres_etapas[i]}</p><span style='color:#666'>En espera</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Botón de control para el operador en planta
    if st.session_state.etapa <= 6:
        etapa_act = st.session_state.etapa
        st.markdown(f"### ⚙️ Control de Operador (Etapa actual: {nombres_etapas[etapa_act-1]})")
        
        if st.button(f"FINALIZAR {nombres_etapas[etapa_act-1].upper()} ✓", type="primary"):
            ahora = time.time()
            duracion = int(ahora - st.session_state.tiempos["inicio_etapa"])
            st.session_state.tiempos[nombres_etapas[etapa_act-1]] = f"{duracion}s"
            
            if st.session_state.etapa == 6:
                # Guardar al historial final
                st.success("¡Orden completada de forma segura! Registrando datos...")
                time.sleep(2)
                st.session_state.etapa = 0  # Reiniciar
            else:
                st.session_state.etapa += 1
                st.session_state.tiempos["inicio_etapa"] = ahora
            st.rerun()
            
    if st.button("❌ Cancelar Orden"):
        st.session_state.etapa = 0
        st.rerun()