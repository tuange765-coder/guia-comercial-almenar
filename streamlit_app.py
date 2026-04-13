import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- CONEXIÓN A NEON (POSTGRESQL) ---
# Usamos st.connection para que Streamlit se encargue de la comunicación con Neon
conn = st.connection("postgresql", type="sql")

# --- CREACIÓN DE TABLAS SI NO EXISTEN ---
with conn.session as s:
    s.execute("""
        CREATE TABLE IF NOT EXISTS comercios (
            id SERIAL PRIMARY KEY, 
            nombre TEXT, 
            categoria TEXT, 
            ubicacion TEXT, 
            foto_url TEXT, 
            reseña_willian TEXT, 
            estrellas_w INTEGER, 
            maps_url TEXT
        )
    """)
    s.execute("""
        CREATE TABLE IF NOT EXISTS opiniones (
            id SERIAL PRIMARY KEY, 
            comercio_id INTEGER, 
            usuario TEXT, 
            comentario TEXT, 
            estrellas_u INTEGER, 
            fecha TEXT
        )
    """)
    s.commit()

# --- ESTILO VENEZUELA (Tu diseño original intacto) ---
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
    }
    .stars-arc { color: white; font-size: 2.5em; letter-spacing: 15px; text-shadow: 3px 3px 6px #000; }
    input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; }
    .footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
    .maps-btn { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS REALES ---
def precargar_datos():
    df_check = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if df_check.iloc[0,0] == 0:
        datos = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete y dulces frescos.", 5, "http://maps.google.com/0"),
            # ... (Aquí irían los otros 19 que ya tienes)
            ("Cordonería Almenar", "Otros", "Casco Central", "https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?w=400", "Servicio artesanal de reparación de calzado con años en el Tuy.", 5, "http://maps.google.com/18")
        ]
        with conn.session as s:
            for d in datos:
                s.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :f, :r, :e, :m)", 
                          {"n":d[0], "c":d[1], "u":d[2], "f":d[3], "r":d[4], "e":d[5], "m":d[6]})
            s.commit()

precargar_datos()

# --- BUSCADOR Y CUERPO ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

busq = st.text_input("🔍 ¿Qué estás buscando hoy?", placeholder="Ej: Farmacia...")
df = conn.query("SELECT * FROM comercios", ttl=0)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            st.write(f"📍 **Ubicación:** {r['ubicacion']}")
            st.info(f"**Reseña:** {r['reseña_willian']}")
            if r['maps_url']:
                st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Google Maps</a>', unsafe_allow_html=True)

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
