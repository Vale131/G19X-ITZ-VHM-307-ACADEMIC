import streamlit as st
import pandas as pd
import datetime
from modules.database import obtener_cartera_db, guardar_cartera_db

def render_modulo_cartera():
    """Renderiza el módulo de Cartera de Cuentas por Cobrar (CxC) y Pagar (CxP) con Aging Analysis."""
    st.subheader("📋 Gestión de Cartera Documentada (CxC / CxP)")
    st.caption("Edición interactiva con persistencia automática en SQLite y análisis de antigüedad de saldos (Aging).")

    df_cartera = obtener_cartera_db()

    # Si la base de datos está vacía, inicializar con estructura predeterminada
    if df_cartera.empty or not set(['fecha', 'monto', 'tipo', 'probabilidad', 'descripcion']).issubset(df_cartera.columns):
        df_cartera = pd.DataFrame([
            {"fecha": datetime.date.today() + datetime.timedelta(days=10), "monto": 120000.0, "tipo": "Cobro", "probabilidad": 0.95, "descripcion": "Factura Cliente Alfa"},
            {"fecha": datetime.date.today() - datetime.timedelta(days=15), "monto": 45000.0, "tipo": "Cobro", "probabilidad": 0.80, "descripcion": "Factura Cliente Beta (Vencida)"},
            {"fecha": datetime.date.today() + datetime.timedelta(days=5), "monto": 80000.0, "tipo": "Pago", "probabilidad": 1.00, "descripcion": "Proveedor Insumos X"},
            {"fecha": datetime.date.today() - datetime.timedelta(days=45), "monto": 30000.0, "tipo": "Cobro", "probabilidad": 0.60, "descripcion": "Factura Cliente Gamma (Crítica)"}
        ])

    # CONVERSIÓN CLAVE: Convertir la columna 'fecha' a tipo date para evitar la StreamlitAPIException
    df_cartera['fecha'] = pd.to_datetime(df_cartera['fecha']).dt.date

    col_editor, col_aging = st.columns([3.5, 2.5])

    with col_editor:
        st.markdown("##### ✏️ **Editor de Movimientos de Cartera**")
        df_editado = st.data_editor(
            df_cartera,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_cartera_db",
            column_config={
                "fecha": st.column_config.DateColumn("Fecha Compromiso", format="YYYY-MM-DD", required=True),
                "monto": st.column_config.NumberColumn("Monto ($ MXN)", format="$%.2f", min_value=0.0, required=True),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=["Cobro", "Pago"], required=True),
                "probabilidad": st.column_config.NumberColumn("Prob. Cobro (0-1)", format="%.2f", min_value=0.0, max_value=1.0, required=True),
                "descripcion": st.column_config.TextColumn("Descripción / Cliente", required=True)
            }
        )

        if st.button("💾 Guardar Cambios en Base de Datos", type="primary", use_container_width=True):
            guardar_cartera_db(df_editado)
            st.success("¡Base de datos SQLite actualizada correctamente!")
            st.rerun()

    with col_aging:
        st.markdown("##### ⏳ **Análisis de Antigüedad de Saldos (Aging)**")
        
        if not df_editado.empty:
            hoy = datetime.date.today()
            df_cxc = df_editado[df_editado['tipo'] == 'Cobro'].copy()
            
            if not df_cxc.empty:
                df_cxc['dias_vencido'] = df_cxc['fecha'].apply(lambda x: (hoy - x).days if isinstance(x, datetime.date) else 0)

                por_vencer = df_cxc[df_cxc['dias_vencido'] <= 0]['monto'].sum()
                vencido_1_30 = df_cxc[(df_cxc['dias_vencido'] > 0) & (df_cxc['dias_vencido'] <= 30)]['monto'].sum()
                vencido_31_60 = df_cxc[(df_cxc['dias_vencido'] > 30) & (df_cxc['dias_vencido'] <= 60)]['monto'].sum()
                vencido_mas_60 = df_cxc[df_cxc['dias_vencido'] > 60]['monto'].sum()

                df_aging_resumen = pd.DataFrame([
                    {"Tramo de Antigüedad": "🟢 Por Vencer", "Monto ($ MXN)": por_vencer},
                    {"Tramo de Antigüedad": "🟡 1 a 30 Días", "Monto ($ MXN)": vencido_1_30},
                    {"Tramo de Antigüedad": "🟠 31 a 60 Días", "Monto ($ MXN)": vencido_31_60},
                    {"Tramo de Antigüedad": "🔴 +60 Días (Crítico)", "Monto ($ MXN)": vencido_mas_60}
                ])

                st.dataframe(df_aging_resumen, use_container_width=True, hide_index=True)

                total_vencido = vencido_1_30 + vencido_31_60 + vencido_mas_60
                st.warning(f"⚠️ **Cartera Total Vencida:** ${total_vencido:,.2f} MXN")
            else:
                st.info("No hay registros de cuentas por cobrar (Cobros) en la cartera.")