import streamlit as st
import pandas as pd
from modules.database import obtener_cartera_db, guardar_cartera_db

def render_modulo_cartera():
    st.subheader("Capital de Trabajo & Cartera Operativa (CxC / CxP)")
    st.caption("Gestión unificada de Cuentas por Cobrar y Pagar integradas al pronóstico ponderadas por su probabilidad.")

    df_cartera = obtener_cartera_db()

    tab_ver, tab_agregar = st.tabs(["📋 Cartera Registrada", "➕ Agregar Compromiso"])

    with tab_ver:
        if not df_cartera.empty:
            st.dataframe(df_cartera, use_container_width=True, hide_index=True)
            
            c_id, c_est, c_btn = st.columns([2, 2, 2])
            with c_id:
                reg_id = st.number_input("ID del Registro a actualizar", min_value=1, step=1)
            with c_est:
                nuevo_estatus = st.selectbox("Nuevo Estatus", ["Pendiente", "Pagado", "Cancelado"])
            with c_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Actualizar Estatus"):
                    if reg_id in df_cartera['id'].values:
                        df_cartera.loc[df_cartera['id'] == reg_id, 'estatus'] = nuevo_estatus
                        guardar_cartera_db(df_cartera)
                        st.success(f"Registro #{reg_id} actualizado a '{nuevo_estatus}'.")
                        st.rerun()
                    else:
                        st.error("ID no encontrado.")
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
            btn_guardar = st.form_submit_button("Guardar en Cartera")

            if btn_guardar:
                if cliente_prov.strip():
                    nuevo_reg = pd.DataFrame([{
                        'tipo': tipo_code,
                        'cliente_proveedor': cliente_prov.strip(),
                        'monto': float(monto),
                        'fecha_vencimiento': str(fecha_venc),
                        'probabilidad': float(prob / 100.0),
                        'estatus': estatus
                    }])
                    
                    df_unido = pd.concat([df_cartera, nuevo_reg], ignore_index=True)
                    if 'id' in df_unido.columns:
                        df_unido['id'] = range(1, len(df_unido) + 1)
                    
                    guardar_cartera_db(df_unido)
                    st.success("Compromiso registrado correctamente en la cartera.")
                    st.rerun()
                else:
                    st.warning("Por favor especifica la descripción.")