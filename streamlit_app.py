import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- ESTILO VENEZUELA (FONDO OSCURO Y ESTRELLAS) ---
st.markdown("""
    <style>
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; }
    .venezuela-header {
        text-align: center; padding: 30px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 15px; margin-bottom: 20px;
    }
    .stars-arc { color: white; font-size: 2em; letter-spacing: 12px; font-weight: bold; }
    .category-header { background-color: #3b82f6; color: white; padding: 10px; border-radius: 8px; border-left: 8px solid #ffcc00; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; font-weight: bold; }
    .footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
conn.commit()

# --- PANEL ADMIN (AÑADIR Y MODIFICAR) ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave", type="password")

if admin_pass == "Juan*316*":
    menu = st.sidebar.radio("Acción:", ["Ver/Buscar", "Añadir", "Modificar", "Borrar"])
    
    if menu == "Añadir":
        with st.sidebar.form("add_form"):
            n = st.text_input("Nombre del Negocio")
            cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
            ub = st.text_input("Ubicación")
            res = st.text_area("Reseña")
            est = st.slider("Estrellas", 1, 5, 5)
            if st.form_submit_button("Guardar"):
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, "https://via.placeholder.com/150", res, est))
                conn.commit()
                st.sidebar.success("¡Guardado!")
                st.rerun()

    elif menu == "Modificar":
        df_mod = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_mod.empty:
            target = st.sidebar.selectbox("Elegir Negocio", df_mod['nombre'].tolist())
            row = df_mod[df_mod['nombre'] == target].iloc[0]
            with st.sidebar.form("edit_form"):
                new_n = st.text_input("Nombre", value=row['nombre'])
                new_res = st.text_area("Reseña", value=row['reseña_willian'])
                if st.form_submit_button("Actualizar"):
                    c.execute("UPDATE comercios SET nombre=?, reseña_willian=? WHERE id=?", (new_n, new_res, int(row['id'])))
                    conn.commit()
                    st.sidebar.success("¡Actualizado!")
                    st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

# Compartir por WhatsApp
link_app = "https://guia-comercial-almenar.streamlit.app"
whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía de Santa Teresa! 🚀 {link_app}"
st.markdown(f'<a href="{whatsapp_url}" target="_blank"><div style="background-color:#25d366; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:bold;">📲 Compartir por WhatsApp</div></a>', unsafe_allow_html=True)

# Buscador
busq = st.text_input("🔍 ¿Qué buscas hoy?", placeholder="Ej: Farmacia, Repuestos...")
df = pd.read_sql_query("SELECT * FROM comercios", conn)
if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            st.write(f"📍 **Ubicación:** {r['ubicacion']}")
            st.write(f"⭐ **Calificación:** {'⭐' * r['estrellas_w']}")
            st.info(f"**Reseña:** {r['reseña_willian']}")

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
