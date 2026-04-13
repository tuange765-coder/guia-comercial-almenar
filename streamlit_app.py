import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from PIL import Image, ImageFile

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- CONEXIÓN A NEON (POSTGRESQL) ---
# Asegúrate de tener la URL en Settings > Secrets de Streamlit Cloud
conn = st.connection("postgresql", type="sql")

# --- CREACIÓN DE TABLAS (Sintaxis Postgres con SQLAlchemy text) ---
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

# --- ESTILO VENEZUELA (FONDO OSCURO Y ARCO TRICOLOR) ---
st.markdown("""
    <style>
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: bold;
    }
    .venezuela-header {
        text-align: center;
        padding: 60px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stars-arc { 
        color: white; font-size: 2.5em; letter-spacing: 15px; font-weight: bold; 
        text-shadow: 3px 3px 6px #000; margin-top: -15px;
    }
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; 
    }
    .stTextInput input, .stTextArea textarea { color: #000000 !important; }
    .share-link-box {
        background-color: #1f2937; border: 2px dashed #3b82f6;
        padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0;
    }
    .footer-willian { 
        background: #000; color: #fff; padding: 30px; text-align: center; 
        border-top: 4px solid #ffcc00; margin-top: 50px; 
    }
    .maps-btn {
        display: inline-block; padding: 10px 20px; background-color: #ea4335;
        color: white !important; text-decoration: none; border-radius: 5px;
        font-weight: bold; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        datos = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete y dulces frescos.", 5, "https://maps.google.com/?q=Panaderia+El+Gran+Paseo"),
            ("Farmatodo Santa Teresa", "Farmacias", "Carretera Nacional, entrada a la ciudad", "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400", "El punto de referencia para medicinas y artículos personales 24h.", 5, "https://maps.google.com/?q=Farmatodo+Santa+Teresa"),
            ("Pollos El Samán", "Otros", "Av. Bolívar, sector El Centro", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400", "Los mejores pollos a la brasa con el sabor típico de la zona.", 4, "https://maps.google.com/?q=Pollos+El+Saman"),
            ("Centro Médico Tuy", "Salud", "Calle principal, Casco Central", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400", "Atención médica integral y laboratorios con años de servicio.", 4, "https://maps.google.com/?q=Centro+Medico+Tuy"),
            ("Cordonería Almenar", "Otros", "Casco Central", "https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?w=400", "Servicio artesanal de reparación de calzado con años en el Tuy.", 5, "https://maps.google.com/?q=Santa+Teresa+del+Tuy")
        ]
        with conn.session as s:
            for d in datos:
                s.execute(text("""
                    INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) 
                    VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)
                """), {"nombre": d[0], "cat": d[1], "ub": d[2], "foto": d[3], "res": d[4], "est": d[5], "maps": d[6]})
            s.commit()

precargar_datos()

# --- PANEL ADMIN EN EL SIDEBAR ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave de Acceso", type="password")

if admin_pass == "Juan*316*":
    menu = st.sidebar.radio("Acción:", ["Ver/Buscar", "Añadir", "Modificar", "Borrar"])
    
    if menu == "Añadir":
        with st.sidebar.form("add_form"):
            n = st.text_input("Nombre del Negocio")
            cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
            ub = st.text_input("Ubicación")
            res = st.text_area("Reseña")
            est = st.slider("Estrellas", 1, 5, 5)
            url_m = st.text_input("URL Google Maps")
            if st.form_submit_button("Guardar Negocio"):
                with conn.session as s:
                    s.execute(text("""
                        INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) 
                        VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)
                    """), {"nombre": n, "cat": cat, "ub": ub, "foto": "https://via.placeholder.com/400", "res": res, "est": est, "maps": url_m})
                    s.commit()
                st.sidebar.success("¡Guardado en Neon!")
                st.rerun()

    elif menu == "Modificar":
        df_mod = conn.query("SELECT * FROM comercios", ttl=0)
        if not df_mod.empty:
            target = st.sidebar.selectbox("Elegir Negocio para Editar", df_mod['nombre'].tolist())
            row = df_mod[df_mod['nombre'] == target].iloc[0]
            with st.sidebar.form("edit_form"):
                new_n = st.text_input("Nombre", value=row['nombre'])
                new_res = st.text_area("Reseña", value=row['reseña_willian'])
                if st.form_submit_button("Actualizar"):
                    with conn.session as s:
                        s.execute(text("UPDATE comercios SET nombre=:nombre, reseña_willian=:res WHERE id=:id"), 
                                 {"nombre": new_n, "res": new_res, "id": int(row['id'])})
                        s.commit()
                    st.sidebar.success("¡Actualizado en Neon!")
                    st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

# --- SECCIÓN PARA COMPARTIR ---
link_app = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía Comercial de Santa Teresa! 🚀 Accede aquí: {link_app}"

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.1em;">📲 Compartir por WhatsApp</div></a>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div class="share-link-box"><small>🔗 Enlace Directo:</small><br><b style="color:#ffcc00;">{link_app}</b></div>', unsafe_allow_html=True)

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
