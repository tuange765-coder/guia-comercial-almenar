import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar",
layout="wide", page_icon="🚀")
 
# --- ESTILO VENEZUELA
# (FONDO OSCURO Y ARCO TRICOLOR) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color:
#111827; color: #ffffff; }
    
    /* Panel lateral */
    [data-testid="stSidebar"] { background-color: #1f2937; }
    [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"]
label {
        color: #ffffff !important;
        font-weight: bold;
    }
 
    /* Encabezado Tricolor en forma de ARCO
PROFESIONAL */
    .venezuela-header {
        text-align: center;
        padding: 60px 10px 40px
10px;
        background:
linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
     border-radius: 100% 100% 25px 25px / 120%
120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px
rgba(0,0,0,0.6);
        border: 1px solid
rgba(255,255,255,0.1);
    }
    .stars-arc { 
        color: white; 
        font-size: 2.5em; 
        letter-spacing: 15px; 
        font-weight: bold; 
        text-shadow: 3px 3px 6px
#000;
        margin-top: -15px;
    }
    
    /* RECUADROS DE TEXTO: Letras Negras sobre
Fondo Blanco */
    input, textarea,
[data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Forzar visibilidad del texto escrito */
    .stTextInput input, .stTextArea
textarea {
        color: #000000 !important;
    }
 
    .share-link-box {
        background-color: #1f2937;
        border: 2px dashed
#3b82f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
 
    .footer-willian { background:
#000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid
#ffcc00; margin-top: 50px; }

    .logo-container { text-align: center; margin-top: -80px; margin-bottom: 20px; }
    .app-logo { border-radius: 50%; border: 3px solid #ffcc00; background: white; }
    </style>
    """,
unsafe_allow_html=True)
 
# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
# Nueva tabla para ajustes como el logo
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_data TEXT)')
conn.commit()

# --- CARGAR LOGO PERSONALIZADO ---
c.execute("SELECT logo_data FROM ajustes WHERE id=1")
res_logo = c.fetchone()
current_logo = res_logo[0] if res_logo else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
 
# --- PANEL ADMIN (AÑADIR Y MODIFICAR) ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave de Acceso",
type="password")
 
if admin_pass == "Juan*316*":
    menu = st.sidebar.radio("Acción:", ["Ver/Buscar", "Añadir", "Modificar", "Borrar", "Gestionar Comentarios", "Personalizar Logo"])
    
    if menu == "Añadir":
        with st.sidebar.form("add_form"):
            n = st.text_input("Nombre del Negocio")
            cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
            ub = st.text_input("Ubicación")
            # Opción de subir foto desde PC
            foto_file = st.file_uploader("Subir foto del negocio", type=['png', 'jpg', 'jpeg'])
            res = st.text_area("Reseña")
            est = st.slider("Estrellas", 1, 5, 5)
            if st.form_submit_button("Guardar Negocio"):
                img_str = "https://via.placeholder.com/150"
                if foto_file:
                    img_str = f"data:image/png;base64,{base64.b64encode(foto_file.read()).decode()}"
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, img_str, res, est))
                conn.commit()
                st.sidebar.success("¡Guardado!")
                st.rerun()
 
    elif menu == "Modificar":
        df_mod = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_mod.empty:
            target = st.sidebar.selectbox("Elegir Negocio para Editar", df_mod['nombre'].tolist())
            row = df_mod[df_mod['nombre'] == target].iloc[0]
            with st.sidebar.form("edit_form"):
                new_n = st.text_input("Nombre", value=row['nombre'])
                new_cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"], index=["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"].index(row['categoria']))
                new_ub = st.text_input("Ubicación", value=row['ubicacion'])
                new_res = st.text_area("Reseña", value=row['reseña_willian'])
                new_foto = st.file_uploader("Cambiar foto (Opcional)", type=['png', 'jpg', 'jpeg'])
                if st.form_submit_button("Actualizar"):
                    if new_foto:
                        new_img_str = f"data:image/png;base64,{base64.b64encode(new_foto.read()).decode()}"
                        c.execute("UPDATE comercios SET nombre=?, categoria=?, ubicacion=?, reseña_willian=?, foto_url=? WHERE id=?", (new_n, new_cat, new_ub, new_res, new_img_str, int(row['id'])))
                    else:
                        c.execute("UPDATE comercios SET nombre=?, categoria=?, ubicacion=?, reseña_willian=? WHERE id=?", (new_n, new_cat, new_ub, new_res, int(row['id'])))
                    conn.commit()
                    st.sidebar.success("¡Actualizado!")
                    st.rerun()

    elif menu == "Borrar":
        df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_del.empty:
            target_del = st.sidebar.selectbox("Elegir Negocio para ELIMINAR", df_del['nombre'].tolist())
            if st.sidebar.button("🔴 ELIMINAR PERMANENTEMENTE"):
                c.execute("DELETE FROM comercios WHERE nombre=?", (target_del,))
                conn.commit()
                st.sidebar.warning(f"{target_del} eliminado.")
                st.rerun()

    elif menu == "Gestionar Comentarios":
        st.sidebar.markdown("### Borrar Comentarios")
        df_ops = pd.read_sql_query("SELECT opiniones.id, comercios.nombre, opiniones.usuario, opiniones.comentario FROM opiniones JOIN comercios ON opiniones.comercio_id = comercios.id", conn)
        if not df_ops.empty:
            op_id = st.sidebar.selectbox("Selecciona comentario a eliminar", df_ops['id'].tolist(), format_func=lambda x: f"De: {df_ops[df_ops['id']==x]['usuario'].values[0]}")
            if st.sidebar.button("Eliminar Comentario"):
                c.execute("DELETE FROM opiniones WHERE id=?", (op_id,))
                conn.commit()
                st.rerun()

    elif menu == "Personalizar Logo":
        st.sidebar.markdown("### Cambiar Logo de la App")
        new_logo_file = st.sidebar.file_uploader("Sube tu logo desde la PC", type=['png', 'jpg', 'jpeg'])
        if new_logo_file and st.sidebar.button("Aplicar nuevo logo"):
            encoded_logo = base64.b64encode(new_logo_file.read()).decode()
            logo_data = f"data:image/png;base64,{encoded_logo}"
            c.execute("INSERT OR REPLACE INTO ajustes (id, logo_data) VALUES (1, ?)", (logo_data,))
            conn.commit()
            st.rerun()
 
# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>',
unsafe_allow_html=True)
# Mostrar Logo
st.markdown(f'<div class="logo-container"><img src="{current_logo}" class="app-logo" width="150"></div>', unsafe_allow_html=True)

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
df = pd.read_sql_query("SELECT * FROM comercios", conn)
 
if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                st.image(r['foto_url'])
            with col_txt:
                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                st.write(f"⭐ **Calificación:** {'⭐' * r['estrellas_w']}")
                st.info(f"**Reseña:** {r['reseña_willian']}")
            
            # --- SECCIÓN DE COMENTARIOS ---
            st.markdown("---")
            st.write("💬 **Opiniones de la comunidad:**")
            with st.form(f"comentario_{r['id']}"):
                u_name = st.text_input("Tu Nombre", key=f"user_{r['id']}")
                u_msg = st.text_area("Deja tu comentario", key=f"msg_{r['id']}")
                if st.form_submit_button("Publicar Comentario"):
                    if u_name and u_msg:
                        c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, fecha) VALUES (?,?,?,?)", (r['id'], u_name, u_msg, datetime.now().strftime("%d/%m/%Y")))
                        conn.commit()
                        st.rerun()
            
            # Mostrar comentarios existentes
            ops = pd.read_sql_query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']} ORDER BY id DESC", conn)
            for _, op in ops.iterrows():
                st.markdown(f"**{op['usuario']}** ({op['fecha']}): {op['comentario']}")
 
st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
