import streamlit as st
import sqlite3
import pandas as pd
import os
import shutil  # Nueva librería para copiar el archivo
from datetime import datetime
import base64
import urllib.parse

# --- FUNCIÓN DE RESPALDO AUTOMÁTICO ---
def crear_respaldo():
    if not os.path.exists('respaldos'):
        os.makedirs('respaldos')
    
    # Nombre del archivo con fecha y hora: Ej. respaldo_2026-04-09_18-30.db
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_respaldo = f"respaldos/respaldo_guia_{timestamp}.db"
    
    try:
        shutil.copy2('guia_santa_teresa.db', nombre_respaldo)
        return nombre_respaldo
    except Exception as e:
        return None

# --- FUNCIÓN PARA MÚSICA DE FONDO ---
def autoplay_music(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio id="audio-player" loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <div id="music-control" onclick="playAudio()" style="text-align:center; padding:15px; background:#1f2937; border:2px solid #ffcc00; border-radius:15px; cursor:pointer; margin-bottom:20px; transition: 0.3s;">
                    <p style="color:#ffcc00; margin:0; font-weight:bold; font-size:1.1em;">🎵 ACTIVAR MÚSICA AMBIENTAL 🎵</p>
                    <small style="color:white;">(Haz clic aquí para iniciar el sonido)</small>
                </div>
                <script>
                    var audio = document.getElementById("audio-player");
                    audio.volume = 0.3;
                    
                    function playAudio() {{
                        audio.play().then(() => {{
                            document.getElementById("music-control").style.display = "none";
                        }}).catch(function(error) {{
                            console.log("Error al reproducir:", error);
                        }});
                    }}
                    document.body.addEventListener('click', playAudio, {{ once: true }});
                </script>
                """
            st.markdown(md, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- ACTIVAR MÚSICA ---
autoplay_music("música/musica1.mp3")

# --- ESTILO VENEZUELA ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp { background-color: #111827; color: #ffffff; }
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #ffffff !important; }
button[data-baseweb="tab"] p { color: #ffcc00 !important; font-weight: bold !important; font-size: 1.1em !important; }
.venezuela-header {
    text-align: center;
    padding: 60px 10px 40px 10px;
    background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
    border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
    margin-bottom: 30px;
    box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
}
.stars-arc { color: white; font-size: 2.5em; letter-spacing: 15px; font-weight: bold; text-shadow: 3px 3px 6px #000; margin-top: -15px; }
.logo-container { text-align: center; margin-top: -50px; margin-bottom: 20px; }
.app-logo { border-radius: 50% / 30%; border: 3px solid #ffcc00; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
input, textarea, [data-baseweb="select"] { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
.footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
.gold-text { background: linear-gradient(to bottom, #cf9710 22%, #ffcc00 24%, #f1c40f 26%, #fff700 27%, #ffcc00 40%, #e1aa33 78%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; font-size: 1.2em; }
.maps-button { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; text-align: center; }
.copy-button { display: inline-block; padding: 12px 25px; background: linear-gradient(to right, #ffcc00, #0033a0, #ce1126); color: white !important; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; margin: 15px 0; transition: 0.3s; box-shadow: 0px 4px 15px rgba(0,0,0,0.4); }
.copy-button:hover { transform: scale(1.05); box-shadow: 0px 6px 20px rgba(255, 204, 0, 0.4); }
.visitas-badge { text-align: center; background: rgba(255, 204, 0, 0.1); border: 1px solid #ffcc00; border-radius: 10px; padding: 10px; margin-bottom: 20px; }
.opinion-card { background: #1f2937; padding: 10px; border-left: 4px solid #ffcc00; margin-bottom: 10px; border-radius: 0 10px 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS LOCAL (SQLITE) ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False, isolation_level=None)
c = conn.cursor()
c.execute('PRAGMA journal_mode=WAL;') 
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_url TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS visitas (fecha TEXT PRIMARY KEY, conteo INTEGER)')

# --- DATOS REALES DE SANTA TERESA DEL TUY ---
def precargar_datos():
    c.execute("SELECT COUNT(*) FROM comercios")
    if c.fetchone()[0] == 0:
        comercios_iniciales = [
            ("Farmatodo Santa Teresa", "Farmacias", "Av. Ayacucho", "https://via.placeholder.com/600x300?text=Farmatodo", "Excelente atención y variedad de productos.", 5),
            ("Supermercado El Dorado", "Supermercados", "Calle Comercio", "https://via.placeholder.com/600x300?text=El+Dorado", "Precios competitivos en la zona.", 4),
            ("Óptica Santa Teresa", "Ópticas", "C.C. Paseo Tuy", "https://via.placeholder.com/600x300?text=Optica", "Profesionalismo en exámenes visuales.", 5),
            ("Ferretería El Ancla", "Ferreterías", "Sector El Rincón", "https://via.placeholder.com/600x300?text=El+Ancla", "Todo lo que necesitas para el hogar.", 4),
            ("Laboratorio Clínico Tuy", "Laboratorios", "Av. Alí Primera", "https://via.placeholder.com/600x300?text=Laboratorio", "Resultados rápidos y confiables.", 5),
            ("Panadería La Mansión", "Panadería", "Casco Central", "https://via.placeholder.com/600x300?text=Panaderia", "Los mejores panes y dulces del Tuy.", 5),
            ("Carnicería El Torazo", "Carnicerías", "Mercado Municipal", "https://via.placeholder.com/600x300?text=El+Torazo", "Cortes frescos y de calidad.", 4),
            ("Abasto Los Compadres", "Abastos", "Urb. Las Flores", "https://via.placeholder.com/600x300?text=Los+Compadres", "Atención familiar y cercana.", 4),
            ("Repuestos El Motor", "Repuestos", "Sector Dos Lagunas", "https://via.placeholder.com/600x300?text=Repuestos", "Variedad en piezas para vehículos.", 4),
            ("Charcutería El Quesote", "Charcuterías", "Av. Independencia", "https://via.placeholder.com/600x300?text=El+Quesote", "Quesos frescos de la región.", 5),
            ("Multiservicios Fibra Tuy", "Fibra Óptica", "C.C. El Tuy", "https://via.placeholder.com/600x300?text=Fibra+Tuy", "Velocidad estable en internet.", 5),
            ("Línea Taxis El Tuy", "Taxis", "Terminal de Pasajeros", "https://via.placeholder.com/600x300?text=Taxis", "Servicio seguro y puntual.", 4),
            ("Cooperativa Mototaxis", "Mototaxis", "Entrada Las Flores", "https://via.placeholder.com/600x300?text=Mototaxis", "Rapidez para tus traslados.", 3),
            ("Electro Tuy", "Electrodomésticos", "Av. Ayacucho", "https://via.placeholder.com/600x300?text=Electro+Tuy", "Garantía y buenas marcas.", 5),
            ("Perfumería Esencias", "Perfumerías", "C.C. Las Flores", "https://via.placeholder.com/600x300?text=Perfumeria", "Fragancias duraderas.", 4),
            ("Alcaldía Independencia", "Entes públicos", "Frente a la Plaza Bolívar", "https://via.placeholder.com/600x300?text=Alcaldia", "Gestión de trámites municipales.", 3),
            ("Clínica Paso Real", "Salud", "Sector Paso Real", "https://via.placeholder.com/600x300?text=Clinica", "Atención médica especializada.", 5),
            ("Repostería Mágica", "Dulces", "Urb. Ciudad Betania", "https://via.placeholder.com/600x300?text=Reposteria", "Tortas personalizadas increíbles.", 5),
            ("Ferretería La Roca", "Ferreterías", "Carretera Nacional", "https://via.placeholder.com/600x300?text=La+Roca", "Materiales de construcción pesados.", 4),
            ("Servicio Técnico PC", "Servicios", "Centro Comercial Paseo", "https://via.placeholder.com/600x300?text=Tecnico+PC", "Reparación confiable de equipos.", 5)
        ]
        c.executemany("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", comercios_iniciales)

precargar_datos()

# --- REGISTRO DE VISITA ---
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
c.execute("INSERT OR IGNORE INTO visitas (fecha, conteo) VALUES (?, 0)", (fecha_hoy,))
c.execute("UPDATE visitas SET conteo = conteo + 1 WHERE fecha = ?", (fecha_hoy,))

# --- CARGA DE LOGO ---
c.execute("SELECT logo_url FROM ajustes WHERE id=1")
res_logo = c.fetchone()
current_logo = res_logo[0] if res_logo else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- CABECERA ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="logo-container"><img src="{current_logo}" class="app-logo" width="180"></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

# --- CATEGORÍAS ---
lista_maestra_categorias = [
    "Salud", "Ópticas", "Laboratorios", "Farmacias", "Panadería", "Dulces", 
    "Abastos", "Supermerkados", "Ferreterías", "Carnicerías", 
    "Charcuterías", "Electrodomésticos", "Perfumerías", "Repuestos", 
    "Fibra Óptica", "Taxis", "Mototaxis", "Entes públicos", "Servicios"
]

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- GESTIÓN DE PESTAÑAS ---
tab_list = ["🏪 Guía Comercial", "🔑 Panel de Control"]
tab_publico, tab_llave_admin = st.tabs(tab_list)

with tab_llave_admin:
    st.markdown("### ⚙️ Gestión de Sistema")
    if not st.session_state.admin_logged_in:
        with st.expander("Abrir Cerradura Administrativa", expanded=True):
            admin_pass = st.text_input("Introduce la clave maestra", type="password", key="pass_admin_main")
            if st.button("Validar Acceso"):
                if admin_pass == "Juan*316*":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Clave incorrecta")
    
    if st.session_state.admin_logged_in:
        st.warning("⚠️ MODO EDICIÓN: El sistema mantiene todos los cambios guardados permanentemente en el disco.")

        if st.button("Cerrar Sesión"):
            crear_respaldo() 
            st.session_state.admin_logged_in = False
            st.rerun()
            
        accion = st.radio("Acción:", ["Añadir", "Borrar Negocio", "Ajustes Logo"], horizontal=True)
        
        if accion == "Añadir":
            with st.form("admin_add"):
                n = st.text_input("Nombre del Negocio")
                cat = st.selectbox("Categoría", lista_maestra_categorias)
                ub = st.text_input("Ubicación")
                up_file = st.file_uploader("Subir foto", type=['png', 'jpg', 'jpeg'])
                url_img = st.text_input("O Link de Imagen", value="https://via.placeholder.com/600x300")
                res = st.text_area("Escribir Reseña Inicial")
                est = st.slider("Estrellas Willian", 1, 5, 5)
                if st.form_submit_button("Guardar Negocio"):
                    final_img = url_img
                    if up_file:
                        final_img = f"data:image/png;base64,{base64.b64encode(up_file.read()).decode()}"
                    c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, final_img, res, est))
                    crear_respaldo()
                    st.success("¡Datos guardados permanentemente en el repositorio!")

        elif accion == "Ajustes Logo":
            new_logo = st.file_uploader("Seleccionar Logo", type=['png', 'jpg', 'jpeg'])
            if new_logo and st.button("Aplicar Logo"):
                encoded_logo = base64.b64encode(new_logo.read()).decode()
                c.execute("INSERT OR REPLACE INTO ajustes (id, logo_url) VALUES (1, ?)", (f"data:image/png;base64,{encoded_logo}",))
                crear_respaldo()
                st.rerun()

# --- VISTA PÚBLICA ---
with tab_publico:
    total_visitas_res = pd.read_sql_query("SELECT SUM(conteo) as total FROM visitas", conn)['total'].iloc[0]
    st.markdown(f'<div class="visitas-badge"><span style="color: #ffcc00; font-weight: bold; font-size: 1.2em;">👥 COMUNIDAD ACTIVA: {total_visitas_res if total_visitas_res else 0} Visitas</span>', unsafe_allow_html=True)
    
    app_url = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
    st.markdown(f"""
        <div style="text-align:center; margin-bottom: 20px;">
            <button class="copy-button" onclick="navigator.clipboard.writeText('{app_url}').then(() => alert('✅ ¡Enlace de la Guía copiado con éxito!'))">
                🔗 COPIAR DIRECCIÓN DE LA APP
            </button>
            <p style="color: #ffcc00; font-size: 0.9em; font-weight: bold;">{app_url}</p>
        </div>
    """, unsafe_allow_html=True)

    busq = st.text_input("🔍 ¿Qué buscas hoy en Santa Teresa?")
    df = pd.read_sql_query("SELECT * FROM comercios", conn)
    
    # FUNCIÓN CORREGIDA PARA EVITAR CLAVES DUPLICADAS
    def renderizar_tarjeta(r, prefix=""):
        st.markdown(f"##### 🏢 **{r['nombre']}**")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(r['foto_url'], use_container_width=True)
            st.write(f"📍 {r['ubicacion']}")
            st.markdown(f"⭐ Calificación Willian: {'★' * r['estrellas_w']}{'☆' * (5 - r['estrellas_w'])}")
            st.markdown(f'<a href="https://www.google.com/maps/search/{urllib.parse.quote(r["nombre"] + " Santa Teresa del Tuy")}" target="_blank" class="maps-button">📍 Ver Mapa</a>', unsafe_allow_html=True)
            
            with st.expander("✍️ Dejar mi opinión"):
                # Se agrega el prefix a las llaves (keys) para evitar el error de duplicados
                with st.form(f"{prefix}form_op_{r['id']}"):
                    u_nombre = st.text_input("Tu Nombre", key=f"{prefix}user_{r['id']}")
                    u_comentario = st.text_area("Tu comentario", key=f"{prefix}comm_{r['id']}")
                    u_estrellas = st.select_slider("Calificación", options=[1, 2, 3, 4, 5], value=5, key=f"{prefix}star_{r['id']}")
                    if st.form_submit_button("Publicar Opinión"):
                        if u_nombre and u_comentario:
                            fecha_op = datetime.now().strftime("%d/%m/%Y %H:%M")
                            c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (?,?,?,?,?)", 
                                      (r['id'], u_nombre, u_comentario, u_estrellas, fecha_op))
                            st.success("¡Gracias por tu opinión!")
                            st.rerun()
                        else:
                            st.warning("Por favor rellena los campos.")
        with col2:
            st.info(f"**Willian dice:** {r['reseña_willian']}" if r['reseña_willian'] else "Sin reseña.")
            st.markdown("**Comentarios de la comunidad:**")
            ops = pd.read_sql_query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']} ORDER BY id DESC", conn)
            if not ops.empty:
                for _, op in ops.iterrows():
                    cant_estrellas = int(op['estrellas_u']) if op['estrellas_u'] else 0
                    st.markdown(f"""
                    <div class='opinion-card'>
                        <span style='color:#ffcc00;'>{'★' * cant_estrellas}</span><br>
                        <b>{op['usuario']}</b>: {op['comentario']}<br>
                        <small style='color:gray;'>{op['fecha']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("Sé el primero en opinar.")
        st.markdown("---")

    if busq:
        df_busqueda = df[df['nombre'].str.contains(busq, case=False, na=False) | df['categoria'].str.contains(busq, case=False, na=False)]
        for _, row in df_busqueda.iterrows():
            renderizar_tarjeta(row, prefix="busq_") # Clave única para búsqueda
    
    st.markdown("### 🗂️ Explorar por Categorías")
    tabs_negocios = st.tabs(lista_maestra_categorias)
    for i, cat_name in enumerate(lista_maestra_categorias):
        with tabs_negocios[i]:
            filtrado = df[df['categoria'] == cat_name]
            if not filtrado.empty:
                for _, r in filtrado.iterrows():
                    renderizar_tarjeta(r, prefix="cat_") # Clave única para categorías

# --- PIE DE PÁGINA ---
st.markdown("""
<div class='footer-willian'>
<span class='gold-text'>Creacion Willian Almenar. Prohibida su reproducción total o pacial. TODOS LOS DERECHOS RESERVADOS.</span><br>
<span style='color: #ffcc00; font-size: 0.9em;'>Santa Teresa del Tuy 2.026</span>
</div>
""", unsafe_allow_html=True)
