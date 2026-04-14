import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from PIL import Image, ImageFile

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
    .admin-zone { background: #1f2937; padding: 20px; border: 3px solid #ffcc00; border-radius: 15px; margin: 20px 0; }
    .logo-container { text-align: center; margin-bottom: 10px; }
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

# --- CABECERA ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

# --- MODIFICACIÓN DEL LOGO ---
logo_file = st.sidebar.file_uploader("🖼️ Cambiar Logo (Desde tu laptop)", type=["png", "jpg", "jpeg"])
if logo_file:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(logo_file, width=150)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy")

# --- ACCESO DE ADMINISTRADOR ---
clave = st.sidebar.text_input("🔑 Clave de Autor:", type="password", placeholder="Clave para gestionar...")

if clave == "Juan*316*":
    st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
    st.subheader("👨‍💻 Panel de Control Total")
    
    tab_com, tab_opi = st.tabs(["🏬 Gestionar Comercios", "💬 Gestionar Opiniones"])
    
    with tab_com:
        admin_op = st.radio("Acción:", ["Agregar", "Modificar", "Quitar"], horizontal=True)
        
        if admin_op == "Agregar":
            with st.form("add_biz_full"):
                n = st.text_input("Nombre")
                c = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
                u = st.text_input("Ubicación")
                f = st.text_input("URL Foto (o dejar por defecto)", "https://via.placeholder.com/400")
                r = st.text_area("Reseña")
                e = st.slider("Calificación Willian", 1, 5, 5)
                m = st.text_input("URL Maps")
                if st.form_submit_button("✅ Guardar"):
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :f, :r, :e, :m)"),
                                  {"n": n, "c": c, "u": u, "f": f, "r": r, "e": e, "m": m})
                        s.commit()
                    st.success("Comercio agregado.")
                    st.rerun()

        elif admin_op == "Modificar":
            df_mod = conn.query("SELECT * FROM comercios", ttl=0)
            target_mod = st.selectbox("Comercio a modificar:", df_mod['nombre'].tolist())
            datos = df_mod[df_mod['nombre'] == target_mod].iloc[0]
            
            with st.form("mod_biz_form"):
                mn = st.text_input("Nombre", value=datos['nombre'])
                mc = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"], index=["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"].index(datos['categoria']))
                mu = st.text_input("Ubicación", value=datos['ubicacion'])
                mf = st.text_input("URL Foto", value=datos['foto_url'])
                mr = st.text_area("Reseña", value=datos['reseña_willian'])
                me = st.slider("Calificación", 1, 5, int(datos['estrellas_w']))
                mm = st.text_input("URL Maps", value=datos['maps_url'])
                if st.form_submit_button("💾 Actualizar"):
                    with conn.session as s:
                        s.execute(text("UPDATE comercios SET nombre=:n, categoria=:c, ubicacion=:u, foto_url=:f, reseña_willian=:r, estrellas_w=:e, maps_url=:m WHERE id=:id"),
                                  {"n": mn, "c": mc, "u": mu, "f": mf, "r": mr, "e": me, "m": mm, "id": int(datos['id'])})
                        s.commit()
                    st.success("Actualizado correctamente.")
                    st.rerun()

        elif admin_op == "Quitar":
            df_del = conn.query("SELECT id, nombre FROM comercios", ttl=0)
            target_del = st.selectbox("Comercio a quitar:", df_del['nombre'].tolist())
            if st.button("🚨 Eliminar Definitivamente"):
                id_t = df_del[df_del['nombre'] == target_del]['id'].values[0]
                with conn.session as s:
                    s.execute(text("DELETE FROM comercios WHERE id=:id"), {"id": int(id_t)})
                    s.commit()
                st.warning(f"Eliminado: {target_del}")
                st.rerun()

    with tab_opi:
        df_opi = conn.query("SELECT * FROM opiniones", ttl=0)
        if df_opi.empty:
            st.write("No hay opiniones registradas aún.")
        else:
            st.dataframe(df_opi)
            opi_del = st.number_input("ID de la opinión a quitar:", min_value=1, step=1)
            if st.button("Quitar Opinión"):
                with conn.session as s:
                    s.execute(text("DELETE FROM opiniones WHERE id=:id"), {"id": opi_del})
                    s.commit()
                st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- BUSCADOR PÚBLICO ---
busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Ej: Panadería...")
df = conn.query("SELECT * FROM comercios", ttl=0)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(r['foto_url'], use_container_width=True)
            with c2:
                st.write(f"📍 {r['ubicacion']}")
                st.write(f"Calificación: {'⭐' * int(r['estrellas_w'])}")
                st.info(f"{r['reseña_willian']}")
                
                # Botón de Maps
                if r['maps_url']:
                    st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Maps</a>', unsafe_allow_html=True)
                
                # --- SECCIÓN DE OPINIONES ---
                st.divider()
                st.write("💬 **Deja tu opinión:**")
                with st.form(f"opi_{r['id']}"):
                    u_name = st.text_input("Tu nombre", key=f"u_{r['id']}")
                    u_com = st.text_area("Comentario", key=f"c_{r['id']}")
                    u_est = st.select_slider("Califica", options=[1, 2, 3, 4, 5], key=f"s_{r['id']}")
                    if st.form_submit_button("Enviar"):
                        with conn.session as s:
                            s.execute(text("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (:id, :u, :com, :est, :f)"),
                                      {"id": r['id'], "u": u_name, "com": u_com, "est": u_est, "f": datetime.now().strftime("%d/%m/%Y")})
                            s.commit()
                        st.rerun()

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Miranda.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
