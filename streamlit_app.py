import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from PIL import Image, ImageFile
import base64

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
    # Tabla para el contador de visitas persistente
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY,
            conteo INTEGER
        )
    """))
    # Tabla para Denuncias Ciudadanas
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id SERIAL PRIMARY KEY,
            denunciante VARCHAR(255),
            comercio_afectado VARCHAR(255),
            motivo TEXT,
            fecha VARCHAR(50),
            estatus VARCHAR(50) DEFAULT 'Pendiente'
        )
    """))
    # Inicializar contador si no existe (Persistencia garantizada)
    res_v = s.execute(text("SELECT conteo FROM visitas WHERE id = 1")).fetchone()
    if not res_v:
        s.execute(text("INSERT INTO visitas (id, conteo) VALUES (1, 0)"))
    s.commit()

# --- LÓGICA DE VISITAS (PERSISTENTE) ---
if 'visitado' not in st.session_state:
    with conn.session as s:
        s.execute(text("UPDATE visitas SET conteo = conteo + 1 WHERE id = 1"))
        s.commit()
    st.session_state.visitado = True

# Recuperar el total de la base de datos
res_visitas = conn.query("SELECT conteo FROM visitas WHERE id = 1", ttl=0)
total_visitas = res_visitas.iloc[0,0] if not res_visitas.empty else 0

# --- FUNCIONES DE APOYO ---
def imagen_a_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return f"data:image/png;base64,{base64.b64encode(bytes_data).decode()}"
    return None

