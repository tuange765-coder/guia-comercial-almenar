import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- ESTILO VENEZUELA (FONDO OSCURO Y ARCO TRICOLOR) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #111827; color: #ffffff; }
    
    /* Panel lateral */
    [data-testid="stSidebar"] { background-color: #1f2937; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: bold;
    }

    /* Encabezado Tricolor en forma de ARCO */
    .venezuela-header {
        text-align: center;
        padding: 60px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 20px 20px / 100% 100% 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .stars-arc { 
        color: white; 
        font-size: 2.5em; 
        letter-spacing: 15px; 
        font-weight: bold; 
        text-shadow: 2px 2px 5px #000;
        margin-top: -20px;
    }
    
    /* Categorías */
    .category-header { background-color: #3b82f6; color: white; padding: 10px; border-radius: 8px; border-left: 8px solid #ffcc00; }
    
    /* RECUADROS DE TEXTO */
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        color: #000000 !important;
    }

    .share-link-box {
        background-color: #1f2937;
        border: 2px dashed #3b82f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }

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

# --- SECCIÓN PARA COMPARTIR ---
link_app = "https://guia-comercial-almenar.streamlit.app"
whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía de Santa Teresa! 🚀 {link_app}"

col_share1, col_share2 = st.columns(2)

with col_share1:
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.1em;">📲 Compartir por WhatsApp</div></a>', unsafe_allow_html=True)

with col_share2:
    st.markdown(f"""
        <div class="share-link-box">
            <small>🔗 Enlace de la App:</small><br>
            <b style="color:#ffcc00;">{link_app}</b>
        </div>
    """, unsafe_allow_html=True)

# --- BUSCADOR ---
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
