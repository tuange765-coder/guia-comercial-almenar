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
        padding: 60px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
    }
    .stars-arc { color: white; font-size: 2.5em; letter-spacing: 15px; font-weight: bold; text-shadow: 3px 3px 6px #000; margin-top: -15px;}
    input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    .footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
    .maps-btn { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }
    .admin-zone { background-color: #1f2937; padding: 25px; border-radius: 15px; border: 2px solid #ffcc00; margin-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS (INTEGRADA) ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    cuenta_actual = res.iloc[0,0]

    # Paso 1: Cargar los primeros 5 si la tabla está totalmente vacía
    if cuenta_actual == 0:
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
        cuenta_actual = 5

    # Paso 2: Cargar el resto si solo hay 5 o menos
    if cuenta_actual <= 5:
        datos_faltantes = [
            ("Licorería El Recreo", "Otros", "Sector El Rincón", "https://images.unsplash.com/photo-1569937756447-1d44f657dc69?w=400", "Gran variedad de bebidas y atención rápida.", 4, "https://maps.google.com"),
            ("Supermercado Unicasa", "Supermercados", "C.C. Paseo Tuy", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400", "Víveres frescos y excelente atención en el centro comercial.", 5, "https://maps.google.com"),
            # --- AGREGA AQUÍ LOS OTROS 13 NEGOCIOS SIGUIENDO EL MISMO FORMATO ---
            ("Repuestos El Tuy", "Otros", "Av. Principal", "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=400", "Todo para su vehículo con asesoría experta.", 5, "https://maps.google.com"),
        ]
        with conn.session as s:
            for d in datos_faltantes:
                s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)"),
                          {"nombre": d[0], "cat": d[1], "ub": d[2], "foto": d[3], "res": d[4], "est": d[5], "maps": d[6]})
            s.commit()

precargar_datos()

# --- PANEL ADMIN (SIDEBAR) ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave de Acceso", type="password")

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

# --- NUEVO PANEL DE ADMINISTRADOR SUPERIOR ---
if admin_pass == "Juan*316*":
    st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
    st.subheader("👨‍💻 Panel de Gestión de Willian")
    
    op_admin = st.radio("Seleccione tarea:", ["Añadir Nuevo Comercio", "Modificar Existente", "Eliminar Registro"], horizontal=True)
    
    if op_admin == "Añadir Nuevo Comercio":
        with st.form("top_add_form"):
            col1, col2 = st.columns(2)
            n_name = col1.text_input("Nombre del Comercio")
            n_cat = col2.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
            n_ub = st.text_input("Ubicación")
            n_res = st.text_area("Tu Reseña")
            n_url_map = st.text_input("URL Google Maps")
            n_est = st.slider("Estrellas", 1, 5, 5)
            if st.form_submit_button("✅ Guardar en Neon"):
                with conn.session as s:
                    s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)"),
                              {"nombre": n_name, "cat": n_cat, "ub": n_ub, "foto": "https://via.placeholder.com/400", "res": n_res, "est": n_est, "maps": n_url_map})
                    s.commit()
                st.success("¡Comercio guardado exitosamente!")
                st.rerun()

    elif op_admin == "Eliminar Registro":
        df_del = conn.query("SELECT id, nombre FROM comercios", ttl=0)
        target_del = st.selectbox("Comercio a eliminar:", df_del['nombre'].tolist())
        if st.button("🚨 Confirmar Eliminación"):
            id_to_del = df_del[df_del['nombre'] == target_del]['id'].values[0]
            with conn.session as s:
                s.execute(text("DELETE FROM comercios WHERE id=:id"), {"id": int(id_to_del)})
                s.commit()
            st.warning(f"Se ha eliminado {target_del}")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- BUSCADOR ---
busq = st.text_input("🔍 ¿Qué estás buscando hoy?", placeholder="Ej: Farmacia, Repuestos...")
df = conn.query("SELECT * FROM comercios", ttl=0)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(r['foto_url'], use_container_width=True)
            with col2:
                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                st.write(f"⭐ **Calificación:** {'⭐' * int(r['estrellas_w'])}")
                st.info(f"**Reseña:** {r['reseña_willian']}")
                if r['maps_url']:
                    st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Google Maps</a>', unsafe_allow_html=True)

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
