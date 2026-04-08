import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile
import base64
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- ESTILO VENEZUELA (TU DISEÑO ORIGINAL) ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.viewerBadge_container__1QSob {display: none !important;}
.stDeployButton {display: none !important;}
.stAppToolbar {visibility: hidden !important; display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
button[title="Manage app"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.stAppDeployButton {display: none !important;}

.stApp { background-color: #111827; color: #ffffff; }

.venezuela-header {
    text-align: center;
    padding: 60px 10px 40px 10px;
    background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
    border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
    margin-bottom: 30px;
    box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
}
.stars-arc {
    color: white;
    font-size: 2.5em;
    letter-spacing: 15px;
    font-weight: bold;
    text-shadow: 3px 3px 6px #000;
    margin-top: -15px;
}

input, textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: bold !important;
}

.footer-willian {
    background: #000;
    color: #fff;
    padding: 30px;
    text-align: center;
    border-top: 4px solid #ffcc00;
    margin-top: 50px;
}
.gold-text {
    background: linear-gradient(to bottom, #cf9710 22%, #ffcc00 24%, #f1c40f 26%, #fff700 27%, #ffcc00 40%, #e1aa33 78%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
    font-size: 1.2em;
}

.maps-button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #ea4335;
    color: white !important;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    margin-top: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
conn.commit()

# --- CABECERA ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

# --- NUEVO ACCESO DE ADMINISTRADOR (VISIBLE) ---
with st.expander("🔑 Acceso Administrativo"):
    admin_pass = st.text_input("Introduce la clave para gestionar negocios", type="password")
    if admin_pass == "Juan*316*":
        st.success("Modo Editor Activado")
        lista_categorias = ["Salud", "Farmacias", "Ópticas", "Ferretería", "Abastos", "Supermercados", "Electrodomésticos", "Telefonía", "Carnicerías", "Tienda de ropa", "Servicios"]
        
        accion = st.radio("Selecciona acción:", ["Añadir", "Borrar"])
        if accion == "Añadir":
            with st.form("admin_add"):
                n = st.text_input("Nombre del Negocio")
                cat = st.selectbox("Categoría", lista_categorias)
                ub = st.text_input("Ubicación")
                img = st.text_input("URL de la Imagen", value="https://via.placeholder.com/600x300")
                res = st.text_area("Tu Reseña")
                if st.form_submit_button("Guardar"):
                    c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, img, res, 5))
                    conn.commit()
                    st.rerun()
        elif accion == "Borrar":
            df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
            if not df_del.empty:
                target = st.selectbox("Negocio a eliminar:", df_del['nombre'].tolist())
                if st.button("Confirmar Eliminación"):
                    c.execute("DELETE FROM comercios WHERE nombre=?", (target,))
                    conn.commit()
                    st.rerun()

# --- BÚSQUEDA Y CONTENIDO ---
busq = st.text_input("🔍 ¿Qué buscas hoy en Santa Teresa?")
df = pd.read_sql_query("SELECT * FROM comercios", conn)

if not df.empty:
    categorias_db = df['categoria'].unique().tolist()
    tabs = st.tabs(categorias_db if categorias_db else ["General"])
    for i, cat_name in enumerate(categorias_db):
        with tabs[i]:
            filtrado = df[(df['categoria'] == cat_name) & (df['nombre'].str.contains(busq, case=False))]
            for idx, r in filtrado.iterrows():
                st.markdown(f"##### 🏢 **{r['nombre']}**")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.image(r['foto_url'], use_container_width=True)
                    st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                    query_maps = urllib.parse.quote(f"{r['nombre']} {r['ubicacion']} Santa Teresa del Tuy")
                    st.markdown(f'<a href="https://www.google.com/maps/search/{query_maps}" target="_blank" class="maps-button">📍 Ver en Google Maps</a>', unsafe_allow_html=True)
                with col2:
                    st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                st.markdown("---")

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class='footer-willian'>
    <span class='gold-text'>© {datetime.now().year} - Diseñada por Willian Almenar</span><br>
    Santa Teresa del Tuy 2026
</div>
""", unsafe_allow_html=True)