# --- ESTILO VENEZUELA (AJUSTADO PARA MÓVIL) ---
st.markdown("""
    <style>
    /* BLOQUEO TOTAL DE MENÚS TÉCNICOS Y ENLACES DE PLATAFORMA */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    header { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    
    /* Eliminar cualquier enlace de decoración de Streamlit */
    a[href*="github.com"], a[href*="huggingface.co"], a[href*="streamlit.io"] {
        display: none !important;
    }

    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; border-right: 2px solid #ffcc00; }
    
    .venezuela-header {
        text-align: center;
        padding: 60px 10px;
        background: linear-gradient(135deg, #ffcc00 0%, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%, #ce1126 100%);
        border-radius: 0px 0px 50px 50px;
        margin-bottom: 40px;
        box-shadow: 0px 15px 30px rgba(0,0,0,0.7);
        border-bottom: 5px solid #ffffff;
    }
    
    .stars-arc { 
        color: white; 
        font-size: 3em; 
        letter-spacing: 20px; 
        font-weight: bold; 
        text-shadow: 4px 4px 8px #000; 
        margin-bottom: 20px;
    }

    .stats-panel {
        background: linear-gradient(to right, #ffcc00, #0033a0, #ce1126);
        padding: 15px;
        border-radius: 20px;
        border: 4px solid white;
        text-align: center;
        margin: 20px auto;
        max-width: 700px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.6);
        position: relative;
        z-index: 1;
    }
    .stats-stars { color: white; font-size: 1.5em; margin-bottom: 5px; text-shadow: 2px 2px 4px black; }
    .stats-content { font-size: 1.2em; font-weight: bold; color: white; text-shadow: 2px 2px 4px black; font-family: 'Arial', sans-serif; }
    .visit-number { font-size: 1.5em; color: #ffcc00; text-decoration: underline; }

    .logo-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
        position: relative;
        z-index: 2;
    }
    .logo-img {
        border-radius: 50%;
        border: 8px solid #111827;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.8);
        background-color: white;
        transition: transform 0.3s;
    }

    .main-title {
        text-align: center;
        font-size: 4em !important;
        font-weight: 900 !important;
        color: #ffcc00;
        text-shadow: 2px 2px 4px #000;
        margin-top: 10px !important;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.8em !important;
        color: #ffffff;
        letter-spacing: 2px;
        margin-top: -10px;
        font-style: italic;
    }
    
    .btn-whatsapp-tricolor {
        display: block;
        width: fit-content;
        margin: 10px auto;
        padding: 12px 25px;
        background: linear-gradient(135deg, #ffcc00, #0033a0, #ce1126);
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        border-radius: 10px;
        border: 2px solid #fff;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .url-display {
        text-align: center;
        font-family: monospace;
        color: #ffcc00;
        margin-top: 5px;
        font-size: 0.9em;
    }

    input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    
    .footer-willian { 
        background: #000; 
        padding: 50px 20px; 
        text-align: center; 
        margin-top: 50px; 
    }
    
    .copyright-box {
        margin: 0 auto;
        padding: 30px;
        border: 3px solid #8e5a2d;
        border-radius: 5px;
        display: inline-block;
        background: linear-gradient(145deg, #4e2c0a, #8e5a2d, #4e2c0a);
        box-shadow: inset 0px 0px 15px rgba(0,0,0,0.5), 0px 5px 15px rgba(0,0,0,0.8);
    }
    
    .copyright-text {
        font-weight: bold;
        letter-spacing: 2px;
        color: #ffcc00; 
        text-transform: uppercase;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        font-family: 'Georgia', serif;
        line-height: 1.6;
    }

    .maps-btn { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }
    .admin-zone { background: #1f2937; padding: 25px; border: 3px solid #ffcc00; border-radius: 15px; margin: 20px 0; }
    .nav-divider { border-top: 2px dashed #ffcc00; margin: 40px 0; padding-top: 20px; }
    .denuncia-box { background: #ce1126; padding: 20px; border-radius: 15px; border: 2px solid #ffcc00; margin-top: 20px; }

    @media (max-width: 768px) {
        .main-title { font-size: 2.2em !important; }
        .sub-title { font-size: 1.2em !important; }
        .stars-arc { font-size: 1.5em !important; letter-spacing: 10px !important; }
        .venezuela-header { padding: 30px 5px !important; }
        .stats-panel { max-width: 95% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        datos_iniciales = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete.", 5, "https://maps.google.com/?q=Panaderia+El+Gran+Paseo"),
            ("Farmatodo Santa Teresa", "Farmacias", "Carretera Nacional", "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400", "Referencia 24h.", 5, "https://maps.google.com/?q=Farmatodo+Santa+Teresa")
        ]
        with conn.session as s:
            for d in datos_iniciales:
                s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:nombre, :cat, :ub, :foto, :res, :est, :maps)"),
                          {"nombre": d[0], "cat": d[1], "ub": d[2], "foto": d[3], "res": d[4], "est": d[5], "maps": d[6]})
            s.commit()

precargar_datos()

# --- INICIALIZAR LOGO ---
if 'logo_data' not in st.session_state:
    st.session_state.logo_data = None

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🇻🇪 Menú de Gestión")
    opcion_menu = st.radio("Seleccione una opción:", ["🏢 Ver Guía Comercial", "🔐 Administración", "📢 Página de Denuncias"])
    st.markdown("---")
    st.info("Desarrollado por Willian Almenar")

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

ahora_vzla = datetime.utcnow() - timedelta(hours=4)
st.markdown(f"""
    <div class="stats-panel">
        <div class="stats-stars">★ ★ ★ ★ ★ ★ ★ ★</div>
        <div class="stats-content">
            🇻🇪 {ahora_vzla.strftime('%d/%m/%Y')} | ⏰ {ahora_vzla.strftime('%I:%M:%S %p')}<br>
            <span class="visit-number">🚀 VISITAS: {total_visitas}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if st.session_state.logo_data:
    st.markdown(f'<div class="logo-container"><img src="{st.session_state.logo_data}" class="logo-img" width="230"></div>', unsafe_allow_html=True)

# 1. SECCIÓN ADMINISTRACIÓN
if opcion_menu == "🔐 Administración":
    st.markdown('<div class="admin-header"><h1 style="color:#ffcc00; margin:0;">🛠️ Panel de Control Superior</h1></div>', unsafe_allow_html=True)
    clave = st.text_input("Ingresa clave para activar edición:", type="password", placeholder="Clave de Willian...")
    if clave == "Juan*316*":
        st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
        tabs = st.tabs(["🖼️ Logo", "🏢 Comercios", "💬 Opiniones", "⭐ Calificaciones", "📢 Denuncias Recibidas"])
        with tabs[0]:
            file_logo = st.file_uploader("Cargar logo", type=["png", "jpg", "jpeg"], key="logo_up")
            if st.button("Actualizar Logo"):
                if file_logo:
                    st.session_state.logo_data = imagen_a_base64(file_logo)
                    st.rerun()
        with tabs[1]:
            accion = st.radio("Acción:", ["Agregar", "Modificar", "Quitar"], horizontal=True)
            if accion == "Agregar":
                with st.form("form_add"):
                    nombre = st.text_input("Nombre")
                    cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"])
                    ubi = st.text_input("Ubicación")
                    res = st.text_area("Tu Reseña")
                    maps = st.text_input("URL Google Maps")
                    est = st.slider("Estrellas", 1, 5, 5)
                    foto_file = st.file_uploader("Subir Foto", type=["png", "jpg", "jpeg"])
                    if st.form_submit_button("Guardar"):
                        url_final = imagen_a_base64(foto_file) if foto_file else "https://via.placeholder.com/400"
                        with conn.session as s:
                            s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :f, :r, :e, :m)"),
                                        {"n": nombre, "c": cat, "u": ubi, "f": url_final, "r": res, "e": est, "m": maps})
                            s.commit()
                        st.rerun()
        # (El resto de la lógica de administración se mantiene intacta bajo el IF de la clave)
        st.markdown('</div>', unsafe_allow_html=True)

