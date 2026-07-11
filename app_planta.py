import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Grupo Sánchez - Control de Mezcladores", layout="wide")

# =========================================================================
# CONFIGURACIÓN DE ENLACES DIRECTOS
# =========================================================================
SHEET_ID = "18k2Zn-7IAqMB62dw4Lv_kWVOI2nmz4Syck_I6rQhWEl"
LECTURA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Historial"
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwU4j05N-6peH6hC1cd3swfn4oerY6C2byX9HEPvfEbJFJqKWfsA42LlLW1wSldUve6SQ/exec"

# Inicializar memoria para los 3 mezcladores independientes si no existe
for m in [1, 2, 3]:
    if f"m{m}_etapa" not in st.session_state:
        st.session_state[f"m{m}_etapa"] = 0
        st.session_state[f"m{m}_orden"] = ""
        st.session_state[f"m{m}_lote"] = ""
        st.session_state[f"m{m}_kg"] = 0
        st.session_state[f"m{m}_tiempos"] = {}

nombres_etapas = ["Pre-pesado", "Pesado", "Mezclado (20 min)", "Recirc. Manual", "Recirc. Auto (10 min)", "Envasado"]
iconos = ["📦", "⚖️", "🔄", "🛠️", "🔁", "🛍️"]

# ==========================================
# MENÚ LATERAL: CAMBIO DE INTERFAZ
# ==========================================
st.sidebar.markdown("# 🔐 Control de Acceso")
rol_seleccionado = st.sidebar.radio(
    "Selecciona tu perfil de visualización:",
    ["🎛️ Nivel Operativo (Mezcladores)", "📊 Nivel Ingeniero de Procesos"]
)

