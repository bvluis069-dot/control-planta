import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Grupo Sánchez - Control de Mezcladores", layout="wide")

# =========================================================================
# CONFIGURACIÓN DE ENLACES
# =========================================================================
SHEET_ID = "18k2Zn-7IAqMB62dw4Lv_kWVOI2nmz4Syck_I6rQhWEl"
LECTURA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Historial"
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwU4j05N-6peH6hC1cd3swfn4oerY6C2byX9HEPvfEbJFJqKWfsA42LlLW1wSldUve6SQ/exec"

# =========================================================================
# ESTRUCTURA DE MEMORIA GLOBAL (Sin bloqueos que tiren el servidor)
# =========================================================================
class MemoriaPlanta:
    def __init__(self):
        # Usar una clase oculta los cambios al inspector estricto de Streamlit
        self.datos = {
            1: {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}},
            2: {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}},
            3: {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}}
        }

@st.cache_resource
def obtener_instancia_planta():
    return MemoriaPlanta()

memoria_global = obtener_instancia_planta()

# Definición de las 8 etapas
nombres_etapas = [
    "Pre-pesado", 
    "Pesado", 
    "Control de Calidad (C.C. 1)", 
    "Mezclado (20 min)", 
    "Recirc. Manual", 
    "Recirc. Auto (10 min)", 
    "Control de Calidad (C.C. 2)", 
    "Envasado"
]
iconos = ["📦", "⚖️", "🧪", "🔄", "🛠️", "🔁", "🧪", "🛍️"]