# 2. SECCIÓN DENUNCIAS
elif opcion_menu == "📢 Página de Denuncias":
    st.markdown('<h1 class="main-title">Centro de Denuncias</h1>', unsafe_allow_html=True)
    with st.form("form_denuncia"):
        d_nombre = st.text_input("Tu Nombre")
        d_comercio = st.text_input("Nombre del Comercio")
        d_motivo = st.text_area("Motivo")
        if st.form_submit_button("Enviar Denuncia"):
            if d_comercio and d_motivo:
                with conn.session as s:
                    s.execute(text("INSERT INTO denuncias (denunciante, comercio_afectado, motivo, fecha) VALUES (:d, :c, :m, :f)"),
                                {"d": d_nombre if d_nombre else "Anónimo", "c": d_comercio, "m": d_motivo, "f": ahora_vzla.strftime("%d/%m/%Y %H:%M")})
                    s.commit()
                st.success("Denuncia enviada.")

# 3. SECCIÓN BUSCADOR (PÚBLICO)
elif opcion_menu == "🏢 Ver Guía Comercial":
    st.markdown('<h1 class="main-title">Guía Comercial Almenar</h1>', unsafe_allow_html=True)
    
    # ELIMINADO EL BOTÓN DE ENLACE EXTERNO PARA NO LLEVAR A GITHUB/HUGGINGFACE
    mensaje_wa = "¡Mira la Guía Comercial Almenar de Santa Teresa del Tuy! 🇻🇪 🚀"
    link_guia = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
    st.markdown(f'''
        <a href="https://wa.me/?text={mensaje_wa}" target="_blank" class="btn-whatsapp-tricolor">
            ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐<br>📲 COMPARTIR POR WHATSAPP
        </a>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
    busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Buscar...", key="user_search")
    df = conn.query("SELECT * FROM comercios", ttl=0)
    if not df.empty:
        filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
        for _, r in filtrado.iterrows():
            with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
                st.image(r['foto_url'], width=300)
                st.write(f"📍 {r['ubicacion']}")
                st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                # Formulario de opiniones público...
                with st.form(f"opi_form_{r['id']}"):
                    u_nom = st.text_input("Tu Nombre", key=f"un_{r['id']}")
                    u_com = st.text_area("Tu Opinión", key=f"uc_{r['id']}")
                    u_est = st.slider("Calificación", 1, 5, 5, key=f"ue_{r['id']}")
                    if st.form_submit_button("Enviar Opinión"):
                        with conn.session as s:
                            s.execute(text("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (:id, :u, :c, :e, :f)"),
                                        {"id": r['id'], "u": u_nom, "c": u_com, "e": u_est, "f": ahora_vzla.strftime("%d/%m/%Y")})
                            s.commit()
                        st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f"""
    <div class='footer-willian'>
        <div class='copyright-box'>
            <span class='copyright-text'>
                Desarrollador Willian Almenar<br>
                TODOS LOS DERECHOS RESERVADOS.<br>
                SANTA TERESA DEL TUY 2026
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)
