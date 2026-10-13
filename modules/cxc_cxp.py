import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import init_db, guardar_cartera_db, obtener_cartera_db

def calcular_aging(cartera_df):
    """Clasifica la cartera por cobrar en rangos de antigüedad (Aging)."""
    if cartera_df is None or cartera_df.empty:
        return None
    
    df = cartera_df.copy()
    hoy = datetime.today()
    df["dias_vencimiento"] = (pd.to_datetime(df["fecha"]) - hoy).dt.days
    
    cxc = df[df["tipo"].astype(str).str.upper() == "CXC"].copy()
    if cxc.empty:
        return None

    cxc["rango"] = "Por Vencer"
    cxc.loc[cxc["dias_vencimiento"] < 0, "rango"] = "1-30 días vencida"
    cxc.loc[cxc["dias_vencimiento"] < -30, "rango"] = "31-60 días vencida"
    cxc.loc[cxc["dias_vencimiento"] < -60, "rango"] = "+60 días (Crítica)"

    resumen = cxc.groupby("rango")["monto"].agg(["sum", "count"]).reset_index()
    resumen.columns = ["Rango de Antigüedad", "Monto Total ($ MXN)", "Número de Facturas"]
    return resumen

def render_modulo_cartera(cartera_input=None):
    """Renderiza el editor interactivo de cartera, sincronizado con SQLite."""
    st.subheader("📋 Gestión de Cartera Documentada (CxC / CxP)")
    st.caption("Los cambios realizados aquí se guardan de forma permanente en la base de datos local SQLite.")

    init_db()
    cartera_db = obtener_cartera_db()
    
    if not cartera_db.empty:
        df_base = cartera_db
    elif cartera_input is not None and not cartera_input.empty:
        df_base = cartera_input
    else:
        df_base = pd.DataFrame([
            {"fecha": "2026-10-25", "monto": 85000.0, "tipo": "CXC", "probabilidad": 0.90, "descripcion": "Factura Cliente Alpha"},
            {"fecha": "2026-10-31", "monto": 42000.0, "tipo": "CXP", "probabilidad": 1.00, "descripcion": "Pago Renta Oficinas"},
            {"fecha": "2026-11-05", "monto": 120000.0, "tipo": "CXC", "probabilidad": 0.75, "descripcion": "Licitación PluriOne"}
        ])

    st.markdown("##### ✏️ Tabla Editable de Facturas (Persistencia Activa)")
    df_editado = st.data_editor(
        df_base,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "monto": st.column_config.NumberColumn("Monto ($ MXN)", format="$%.2f"),
            "probabilidad": st.column_config.NumberColumn("Probabilidad (0.0 - 1.0)", min_value=0.0, max_value=1.0, step=0.05),
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["CXC", "CXP"])
        },
        key="editor_cartera"
    )

    if st.button("💾 Guardar Cambios en Base de Datos", type="primary"):
        guardar_cartera_db(df_editado)
        st.success("¡Datos guardados correctamente en la base de datos `flujo_efectivo.db`!")

    st.divider()

    st.markdown("##### ⏳ Matriz de Antigüedad de Saldos (Aging Analysis)")
    df_aging = calcular_aging(df_editado)
    if df_aging is not None:
        col_aging, col_stats = st.columns([1.5, 1])
        with col_aging:
            st.dataframe(df_aging, use_container_width=True)
        with col_stats:
            monto_cxc = df_editado[df_editado["tipo"] == "CXC"]["monto"].sum()
            monto_cxp = df_editado[df_editado["tipo"] == "CXP"]["monto"].sum()
            st.metric("Total Cuentas por Cobrar (CXC)", f"${monto_cxc:,.2f} MXN")
            st.metric("Total Cuentas por Pagar (CXP)", f"${monto_cxp:,.2f} MXN", delta=f"${monto_cxc - monto_cxp:,.2f} Neto", delta_color="normal")

    return df_editado