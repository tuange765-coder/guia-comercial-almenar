import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile
import base64
import urllib.parse

# --- FUNCIÓN PARA MÚSICA DE FONDO (CONTROL MANUAL PARA COMPATIBILIDAD) ---
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

# --- ESTILO VENEZUELA (DISEÑO ORIGINAL) ---
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

h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
color: #ffffff !important;
}

button[data-baseweb="tab"] p {
color: #ffcc00 !important;
font-weight: bold !important;
font-size: 1.1em !important;
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

.logo-container {
text-align: center;
margin-top: -50px;
margin-bottom: 20px;
}
.app-logo {
border-radius: 50% / 30%;
border: 3px solid #ffcc00;
box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
}

input, textarea, [data-baseweb="select"] {
background-color: #ffffff !important;
color: #000000 !important;
font-weight: bold !important;
}

.footer-willian {
background: #000;
color: #fff;
padding: 30px; text-align: center;
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

[data-testid="stSidebar"] {
background-color: #1f2937;
border-right: 2px solid #ffcc00;
}

.visitas-badge {
    text-align: center;
    background: rgba(255, 204, 0, 0.1);
    border: 1px solid #ffcc00;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 20px;
}

.opinion-card {
    background: #1f2937;
    padding: 10px;
    border-left: 4px solid #ffcc00;
    margin-bottom: 10px;
    border-radius: 0 10px 10px 0;
}
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_url TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS visitas (fecha TEXT PRIMARY KEY, conteo INTEGER)')
conn.commit()

# --- REGISTRO DE VISITA DIARIA ---
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
c.execute("INSERT OR IGNORE INTO visitas (fecha, conteo) VALUES (?, 0)", (fecha_hoy,))
c.execute("UPDATE visitas SET conteo = conteo + 1 WHERE fecha = ?", (fecha_hoy,))
conn.commit()

# --- CARGA DE LOGO ---
c.execute("SELECT logo_url FROM ajustes WHERE id=1")
res_logo = c.fetchone()
current_logo = res_logo[0] if res_logo else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- CABECERA ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="logo-container"><img src="{current_logo}" class="app-logo" width="180"></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

# --- LISTA MAESTRA DE CATEGORÍAS ---
lista_maestra_categorias = [
    "Salud", "Ópticas", "Laboratorios", "Farmacias", "Dulces", 
    "Abastos", "Supermercados", "Ferreterías", "Carnicerías", 
    "Charcuterías", "Electrodomésticos", "Perfumerías", "Repuestos", 
    "Fibra Óptica", "Taxis", "Mototaxis", "Entes públicos", "Servicios"
]

# --- CONTROL POR PESTAÑAS PRINCIPALES (TAB) ---
tab_publico, tab_llave_admin = st.tabs(["🏪 Guía Comercial", "🔑 Panel de Control"])

with tab_llave_admin:
    st.markdown("### ⚙️ Gestión de Sistema")
    with st.expander("Abrir Cerradura Administrativa", expanded=False):
        admin_pass = st.text_input("Introduce la clave maestra", type="password", key="pass_admin_main")
        if admin_pass == "Juan*316*":
            st.success("Modo Editor Total Activado")
            st.markdown("### 📊 Estadísticas de Visitas")
            df_visitas = pd.read_sql_query("SELECT fecha as 'Fecha', conteo as 'Usuarios' FROM visitas ORDER BY fecha DESC LIMIT 7", conn)
            st.table(df_visitas)
            
            accion = st.radio("Acción:", ["Añadir", "Modificar/Quitar", "Borrar Negocio", "Ajustes Logo"], horizontal=True)
            
            if accion == "Añadir":
                with st.form("admin_add"):
                    n = st.text_input("Nombre del Negocio")
                    cat = st.selectbox("Categoría", lista_maestra_categorias)
                    ub = st.text_input("Ubicación")
                    up_file = st.file_uploader("Subir foto de negocio (PC)", type=['png', 'jpg', 'jpeg'])
                    url_img = st.text_input("O Link de Imagen", value="https://via.placeholder.com/600x300")
                    res = st.text_area("Escribir Reseña Inicial")
                    if st.form_submit_button("Guardar Negocio"):
                        final_img = url_img
                        if up_file:
                            final_img = f"data:image/png;base64,{base64.b64encode(up_file.read()).decode()}"
                        c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, final_img, res, 5))
                        conn.commit()
                        st.rerun()
            
            elif accion == "Ajustes Logo":
                st.write("Carga el logo de cabecera:")
                new_logo = st.file_uploader("Seleccionar Logo", type=['png', 'jpg', 'jpeg'])
                if new_logo and st.button("Aplicar Logo"):
                    encoded_logo = base64.b64encode(new_logo.read()).decode()
                    c.execute("INSERT OR REPLACE INTO ajustes (id, logo_url) VALUES (1, ?)", (f"data:image/png;base64,{encoded_logo}",))
                    conn.commit()
                    st.rerun()