# ==========================================
# MENÚ LATERAL: CONTROL DE ACCESO
# ==========================================
st.sidebar.markdown("# 🔐 Control de Acceso")
rol_seleccionado = st.sidebar.radio(
    "Selecciona tu perfil de visualización:",
    ["🎛️ Nivel Operativo (Mezcladores)", "📊 Nivel Ingeniero de Procesos"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Sincronizar / Actualizar Tablero"):
    st.rerun()

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
            
            estado_mezclador = memoria_global.datos[m]
            
            if estado_mezclador["etapa"] == 0:
                st.markdown("### 📝 Nueva Orden")
                with st.form(f"form_m{m}"):
                    orden = st.text_input("Número de Orden", key=f"input_o_m{m}", placeholder="Ej. ORD-2026")
                    lote = st.text_input("Número de Lote", key=f"input_l_m{m}", placeholder="Ej. L-1044431")
                    kg = st.number_input("Kilogramos (Kg)", key=f"input_k_m{m}", min_value=0, value=1000)
                    
                    btn_iniciar = st.form_submit_button("INICIAR PROCESO ➔")
                    if btn_iniciar and orden and lote:
                        memoria_global.datos[m]["orden"] = orden
                        memoria_global.datos[m]["lote"] = lote
                        memoria_global.datos[m]["kg"] = kg
                        memoria_global.datos[m]["etapa"] = 1
                        memoria_global.datos[m]["tiempos"] = {
                            "Inicio_Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "t_etapa": time.time()
                        }
                        st.rerun()
            else:
                ord_act = estado_mezclador["orden"]
                lot_act = estado_mezclador["lote"]
                kg_act = estado_mezclador["kg"]
                etapa_act = estado_mezclador["etapa"]
                
                st.info(f"**Orden:** {ord_act} | **Lote:** {lot_act} | **Kg:** {kg_act}")
                
                for idx_e, text_e in enumerate(nombres_etapas):
                    num_e = idx_e + 1
                    if etapa_act > num_e:
                        st.markdown(f"🟢 {iconos[idx_e]} {text_e} ✓")
                    elif etapa_act == num_e:
                        st.markdown(f"🟠 **[{iconos[idx_e]} {text_e}]** <-- En Proceso")
                    else:
                        st.markdown(f"⚪ {iconos[idx_e]} {text_e}")
                
                st.markdown("---")
                
                if etapa_act <= 8:
                    text_etapa_actual = nombres_etapas[etapa_act - 1]
                    if st.button(f"FINALIZAR {text_etapa_actual.upper()} ✓", key=f"btn_sig_m{m}", type="primary"):
                        ahora = time.time()
                        duracion_min = round((ahora - estado_mezclador["tiempos"]["t_etapa"]) / 60, 2)
                        
                        memoria_global.datos[m]["tiempos"][text_etapa_actual] = f"{duracion_min} min"
                        
                        if etapa_act == 8:
                            st.toast("Subiendo lote finalizado a la nube...")
                            nueva_fila = {
                                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                                "Mezclador": f"Mezclador {m}",
                                "Orden": ord_act,
                                "Lote": lot_act,
                                "Kg": int(kg_act),
                                "Inicio": memoria_global.datos[m]["tiempos"]["Inicio_Proceso"],
                                "Fin": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Pre_pesado": memoria_global.datos[m]["tiempos"].get("Pre-pesado", "0 min"),
                                "Pesado": memoria_global.datos[m]["tiempos"].get("Pesado", "0 min"),
                                "CC_1": memoria_global.datos[m]["tiempos"].get("Control de Calidad (C.C. 1)", "0 min"),
                                "Mezclado": memoria_global.datos[m]["tiempos"].get("Mezclado (20 min)", "0 min"),
                                "Recirc_Manual": memoria_global.datos[m]["tiempos"].get("Recirc. Manual", "0 min"),
                                "Recirc_Auto": memoria_global.datos[m]["tiempos"].get("Recirc. Auto (10 min)", "0 min"),
                                "CC_2": memoria_global.datos[m]["tiempos"].get("Control de Calidad (C.C. 2)", "0 min"),
                                "Envasado": memoria_global.datos[m]["tiempos"].get("Envasado", "0 min")
                            }
                            
                            try:
                                res = requests.post(WEBAPP_URL, json=nueva_fila)
                                if res.status_code == 200:
                                    st.success("¡Historial sincronizado!")
                                else:
                                    st.error("Error al conectar con Google Sheets.")
                            except Exception as err:
                                st.error(f"Falla de conexión: {err}")
                                
                            memoria_global.datos[m] = {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}}
                        else:
                            memoria_global.datos[m]["etapa"] += 1
                            memoria_global.datos[m]["tiempos"]["t_etapa"] = ahora
                        st.rerun()
                
                if st.button("❌ Cancelar Orden", key=f"btn_can_m{m}"):
                    memoria_global.datos[m] = {"etapa": 0, "orden": "", "lote": "", "kg": 0, "tiempos": {}}
                    st.rerun()

# ==========================================
# VISTA 2: INTERFAZ NIVEL INGENIERO DE PROCESOS
# ==========================================
else:
    st.title("📊 Panel de Análisis e Indicadores — Ingeniero de Procesos")
    st.markdown("---")
    
    st.subheader("⚠️ Órdenes Actualmente en Ejecución (Planta Activa)")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    f_cols = [f_col1, f_col2, f_col3]
    
    for m in [1, 2, 3]:
        est = memoria_global.datos[m]
        with f_cols[m-1]:
            if est["etapa"] > 0:
                st.warning(f"**Mezclador {m} — ACTIVO**")
                st.markdown(f"* **Orden:** {est['orden']}\n* **Lote:** {est['lote']}\n* **Carga:** {est['kg']} Kg")
                st.markdown(f"* ⚙️ **Etapa Actual:** {nombres_etapas[est['etapa']-1]}")
            else:
                st.success(f"**Mezclador {m} — DISPONIBLE**\n\nSin órdenes en este momento.")
                
    st.markdown("---")
    
    try:
        df_historial = pd.read_csv(LECTURA_URL)
        df_historial = df_historial.dropna(subset=["Orden"])
        error_carga = False
    except Exception:
        error_carga = True
        df_historial = pd.DataFrame([
            {"Fecha": "2026-07-11", "Mezclador": "Mezclador 1", "Orden": "ORD-P1", "Lote": "L-01", "Kg": 1000, "Pre_pesado": "12 min", "Pesado": "15 min", "CC_1": "8 min", "Mezclado": "20 min", "Recirc_Manual": "10 min", "Recirc_Auto": "10 min", "CC_2": "7 min", "Envasado": "15 min"}
        ])

    st.subheader("⏱️ Análisis Estadístico de Tiempos Promedio por Etapa")
    
    if not error_carga and len(df_historial) > 0:
        columnas_tiempos_bd = ["Pre_pesado", "Pesado", "CC_1", "Mezclado", "Recirc_Manual", "Recirc_Auto", "CC_2", "Envasado"]
        nombres_grafica = ["Pre-pesado", "Pesado", "C.C. 1", "Mezclado", "Recirc. Manual", "Recirc. Auto", "C.C. 2", "Envasado"]
        
        promedios = []
        for col_t in columnas_tiempos_bd:
            if col_t in df_historial.columns:
                valores_numericos = pd.to_numeric(df_historial[col_t].astype(str).str.replace(" min", "", regex=False), errors='coerce').fillna(0)
                promedios.append(round(valores_numericos.mean(), 2))
            else:
                promedios.append(0)
        
        df_estadisticas = pd.DataFrame({
            "Etapa del Proceso": nombres_grafica,
            "Minutos Promedio": promedios
        })
        
        st.bar_chart(data=df_estadisticas, x="Etapa del Proceso", y="Minutos Promedio")
        
        st.markdown("### 📈 Resumen Operativo")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric(label="Total de Órdenes Procesadas", value=len(df_historial))
        with k2:
            df_historial["Kg"] = pd.to_numeric(df_historial["Kg"], errors='coerce').fillna(0)
            st.metric(label="Volumen Total Controlado", value=f"{int(df_historial['Kg'].sum()):,} Kg")
        with k3:
            tiempo_total_promedio = sum(promedios)
            st.metric(label="Tiempo Ciclo Promedio Completo", value=f"{round(tiempo_total_promedio, 1)} min")
            
    else:
        st.info("💡 Las gráficas de tiempos se generarán cuando finalices la primera orden.")

    st.markdown("---")
    st.subheader("📋 Auditoría de Tiempos y Trazabilidad Completa")
    st.dataframe(df_historial)
