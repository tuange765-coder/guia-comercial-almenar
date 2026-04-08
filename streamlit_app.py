import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile
import base64
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- 2. ESTILO VENEZUELA (ARCO Y SEGURIDAD) ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp { background-color: #111827; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #1f2937; min-width: 300px; }
.venezuela-header {
    text-align: center;
    padding: 60px 10px 40px 10px;
    background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
    border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
    margin-bottom: 30px;
}
.stars-arc { color: white; font-size: 2.5em; letter-spacing: 15px; font-weight: bold; }
input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; }
.footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
.gold-text { color: #ffcc00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_url TEXT)')
conn.commit()

# --- 4. PANEL DE ADMINISTRADOR (EL CORAZÓN DEL CONTROL) ---
# Esta sección crea la barra lateral que NO veías
with st.sidebar:
    st.title("🛠️ Panel de Control")
    admin_pass = st.text_input("Introduce la Clave Maestra", type="password")
    
    lista_categorias = [
        "Salud", "Farmacias", "Ópticas", "Ferretería", "Abastos",
        "Supermercados", "Electrodomésticos y línea blanca",
        "Telefonía y Tecnología", "Servicios de Fibra Óptica",
        "Carnicerías", "Charcuterías", "Comida rápida",
        "Tienda de ropa", "Perfumerías", "Entes gubernamentales",
        "Taxis y mototaxis", "Servicios"
    ]

    if admin_pass == "Juan*316*":
        st.success("Acceso Autorizado")
        accion = st.radio("¿Qué deseas hacer?", ["Añadir Negocio", "Eliminar Negocio", "Ver Registros"])
        
        if accion == "Añadir Negocio":
            with st.form("nuevo_comercio"):
                n = st.text_input("Nombre")
                cat = st.selectbox("Categoría", lista_categorias)
                ub = st.text_input("Ubicación")
                res = st.text_area("Tu Reseña como Autor")
                if st.form_submit_button("Guardar"):
                    c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", 
                              (n, cat, ub, "https://via.placeholder.com/600x300", res, 5))
                    conn.commit()
                    st.success(f"¡{n} guardado con éxito!")
                    st.rerun()

        elif accion == "Eliminar Negocio":
            df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
            if not df_del.empty:
                opcion = st.selectbox("Selecciona para borrar:", df_del['nombre'].tolist())
                if st.button("Confirmar Borrado"):
                    c.execute("DELETE FROM comercios WHERE nombre=?", (opcion,))
                    conn.commit()
                    st.rerun()
    else:
        st.info("Ingresa la clave para gestionar los datos.")

# --- 5. CUERPO DE LA APP ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa del Tuy?")
df = pd.read_sql_query("SELECT * FROM comercios", conn)

if not df.empty:
    tabs = st.tabs(lista_categorias)
    for i, cat_name in enumerate(lista_categorias):
        with tabs[i]:
            filtrado = df[(df['categoria'] == cat_name) & (df['nombre'].str.contains(busq, case=False))]
            if not filtrado.empty:
                for idx, r in filtrado.iterrows():
                    st.subheader(f"🏢 {r['nombre']}")
                    st.write(f"📍 {r['ubicacion']}")
                    st.info(f"✍️ {r['reseña_willian']}")
                    st.markdown("---")
            else:
                st.write("No hay negocios registrados en esta categoría.")

# --- 6. PIE DE PÁGINA ---
st.markdown(f"""
<div class='footer-willian'>
    <span class='gold-text'>© {datetime.now().year} - Diseñada por Willian Almenar</span><br>
    Santa Teresa del Tuy, Venezuela.
</div>
""", unsafe_allow_html=True)