with tab_publico:
    total_visitas_res = pd.read_sql_query("SELECT SUM(conteo) as total FROM visitas", conn)['total'].iloc[0]
    total_visitas = total_visitas_res if total_visitas_res else 0
    st.markdown(f'<div class="visitas-badge"><span style="color: #ffcc00; font-weight: bold; font-size: 1.2em;">👥 COMUNIDAD ACTIVA: {total_visitas} Visitas</span></div>', unsafe_allow_html=True)

    busq = st.text_input("🔍 ¿Qué buscas hoy en Santa Teresa?")
    df = pd.read_sql_query("SELECT * FROM comercios", conn)
    
    mumu_data = {
        'id': 9999, # ID ficticio para Donas Mumu
        'nombre': 'Donas Mumu',
        'categoria': 'Dulces',
        'ubicacion': 'Santa Teresa del Tuy, Sector Centro',
        'foto_url': 'https://img.freepik.com/foto-gratis/donas-glaseadas-frescas-variedad-sabores_23-2149021430.jpg',
        'reseña_willian': 'Las mejores donas de la zona, frescura garantizada y un sabor que te transporta. ¡Altamente recomendadas!',
        'estrellas_w': 5
    }

    if not df.empty:
        mask = (df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False) | df['ubicacion'].str.contains(busq, case=False) | df['reseña_willian'].str.contains(busq, case=False))
        df_busqueda = df[mask]
    else:
        df_busqueda = pd.DataFrame(columns=['id', 'nombre', 'categoria', 'ubicacion', 'foto_url', 'reseña_willian', 'estrellas_w'])

    if busq and not df_busqueda.empty:
        st.success(f"✅ Se encontraron coincidencias para '{busq}'")
            
    tabs_negocios = st.tabs(lista_maestra_categorias)
    for i, cat_name in enumerate(lista_maestra_categorias):
        with tabs_negocios[i]:
            filtrado_pestaña = df_busqueda[df_busqueda['categoria'] == cat_name]
            
            # --- FUNCIÓN INTERNA PARA MOSTRAR SECCIÓN DE OPINIONES ---
            def mostrar_opiniones(comercio_id, nombre_negocio):
                st.markdown(f"---")
                st.markdown(f"💬 **Opiniones sobre {nombre_negocio}**")
                
                # Formulario para nueva opinión
                with st.expander("Escribir mi opinión"):
                    with st.form(f"form_op_{comercio_id}"):
                        u_name = st.text_input("Tu Nombre", key=f"name_{comercio_id}")
                        u_comment = st.text_area("¿Qué te pareció este lugar?", key=f"comm_{comercio_id}")
                        u_stars = st.slider("Calificación", 1, 5, 5, key=f"star_{comercio_id}")
                        if st.form_submit_button("Enviar Opinión"):
                            if u_name and u_comment:
                                fecha_op = datetime.now().strftime("%d/%m/%Y %H:%M")
                                c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (?,?,?,?,?)", 
                                          (comercio_id, u_name, u_comment, u_stars, fecha_op))
                                conn.commit()
                                st.success("¡Gracias por tu opinión!")
                                st.rerun()
                            else:
                                st.warning("Por favor rellena tu nombre y comentario.")

                # Mostrar opiniones existentes
                ops = pd.read_sql_query(f"SELECT * FROM opiniones WHERE comercio_id = {comercio_id} ORDER BY id DESC", conn)
                if not ops.empty:
                    for _, op in ops.iterrows():
                        st.markdown(f"""
                        <div class="opinion-card">
                            <span style="color:#ffcc00; font-weight:bold;">{op['usuario']}</span> 
                            <span style="color:#888; font-size:0.8em;">({op['fecha']})</span><br>
                            {"⭐" * op['estrellas_u']}<br>
                            <p style="margin-top:5px;">{op['comentario']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("*Aún no hay opiniones. ¡Sé el primero!*")

            # --- BLOQUE DONAS MUMU ---
            if cat_name == "Dulces" and (not busq or "donas" in busq.lower() or "mumu" in busq.lower()):
                st.markdown(f"##### 🏢 **{mumu_data['nombre']}**")
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.image(mumu_data['foto_url'], use_container_width=True)
                    st.write(f"📍 **Ubicación:** {mumu_data['ubicacion']}")
                    q_maps = urllib.parse.quote(f"{mumu_data['nombre']} {mumu_data['ubicacion']} Santa Teresa del Tuy")
                    st.markdown(f'<a href="https://www.google.com/maps/search/{q_maps}" target="_blank" class="maps-button">📍 Ver en Google Maps</a>', unsafe_allow_html=True)
                with c2:
                    st.info(f"**Reseña de Willian:** {mumu_data['reseña_willian']}")
                    st.warning(f"⭐ Puntuación: {mumu_data['estrellas_w']}/5")
                mostrar_opiniones(mumu_data['id'], mumu_data['nombre'])
                st.markdown("---")

            # --- OTROS COMERCIOS ---
            if filtrado_pestaña.empty and not (cat_name == "Dulces" and (not busq or "donas" in busq.lower())):
                st.write(f"ℹ️ No hay más comercios registrados en **{cat_name}** aún.")
            else:
                for idx, r in filtrado_pestaña.iterrows():
                    if r['nombre'] == 'Donas Mumu' and cat_name == "Dulces": continue
                    st.markdown(f"##### 🏢 **{r['nombre']}**")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image(r['foto_url'], use_container_width=True)
                        st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                        query_maps = urllib.parse.quote(f"{r['nombre']} {r['ubicacion']} Santa Teresa del Tuy")
                        st.markdown(f'<a href="https://www.google.com/maps/search/{query_maps}" target="_blank" class="maps-button">📍 Ver en Google Maps</a>', unsafe_allow_html=True)
                    with col2:
                        if r['reseña_willian']:
                            st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                        else:
                            st.write("*Sin reseña disponible por ahora.*")
                    mostrar_opiniones(r['id'], r['nombre'])
                    st.markdown("---")

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class='footer-willian'>
<span class='gold-text'>© {datetime.now().year} - Diseñada por Willian Almenar</span><br>
<a href='https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app' target='_blank' style='color: #ffcc00; text-decoration: none; font-weight: bold; font-size: 1.1em;'>🔗 COMPARTIR GUÍA OFICIAL</a><br>
<p style='margin-top:10px; font-size:0.9em; opacity:0.8;'>
Aplicacion creada por Willian Almenar. Prohibida su reproduccion parcial o total, <br>
DERECHOS RESERVADOS, SANTA TERESA DEL TUY 2026.
</p>
</div>
""", unsafe_allow_html=True)
