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

[data-testid="stSidebar"] { background-color: #1f2937; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
color: #ffffff !important;
font-weight: bold !important;
font-size: 1.1em !important;
}

.sidebar-logo-oval {
display: block;
margin-left: auto;
margin-right: auto;
border-radius: 50% / 30%;
border: 3px solid #ffcc00;
object-fit: cover;
}

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
text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.comment-box {
background-color: #374151;
padding: 10px;
border-radius: 5px;
margin-bottom: 5px;
border-left: 5px solid #ffcc00;
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
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_url TEXT)')
conn.commit()

# --- CARGA INICIAL ---
c.execute("SELECT COUNT(*) FROM comercios")
if c.fetchone()[0] == 0:
    comercios_iniciales = [
        ("Farmatodo Santa Teresa", "Farmacias", "Av. Ayacucho", "https://images.unsplash.com/photo-1587854692152-cbe660fe0870", "Excelente atención 24 horas.", 5),
        ("Supermercado Unicasa", "Supermercados", "C.C. Paseo Tuy", "https://images.unsplash.com/photo-1542838132-92c53300491e", "Referencia para compras.", 5)
    ]
    for nom, cat, ubi, img, res, est in comercios_iniciales:
        c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (nom, cat, ubi, img, res, est))
    conn.commit()

c.execute("SELECT logo_url FROM ajustes WHERE id=1")
res_logo = c.fetchone()
current_logo = res_logo[0] if res_logo else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- PANEL ADMIN ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave de Acceso", type="password")

lista_categorias = [
    "Salud", "Farmacias", "Ópticas", "Ferretería", "Abastos",
    "Supermercados", "Electrodomésticos y línea blanca",
    "Telefonía y Tecnología", "Servicios de Fibra Óptica",
    "Carnicerías", "Charcuterías", "Comida rápida",
    "Tienda de ropa", "Perfumerías", "Entes gubernamentales",
    "Taxis y mototaxis", "Servicios"
]

if admin_pass == "Juan*316*":
    st.sidebar.markdown(f'<img src="{current_logo}" class="sidebar-logo-oval" width="200">', unsafe_allow_html=True)
    st.sidebar.warning("🔒 Datos vinculados a 'guia_santa_teresa.db'.")
    menu = st.sidebar.radio("Acción:", ["Ver/Buscar", "Añadir", "Modificar", "Borrar", "Ajustes Logo"])
    
    if menu == "Ajustes Logo":
        uploaded_logo = st.sidebar.file_uploader("Sube el logo", type=['png', 'jpg', 'jpeg'])
        if uploaded_logo and st.sidebar.button("Guardar Logo"):
            encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
            c.execute("INSERT OR REPLACE INTO ajustes (id, logo_url) VALUES (1, ?)", (f"data:image/png;base64,{encoded_logo}",))
            conn.commit()
            st.rerun()

    elif menu == "Añadir":
        with st.sidebar.form("add_form"):
            n = st.text_input("Nombre")
            cat = st.selectbox("Categoría", lista_categorias)
            ub = st.text_input("Ubicación")
            up_file = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
            url_img = st.text_input("O Link URL")
            res = st.text_area("Reseña")
            if st.form_submit_button("Guardar"):
                final_img = url_img if url_img else "https://via.placeholder.com/600x300"
                if up_file:
                    final_img = f"data:image/png;base64,{base64.b64encode(up_file.read()).decode()}"
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, final_img, res, 5))
                conn.commit()
                st.rerun()

    elif menu == "Borrar":
        df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_del.empty:
            target_del = st.sidebar.selectbox("Eliminar", df_del['nombre'].tolist())
            if st.sidebar.button("⚠️ CONFIRMAR"):
                c.execute("DELETE FROM comercios WHERE nombre=?", (target_del,))
                conn.commit()
                st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

st.markdown(f"""
<div class="share-link-box">
<p style="margin:0; font-weight:bold; color:#3b82f6;">🔗 Comparte nuestra Guía:</p>
<code style="color:#ffffff; background:none;">https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app</code>
</div>
""", unsafe_allow_html=True)

busq = st.text_input("🔍 ¿Qué buscas hoy?")
df = pd.read_sql_query("SELECT * FROM comercios", conn)

if not df.empty:
    tabs = st.tabs(lista_categorias)
    for i, categoria_nombre in enumerate(lista_categorias):
        with tabs[i]:
            filtrado = df[(df['categoria'] == categoria_nombre) & (df['nombre'].str.contains(busq, case=False))]
            if not filtrado.empty:
                for idx, r in filtrado.iterrows():
                    st.markdown(f"##### 🏢 **{r['nombre']}**")
                    with st.expander("Ver detalles y opiniones"):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.image(r['foto_url'], use_container_width=True)
                            st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                            query_maps = urllib.parse.quote(f"{r['nombre']} {r['ubicacion']} Santa Teresa del Tuy")
                            st.markdown(f"""
                            <a href="https://www.google.com/maps/search/?api=1&query={query_maps}" target="_blank" class="maps-button">
                            📍 Ver en Google Maps
                            </a>
                            """, unsafe_allow_html=True)
                            st.info(f"**Reseña:** {r['reseña_willian']}")
                        with col2:
                            st.subheader("💬 Opiniones")
                            c.execute("SELECT usuario, comentario, fecha FROM opiniones WHERE comercio_id=?", (r['id'],))
                            ops = c.fetchall()
                            for op in ops:
                                st.markdown(f"""<div class="comment-box"><strong>{op[0]}</strong> <small>({op[2]})</small><br>{op[1]}</div>""", unsafe_allow_html=True)
                            with st.form(key=f"f_{idx}_{categoria_nombre}"):
                                u = st.text_input("Nombre", key=f"user_{idx}")
                                m = st.text_area("Comentario", key=f"comm_{idx}")
                                if st.form_submit_button("Enviar"):
                                    c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, fecha) VALUES (?,?,?,?)", (r['id'], u, m, datetime.now().strftime("%d/%m/%Y")))
                                    conn.commit()
                                    st.rerun()
                    st.markdown("---")
            else:
                st.write(f"No hay registros en {categoria_nombre}.")

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class='footer-willian'>
📍 Santa Teresa del Tuy, Venezuela.<br>
<span class='gold-text'>
© {datetime.now().year} - Esta App fue creada y diseñada por Willian Almenar,<br>
Santa Teresa del Tuy 2026
</span>
</div>
""", unsafe_allow_html=True)
