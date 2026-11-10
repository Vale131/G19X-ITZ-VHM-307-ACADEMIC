import streamlit as st
import pandas as pd
from modules.database import (
    obtener_cartera_db, 
    insertar_compromiso_cartera, 
    actualizar_estatus_cartera
)

def render_modulo_cartera():
    st.subheader("Capital de Trabajo & Cartera Operativa (CxC / CxP)")
    st.caption("Gestión unificada de Cuentas por Cobrar y Pagar integradas al pronóstico ponderadas por su probabilidad.")

    df_cartera = obtener_cartera_db()

    tab_ver, tab_agregar = st.tabs(["📋 Cartera Registrada", "➕ Agregar Compromiso"])

    with tab_ver:
        if not df_cartera.empty:
            # Formatear la columna de probabilidad para mejor visualización en pantalla
            df_display = df_cartera.copy()
            if 'probabilidad' in df_display.columns:
                df_display['probabilidad_pct'] = (df_display['probabilidad'] * 100).round(1).astype(str) + '%'
            
            st.dataframe(df_display, width="stretch", hide_index=True)
            
            st.markdown("##### **Actualización de Estatus**")
            c_id, c_est, c_btn = st.columns([2, 2, 2])
            
            with c_id:
                ids_disponibles = df_cartera['id'].tolist() if 'id' in df_cartera.columns else []
                if ids_disponibles:
                    reg_id = st.selectbox("ID del Registro a actualizar", ids_disponibles, key="sb_id_cartera")
                else:
                    reg_id = st.number_input("ID del Registro a actualizar", min_value=1, step=1, key="num_id_cartera")
                    
            with c_est:
                nuevo_estatus = st.selectbox("Nuevo Estatus", ["Pendiente", "Pagado", "Cancelado"], key="sb_estatus_cartera")
                
            with c_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Actualizar Estatus", width="stretch"):
                    if reg_id in df_cartera['id'].values:
                        ok = actualizar_estatus_cartera(int(reg_id), nuevo_estatus)
                        if ok:
                            st.success(f"Registro #{reg_id} actualizado a '{nuevo_estatus}'.")
                            st.rerun()
                        else:
                            st.error("Ocurrió un error al actualizar la base de datos.")
                    else:
                        st.error("El ID seleccionado no existe en la cartera.")
        else:
            st.info("No hay registros en la cartera.")

    with tab_agregar:
        with st.form("form_nueva_cartera"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de Operación", ["CxC (Cuenta por Cobrar)", "CxP (Cuenta por Pagar)"])
                cliente_prov = st.text_input("Cliente / Proveedor / Descripción")
                monto = st.number_input("Monto ($)", min_value=0.01, step=100.0)
            with col2:
                fecha_venc = st.date_input("Fecha de Vencimiento")
                prob = st.slider("Probabilidad de Cobro/Pago (%)", min_value=10, max_value=100, value=90, step=5)
                estatus = st.selectbox("Estatus Inicial", ["Pendiente", "Pagado"])

            tipo_code = "CxC" if "Cobrar" in tipo else "CxP"
            btn_guardar = st.form_submit_button("Guardar en Cartera", width="stretch")

            if btn_guardar:
                if cliente_prov.strip():
                    prob_float = float(prob / 100.0)
                    ok = insertar_compromiso_cartera(
                        tipo=tipo_code,
                        cliente_proveedor=cliente_prov.strip(),
                        monto=float(monto),
                        fecha_vencimiento=str(fecha_venc),
                        probabilidad=prob_float,
                        estatus=estatus
                    )
                    if ok:
                        st.success("Compromiso registrado correctamente en la cartera.")
                        st.rerun()
                    else:
                        st.error("No se pudo guardar el registro en la base de datos.")
                else:
                    st.warning("Por favor especifica la descripción del cliente o proveedor.")