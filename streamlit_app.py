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

# --- ESTILO VENEZUELA (MODIFICADO PARA IMPACTO VISUAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; }
    
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
    }
    .stats-stars { color: white; font-size: 1.5em; margin-bottom: 5px; text-shadow: 2px 2px 4px black; }
    .stats-content { font-size: 1.2em; font-weight: bold; color: white; text-shadow: 2px 2px 4px black; font-family: 'Arial', sans-serif; }
    .visit-number { font-size: 1.5em; color: #ffcc00; text-decoration: underline; }

    .logo-container {
        display: flex;
        justify-content: center;
        margin-top: -100px; 
        margin-bottom: 20px;
    }
    .logo-img {
        border-radius: 50%;
        border: 8px solid #111827;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.8);
        background-color: white;
        transition: transform 0.3s;
    }
    .logo-img:hover { transform: scale(1.05); }

    .main-title {
        text-align: center;
        font-size: 4em !important;
        font-weight: 900 !important;
        color: #ffcc00;
        text-shadow: 2px 2px 4px #000;
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

    .btn-venezuela {
        display: block;
        width: fit-content;
        margin: 20px auto;
        padding: 15px 30px;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
        text-decoration: none;
        color: white !important;
        border-radius: 50px;
        background: linear-gradient(to right, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        box-shadow: 0px 4px 15px rgba(255, 204, 0, 0.4);
        border: 2px solid white;
        transition: all 0.3s ease;
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
        position: relative;
    }
    
    .copyright-text {
        font-weight: bold;
        letter-spacing: 2px;
        color: #ffcc00; 
        text-transform: uppercase;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8), 0px 0px 5px rgba(255, 204, 0, 0.4);
        font-family: 'Georgia', serif;
        line-height: 1.6;
    }

    .maps-btn { display: inline-block; padding: 10px 20px; background-color: #ea4335; color: white !important; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }
    .admin-zone { background: #1f2937; padding: 25px; border: 3px solid #ffcc00; border-radius: 15px; margin: 20px 0; box-shadow: 0px 0px 15px #ffcc00; }
    .nav-divider { border-top: 2px dashed #ffcc00; margin: 40px 0; padding-top: 20px; }
    .denuncia-box { background: #ce1126; padding: 20px; border-radius: 15px; border: 2px solid #ffcc00; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA DE DATOS ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        datos_iniciales = [
            ("Panadería El Gran Paseo", "Otros", "Av. Ayacucho, frente a la Plaza Bolívar", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "Tradición tereseña con el mejor pan de banquete y dulces frescos.", 5, "https://maps.google.com/?q=Panaderia+El+Gran+Paseo"),
            ("Farmatodo Santa Teresa", "Farmacias", "Carretera Nacional, entrada a la ciudad", "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400", "El punto de referencia para medicinas y artículos personales 24h.", 5, "https://maps.google.com/?q=Farmatodo+Santa+Teresa"),
            ("Pollos El Samán", "Otros", "Av. Bolívar, sector El Centro", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400", "Los mejores pollos a la brasa con el sabor típico de la zona.", 4, "https://maps.google.com/?q=Pollos+El+Saman"),
            ("Centro Médico Tuy", "Salud", "Calle principal, Casco Central", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400", "Atención médica integral y laboratorios con años de servicio.", 4, "https://maps.google.com/?q=Centro+Medico+Tuy"),
            ("Cordonería Almenar", "Otros", "Casco Central", "https://images.unsplash.com/photo-1516478177764-9fe5bd7e9717?w=400", "Servicio artesanal de reparación de calzado con años en el Tuy.", 5, "https://maps.google.com/?q=Santa+Teresa+del+Tuy")
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

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

# MÓDULO DE RELOJ, FECHA Y VISITAS (AJUSTADO A VENEZUELA UTC-4)
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
    st.markdown(f'<div class="logo-container"><img src="{st.session_state.logo_data}" class="logo-img" width="250"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Guía Comercial Almenar</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">🚀 El Corazón Comercial de Santa Teresa del Tuy</p>', unsafe_allow_html=True)

st.markdown('<a href="https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app" target="_blank" class="btn-venezuela">🇻🇪 Visitar Guía Oficial</a>', unsafe_allow_html=True)

mensaje_wa = "¡Mira la Guía Comercial Almenar de Santa Teresa del Tuy! 🇻🇪 🚀"
link_guia = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
st.markdown(f'''
    <a href="https://wa.me/?text={mensaje_wa} {link_guia}" target="_blank" class="btn-whatsapp-tricolor">
        ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐<br>📲 COMPARTIR POR WHATSAPP
    </a>
    <div class="url-display">{link_guia}</div>
''', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# --- ACCESO DE ADMINISTRADOR ---
with st.expander("🔐 Gestión Administrativa (Solo Autor)"):
    clave = st.text_input("Ingresa clave para activar edición:", type="password", placeholder="Clave de Willian...")
    
    if clave == "Juan*316*":
        st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
        st.subheader("👨‍💻 Panel de Control Total")
        tabs = st.tabs(["🖼️ Logo", "🏢 Comercios", "💬 Opiniones", "⭐ Calificaciones", "📢 Denuncias Recibidas"])
        
        with tabs[0]:
            st.write("### Modificar Logo")
            file_logo = st.file_uploader("Cargar logo desde mi laptop", type=["png", "jpg", "jpeg"], key="logo_up")
            if st.button("Actualizar Logo"):
                if file_logo:
                    st.session_state.logo_data = imagen_a_base64(file_logo)
                    st.success("Logo actualizado.")
                    st.rerun()

        with tabs[1]:
            accion = st.radio("Acción de Comercio:", ["Agregar", "Modificar", "Quitar"], horizontal=True)
            if accion == "Agregar":
                with st.form("form_add"):
                    col1, col2 = st.columns(2)
                    nombre = col1.text_input("Nombre del Negocio")
                    cat = col2.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"])
                    ubi = st.text_input("Ubicación")
                    res = st.text_area("Tu Reseña")
                    maps = st.text_input("URL Google Maps")
                    est = st.slider("Calificación (Estrellas)", 1, 5, 5)
                    foto_file = st.file_uploader("Subir Foto", type=["png", "jpg", "jpeg"])
                    if st.form_submit_button("Guardar"):
                        url_final = imagen_a_base64(foto_file) if foto_file else "https://via.placeholder.com/400"
                        with conn.session as s:
                            s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :f, :r, :e, :m)"),
                                      {"n": nombre, "c": cat, "u": ubi, "f": url_final, "r": res, "e": est, "m": maps})
                            s.commit()
                        st.success("Agregado.")
                        st.rerun()
            elif accion == "Modificar":
                df_edit = conn.query("SELECT * FROM comercios", ttl=0)
                target_edit = st.selectbox("Comercio a editar:", df_edit['nombre'].tolist())
                row = df_edit[df_edit['nombre'] == target_edit].iloc[0]
                with st.form("form_edit_full"):
                    new_n = st.text_input("Nombre", value=row['nombre'])
                    new_cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"], index=["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"].index(row['categoria']))
                    new_ub = st.text_input("Ubicación", value=row['ubicacion'])
                    new_res = st.text_area("Tu Reseña", value=row['reseña_willian'])
                    new_est = st.slider("Estrellas", 1, 5, int(row['estrellas_w']))
                    new_m = st.text_input("URL Maps", value=row['maps_url'])
                    new_foto_file = st.file_uploader("Nueva Foto (Opcional)", type=["png", "jpg", "jpeg"])
                    if st.form_submit_button("Guardar Cambios"):
                        foto_f = imagen_a_base64(new_foto_file) if new_foto_file else row['foto_url']
                        with conn.session as s:
                            s.execute(text("UPDATE comercios SET nombre=:n, categoria=:c, ubicacion=:u, foto_url=:f, reseña_willian=:r, estrellas_w=:e, maps_url=:m WHERE id=:id"),
                                      {"n": new_n, "c": new_cat, "u": new_ub, "f": foto_f, "r": new_res, "e": new_est, "m": new_m, "id": int(row['id'])})
                            s.commit()
                        st.rerun()
            elif accion == "Quitar":
                df_del = conn.query("SELECT nombre FROM comercios", ttl=0)
                target_del = st.selectbox("Eliminar comercio:", df_del['nombre'].tolist())
                if st.button("Confirmar Eliminación"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM comercios WHERE nombre=:n"), {"n": target_del})
                        s.commit()
                    st.rerun()

        with tabs[2]:
            st.write("### Listado de Opiniones")
            df_opi = conn.query("SELECT * FROM opiniones", ttl=0)
            if not df_opi.empty:
                st.dataframe(df_opi)
                opi_id = st.number_input("ID de Opinión a quitar:", step=1)
                if st.button("Eliminar Opinión"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM opiniones WHERE id=:id"), {"id": opi_id})
                        s.commit()
                    st.rerun()

        with tabs[3]:
            resumen = conn.query("SELECT c.nombre, c.estrellas_w, AVG(o.estrellas_u) FROM comercios c LEFT JOIN opiniones o ON c.id = o.comercio_id GROUP BY c.id, c.nombre, c.estrellas_w", ttl=0)
            st.table(resumen)

        with tabs[4]:
            st.write("### Denuncias de Usuarios")
            df_den = conn.query("SELECT * FROM denuncias", ttl=0)
            if not df_den.empty:
                st.dataframe(df_den)
                den_id = st.number_input("ID de Denuncia para cambiar estatus/borrar:", step=1)
                col_d1, col_d2 = st.columns(2)
                if col_d1.button("Marcar como Atendido"):
                    with conn.session as s:
                        s.execute(text("UPDATE denuncias SET estatus='Atendido' WHERE id=:id"), {"id": den_id})
                        s.commit()
                    st.rerun()
                if col_d2.button("Eliminar Registro"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM denuncias WHERE id=:id"), {"id": den_id})
                        s.commit()
                    st.rerun()
            else:
                st.info("No hay denuncias registradas.")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if clave != "": st.error("Clave incorrecta")

# --- SECCIÓN DE DENUNCIAS PÚBLICAS ---
st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
with st.expander("📢 PÁGINA DE DENUNCIAS Y RECLAMOS"):
    st.markdown("""
        <div class="denuncia-box">
            <h2 style="color: white; text-align: center;">🛡️ Centro de Atención al Ciudadano</h2>
            <p style="color: white; text-align: center;">Si has tenido una mala experiencia o quieres reportar una irregularidad, infórmanos aquí.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_denuncia"):
        d_nombre = st.text_input("Tu Nombre (Opcional)", placeholder="Anónimo")
        d_comercio = st.text_input("Nombre del Comercio/Lugar", placeholder="Ej: Supermerkado Central")
        d_motivo = st.text_area("Describe lo sucedido (Maltrato, Precios, Higiene, etc.)")
        if st.form_submit_button("Enviar Denuncia"):
            if d_comercio and d_motivo:
                with conn.session as s:
                    s.execute(text("INSERT INTO denuncias (denunciante, comercio_afectado, motivo, fecha) VALUES (:d, :c, :m, :f)"),
                              {"d": d_nombre if d_nombre else "Anónimo", "c": d_comercio, "m": d_motivo, "f": ahora_vzla.strftime("%d/%m/%Y %H:%M")})
                    s.commit()
                st.success("Denuncia enviada correctamente. Willian Almenar revisará este reporte.")
            else:
                st.warning("Por favor, indica el comercio y el motivo.")

# --- BUSCADOR PÚBLICO ---
st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Ej: Panadería, Farmacia...", key="user_search")
df = conn.query("SELECT * FROM comercios", ttl=0)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(r['foto_url'], use_container_width=True)
            with c2:
                st.write(f"📍 {r['ubicacion']}")
                st.write(f"Calificación del Autor: {'⭐' * int(r['estrellas_w'])}")
                st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                if r['maps_url']: st.markdown(f'<a href="{r["maps_url"]}" target="_blank" class="maps-btn">📍 Ver en Maps</a>', unsafe_allow_html=True)
                st.write("---")
                st.write("💬 **Opiniones de la comunidad:**")
                df_op = conn.query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']}", ttl=0)
                for _, op in df_op.iterrows():
                    st.caption(f"**{op['usuario']}** ({op['fecha']}): {op['comentario']} - {'⭐'*op['estrellas_u']}")
                
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
                Prohibida su reproducción total o parcial.<br>
                TODOS LOS DERECHOS RESERVADOS.<br>
                SANTA TERESA DEL TUY 2026
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)
