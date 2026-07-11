import streamlit as st
import pandas as pd
import urllib.request
import json
import time
from datetime import datetime

st.set_page_config(page_title="Control Planta", layout="wide")

# URL de tu WebApp (La que ya tienes)
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwU4j05N-6peH6hC1cd3swfn4oerY6C2byX9HEPvfEbJFJqKWfsA42LlLW1wSldUve6SQ/exec"
LECTURA_URL = "https://docs.google.com/spreadsheets/d/18k2Zn-7IAqMB62dw4Lv_kWVOI2nmz4Syck_I6rQhWEl/gviz/tq?tqx=out:csv&sheet=Historial"

# Memoria compartida ultra ligera
if 'memoria' not in st.session_state:
    st.session_state.memoria = {
        m: {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}} for m in [1, 2, 3]
    }

# Definición etapas
nombres_etapas = ["Pre-pesado", "Pesado", "Control de Calidad (C.C. 1)", "Mezclado (20 min)", "Recirc. Manual", "Recirc. Auto (10 min)", "Control de Calidad (C.C. 2)", "Envasado"]

# Interfaz simplificada
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Perfil:", ["Operativo", "Ingeniería"])

if opcion == "Operativo":
    st.title("Control de Mezcladores")
    cols = st.columns(3)
    for i in range(3):
        m = i + 1
        with cols[i]:
            st.subheader(f"Mezclador {m}")
            est = st.session_state.memoria[m]
            
            if est["etapa"] == 0:
                with st.form(f"f{m}"):
                    ord_in = st.text_input("Orden")
                    lote_in = st.text_input("Lote")
                    if st.form_submit_button("Iniciar"):
                        est.update({"etapa": 1, "orden": ord_in, "lote": lote_in, "tiempos": {"t": time.time(), "inicio": datetime.now().strftime("%H:%M")}})
                        st.rerun()
            else:
                st.write(f"Orden: {est['orden']}")
                etapa_idx = est["etapa"] - 1
                if st.button(f"Finalizar {nombres_etapas[etapa_idx]}"):
                    if est["etapa"] == 8:
                        # ENVÍO NATIVO (Sin librería externa)
                        datos = json.dumps({"Fecha": datetime.now().strftime("%Y-%m-%d"), "Orden": est["orden"], "Lote": est["lote"]})
                        req = urllib.request.Request(WEBAPP_URL, data=datos.encode('utf-8'), headers={'Content-Type': 'application/json'})
                        urllib.request.urlopen(req)
                        st.session_state.memoria[m] = {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}}
                    else:
                        est["etapa"] += 1
                    st.rerun()
else:
    st.title("Panel Ingeniero")
    try:
        df = pd.read_csv(LECTURA_URL)
        st.dataframe(df)
    except:
        st.write("Cargando datos...")
