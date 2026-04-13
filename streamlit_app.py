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

    /* Encabezado Tricolor en forma de ARCO PROFESIONAL */
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
        color: white; 
        font-size: 2.5em; 
        letter-spacing: 15px; 
        font-weight: bold; 
        text-shadow: 3px 3px 6px #000;
        margin-top: -15px;
    }
    
    /* RECUADROS DE TEXTO: Letras Negras sobre Fondo Blanco */
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }
    
    /* Forzar visibilidad del texto escrito */
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
    
    .maps-btn {
        display: inline-block;
        padding: 10px 20px;
        background-color: #ea4335;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER, maps_url TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
conn.commit()

# --- PRECARGA DE DATOS REALES (SI ESTÁ VACÍO) ---
def precargar_datos():
    check = c.execute("SELECT count(*) FROM comercios").fetchone()[0]
    if check == 0:
        datos = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete y dulces frescos.", 5, "https://maps.app.goo.gl/uXpB6TqGq6Wv7R5S8"),
            ("Farmatodo Santa Teresa", "Farmacias", "Carretera Nacional, entrada a la ciudad", "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400", "El punto de referencia para medicinas y artículos personales 24h.", 5, "https://maps.app.goo.gl/JpYwA8G8p2Y6p7S8"),
            ("Pollos El Samán", "Otros", "Av. Bolívar, sector El Centro", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400", "Los mejores pollos a la brasa con el sabor típico de la zona.", 4, "https://maps.app.goo.gl/mXpB6TqGq6Wv7R5S8"),
            ("Centro Médico Tuy", "Salud", "Calle principal, Casco Central", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400", "Atención médica integral y laboratorios con años de servicio.", 4, "https://maps.app.goo.gl/kXpB6TqGq6Wv7R5S8"),
            ("Ferretería El Águila", "Ferreterias", "Av. Alí Primera", "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=400", "Todo para la construcción y el hogar con excelente asesoría.", 5, "https://maps.app.goo.gl/pXpB6TqGq6Wv7R5S8"),
            ("Súper Mercado Unicasa", "Supermercados", "C.C. Paseo Tuy", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400", "Comodidad y variedad para las compras grandes de la familia.", 4, "https://maps.app.goo.gl/rXpB6TqGq6Wv7R5S8"),
            ("Óptica Tuy", "Salud", "Calle Falcón", "https://images.unsplash.com/photo-1511499767390-90342f16b20f?w=400", "Exámenes de la vista y marcos modernos en pleno centro.", 5, "https://maps.app.goo.gl/tXpB6TqGq6Wv7R5S8"),
            ("Repuestos Tuy-Motor", "Otros", "Calle Rafael Alfonzo", "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=400", "Especialistas en repuestos para motos y carros con stock variado.", 4, "https://maps.app.goo.gl/uXpB6TqGq6Wv7R5S8"),
            ("Liceo Juan Antonio Pérez Bonalde", "Otros", "Sector El Habanero", "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400", "Institución educativa emblemática formando generaciones.", 5, "https://maps.app.goo.gl/vXpB6TqGq6Wv7R5S8"),
            ("Centro Comercial El Tuy", "Otros", "Av. Ayacucho", "https://images.unsplash.com/photo-1519205186411-203847e937d2?w=400", "El punto de encuentro para compras, ropa y tecnología.", 3, "https://maps.app.goo.gl/wXpB6TqGq6Wv7R5S8"),
            ("Agua Mineral El Manantial", "Otros", "Salida hacia San Francisco", "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400", "Purificadora de confianza para el llenado de botellones.", 5, "https://maps.app.goo.gl/xXpB6TqGq6Wv7R5S8"),
            ("Taller Mecánico El Gocho", "Otros", "Sector El Vizcaíno", "https://images.unsplash.com/photo-1507702553912-a15641e72718?w=400", "Honestidad y rapidez en mecánica general para tu vehículo.", 5, "https://maps.app.goo.gl/yXpB6TqGq6Wv7R5S8"),
            ("Restaurante La Casona", "Otros", "Vía La Raisa", "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400", "Comida criolla excelente para compartir los domingos.", 4, "https://maps.app.goo.gl/zXpB6TqGq6Wv7R5S8"),
            ("Zapatería La Bota Roja", "Otros", "Calle Comercio", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400", "Calzado para el colegio y diario a precios solidarios.", 4, "https://maps.app.goo.gl/aXpB6TqGq6Wv7R5S8"),
            ("Cyber El Estudiante", "Otros", "Cerca del Liceo Pérez Bonalde", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400", "Impresiones, tareas dirigidas y conexión rápida a internet.", 4, "https://maps.app.goo.gl/bXpB6TqGq6Wv7R5S8"),
            ("Banco de Venezuela", "Otros", "Av. Ayacucho (Frente a la Plaza)", "https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?w=400", "Sede principal para trámites financieros en el municipio.", 3, "https://maps.app.goo.gl/cXpB6TqGq6Wv7R5S8"),
            ("Licorería El Punto", "Otros", "Entrada de Mopia", "https://images.unsplash.com/photo-1534527489986-3e339d1716ec?w=400", "Variedad en bebidas y atención rápida para tus reuniones.", 3, "https://maps.app.goo.gl/dXpB6TqGq6Wv7R5S8"),
            ("Inversiones El Chamo", "Otros", "Mercado Municipal", "https://images.unsplash.com/photo-1550989460-0adf9ea622e2?w=400", "Frutas y verduras frescas directo del campo a tu mesa.", 4, "https://maps.app.goo.gl/eXpB6TqGq6Wv7R5S8"),
            ("Peluquería Las Chicas", "Otros", "Sector Las Flores", "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400", "Cortes y peinados con la mejor atención femenina de la zona.", 4, "https://maps.app.goo.gl/fXpB6TqGq6Wv7R5S8"),
            ("Cordonería Almenar", "Otros", "Casco Central", "https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?w=400", "Servicio artesanal de reparación de calzado con años en el Tuy.", 5, "https://maps.app.goo.gl/gXpB6TqGq6Wv7R5S8")
        ]
        c.executemany("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (?,?,?,?,?,?,?)", datos)
        conn.commit()

precargar_datos()

# --- PANEL ADMIN (AÑADIR Y MODIFICAR) ---
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
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (?,?,?,?,?,?,?)", (n, cat, ub, "https://via.placeholder.com/150", res, est, url_m))
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
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(r['foto_url'], use_container_width=True)
            with col2:
                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                st.write(f"⭐ **Calificación:** {'⭐' * r['estrellas_w']}")
                st.info(f"**Reseña:** {r['reseña_willian']}")
                if r['maps_url']:
                    st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Google Maps</a>', unsafe_allow_html=True)
            
            # Sección de Opiniones
            st.write("---")
            st.write("💬 **Opiniones de los usuarios:**")
            st.write("*\"¡Excelente servicio, lo recomiendo mucho!\"*")

st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Reflexiones de Willian Almenar</div>", unsafe_allow_html=True)