# ==========================================
# VISTA 1: INTERFAZ NIVEL OPERATIVO
# ==========================================
if rol_seleccionado == "🎛️ Nivel Operativo (Mezcladores)":
    st.title("🏭 Monitoreo y Control de Procesos — Base Solvente T2")
    st.markdown("---")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    mezcladores_cols = [col_m1, col_m2, col_m3]

    for i, col in enumerate(mezcladores_cols):
        m = i + 1
        with col:
            st.markdown(f"## 🔄 Mezclador {m}")
            
            if st.session_state[f"m{m}_etapa"] == 0:
                st.markdown("### 📝 Nueva Orden")
                with st.form(f"form_m{m}"):
                    orden = st.text_input("Número de Orden", key=f"input_o_m{m}", placeholder="Ej. ORD-2026")
                    lote = st.text_input("Número de Lote", key=f"input_l_m{m}", placeholder="Ej. L-1044431")
                    kg = st.number_input("Kilogramos (Kg)", key=f"input_k_m{m}", min_value=0, value=1000)
                    
                    btn_iniciar = st.form_submit_button("INICIAR PROCESO ➔")
                    if btn_iniciar and orden and lote:
                        st.session_state[f"m{m}_orden"] = orden
                        st.session_state[f"m{m}_lote"] = lote
                        st.session_state[f"m{m}_kg"] = kg
                        st.session_state[f"m{m}_etapa"] = 1
                        st.session_state[f"m{m}_tiempos"]["Inicio_Proceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state[f"m{m}_tiempos"]["t_etapa"] = time.time()
                        st.rerun()
            else:
                ord_act = st.session_state[f"m{m}_orden"]
                lot_act = st.session_state[f"m{m}_lote"]
                kg_act = st.session_state[f"m{m}_kg"]
                etapa_act = st.session_state[f"m{m}_etapa"]
                
                st.info(f"**Orden:** {ord_act} | **Lote:** {lot_act} | **Kg:** {kg_act}")
                
                for idx_e, text_e in enumerate(nombres_etapas):
                    num_e = idx_e + 1
                    if etapa_act > num_e:
                        st.markdown(f"🟢 {iconos[idx_e]} {text_e} ✓")
                    elif etapa_act == num_e:
                        st.markdown(f"🟠 **[{iconos[idx_e]} {text_e}]** <-- Activo")
                    else:
                        st.markdown(f"⚪ {iconos[idx_e]} {text_e}")
                
                st.markdown("---")
                
                if etapa_act <= 6:
                    text_etapa_actual = nombres_etapas[etapa_act - 1]
                    if st.button(f"FINALIZAR {text_etapa_actual.upper()} ✓", key=f"btn_sig_m{m}", type="primary"):
                        ahora = time.time()
                        duracion_min = round((ahora - st.session_state[f"m{m}_tiempos"]["t_etapa"]) / 60, 2)
                        st.session_state[f"m{m}_tiempos"][text_etapa_actual] = f"{duracion_min} min"
                        
                        if etapa_act == 6:
                            st.toast("Enviando registro final a la base de datos...")
                            nueva_fila = {
                                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                                "Mezclador": f"Mezclador {m}",
                                "Orden": ord_act,
                                "Lote": lot_act,
                                "Kg": int(kg_act),
                                "Inicio": st.session_state[f"m{m}_tiempos"]["Inicio_Proceso"],
                                "Fin": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Pre_pesado": st.session_state[f"m{m}_tiempos"].get("Pre-pesado", "0 min"),
                                "Pesado": st.session_state[f"m{m}_tiempos"].get("Pesado", "0 min"),
                                "Mezclado": st.session_state[f"m{m}_tiempos"].get("Mezclado (20 min)", "0 min"),
                                "Recirc_Manual": st.session_state[f"m{m}_tiempos"].get("Recirc. Manual", "0 min"),
                                "Recirc_Auto": st.session_state[f"m{m}_tiempos"].get("Recirc. Auto (10 min)", "0 min"),
                                "Envasado": st.session_state[f"m{m}_tiempos"].get("Envasado", "0 min")
                            }
                            
                            # Envío directo por método POST a tu Macro Web
                            try:
                                res = requests.post(WEBAPP_URL, json=nueva_fila)
                                if res.status_code == 200:
                                    st.success("¡Historial actualizado en la nube con éxito!")
                                else:
                                    st.error("Error en la respuesta del servidor de Google.")
                            except Exception as err:
                                st.error(f"Falla de conexión: {err}")
                            
                            st.session_state[f"m{m}_etapa"] = 0
                        else:
                            st.session_state[f"m{m}_etapa"] += 1
                            st.session_state[f"m{m}_tiempos"]["t_etapa"] = ahora
                        st.rerun()
                
                if st.button("❌ Cancelar Orden", key=f"btn_can_m{m}"):
                    st.session_state[f"m{m}_etapa"] = 0
                    st.rerun()

# ==========================================
# VISTA 2: INTERFAZ NIVEL INGENIERO DE PROCESOS
# ==========================================
else:
    st.title("📊 Panel de Análisis e Indicadores — Ingeniero de Procesos")
    st.markdown("---")
    
    # Carga automática de datos en tiempo real leyendo el CSV público
    try:
        df_historial = pd.read_csv(LECTURA_URL)
        df_historial = df_historial.dropna(subset=["Orden"])
        error_carga = False
    except Exception:
        error_carga = True
        df_historial = pd.DataFrame([
            {"Fecha": "2026-07-11", "Mezclador": "Mezclador 1", "Orden": "ORD-101", "Lote": "L-5541", "Kg": 1200, "Inicio": "10:00:00", "Fin": "11:15:00", "Pre_pesado": "10 min", "Pesado": "15 min", "Mezclado": "20 min", "Recirc_Manual": "10 min", "Recirc_Auto": "10 min", "Envasado": "10 min"}
        ])

    if error_carga:
        st.info("💡 Consejo: Una vez que realices tu primera fabricación completa desde el panel operativo, los datos reales aparecerán aquí automáticamente.")

    # MÓDULO DE INDICADORES (KPIs)
    st.subheader("📈 Rendimiento Global de la Planta")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric(label="Total de Órdenes Completadas", value=len(df_historial))
    with k2:
        if "Kg" in df_historial.columns:
            df_historial["Kg"] = pd.to_numeric(df_historial["Kg"], errors='coerce').fillna(0)
            total_toneladas = df_historial["Kg"].sum()
            st.metric(label="Volumen Total Controlado", value=f"{int(total_toneladas):,} Kg")
        else:
            st.metric(label="Volumen Total Controlado", value="0 Kg")
    with k3:
        st.metric(label="Disponibilidad de Mezcladores", value="100 %")
        
    st.markdown("---")
    
    # GRÁFICA EN TIEMPO REAL PARA INGENIERÍA
    st.subheader("📊 Distribución de Producción por Equipo (Kilogramos)")
    if "Mezclador" in df_historial.columns and "Kg" in df_historial.columns:
        df_resumen = df_historial.groupby("Mezclador")["Kg"].sum().reset_index()
        st.bar_chart(data=df_resumen, x="Mezclador", y="Kg")
        
    st.markdown("---")
    
    # HISTORIAL COMPLETO
    st.subheader("📋 Auditoría de Tiempos y Trazabilidad")
    st.dataframe(df_historial)
