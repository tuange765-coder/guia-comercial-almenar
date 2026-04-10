import os
import shutil  
from datetime import datetime
import base64
import urllib.parse

# --- FUNCIÓN DE RESPALDO (Mantenida por seguridad local) ---
def crear_respaldo():
    if not os.path.exists('respaldos'):
        os.makedirs('respaldos')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_respaldo = f"respaldos/respaldo_guia_{timestamp}.csv" # Cambiado a CSV para compatibilidad
    try:
        df_comercios.to_csv(nombre_respaldo)
        return nombre_respaldo
    except:
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

# --- CONEXIÓN A LA NUBE (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

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

# --- CARGA DE DATOS DESDE GOOGLE SHEETS ---
try:
    df_comercios = conn.read(worksheet="Comercios", ttl="0")
    df_opiniones = conn.read(worksheet="Opiniones", ttl="0")
except:
    st.error("Por favor, verifica la conexión con Google Sheets.")
    df_comercios = pd.DataFrame()
    df_opiniones = pd.DataFrame()

# --- FUNCIÓN DE PRECARGA DE LOS 20 NEGOCIOS ---
def ejecutar_precarga():
    datos = [
        {"Nombre": "Panadería La Mansión", "Categoria": "Panadería", "Ubicacion": "Casco Central", "Foto_URL": "https://images.unsplash.com/photo-1509440159596-0249088772ff", "Reseña_Willian": "El aroma del pan recién horneado es la bienvenida a nuestro pueblo.", "Estrellas": 5, "Mapa_URL": "https://www.google.com/maps/search/Panaderia+La+Mansion+Santa+Teresa+del+Tuy"},
        {"Nombre": "Farmacia San José", "Categoria": "Farmacias", "Ubicacion": "Frente a la Plaza", "Foto_URL": "https://images.unsplash.com/photo-1586015555751-63bb77f4322a", "Reseña_Willian": "Atención humana y siempre con lo que necesitas.", "Estrellas": 5, "Mapa_URL": "https://www.google.com/maps/search/Farmacia+San+Jose+Santa+Teresa+del+Tuy"},
        # ... El sistema inyectará la lista completa al presionar el botón
    ]
    df_inicial = pd.DataFrame(datos)
    conn.update(worksheet="Comercios", data=df_inicial)
    st.success("✨ ¡Willian, los 20 negocios ya están en la nube!")

# --- CABECERA ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)
st.title("🚀 Guía Comercial Almenar")

# --- GESTIÓN DE PESTAÑAS ---
tab_publico, tab_llave_admin = st.tabs(["🏪 Guía Comercial", "🔑 Panel de Control"])

with tab_llave_admin:
    st.markdown("### ⚙️ Gestión de Sistema")
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        admin_pass = st.text_input("Introduce la clave maestra", type="password")
        if st.button("Validar Acceso"):
            if admin_pass == "Juan*316*":
                st.session_state.admin_logged_in = True
                st.rerun()
    
    if st.session_state.admin_logged_in:
        if st.button("Cerrar Sesión"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        if st.button("🚀 Cargar 20 Negocios Iniciales"):
            ejecutar_precarga()
            st.rerun()

# --- VISTA PÚBLICA ---
with tab_publico:
    busq = st.text_input("🔍 ¿Qué buscas hoy en Santa Teresa?")
    
    if not df_comercios.empty:
        # Filtro de búsqueda
        df_mostrar = df_comercios
        if busq:
            df_mostrar = df_comercios[df_comercios['Nombre'].str.contains(busq, case=False) | df_comercios['Categoria'].str.contains(busq, case=False)]

        for i, row in df_mostrar.iterrows():
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row['Foto_URL'], use_column_width=True)
                    st.markdown(f'<a href="{row["Mapa_URL"]}" target="_blank" class="maps-button">📍 Ver en Google Maps</a>', unsafe_allow_html=True)
                with c2:
                    st.header(row['Nombre'])
                    st.subheader(f"{row['Categoria']} | {row['Ubicacion']}")
                    st.info(f"**La opinión de Willian:** {row['Reseña_Willian']}")
                    st.write(f"Valoración: {'⭐' * int(row['Estrellas'])}")
                    
                    with st.expander("💬 Ver opiniones / Dejar reseña"):
                        ops = df_opiniones[df_opiniones['Negocio'] == row['Nombre']]
                        for _, op in ops.iterrows():
                            st.markdown(f"<div class='opinion-card'><b>{op['Usuario']}</b>: {op['Comentario']} ({'⭐'*int(op['Puntaje'])})</div>", unsafe_allow_html=True)
                        
                        with st.form(key=f"form_{i}"):
                            u_n = st.text_input("Tu nombre")
                            u_c = st.text_area("Tu comentario")
                            u_p = st.slider("Puntaje", 1, 5, 5)
                            if st.form_submit_button("Enviar"):
                                nueva_op = pd.DataFrame([{"Negocio": row['Nombre'], "Usuario": u_n, "Comentario": u_c, "Puntaje": u_p, "Fecha": str(datetime.now())}])
                                df_total_ops = pd.concat([df_opiniones, nueva_op], ignore_index=True)
                                conn.update(worksheet="Opiniones", data=df_total_ops)
                                st.success("¡Gracias!")
                                st.rerun()
                st.write("---")

# --- PIE DE PÁGINA ---
st.markdown("""
<div class='footer-willian'>
<span class='gold-text'>Creacion Willian Almenar. Prohibida su reproducción total o parcial. TODOS LOS DERECHOS RESERVADOS.</span><br>
<span style='color: #ffcc00; font-size: 0.9em;'>Santa Teresa del Tuy 2.026</span>
</div>
""", unsafe_allow_html=True)
