import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from PIL import Image, ImageFile
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- CONEXIÓN A NEON (POSTGRESQL) ---
conn = st.connection("postgresql", type="sql")

# --- CREACIÓN DE TABLAS ---
with conn.session as s:
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS comercios (
            id SERIAL PRIMARY KEY, 
            nombre VARCHAR(255), 
            categoria VARCHAR(100), 
            ubicacion TEXT, 
            foto_url TEXT, 
            reseña_willian TEXT, 
            estrellas_w INTEGER, 
            maps_url TEXT
        )
    """))
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS opiniones (
            id SERIAL PRIMARY KEY, 
            comercio_id INTEGER, 
            usuario VARCHAR(100), 
            comentario TEXT, 
            estrellas_u INTEGER, 
            fecha VARCHAR(50)
        )
    """))
    s.commit()

# --- FUNCIONES DE APOYO ---
def imagen_a_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return f"data:image/png;base64,{base64.b64encode(bytes_data).decode()}"
    return None

# --- ESTILO VENEZUELA ---
st.markdown("""
    <style>
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; }
    .venezuela-header {
        text-align: center;
        padding: 40px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
    }
    .stars-arc { color: white; font-size: 2.5em; letter-spacing: 15px; font-weight: bold; text-shadow: 3px 3px 6px #000; margin-top: -15px;}
    input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    .footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
    .maps-btn { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }
    .admin-zone { background: #1f2937; padding: 25px; border: 3px solid #ffcc00; border-radius: 15px; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        datos_iniciales = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete y dulces frescos.", 5, "https://maps.google.com/?q=Panaderia+El+Gran+Paseo"),
            ("Farmatodo Santa Teresa", "Farmacias", "Carretera Nacional, entrada a la ciudad", "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400", "El punto de referencia para medicinas y artículos personales 24h.", 5, "https://maps.google.com/?q=Farmatodo+Santa+Teresa"),
            ("Pollos El Samán", "Otros", "Av. Bolívar, sector El Centro", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400", "Los mejores pollos a la brasa con el sabor típico de la zona.", 4, "https://maps.google.com/?q=Pollos+El+Saman"),
            ("Centro Médico Tuy", "Salud", "Calle principal, Casco Central", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400", "Atención médica integral y laboratorios con años de servicio.", 4, "https://maps.google.com/?q=Centro+Medico+Tuy"),
            ("Cordonería Almenar", "Otros", "Casco Central", "https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?w=400", "Servicio artesanal de reparación de calzado con años en el Tuy.", 5, "https://maps.google.com/?q=Santa+Teresa+del+Tuy")
        ]
        with conn.session as s:
            for d in datos_iniciales:
                s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)"),
                          {"nombre": d[0], "cat": d[1], "ub": d[2], "foto": d[3], "res": d[4], "est": d[5], "maps": d[6]})
            s.commit()

precargar_datos()

# --- INICIALIZAR LOGO ---
if 'logo_data' not in st.session_state:
    st.session_state.logo_data = None

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

# Mostrar Logo si existe
if st.session_state.logo_data:
    st.image(st.session_state.logo_data, width=150)

st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy")

# --- ACCESO DE ADMINISTRADOR ---
clave = st.text_input("🔑 Acceso de Autor (Willian):", type="password", placeholder="Escribe tu clave aquí para gestionar la guía...")

if clave == "Juan*316*":
    st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
    st.subheader("👨‍💻 Panel de Control Total")
    
    tabs = st.tabs(["🖼️ Logo", "🏢 Comercios", "💬 Opiniones", "⭐ Calificaciones"])
    
    # 1. Gestión de LOGO
    with tabs[0]:
        st.write("### Modificar Logo")
        file_logo = st.file_uploader("Cargar logo desde mi laptop", type=["png", "jpg", "jpeg"], key="logo_up")
        if st.button("Actualizar Logo"):
            if file_logo:
                st.session_state.logo_data = imagen_a_base64(file_logo)
                st.success("Logo actualizado.")
                st.rerun()

    # 2. Gestión de COMERCIOS
    with tabs[1]:
        accion = st.radio("Seleccione Acción:", ["Agregar", "Modificar", "Quitar"], horizontal=True)
        
        if accion == "Agregar":
            with st.form("form_add"):
                col1, col2 = st.columns(2)
                nombre = col1.text_input("Nombre del Negocio")
                cat = col2.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
                ubi = st.text_input("Ubicación")
                res = st.text_area("Tu Reseña")
                maps = st.text_input("URL Google Maps")
                est = st.slider("Calificación (Estrellas)", 1, 5, 5)
                foto_file = st.file_uploader("Subir Foto del Comercio", type=["png", "jpg", "jpeg"])
                
                if st.form_submit_button("Guardar Comercio"):
                    url_final = imagen_a_base64(foto_file) if foto_file else "https://via.placeholder.com/400"
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :f, :r, :e, :m)"),
                                  {"n": nombre, "c": cat, "u": ubi, "f": url_final, "r": res, "e": est, "m": maps})
                        s.commit()
                    st.success(f"{nombre} agregado con éxito.")
                    st.rerun()

        elif accion == "Modificar":
            df_edit = conn.query("SELECT * FROM comercios", ttl=0)
            target_edit = st.selectbox("Comercio a editar:", df_edit['nombre'].tolist())
            row = df_edit[df_edit['nombre'] == target_edit].iloc[0]
            
            with st.form("form_edit"):
                new_n = st.text_input("Nombre", value=row['nombre'])
                new_cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"], index=["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"].index(row['categoria']))
                new_ub = st.text_input("Ubicación", value=row['ubicacion'])
                new_res = st.text_area("Reseña", value=row['reseña_willian'])
                new_est = st.slider("Estrellas", 1, 5, int(row['estrellas_w']))
                new_m = st.text_input("URL Maps", value=row['maps_url'])
                if st.form_submit_button("Actualizar"):
                    with conn.session as s:
                        s.execute(text("UPDATE comercios SET nombre=:n, categoria=:c, ubicacion=:u, reseña_willian=:r, estrellas_w=:e, maps_url=:m WHERE id=:id"),
                                  {"n": new_n, "c": new_cat, "u": new_ub, "r": new_res, "e": new_est, "m": new_m, "id": int(row['id'])})
                        s.commit()
                    st.success("Cambios guardados.")
                    st.rerun()

        elif accion == "Quitar":
            df_del = conn.query("SELECT id, nombre FROM comercios", ttl=0)
            target_del = st.selectbox("Comercio a eliminar:", df_del['nombre'].tolist())
            if st.button("Confirmar Eliminación"):
                with conn.session as s:
                    s.execute(text("DELETE FROM comercios WHERE nombre=:n"), {"n": target_del})
                    s.commit()
                st.warning(f"Se ha eliminado {target_del}")
                st.rerun()

    # 3. Gestión de OPINIONES
    with tabs[2]:
        st.write("### Listado de Opiniones de Usuarios")
        df_opi = conn.query("SELECT * FROM opiniones", ttl=0)
        if not df_opi.empty:
            st.dataframe(df_opi)
            opi_id = st.number_input("ID de Opinión a quitar:", step=1)
            if st.button("Eliminar Opinión"):
                with conn.session as s:
                    s.execute(text("DELETE FROM opiniones WHERE id=:id"), {"id": opi_id})
                    s.commit()
                st.success("Opinión eliminada.")
                st.rerun()
        else:
            st.write("No hay opiniones aún.")

    # 4. Gestión de CALIFICACIONES (Resumen Técnico)
    with tabs[3]:
        st.write("### Promedio de Calificaciones por Negocio")
        resumen = conn.query("""
            SELECT c.nombre, c.estrellas_w as estrellas_autor, AVG(o.estrellas_u) as promedio_usuarios 
            FROM comercios c 
            LEFT JOIN opiniones o ON c.id = o.comercio_id 
            GROUP BY c.id, c.nombre, c.estrellas_w
        """, ttl=0)
        st.table(resumen)
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- BUSCADOR PÚBLICO ---
busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Ej: Panadería, Farmacia...")
df = conn.query("SELECT * FROM comercios", ttl=0)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            c1, c2 = st.columns([1, 2])
            with c1: 
                st.image(r['foto_url'], use_container_width=True)
            with c2:
                st.write(f"📍 {r['ubicacion']}")
                st.write(f"Calificación del Autor: {'⭐' * int(r['estrellas_w'])}")
                st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                
                if r['maps_url']:
                    st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Maps</a>', unsafe_allow_html=True)
                
                # SECCIÓN DE OPINIONES DE USUARIOS
                st.write("---")
                st.write("💬 **Opiniones de la comunidad:**")
                df_op = conn.query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']}", ttl=0)
                for _, op in df_op.iterrows():
                    st.caption(f"**{op['usuario']}** ({op['fecha']}): {op['comentario']} - {'⭐'*op['estrellas_u']}")
                
                with st.form(f"opi_form_{r['id']}"):
                    u_nom = st.text_input("Tu Nombre", key=f"un_{r['id']}")
                    u_com = st.text_area("Tu Opinión", key=f"uc_{r['id']}")
                    u_est = st.slider("Calificación", 1, 5, 5, key=f"ue_{r['id']}")
                    if st.form_submit_button("Enviar Opinión"):
                        with conn.session as s:
                            s.execute(text("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (:id, :u, :c, :e, :f)"),
                                      {"id": r['id'], "u": u_nom, "c": u_com, "e": u_est, "f": datetime.now().strftime("%d/%m/%Y")})
                            s.commit()
                        st.rerun()

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Miranda.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
